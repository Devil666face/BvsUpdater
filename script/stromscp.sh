#!/bin/bash
HOME=$PWD
DATE=$(date "+%Y%m%d")
SSH=$1

helpmsg() {
	echo "Usage: ./script/stromscp [SSH DESTINATION (always)] [DATE TAG (necessary)]"
  	echo "Options:"
  	echo "-h, --help                Display this help message"
  	echo "Example:"
	echo "./script/stromscp root@10.148.3.85"
	echo "./script/stromscp root@10.148.3.85 20230426"
	echo "./script/stromscp root@10.148.3.86"
	echo "./script/stromscp root@10.148.3.86 20230426"
	echo "Use only root user"
  	exit 0
}

check_have_dir() {
  if [ ! -d $HOME/$DATE ]; then
    echo "Not found dir for date: $DATE"
    exit 1
  fi
  echo "Dir with base $DATE was found"
	if [ -z "$(readlink -e "$HOME/$DATE/updates_$DATE.zip")" ]; then
   	echo "Not found file for date: $DATE"
 		exit 1
	fi
}

kill_scansend() {
	PID_STRING=$(ssh $SSH "ps -eH | grep ScanSendService")
	PID=$(echo $PID_STRING | cut -d ' ' -f 1)
	ssh $SSH "kill $PID"
}

scp_base() {
	scp $FILE $SSH:/strom/Updates
}

start_scansend() {
	ssh $SSH "cd /strom/ && ./ScanSendService &"
}

if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
	helpmsg
fi

if [ ! -z "$2" ]; then
  DATE=$2
fi

check_have_dir

FILE=$HOME/$DATE/updates_$DATE.zip
kill_scansend
scp_base
start_scansend
exit 0
