#!/bin/bash
HOME=$PWD
REMOTE_DIR_FOR_BASE=/mnt/ftp
LOG_FILE=$HOME/script/$(basename "$0" .sh).log
DATE=$(date "+%Y%m%d")

log() {
	echo "$1"
	echo "$(date "+%d.%m.%Y %H:%M:%S")--> $1" >> "$LOG_FILE"
}

remove() {
	log "Remove old bases from FTP"
	rm $REMOTE_DIR_FOR_BASE/DrWeb/Update/full/*
	rm $REMOTE_DIR_FOR_BASE/Kaspersky/Update/full/* 
	rm $REMOTE_DIR_FOR_BASE/Kaspersky/Update/weekly/*
	rm $REMOTE_DIR_FOR_BASE/DrWeb/Update/weekly/*
	rm $REMOTE_DIR_FOR_BASE/KPDA/*
}

copy(){
	log "Start copy archives for FTP"
	cp -r $HOME/$DATE/DrWeb/full/* $REMOTE_DIR_FOR_BASE/DrWeb/Update/full/
	cp -r $HOME/$DATE/Kaspersky/full/* $REMOTE_DIR_FOR_BASE/Kaspersky/Update/full/
	cp -r $HOME/$DATE/KPDA/* $REMOTE_DIR_FOR_BASE/KPDA/
	cp -r $HOME/$DATE/DrWeb/weekly/* $REMOTE_DIR_FOR_BASE/DrWeb/Update/weekly/
	cp -r $HOME/$DATE/Kaspersky/weekly/* $REMOTE_DIR_FOR_BASE/Kaspersky/Update/weekly/
	cp -r $HOME/$DATE/LiveCD/k* $REMOTE_DIR_FOR_BASE/Kaspersky/Utility/
	cp -r $HOME/$DATE/LiveCD/d* $REMOTE_DIR_FOR_BASE/DrWeb/Utility/
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
