#!/bin/bash
# This script copies TEC files (*.dat) to a destination
# Previously these files are compressed 
FOLDER_HOME="/home/cesar/Desktop/luisd/scripts/"
FOLDER_SRC="${FOLDER_HOME}Obtencion_TEC/data_output/"
FOLDER_SRC2="${FOLDER_HOME}Obtencion_TEC/data_output/ToUpload/"
FOLDER_DST="${FOLDER_HOME}Main/Output_files/ToUpload/"

echo 'Compressing and moving TEC files ...'

# Compressing files
gzip --force ${FOLDER_SRC}*dat ${FOLDER_SRC2}*dat 

# Moving files 
mv ${FOLDER_SRC2}*dat.gz ${FOLDER_DST}

echo 'Done!'
