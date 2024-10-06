#!/bin/bash

# Проверка на выполнение с правами суперпользователя
if [ "$EUID" -ne 0 ]; then
    echo "Пожалуйста, запустите скрипт с правами суперпользователя (например, с помощью sudo)."
    exit 1
fi

# Установка необходимых пакетов
echo "Установка зависимостей..."
apt update
apt install -y auditd audispd-plugins python3 postgresql-client

# Изменение конфигурационных файлов и правил детектирования
AUDITD_CONF="/etc/audit/auditd.conf"

rm /etc/audit/rules.d/audit.rules
cp ./audit.rules /etc/audit/rules.d/audit.rules

AUDISP_REM_CONF="/etc/audit/audisp-remote.conf"
AUREMOTE_CONF="/etc/audit/plugins.d/au-remote.conf"

echo "Изменение конфигурационных файлов..."
sed -i 's/^remote_server = .*/remote_server = <your_ip>/' "$AUDISP_REM_CONF"
sed -i 's/^port = .*/port = 60/' "$AUDISP_REM_CONF"
sed -i 's/^name_format = .*/name_format = hostname/' "$AUDITD_CONF"
sed -i 's/^active = .*/active = yes/' "$AUREMOTE_CONF"

# Перезагрузка служб
echo "Перезагрузка служб auditd и audispd..."
systemctl restart auditd

echo "Скрипт завершен. Пакеты установлены, конфигурации изменены и службы перезагружены."