import time
import os
import re
import psycopg2
from psycopg2 import sql
# from clickhouse_driver import Client

def connect_DB():
    conn = psycopg2.connect(
        dbname='your_database',
        user='your_username',
        password='your_password',
        host='localhost',
        port='5432'
    )

    return(conn)


def log_parser(line):
    if "SYSCALL" in line:
        hostname = (re.search(r'node=.+?\s', line)).group(0).strip()
        event_type = (re.search(r'type=.+?\s', line)).group(0).strip()
        pid = (re.search(r'pid=\d+?', line)).group(0).strip()
        ppid = (re.search(r'ppid=\d+?', line)).group(0).strip()
        cmdline = (re.search(r'comm=.+?\s', line)).group(0).strip()
        exe_path = (re.search(r'exe=.+?\s', line)).group(0).strip()

        parsed_log = (hostname, event_type, pid, ppid, cmdline, exe_path)
    
    elif "EXECVE" in line:
        hostname = (re.search(r'node=.+?\s', line)).group(0).strip()
        event_type = (re.search(r'type=.+?\s', line)).group(0).strip()
        cmdargs = (re.search(r'a0.+$', line)).group(0).strip()

        parsed_log = (hostname, event_type, cmdargs)

    if parsed_log == None:
        pass
    else:
        return parsed_log


def log_collector(filename):
    with open(filename, 'r') as f:
        f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue

            yield line


def EXECVE_template(logs, conn):
    cur = conn.cursor()
    insert_query = sql.SQL("""
            INSERT INTO {EXECVEL} (hostname, event_type, cmdargs)
            VALUES (%s, %s, %s)
        """)
    
    data_to_insert = (f'{logs[0]}', f'{logs[1]}' , f'{logs[2]}')
    
    push_to_DB(conn, insert_query, data_to_insert)


def SYSCALL_template(logs, conn):
    insert_query = sql.SQL("""
            INSERT INTO {SYSCALL} (parsed_log, event_type, pid, ppid, cmdline, exe_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """)
    
    data_to_insert = (f'{logs[0]}', f'{logs[1]}', f'{logs[2]}' , f'{logs[3]}' , f'{logs[4]}' , f'{logs[5]}')

    push_to_DB(conn, insert_query, data_to_insert)


def push_to_DB(conn, insert_query, data_to_insert):
    cur = conn.cursor()
    try:
        cur.execute(insert_query, data_to_insert)
        conn.commit()
        print("Данные успешно вставлены")
    except Exception as e:
        print(f"Ошибка при вставке данных: {e}")
        conn.rollback()
    finally:
        cur.close()


def insert_logs_to_DB(logs, conn):
    if len(logs) == 6:
       SYSCALL_template(logs, conn)
    elif len(logs) == 3:
        EXECVE_template(logs, conn)


def log_monitor():
    log_file = '/var/log/audit/audit.log'
    conn = connect_DB()

    for line in log_collector(log_file):
        parsed_log = log_parser(line)
        insert_logs_to_DB(parsed_log, conn)
        # check_susp(parsed_log) how postprocessing after sending to DB
        # print(parsed_log) test print