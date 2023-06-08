#!/bin/bash
HOME=$PWD
REMOTE_DIR_FOR_BASE=/mnt/os
LOG_FILE=$HOME/script/$(basename "$0" .sh).log
DATE=$(date "+%Y%m%d")

log() {
	echo "$1"
	echo "$(date "+%d.%m.%Y %H:%M:%S")--> $1" >> "$LOG_FILE"
}

remove() {
	log "Clear SMB directory from previous files"
	rm -rf $REMOTE_DIR_FOR_BASE/KSC_all*
	#rm -rf $REMOTE_DIR_FOR_BASE/Updates/*
	#rm -rf $REMOTE_DIR_FOR_BASE/Updates
}

copy() {
	log "START -> Copying BVS"
	cp $HOME/$DATE/Kaspersky/full/KSC_all_$DATE.zip $REMOTE_DIR_FOR_BASE
	log "START -> Unzip BVS"
	unzip -u $REMOTE_DIR_FOR_BASE/KSC_all_$DATE.zip -d $REMOTE_DIR_FOR_BASE
	#unzip $HOME/$DATE/Kaspersky/full/KSC_all_$DATE.zip -d $REMOTE_DIR_FOR_BASE
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

remove
copy
exit 0
