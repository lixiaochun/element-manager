#!/bin/sh
## create pyc files from py files under src/

## directory path of src/
EM_SRC_DIR=./src

## output destination of the created pyc files
EM_PYC_DIR=./pyc_file
## backup directory
EM_PYC_DIR_BACK=./pyc_file_bk

# cd
cd `dirname "$0"`

## create backup of generated pyc files
if [ -d ${EM_PYC_DIR} -o -d ${EM_PYC_DIR_BACK} ]; then
    rm -rf ${EM_PYC_DIR_BACK}
    mv ${EM_PYC_DIR} ${EM_PYC_DIR_BACK}
fi

## compile py files
echo "py compile start..."
python -m compileall ${EM_SRC_DIR} >/dev/null
echo "py compile end."

## get the list of created pyc files
pyc_file_list=`find ${EM_SRC_DIR} -type f | grep ".pyc"`

for file in ${pyc_file_list}
do
    file_dir=`dirname ${file}`
    if [ ! -d "${EM_PYC_DIR}/${file_dir}" ]; then
        mkdir -p ${EM_PYC_DIR}/${file_dir}
    fi
    # move pyc files to EM_PYC_DIR
    mv ${file} ${EM_PYC_DIR}/${file_dir}
done

echo "PYC CREATE END."
