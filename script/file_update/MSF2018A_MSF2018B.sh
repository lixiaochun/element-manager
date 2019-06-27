#!/bin/bash
##
##  EM_2018CoreSTEP1_2018Self.sh 
##
## In DB schema updates, SQL statement script for updating DB from 2018 core STEP1 development stage 
## to 2018 independent development stage in DB schema updates. 
##
## Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
##

## Current directoy is moved.
cd `dirname "$0"`

## File for environmental configuration is read.
source ./db_env

## Path of SQL file for updating DB schema at each release timing
DB_SCHEMA_UPDATE_SCRIPT="./MSF2018A_to_MSF2018B.sql"

psql -U ${SBY_USER} -h ${SBY_SERVER} -p 5432 ${RESTORE_DB_NAME} < ${DB_SCHEMA_UPDATE_SCRIPT}

exit 0

