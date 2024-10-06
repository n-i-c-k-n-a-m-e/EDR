#!/bin/bash

# Проверка на выполнение с правами суперпользователя
if [ "$EUID" -ne 0 ]; then
    echo "Пожалуйста, запустите скрипт с правами суперпользователя (например, с помощью sudo)."
    exit 1
fi

# Установка необходимых пакетов
echo "Установка зависимостей..."
apt update
apt install -y auditd audispd-plugins python3 clickhouse-server clickhouse-client postgresql

# Изменение конфигурационных файлов и правил детектирования
AUDITD_CONF="/etc/audit/auditd.conf"
rm /etc/audit/rules.d/audit.rules
cp ./audit.rules /etc/audit/rules.d/audit.rules

echo "Изменение конфигурационных файлов..."
sed -i 's/^##tcp_listen_port = .*/tcp_listen_port = 60/' "$AUDITD_CONF"
sed -i 's/^name_format = .*/name_format = hostname/' "$AUDITD_CONF"

# Перезагрузка служб
echo "Перезагрузка служб auditd и audispd..."
systemctl restart auditd
systemctl restart clickhouse-server

echo "Скрипт завершен. Пакеты установлены, конфигурации изменены и службы перезагружены."

echo "Поднимаю БД, создаю таблицу"

echo "Запускаю коллектор и парсер логов..."

python3 ./main_server.py
