#!/bin/bash
HOME=/bvsupdater-build
REMOTE_DIR_FOR_BASE=/mnt/cloud/BVS
SSH=pev@172.25.1.138
LOG_FILE=$HOME/script/$(basename "$0" .sh).log
DATE=$(date "+%Y%m%d")

log() {
        echo "$1"
        echo "$(date "+%d.%m.%Y %H:%M:%S")--> $1" >> "$LOG_FILE"
}

copy() {
	mkdir $REMOTE_DIR_FOR_BASE
	cp -r $HOME/$DATE/DrWeb/full/* /mnt/cloud/BVS
	cp -r $HOME/$DATE/Kaspersky/full/* /mnt/cloud/BVS
	cp -r $HOME/$DATE/KPDA /mnt/cloud/BVS
}

update_throw_ssh() {
	ssh $SSH << EOF
	sudo su
	cd /var/www/owncloud/data/administrator/files/САВЗ/БВС/
	rm -rf */*
	cp /tmp/BVS/KPDA/* /var/www/owncloud/data/administrator/files/САВЗ/БВС/KPDA/
	cp /tmp/BVS/D* /var/www/owncloud/data/administrator/files/САВЗ/БВС/Dr.Web/
	cp /tmp/BVS/K* /var/www/owncloud/data/administrator/files/САВЗ/БВС/Kaspersky/
	chown www-data: */*
	sudo -u www-data php /var/www/owncloud/occ files:scan --path administrator /var/www/owncloud/data/administrator/files/САВЗ/БВС/
	rm -rf /tmp/BVS/*
EOF
}

check_have_dir() {
	if [ ! -d $HOME/$DATE ]; then
		log "Not found dir for date: $DATE"
		exit 1
	fi
	log "Dir with base $DATE was found"
}

exec 2>>$LOG_FILE

if [ ! -z "$1" ]; then
	DATE=$1
fi
log "Find base for date: $DATE"

check_have_dir
log "PID of this process is: $$!"
log "Copying BVS to avz-cloud.mil.ru"
umount -a
mount -a
copy
update_throw_ssh
exit 0
