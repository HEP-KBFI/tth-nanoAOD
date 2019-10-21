#!/bin/bash

# DO NOT SOURCE! IT MAY KILL YOUR SHELL!

# usage:
#
# run_crab_locally.sh -d /path/to/crab/directory -i "1 2 3 4 5" -c test/cfgs/nano_data_RunIIAutumn18MiniAOD_cfg.py
#
# The jobs IDs (1, 2, 3, 4, 5 in the above example) need to be put between quotation marks,
# otherwise the command line parser won't be able to detect IDs beyond the first one.

show_help() {
  THIS_SCRIPT=$0;
  echo -ne "Usage: $(basename $THIS_SCRIPT) -d <directory> -i <job ids>"
  exit 0;
}

RUN=0;
DIRECTORY=""
JOB_IDS=""
CONFIG=""

while getopts "h?rd:i:c:" opt; do
  case "${opt}" in
  h|\?) show_help
        ;;
  r) RUN=1;
     ;;
  d) DIRECTORY=${OPTARG}
     ;;
  i) JOB_IDS=${OPTARG}
     ;;
  c) CONFIG=${OPTARG}
  esac
done

echo "Preparing directory: $DIRECTORY"
echo "Running job ids: $JOB_IDS"
echo "Using config: $CONFIG"

if [[ -z $DIRECTORY || ! -d $DIRECTORY ]]; then
  echo "No such directory: $DIRECTORY";
  exit 1;
fi

if [[ -z $CONFIG || ! -f $CONFIG ]]; then
  echo "No such file: $CONFIG";
  exit 1;
fi

if [[ ! "$DIRECTORY" =~ /local$ ]]; then
  DIRECTORY_LOCAL=$DIRECTORY/local;
  if [ ! -d $DIRECTORY_LOCAL ]; then
    echo "Running preparelocal on $DIRECTORY"
    crab preparelocal -d "$DIRECTORY";
  fi
  DIRECTORY=$DIRECTORY_LOCAL;
fi

INPUTFILES_DIR=$DIRECTORY/input_files
RUNLUMIS_DIR=$DIRECTORY/run_and_lumis

INPUTFILES_TAR=$INPUTFILES_DIR.tar.gz
RUNLUMIS_TAR=$RUNLUMIS_DIR.tar.gz

if [ ! -f $INPUTFILES_TAR ]; then
  echo "Missing file: $INPUTFILES_TAR";
  exit 1;
fi

if [ ! -f $RUNLUMIS_TAR ]; then
  echo "Missing file: $RUNLUMIS_TAR";
  exit 1;
fi

echo "Extracting $INPUTFILES_TAR to $INPUTFILES_DIR";
mkdir -p $INPUTFILES_DIR;
tar zxf $INPUTFILES_TAR -C $INPUTFILES_DIR;

echo "Extracting $RUNLUMIS_TAR to $RUNLUMIS_DIR";
mkdir -p $RUNLUMIS_DIR;
tar zxf $RUNLUMIS_TAR -C $RUNLUMIS_DIR;

INPUTFILES_BASE="job_input_file_list"
RUNLUMIS_BASE="job_lumis"

declare -A INPUT_FILES
declare -A RUNLUMI_FILES

for JOB_ID in $JOB_IDS; do
  INPUTFILES_JOB=$INPUTFILES_DIR/${INPUTFILES_BASE}_${JOB_ID}.txt;
  if [ ! -f $INPUTFILES_JOB ]; then
    echo "File $INPUTFILES_JOB does not exist. Aborting";
    exit 1;
  else
    echo "File $INPUTFILES_JOB exist";
  fi
  INPUT_FILES[$JOB_ID]=$(cat $INPUTFILES_JOB | python -c "import ast, sys; x=ast.literal_eval(sys.stdin.read()); print(' '.join(x))");

  RUNLUMIS_JOB=$RUNLUMIS_DIR/${RUNLUMIS_BASE}_${JOB_ID}.json;
  if [ ! -f $RUNLUMIS_JOB ]; then
    echo "File $RUNLUMIS_JOB does not exist. Aborting";
    exit 1;
  else
    echo "File $RUNLUMIS_JOB exist";
  fi
  RUNLUMI_FILES[$JOB_ID]=$RUNLUMIS_JOB;
done

declare -A INPUT_FILES_LOCAL

for JOB_ID in $JOB_IDS; do
  echo "Copying input files of job $JOB_ID: ${INPUT_FILES[${JOB_ID}]}";
  INPUT_LOCAL_FILES=""
  for INPUT_FILE in ${INPUT_FILES[${JOB_ID}]}; do
    INPUT_FILE_BASEDIR=$(dirname $INPUT_FILE);
    INPUT_FILE_BASENAME=$(basename $INPUT_FILE);
    INPUT_LOCAL_DIR=/hdfs/local/$USER$INPUT_FILE_BASEDIR;
    INPUT_LOCAL_FILE=$INPUT_LOCAL_DIR/$INPUT_FILE_BASENAME

    mkdir -p $INPUT_LOCAL_DIR;
    if [ ! -f $INPUT_LOCAL_FILE ]; then
      xrdcp root://cms-xrd-global.cern.ch/$INPUT_FILE $INPUT_LOCAL_FILE;
    fi
    INPUT_LOCAL_FILES+=" file://$INPUT_LOCAL_FILE";
  done
  INPUT_FILES_LOCAL[$JOB_ID]=$INPUT_LOCAL_FILES;
done

declare -A CONFIG_FILES
declare -A LOG_FILES

for JOB_ID in $JOB_IDS; do
  FILELIST=$(echo ${INPUT_FILES_LOCAL[${JOB_ID}]} | tr ' ' '\n' | sed 's/^\|$/"/g' | sed 's/$/,/g' | tr '\n' ' ')
  JOB_DIR=$(dirname $DIRECTORY)/run_${JOB_ID};
  if [ $(grep "NANOAODSIMoutput" $CONFIG | wc -l) -gt 0 ]; then
    TIER="NANOAODSIM";
  else
    TIER="NANOAOD";
  fi
  REPLACEMENT="process.source.fileNames = cms.untracked.vstring($FILELIST)\n";
  REPLACEMENT+="from FWCore.PythonUtilities.LumiList import LumiList\n";
  REPLACEMENT+="process.source.lumisToProcess = LumiList('${RUNLUMI_FILES[${JOB_ID}]}').getVLuminosityBlockRange()\n";
  REPLACEMENT+="process.${TIER}output.fileName = cms.untracked.string('file://${JOB_DIR}/tree.root')\n";
  REPLACEMENT+="process.options.numberOfThreads=cms.untracked.uint32(4)\n";
  REPLACEMENT+="process.options.numberOfStreams=cms.untracked.uint32(0)\n";
  mkdir -p $JOB_DIR;
  CONFIG_FILES[$JOB_ID]=$JOB_DIR/$(basename $CONFIG);
  LOG_FILES[$JOB_ID]=$JOB_DIR/out_${JOB_ID}.log;
  cat $CONFIG | sed "s|^process.source.fileNames = cms.untracked.vstring()|$REPLACEMENT|g" > ${CONFIG_FILES[${JOB_ID}]};
done

for JOB_ID in $JOB_IDS; do
  echo "`date` Executing jobs ${JOB_ID}";
  if [ $RUN -eq 1 ]; then
    cmsRun ${CONFIG_FILES[${JOB_ID}]} &> ${LOG_FILES[${JOB_ID}]};
  fi
done

echo "All done";
