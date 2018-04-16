#!/bin/sh
#
# EM Start-up Script em_ctl.sh
# Parameter (mandatory) <stop|forcestop>
#
# Shell script executed by RA or a maintenance operator
# and does EM termination or forceful termination.
#
# Copyright(c) 2018 Nippon Telegraph and Telephone Corporation
#

######################################################################
# Environment Definition
# Configures the information to access EM in monitoring module
# Login User Name for EM
USERNAME="user1"
# Login Password for EM
PASSWORD="pass"
# Logical IP Address of EM
IPV4="127.0.0.1"
# Waiting Port of EM
PORT=831
# Time Interval until connection timeout
SSH_TIMEOUT=5
# EC Host Name
EC_HOST="192.168.53.132"
# EC Port
EC_PORT="18080"
# The Number of REST Retries
RESTRETRYNUM=2
# REST Timeout Time
RESTTIMEOUT=5

######################################################################

#######################################################################
# Setting:
# start_try_time: Number of trials for Start-up (times)
# start_wait_time:Waiting time for start-up (seconds)

start_try_time=3
start_wait_time=5

# stop_try_time: Number of trials for termination (times)
# stop_wait_time: Waiting time for termination (seconds)

stop_try_time=3
stop_wait_time=5

#######################################################################


########################
# Initialization

source /root/.bash_profile

ACTION=$1
EM_SUCCESS=0
EM_ERR=1
EM_NOT_RUNNING=7
EM_CHANGEOVER="changeover"

cd `dirname "$0"`
EM_INSTALL_PATH="$(cd "$(dirname "$0")/../"; pwd)/"
main_module="lib/MsfEmMain.py"
monitor_module="bin/EmMonitor.py"
pid_module="bin/em.pid"

target=$(basename ${main_module})

#######################

em_usage() {
    USAGE="Usage: $0 { start | stop [NORMAL_STOP] | status | forcestop }"
    #echo "$USAGE" >&2
    echo "$USAGE"
}

em_start() {
    echo "EM START: PRECHECK OPERATION RUNNING..."
    em_status
    result=$?

    if [ $result = $EM_ERR ]; then
        echo "EM START: ERROR HAS OCCURED IN PRECHECK."
        return $result
    elif [ $result = $EM_SUCCESS ]; then
        echo "EM START: [ SUCCESS ] PROCESS HAS BEEN ALREADY STARTED. CAN'T NEW START."
        return $EM_SUCCESS
    fi

    # No Probrem in Monitor then Start Main Module
    echo "EM START: EM MAIN MODULE STARTING..."

    python "${EM_INSTALL_PATH}${main_module}" > /dev/null 2>&1 &
    echo $! > "${EM_INSTALL_PATH}${pid_module}"
    echo "EM START: AFTER START CHECK RUNNING..."

    result=0
    for i in $(seq 1 ${start_try_time})
    do
        em_status
        if [ $? != $EM_SUCCESS ]; then
            result=$EM_ERR
        else
            result=$EM_SUCCESS
            break
        fi
        echo "EM START: CHECKING MAIN MODULE STATUS..."
        sleep $start_wait_time
    done

    if [  $result = $EM_ERR ]; then
        echo "EM START: [FAIRULE] ERROR HAS OCCURED IN AFTER START CHECK"
        return $result
    fi
        echo "EM START: [ SUCCESS ] MAIN MODULE SUCCESSFULLY STARTED."

    return $result
}

em_stop() {
    echo "EM STOP: PRECHECK OPERATION RUNNING..."
    em_status
    result=$?
    if [ $result = $EM_ERR ]; then
        echo "EM STOP:ERROR OCCURED IN PRECHECK."
        return $result
    elif [ $result = $EM_NOT_RUNNING ]; then
        echo "EM STOP: [ SUCCESS ] PROCESS HAS BEEN ALREADY SHUTDOWN. NOTHING TO DO."
        return $EM_SUCCESS
    else
        echo "EM STOP: PROCESS CONFIRMED. SHUTDOWN MAIN MODULE..."
    fi

    # No Probrem in Monitor then Stop Main Module
    if [ "$1" == ${EM_CHANGEOVER} ]; then
        pkill -USR2 -F "${EM_INSTALL_PATH}${pid_module}"
    else
        pkill -USR1 -F "${EM_INSTALL_PATH}${pid_module}"
    fi

    echo "EM STOP: AFTER STOP CHECK RUNNING..."
    result=0
    for i in $(seq 1 $stop_try_time)
    do
        em_status
        if [ $? != $EM_NOT_RUNNING ]; then
            result=$EM_ERR
        else
            result=$EM_SUCCESS
            break
        fi
        echo "EM STOP: CHECKING MAIN MODULE STATUS(${i})..."
        sleep $stop_wait_time
    done
    if [ $result != $EM_SUCCESS ]; then
        echo "EM STOP: [ FAILURE ] ERROR HAS OCCURED IN AFTER STOP CHECK"
    return $result
    fi

    rm -f "${EM_INSTALL_PATH}${pid_module}"
    echo "EM STOP: [ SUCCESS ] MAIN MODULE SUCCESSFULLY SHUTDOWN."
    return $result
}

em_forcestop() {
    echo "EM FORCESTOP: SEND SIGKILL to EM Main Module..."
    pkill -KILL -F "${EM_INSTALL_PATH}${pid_module}"
    result=$?
    rm -f "${EM_INSTALL_PATH}${pid_module}"
    if [ $result != 0 ] && [ $result != 1  ]; then
        echo "EM FORCESTOP: FAILED!!  (SEND SIGKILL to EM Main Module)"
        echo "              Please Check Errno = ${result}"
        exit $result
    fi

    if [ $result = 0 ]; then
        echo "EM FORCESTOP: [ SUCCESS ] SUCCESSFULLY SEND SIGKILL TO EM MAIN MODULE"
    elif [ $result = 1 ]; then
        echo "EM FORCESTOP: [ SUCCESS ] NO PROCESS FOUND (SEND SIGKILL to EM Main Module)"
    fi

    exit $result
}

em_status() {
    echo "EM STATUS: CHECKING EXISTENCE OF EM PROCESS..."
    if [ -e ${EM_INSTALL_PATH}${pid_module} ]; then
       tmp_pid=`cat ${EM_INSTALL_PATH}${pid_module}`
       process=$(pgrep -f "$target" | grep ${tmp_pid})
    else
       process=""
    fi

    if [ "$process" = "" ]; then
        echo "EM STATUS: [ SUCCESS ] NO RUNNING PROCESS"
        return $EM_NOT_RUNNING
    else
        echo "EM STATUS: PROCESS CONFIRMED."
    fi

    echo "EM STATUS: START MONITORING MODULE..."
    python "${EM_INSTALL_PATH}${monitor_module}" $SSH_TIMEOUT $IPV4 $PORT $USERNAME $PASSWORD > /dev/null 2>&1
    result=$?
    if [ $result != 0 ]; then
        logger -i "EM MONITOR FAILURE@em_ctl.sh:${result}"
        echo "EM STATUS: [ FAILURE ] ERROR OCCURED IN MONITORING MODULE ${result}"
        return $EM_ERR
    else
        echo "EM STATUS: [ SUCCESS ] MONITOR SUCCESSFULLY OPERATED"
    fi

    return $EM_SUCCESS
}

case $ACTION in
    start)
        em_start
        ;;
    stop)
        em_stop $2
        ;;
    forcestop)
        em_forcestop
        ;;
    status)
        em_status
        ;;
    usage|help)
        em_usage
        ;;
    *)
    em_usage
esac
