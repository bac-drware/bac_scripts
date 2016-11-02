#!/bin/bash

FILE=/home/drware/BIND_DOWN

if [[ -n $(pidof -xo $$ named) ]]; then
    echo ""
    echo An instance of Bind is still running
    echo ""
    rm  $FILE
    exit 1
fi


if [ -f $FILE ];
then
   echo "File $FILE exists."
   exit 1
else
   echo "File $FILE does not exist."
   curl -s \
     -F "token=avrzhw3FU38pQ5PXefRyvDBwXo4vEW" \
     -F "user=ZTSGV9hpf8FoqDTkdPYrUD8zegRHJ4" \
     -F "message=Bind DNS is not running" \
     -F "priority=1" \
     -F "sound=gamelan" \
     https://api.pushover.net/1/messages.json
     touch $FILE
fi

