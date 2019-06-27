#!/bin/bash
##
##  em_file_upgrade.sh
##
## Script for updating EM binary file
##
## Copyright(c) 2019 Nippon Telegraph and Telephone Corporation
##

WORK_MAIN=$1

EM_INSTALL_PATH=$2

DATETIME=`date +%Y%m%d%H%M%S`

## Current directory is moved.
cd `dirname "$0"`

## File path of paramter list of parameters to be taken-over
SET_OLD_VALUE=./file_oldparam_env

## Value is acquired from old file and new binary file is updated. 
function takeOverConfFile(){
  echo "start takeOverConfFile"
  for dir_name in conf bin
  do
      for file in `ls ${EM_INSTALL_PATH}/${dir_name}`
      do
          env_file=`grep ^${file}: ${SET_OLD_VALUE} | cut -d ":" -f 2`
          echo ${env_file}
  
          if [ -z "${env_file}" ]; then
              echo "next file."
              continue
          fi

          declare -A update_param_list
          change_file=`cat ${EM_INSTALL_PATH}/${dir_name}/${file} | grep -v '^#' | sed '/^$/d' | grep '=' | sed '/^[^A-Z]/d' | sed '/\s/d'`
          for line in `echo ${change_file}`
          do
              key=`echo ${line} | cut -d "=" -f 1`
              if `echo ${env_file} | grep -q "${key}"` ; then
                  echo "hit"
                    key=`echo ${line} | cut -d "=" -f 1`
                    update_param_list["${key}"]="${line}"
              fi
          done
          echo ${update_param_list[@]}
          change_file=`cat ${EM_INSTALL_PATH}/${dir_name}/${file} | grep -v '^#' | sed '/^$/d' | grep '=' | sed '/^[^A-Z]/d' | sed '/\s/d'`
          for line in `echo ${change_file}`
          do
              key=`echo ${line} | cut -d "=" -f 1`
              key_equal="${key}="
              if `echo ${update_param_list[@]} | grep -wq "${key}"` ; then
                  echo -n "Overwrite. "
                  echo ${update_param_list["${key}"]}
                  sed -i -e "s#^${key_equal}.*#${update_param_list["${key}"]}#g" ${WORK_MAIN}/${dir_name}/${file}
              fi
          done
      done
  done
}


## MAIN

takeOverConfFile

find $WORK_MAIN -name \*.sh -print | xargs chmod 777

chmod 777 $WORK_MAIN/bin/em


mv ${EM_INSTALL_PATH} ${EM_INSTALL_PATH}_${DATETIME}
mv /lib/ocf/resource.d/heartbeat/em /lib/ocf/resource.d/heartbeat/em_${DATETIME}

cp -r ${WORK_MAIN} ${EM_INSTALL_PATH}
cp ${EM_INSTALL_PATH}/bin/em /lib/ocf/resource.d/heartbeat/.

exit 0
