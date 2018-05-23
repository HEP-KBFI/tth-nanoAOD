#!/bin/bash

# DO NOT SOURCE! IT MAY KILL YOUR SHELL!

# https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD#2017_Data_re_miniAOD_94X_version
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD#2017_MC_re_miniAOD_94X_version_2
# JECs according to
#   https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/94X_dataRun2_v6
#   https://cms-conddb.cern.ch/cmsDbBrowser/list/Prod/gts/94X_mc2017_realistic_v13
#
# The recommended MC GT is v14, but the associated JECs are Fall17_17Nov2017_V8_MC, whereas the v6
# data GT has Fall17_17Nov2017_V6_MC JECs; so we decided to downgrade the MC GT such that both data
# and MC JECs have the same version (the only difference between v13 and v14 MC GTs are the JECs)
export AUTOCOND_DATA_2017="94X_dataRun2_v6"
export AUTOCOND_MC_2017="94X_mc2017_realistic_v13"
export JSON_FILE_2017="Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt"
export ERA_ARGS_2017="Run2_2017,run2_nanoAOD_94XMiniAODv1"

export AUTOCOND_DATA_2016="auto:run2_data_relval"
export AUTOCOND_MC_2016="auto:run2_mc"
export JSON_FILE_2016="Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt"
export ERA_ARGS_2016="Run2_2016,run2_miniAOD_80XLegacy"

OPTIND=1 # reset in case getopts has been used previously in the shell

GENERATE_CFGS_ONLY=false
DRYRUN=""
export DATASET_FILE=""
export NANOCFG_DATA=""
export NANOCFG_MC=""

show_help() { echo "Usage: $0 -e <era> [-d] [-g | -f <dataset file>] [-D <data cfg>] [-M <mc cfg>] [-v version] [-w whitelist] [-p path]" 1>&2; exit 0; }

while getopts "h?dgf:D:M:e:v:w:p:" opt; do
  case "${opt}" in
  h|\?) show_help
        ;;
  f) export DATASET_FILE=${OPTARG}
     ;;
  d) DRYRUN="--dryrun"
     ;;
  D) export NANOCFG_DATA=${OPTARG}
     ;;
  M) export NANOCFG_MC=${OPTARG}
     ;;
  g) GENERATE_CFGS_ONLY=true
     ;;
  e) export ERA=${OPTARG}
     ;;
  v) export NANOAOD_VER=${OPTARG}
     ;;
  w) export WHITELIST=${OPTARG}
     ;;
  p) export PRIVATE_MINIAOD_PATH=${OPTARG}
     ;;
  esac
done

check_if_exists() {
  if [ ! -z "$1" ] && [ ! -f "$1" ] && [ ! -d "$1" ]; then
    echo "File or directory '$1' does not exist";
    exit 1;
  fi
}

if [ -z "$ERA" ]; then
  echo "You need to specify era!";
  exit 6;
fi

if [ "$ERA" == "2017" ]; then
  export AUTOCOND_DATA=$AUTOCOND_DATA_2017
  export AUTOCOND_MC=$AUTOCOND_MC_2017
  export JSON_FILE=$JSON_FILE_2017
  export ERA_ARGS=$ERA_ARGS_2017
elif [ "$ERA" == "2016" ]; then
  export AUTOCOND_DATA=$AUTOCOND_DATA_2016
  export AUTOCOND_MC=$AUTOCOND_MC_2016
  export JSON_FILE=$JSON_FILE_2016
  export ERA_ARGS=$ERA_ARGS_2016
else
  echo "Invalid era: $ERA";
fi

if [ -z "$NANOAOD_VER" ]; then
  export NANOAOD_VER="NanoAOD_$ERA_`date '+%Y%b%d'`";
fi

SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export JSON_LUMI="$SCRIPT_DIRECTORY/../data/$JSON_FILE"

generate_cfgs() {
  export CUSTOMISE_COMMANDS="process.MessageLogger.cerr.FwkReport.reportEvery = 1000\\n\
process.source.fileNames = cms.untracked.vstring()\\n\
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables;"
  export CUSTOMISE_COMMANDS_DATA="$CUSTOMISE_COMMANDS addJetSubstructureObservables(process, False)\\n"
  export CUSTOMISE_COMMANDS_MC="$CUSTOMISE_COMMANDS addJetSubstructureObservables(process, True)\\n"

  export COMMON_COMMANDS="nanoAOD --step=NANO --era=$ERA_ARGS --no_exec --fileout=tree.root --number=-1"

  if [ -z "$NANOCFG_DATA" ]; then
    export NANOCFG_DATA="$SCRIPT_DIRECTORY/nano_cfg_data_$ERA.py"
    echo "Generating the skeleton configuration file for CRAB data jobs: $NANOCFG_DATA"
    cmsDriver.py $COMMON_COMMANDS --customise_commands="$CUSTOMISE_COMMANDS_DATA"       \
      --data --eventcontent NANOAOD --datatier NANOAOD --conditions $AUTOCOND_DATA \
      --python_filename=$NANOCFG_DATA --lumiToProcess="$JSON_LUMI"
  else
    echo "Using the following cfg for the data jobs: $NANOCFG_DATA";
  fi

  if [ -z "$NANOCFG_MC" ]; then
    export NANOCFG_MC="$SCRIPT_DIRECTORY/nano_cfg_mc_$ERA.py"
    echo "Generating the skeleton configuration file for CRAB MC jobs: $NANOCFG_MC"
    cmsDriver.py $COMMON_COMMANDS --customise_commands="$CUSTOMISE_COMMANDS_MC"         \
      --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --conditions $AUTOCOND_MC \
      --python_filename="$NANOCFG_MC"
  else
    echo "Using the following cfg for the MC jobs: $NANOCFG_MC";
  fi
}

if [ -z "$DATASET_FILE" ]; then
  if [ $GENERATE_CFGS_ONLY = true ]; then
    generate_cfgs;
    exit 0;
  else
    echo "You must provide the dataset file!";
    exit 2;
  fi
fi

check_if_exists "$DATASET_FILE"
check_if_exists "$NANOCFG_DATA"
check_if_exists "$NANOCFG_MC"
check_if_exists "$JSON_LUMI"
check_if_exists "$PRIVATE_MINIAOD_PATH"

# Saving absolute path
if [[ ! "$DATASET_FILE" =~ ^/ ]]; then
  export DATASET_FILE="$PWD/$DATASET_FILE";
  echo "Full path to the dataset file: $DATASET_FILE";
fi

echo "Checking if crab is available ..."
CRAB_AVAILABLE=$(which crab 2>/dev/null)
if [ -z "$CRAB_AVAILABLE" ]; then
  echo "crab not available! please do: source /cvmfs/cms.cern.ch/crab3/crab.sh"
  exit 3;
fi

echo "Checking if VOMS is available ..."
VOMS_PROXY_AVAILABLE=$(which voms-proxy-info 2>/dev/null)
if [ -z "$VOMS_PROXY_AVAILABLE" ]; then
  echo "VOMS proxy not available! please do: source /cvmfs/grid.cern.ch/glite/etc/profile.d/setup-ui-example.sh";
  exit 4;
fi

echo "Checking if VOMS is open long enough ..."
export MIN_HOURSLEFT=72
export MIN_TIMELEFT=$((3600 * $MIN_HOURSLEFT))
VOMS_PROXY_TIMELEFT=$(voms-proxy-info --timeleft)
if [ "$VOMS_PROXY_TIMELEFT" -lt "$MIN_TIMELEFT" ]; then
  echo "Less than $MIN_HOURSLEFT hours left for the proxy to be open: $VOMS_PROXY_TIMELEFT seconds";
  echo "Please update your proxy: voms-proxy-init -voms cms -valid 192:00";
  exit 5;
fi

export DATASET_PATTERN="^/(.*)/(.*)/[0-9A-Za-z]+$"
declare -A DATA_CATEGORIES=([SingleElectron]= [SingleMuon]= [Tau]= [DoubleEG]= [DoubleMuon]= [MuonEG]=)

generate_cfgs

if [[ ! "$NANOCFG_DATA" =~ ^/ ]]; then
  export NANOCFG_DATA="$PWD/$NANOCFG_DATA";
  echo "Full path to the data cfg file: $NANOCFG_DATA";
fi

if [[ ! "$NANOCFG_MC" =~ ^/ ]]; then
  export NANOCFG_MC="$PWD/$NANOCFG_MC";
  echo "Full path to the MC cfg file: $NANOCFG_MC";
fi

echo "Submitting jobs ..."
cat $DATASET_FILE | while read LINE; do
  export DATASET=$(echo $LINE | awk '{print $1}');
  unset DATASET_CATEGORY;
  unset IS_DATA;

  if [ -z "$DATASET" ]; then
    continue; # it's an empty line, skip silently
  fi

  if [[ "${DATASET:0:1}" == "#" ]]; then
    continue; # it's a comment
  fi

  if [[ ! "$DATASET" =~ $DATASET_PATTERN ]]; then
    echo "Not a valid sample: '$DATASET'";
    continue;
  else
    export DATASET_CATEGORY="${BASH_REMATCH[1]}";
  fi

  if [ -z "$DATASET_CATEGORY" ]; then
    echo "Could not find the dataset category for: '$DATASET'";
    continue;
  fi

  if [[ ${DATA_CATEGORIES[$DATASET_CATEGORY]-X} == ${DATA_CATEGORIES[$DATASET_CATEGORY]} ]]; then
    export IS_DATA=1;
    echo "Found data sample: $DATASET";
  else
    export IS_DATA=0;
    echo "Found MC   sample: $DATASET";
  fi

  export IS_PRIVATE=0;
  DATASET_SPLIT=$(echo "$DATASET" | tr '/' ' ')
  DATASET_LEADING_PART=$(echo "$DATASET_SPLIT" | awk '{print $1}')
  DATASET_SUBLEADING_PART=$(echo "$DATASET_SPLIT" | awk '{print $2}')
  if [ "$DATASET_SUBLEADING_PART" == "private" ]; then
    echo "It's a privately produced sample";
    PRIVATE_DATASET_PATH="$PRIVATE_MINIAOD_PATH/$DATASET_LEADING_PART";
    if [ "$PRIVATE_DATASET_PATH" != /hdfs/cms/* ]; then
      echo "The path to private datasets must start with /hdfs/cms";
      exit 6;
    fi
    if [[ ! -d "$PRIVATE_DATASET_PATH" ]]; then
      echo "Invalid path for dataset $DATASET: $PRIVATE_DATASET_PATH";
      exit 7;
    fi
    export PRIVATE_DATASET_FILES=`find $PRIVATE_DATASET_PATH -type f -name '*.root'`;
    if [ -z "$PRIVATE_DATASET_FILES" ]; then
      echo "No files found in $PRIVATE_DATASET_PATH";
      exit 8;
    fi
    echo "Found the following files in $DATASET:"
    for PRIVATE_DATASET_FILE in $PRIVATE_DATASET_FILES; do
      echo "  $PRIVATE_DATASET_FILE"
    done
    export IS_PRIVATE=1;
  fi

  crab submit $DRYRUN --config="$SCRIPT_DIRECTORY/crab_cfg.py" --wait
done
