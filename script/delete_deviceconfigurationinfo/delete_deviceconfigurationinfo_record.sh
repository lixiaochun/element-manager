#!/bin/bash
##
##  Common function part delete_deviceconfigurationinfo_record.sh 
##
## Shell script for deleting configuration information table
##
## Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
##

## Environmental valuable ##################################

## DB information ##

DB_NAME="msf_em"
DB_HOST="0.0.0.0"
DB_PORT="5432"
DB_USERNAME="root"
DB_PASSWORD=""

TABLE_SIZE_LIMIT=5242880

LEAVE_RECORD_NUM=5

SQL_DIR="./sql_files"

cd `dirname $0`

flag_pgpass=0
if [ -e ~/.pgpass ]; then
    logger -t $0 "There is a .pgpass file in your home directory. Use this file as it is."
else
    logger -t $0 "Create a .pgpass file in your home directory."
    echo $DB_HOST":"$DB_PORT":"$DB_NAME":"$DB_USERNAME":"$DB_PASSWORD > ~/.pgpass
    chmod 600 ~/.pgpass
    flag_pgpass=1
fi

set_psql_param() {
if [ -n "$3" ]; then
    echo $2" "$3" "$1
else
    echo $1
fi
}

psql_param="-d "$DB_NAME
psql_param=`set_psql_param "$psql_param" "-p" "$DB_PORT"`
psql_param=`set_psql_param "$psql_param" "-U" "$DB_USERNAME"`

psql_param=`set_psql_param "$psql_param" "-h" "$DB_HOST"`


## SQL execution function
execute_psql() {
    logger -t $0 "execute : psql -Atq -v exist_num=$LEAVE_RECORD_NUM -f $SQL_DIR"/"$1 $psql_param"
    echo `psql -Atq -v exist_num=$LEAVE_RECORD_NUM -f $SQL_DIR"/"$1 $psql_param`
}

## .pgpass is deleted.
remove_pgpass() {
    if [ $flag_pgpass -eq 1 ]; then
        rm -f ~/.pgpass
        logger -t $0 "Delete ~/.pgpass"
    fi
}


## Main module

table_size=`execute_psql "get_table_size.sql"`
logger -t $0 "Table size       = "$table_size" byte"
logger -t $0 "Table size LIMIT = "$TABLE_SIZE_LIMIT" byte"

if [ -z "$table_size" ]; then
    logger -p user.err -t $0 "Failed to psql (DB access fault)"
    remove_pgpass
    exit 0
fi

if [ $table_size -le $TABLE_SIZE_LIMIT ]; then
    logger -t $0 "Data size is acceptable"
    remove_pgpass
    exit 0
fi
logger -t $0 "Data size exceeded allowable amount"

execute_psql "delete_recode.sql" > /dev/null 2>&1

logger -t $0 "Record deleted"

remove_pgpass

exit 0
