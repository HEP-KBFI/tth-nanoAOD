#!/bin/bash

declare -a DATASET_FILES=(
  "test/datasets/txt/datasets_mc_2016_RunIISummer16MiniAODv3.txt"
  "test/datasets/txt/datasets_mc_2017_RunIIFall17MiniAODv2.txt"
  "test/datasets/txt/datasets_mc_2018_RunIIAutumn18MiniAOD.txt"
)

for DATASET_FILE in "${DATASET_FILES[@]}"; do
  DATASET_FILE_FULLPATH=$CMSSW_BASE/src/tthAnalysis/NanoAOD/$DATASET_FILE;
  if [ ! -f $DATASET_FILE_FULLPATH ]; then
    echo "No such file: $DATASET_FILE_FULLPATH"
    exit 1;
  fi
done

for DATASET_FILE in "${DATASET_FILES[@]}"; do
  DATASET_FILE_FULLPATH=$CMSSW_BASE/src/tthAnalysis/NanoAOD/$DATASET_FILE;
  cat $DATASET_FILE_FULLPATH | while read LINE; do
    DATASET=$(echo $LINE | awk '{print $1}');
    if [[ ! "$DATASET" =~ ^/ ]] || [[ ! "$DATASET" =~ /MINIAODSIM$ ]]; then
      continue;
    fi
    echo "Checking $DATASET ...";
    count_lumis.sh -d $DATASET -v;
  done
done
