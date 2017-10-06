
USERNAME="root"

PASSWORD=""

IPV4="127.0.0.1"

PORT=830

SSH_TIMEOUT=5

start_try_time=3
start_wait_time=5



stop_try_time=3
stop_wait_time=5



source /root/.bash_profile

ACTION=$1
EM_SUCCESS=0
EM_ERR=1
EM_NOT_RUNNING=7


EM_INSTALL_PATH="$(cd "$(dirname "$0")" && pwd)/../"

main_module="lib/MsfEmMain.py"
monitor_module="bin/EmMonitor.py"

target=$(basename ${main_module})


em_usage() {
    USAGE="Usage: $0 { stop | forcestop }"
    echo "$USAGE" >&2
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

    echo "EM START: EM MAIN MODULE STARTING..."
    "${EM_INSTALL_PATH}${main_module}" > /dev/null 2>&1 &
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

    pkill -USR1 -f "${target}"

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

    echo "EM STOP: [ SUCCESS ] MAIN MODULE SUCCESSFULLY SHUTDOWN."
    return $result
}

em_forcestop() {
    echo "EM FORCESTOP: SEND SIGKILL to EM Main Module..."
    pkill -KILL -f "${target}"
    result=$?
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
    process=$(pgrep -f "$target")

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
        em_stop
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
