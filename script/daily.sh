#!/bin/bash
HOME=$PWD
UPDATES_DIR="/Updates"
STROM_DIR="/strom/Updates"
ZIP_NAME="updates_daily.zip"
BASE_ARCHIVE="KSC_all_daily.zip"
LOG_FILE=$HOME/$(basename "$0" .sh).log
DATE=$(date "+%Y%m%d")

log() {
	echo "$1"
	echo "$(date "+%d.%m.%Y %H:%M:%S")--> $1" >> "$LOG_FILE"
}

remove() {
	log "Remove temp files"
	rm $STROM_DIR/$ZIP_NAME
	rm $STROM_DIR/$BASE_ARCHIVE
}

copy(){
  log "Extract $BASE_ARCHIVE"
  unzip $BASE_ARCHIVE -d /
}

find_and_extract() {
  if ! unzip $ZIP_NAME; then
    log "Not found $ZIP_NAME"
    exit 1
  fi
  log "Zip $ZIP_NAME extract successfull"
  rm -rf $UPDATES_DIR
}

exec 2>>$LOG_FILE

cd $STROM_DIR
find_and_extract
log "PID of this process is: $$!"
copy
remove
exit 0
