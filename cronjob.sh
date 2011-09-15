#!/bin/sh
#
# PonyExpress Queue Management
#
# Be sure the .cfg file is copied to /etc/ponyexpress/ponyexpress.cfg
# and the user running this script has write access to /var/log/ponyexpress.*
#


##
# PonyExpress Configuration File
#
PONYEXPRESS_CFG=/etc/ponyexpress/ponyexpress.cfg
export PONYEXPRESS_CFG

##
# Log files
#
PONYEXPRESS_STDOUT_LOG=/var/log/ponyexpress.log
PONYEXPRESS_STDERR_LOG=/var/log/ponyexpress.err.log


##
# Python Binary
#
PYTHON_BIN=/usr/local/bin


log_datetime() {
  local FILE=$1; shift;
  echo "[`date +'%Y-%m-%d %H:%M:%S.%N %Z'`]: $*" >>$FILE
}

log_datetime_utc() {
  local FILE=$1; shift;
  echo "[`date --utc +'%Y-%m-%d %H:%M:%S.%N %Z'`]: $*" >>$FILE
}

##
# Run process
#
log_datetime_utc $PONYEXPRESS_STDOUT_LOG "Start"
log_datetime_utc $PONYEXPRESS_STDERR_LOG "Start"
$PYTHON_BIN -m ponyexpress.queue \
    >> $PONYEXPRESS_STDOUT_LOG \
    2>> $PONYEXPRESS_STDERR_LOG
ret=$?
log_datetime_utc $PONYEXPRESS_STDOUT_LOG "Stop"
log_datetime_utc $PONYEXPRESS_STDERR_LOG "Stop"

##
# Exit with return status of the processing
#
exit $?
