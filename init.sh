#!/bin/bash
FILE=agent.key
if [ -f "$FILE" ]; then
    echo "$FILE файл ключа найден."
else 
    echo "$FILE не найден файл ключа, поместите agent.key в текущую директорию."
    exit 1
fi
rm .env
apt-get update
apt-get install wine -y
apt-get install p7zip -y
apt-get install p7zip-full -y
apt-get install sshfs -y
apt-get install tar -y
apt-get install zip -y
apt-get install rsync -y
apt-get install curl -y
mkdir Python
tar -xzf Python-3.11.tar.gz_ -C Python/
tar -xzf ksc/util.tar.gz_ -C ksc/ 
Python/bin/python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp bvsupdater.service.tpl bvsupdater.service
sed -i 's|%PWD%|'"$PWD"'|g' ./bvsupdater.service
chmod -R 777 *
echo "Создать .env файл? [Y/n]"
read STATUS
if [[ "$STATUS" = "Y" ]]; then
  echo "KPDA_USER:"
  read KPDA_USER
  echo "KPDA_PASSWORD:"
  read KPDA_PASSWORD
  echo "ESS6_USERNAME:"
  read ESS6_USERNAME
  echo "ESS6_PASSWORD:"
  read ESS6_PASSWORD
  echo "ESS6_IP:"
  read ESS6_IP
  echo "ESS6_USERNAME:"
  read ESS6_MSVS_USERNAME
  echo "ESS6_PASSWORD:"
  read ESS6_MSVS_PASSWORD
  echo "ESS6_IP:"
  read ESS6_MSVS_IP
  echo "FSB_LOGIN:"
  read FSB_LOGIN
  echo "FSB_PASSWORD:"
  read FSB_PASSWORD
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
fi
cp agent.key drw/DRW_ESS10/
cp agent.key drw/DRW_ESS11/
cp agent.key drw/DRW_ESS11.00.0,2/
cp agent.key drw/DRW_ESS13/
cp agent.key drw/DRW_SS10/
cp agent.key drw/DRW_SS11.5/
cp agent.key drw/DRW_SS11/
cp agent.key drw/DRW_SS9/
echo "Добавить службу systemd? [Y/n]"
read SYSTEMD
if [[ "$SYSTEMD" = "Y" ]]; then
  rm /etc/systemd/system/bvsupdater.service 
  cp bvsupdater.service /etc/systemd/system
  systemctl daemon-reload
fi

