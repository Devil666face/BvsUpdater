#!/bin/bash
FILE=agent.key
if [ -f "$FILE" ]; then
    echo "$FILE файл ключа найден."
else 
    echo "$FILE не найден файл ключа, поместите agent.key в текущую директорию."
    exit 1
fi
read -p "Установить необходимые для работы пакеты? [y/n] " APT_STATUS
if [[ "$APT_STATUS" = "y" ]]; then
  apt-get update
  apt-get install wine -y
  apt-get install p7zip -y
  apt-get install p7zip-full -y
  apt-get install sshfs -y
  apt-get install zip -y
  apt-get install rsync -y
  apt-get install curl -y
fi
tar -xf ksc/util.tgz -C ksc/ && rm -f ksc/util.tgz
sed -i 's|%PWD%|'"$PWD"'|g' ./bvsupdater.service
chmod -R 777 *
read -p "Создать .env файл? [y/n] " STATUS
if [[ "$STATUS" = "y" ]]; then
  read -p "KPDA_USER:" KPDA_USER
  read -p "KPDA_PASSWORD:" KPDA_PASSWORD
  read -p "ESS6_USERNAME:" ESS6_USERNAME
  read -p "ESS6_PASSWORD:" ESS6_PASSWORD
  read -p "ESS6_IP:" ESS6_IP
  read -p "ESS6_USERNAME:" ESS6_MSVS_USERNAME
  read -p "ESS6_PASSWORD:" ESS6_MSVS_PASSWORD
  read -p "ESS6_IP:" ESS6_MSVS_IP
  read -p "FSB_LOGIN:" FSB_LOGIN
  read -p "FSB_PASSWORD:" FSB_PASSWORD
  read -p "BOT_TOKEN:" BOT_TOKEN
  read -p "CHAT_ID:" CHAT_ID
  echo "KPDA_USER=$KPDA_USER" >> .env
  echo "KPDA_PASSWORD=$KPDA_PASSWORD" >> .env
  echo "ESS6_USERNAME=$ESS6_USERNAME" >> .env
  echo "ESS6_PASSWORD=$ESS6_PASSWORD" >> .env
  echo "ESS6_IP=$ESS6_IP" >> .env
  echo "ESS6_MSVS_USERNAME=$ESS6_MSVS_USERNAME" >> .env
  echo "ESS6_MSVS_PASSWORD=$ESS6_MSVS_PASSWORD" >> .env
  echo "ESS6_MSVS_IP=$ESS6_MSVS_IP" >> .env
  echo "FSB_LOGIN=$FSB_LOGIN" >> .env
  echo "FSB_PASSWORD=$FSB_PASSWORD" >> .env
  echo "BOT_TOKEN=$BOT_TOKEN" >> .env
  echo "CHAT_ID=$CHAT_ID" >> .env
  rm .env.sample
fi
if [[ "$STATUS" = "n" ]]; then
  mv .env.sample .env
fi
cp agent.key drw/DRW_ESS10/
cp agent.key drw/DRW_ESS11/
cp agent.key drw/DRW_ESS11.00.0,2/
cp agent.key drw/DRW_ESS13/
cp agent.key drw/DRW_SS10/
cp agent.key drw/DRW_SS11.5/
cp agent.key drw/DRW_SS11/
cp agent.key drw/DRW_SS9/
read -p "Добавить службу systemd? [y/n] " SYSTEMD
if [[ "$SYSTEMD" = "y" ]]; then
  rm /etc/systemd/system/bvsupdater.service 
  cp bvsupdater.service /etc/systemd/system
  systemctl daemon-reload
fi
echo "$(date +%m.%d) $(date +%H:%M:%S)|INFO|Create log file" > updater.log
