import socket
import threading
import win32evtlog
import time

# Параметры сервера
HOST = '192.168.0.106' # Стандартный loopback interface
PORT = 65432        # Порт для прослушивания

# Лог событий Windows
system_eventlog = win32evtlog.OpenEventLog(None, 'System')
security_eventlog = win32evtlog.OpenEventLog(None, 'Security')
application_eventlog = win32evtlog.OpenEventLog(None, 'Applitcation')


# Клиент TCP
def client():
    #print(type(events))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            try:
                events = []
                flags= win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ#EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
                system_events = win32evtlog.ReadEventLog(system_eventlog, flags, 0)
                security_events = win32evtlog.ReadEventLog(security_eventlog, flags, 0)
                application_events = win32evtlog.ReadEventLog(application_eventlog, flags, 0)
                events.extend(system_events)
                events.extend(security_events)
                events.extend(application_events)
                print(type(events))
                for event in (events):
                    #message = f"EventID: {event.EventID} Type: {event.EventType} SID: {event.Sid} RESERVED: {event.Reserved} Name: {event.SourceName}, PC {event.ComputerName} MSG: {event.StringInserts[0] if event.StringInserts else 'No message'} TIME {event.TimeWritten if event.TimeWritten else '0'}"
                    message = f"{event.EventID};{event.EventType};{event.Sid};{event.Reserved};{event.SourceName};{event.ComputerName};{event.StringInserts[0] if event.StringInserts else 'No message'};{event.TimeWritten if event.TimeWritten else '0'}"
                    s.sendall(message.encode('utf-8'))
                    print('Sent:', message)
            except Exception as e:
                print(f"Ошибка при отправке данных: {e}")
            time.sleep(1) # Задержка для экономии ресурсов

#запусе клиента 
client()
