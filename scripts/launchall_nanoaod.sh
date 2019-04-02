#!/bin/bash

# DO NOT SOURCE! IT MAY KILL YOUR SHELL!

# GT choices based on: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable

export JSON_FILE_2016="Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt"
export JSON_FILE_2017="Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt"
export JSON_FILE_2018="Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt"

# requires CMSSW version 94x
export COND_DATA_2016_v2="94X_dataRun2_v4" # JEC Summer16_23Sep2016AllV4_DATA
export COND_MC_2016_v2="94X_mcRun2_asymptotic_v2" # JEC Summer16_23Sep2016V4_MC
export ERA_ARGS_2016_v2="Run2_2016,run2_miniAOD_80XLegacy"
export ERA_KEY_2016_v2="2016v2"
export DATASET_ERA_2016_v2="RunIISummer16MiniAODv2"

# requires CMSSW version 102x
export COND_DATA_2016_v3="102X_dataRun2_nanoAOD_2016_v1" # JEC Sum16_07Aug2017V11_and_Fall17_17Nov2017V6_DATA
export COND_MC_2016_v3="102X_mcRun2_asymptotic_v6" # JEC Summer16_07Aug2017_V11_MC
export ERA_ARGS_2016_v3="Run2_2016,run2_nanoAOD_94X2016"
export ERA_KEY_2016_v3="2016v3"
export DATASET_ERA_2016_v3="RunIISummer16MiniAODv3"

# these GTs were taken from previous iteration of the analysis; no recommendation found!
# requires CMSSW version 94x
export COND_DATA_2017_v1="94X_dataRun2_v6" # JEC Fall17_17Nov2017BCDEF_V6_DATA
export COND_MC_2017_v1="94X_mc2017_realistic_v14" # JEC Fall17_17Nov2017_V8_MC
export ERA_ARGS_2017_v1="Run2_2017,run2_nanoAOD_94XMiniAODv1"
export ERA_KEY_2017_v1="2017v1"
export DATASET_ERA_2017_v1="RunIIFall17MiniAOD"

# requires CMSSW version 102x
export COND_DATA_2017_v2="102X_dataRun2_v8" # JEC Fall17_17Nov2017_V32_102X_DATA
export COND_MC_2017_v2="102X_mc2017_realistic_v6" # JEC Fall17_17Nov2017_V32_102X_MC
export ERA_ARGS_2017_v2="Run2_2017,run2_nanoAOD_94XMiniAODv2"
export ERA_KEY_2017_v2="2017v2"
export DATASET_ERA_2017_v2="RunIIFall17MiniAODv2"

# requires CMSSW version 102x
export COND_DATA_2018="102X_dataRun2_Sep2018ABC_v2" # JEC Autumn18_RunABCD_V8_DATA
export COND_MC_2018="102X_upgrade2018_realistic_v18" # JEC Autumn18_V8_MC
export ERA_ARGS_2018="Run2_2018,run2_nanoAOD_102Xv1"
export ERA_KEY_2018="2018"
export DATASET_ERA_2018="RunIIAutumn18MiniAOD"

export COND_DATA_2018_PROMPT="102X_dataRun2_Prompt_v13" # JEC Autumn18_RunABCD_V8_DATA
export ERA_KEY_2018_PROMPT="2018prompt"

OPTIND=1 # reset in case getopts has been used previously in the shell

export NOF_EVENTS="-1"
export REPORT_FREQUENCY=1000
export NTHREADS=1

GENERATE_CFGS_ONLY=false
DRYRUN=""
export DATASET_FILE=""
export JOB_TYPE=""

TYPE_DATA="data"
TYPE_MC="mc"
TYPE_FAST="fast"
TYPE_SYNC="sync"

show_help() {
  echo "Usage: $0 -e <era>  -j <type> [-d] [-g] [-f <dataset file>] [-v version] [-w whitelist] [-n <events>] [-r <frequency>] [-t <threads>]" 1>&2;
  echo "Available eras: $ERA_KEY_2016_v2, $ERA_KEY_2016_v3, $ERA_KEY_2017_v1, $ERA_KEY_2017_v2, $ERA_KEY_2018, $ERA_KEY_2018_PROMPT" 1>&2;
  echo "Available job types: $TYPE_DATA, $TYPE_MC, $TYPE_FAST, $TYPE_SYNC"
  exit 0;
}

while getopts "h?dgf:j:e:v:w:n:r:t:" opt; do
  case "${opt}" in
  h|\?) show_help
        ;;
  f) export DATASET_FILE=${OPTARG}
     ;;
  d) DRYRUN="--dryrun"
     ;;
  j) export JOB_TYPE=${OPTARG}
     ;;
  g) GENERATE_CFGS_ONLY=true
     ;;
  e) export ERA=${OPTARG}
     ;;
  v) export NANOAOD_VER=${OPTARG}
     ;;
  w) export WHITELIST=${OPTARG}
     ;;
  n) export NOF_EVENTS=${OPTARG}
     ;;
  r) export REPORT_FREQUENCY=${OPTARG}
     ;;
  t) export NTHREADS=${OPTARG}
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
  exit 1;
fi

if [ "$ERA" == "$ERA_KEY_2016_v2" ]; then
  export COND_DATA=$COND_DATA_2016_v2
  export COND_MC=$COND_MC_2016_v2
  export ERA_ARGS=$ERA_ARGS_2016_v2
  export DATASET_ERA=$DATASET_ERA_2016_v2
  export JSON_FILE=$JSON_FILE_2016
  export YEAR="2016"
  if [[ ! $CMSSW_VERSION =~ ^CMSSW_9_4 ]]; then
    echo "Running $ERA with data GT $COND_DATA and MC GT $COND_MC requires CMSSW version 94x";
    exit 1;
  fi
elif [ "$ERA" == "$ERA_KEY_2016_v3" ]; then
  export COND_DATA=$COND_DATA_2016_v3
  export COND_MC=$COND_MC_2016_v3
  export ERA_ARGS=$ERA_ARGS_2016_v3
  export DATASET_ERA=$DATASET_ERA_2016_v3
  export JSON_FILE=$JSON_FILE_2016
  export YEAR="2016"
  if [[ ! $CMSSW_VERSION =~ ^CMSSW_10_2 ]]; then
    echo "Running $ERA with data GT $COND_DATA and MC GT $COND_MC requires CMSSW version 102x";
    exit 1;
  fi
elif [ "$ERA" == "$ERA_KEY_2017_v1" ]; then
  export COND_DATA=$COND_DATA_2017_v1
  export COND_MC=$COND_MC_2017_v1
  export ERA_ARGS=$ERA_ARGS_2017_v1
  export DATASET_ERA=$DATASET_ERA_2017_v1
  export JSON_FILE=$JSON_FILE_2017
  export YEAR="2017"
  if [[ ! $CMSSW_VERSION =~ ^CMSSW_9_4 ]]; then
    echo "Running $ERA with data GT $COND_DATA and MC GT $COND_MC requires CMSSW version 94x";
    exit 1;
  fi
elif [ "$ERA" == "$ERA_KEY_2017_v2" ]; then
  export COND_DATA=$COND_DATA_2017_v2
  export COND_MC=$COND_MC_2017_v2
  export ERA_ARGS=$ERA_ARGS_2017_v2
  export DATASET_ERA=$DATASET_ERA_2017_v2
  export JSON_FILE=$JSON_FILE_2017
  export YEAR="2017"
  if [[ ! $CMSSW_VERSION =~ ^CMSSW_10_2 ]]; then
    echo "Running $ERA with data GT $COND_DATA and MC GT $COND_MC requires CMSSW version 102x";
    exit 1;
  fi
elif [ "$ERA" == "$ERA_KEY_2018" ]; then
  export COND_DATA=$COND_DATA_2018
  export COND_MC=$COND_MC_2018
  export ERA_ARGS=$ERA_ARGS_2018
  export DATASET_ERA=$DATASET_ERA_2018
  export JSON_FILE=$JSON_FILE_2018
  export YEAR="2018"
  if [[ ! $CMSSW_VERSION =~ ^CMSSW_10_2 ]]; then
    echo "Running $ERA with data GT $COND_DATA and MC GT $COND_MC requires CMSSW version 102x";
    exit 1;
  fi
elif [ "$ERA" == "$ERA_KEY_2018_PROMPT" ]; then
  if [ "$JOB_TYPE" != "$TYPE_DATA" ]; then
    echo "$ERA makes sense only if job type is $TYPE_DATA";
    exit 1;
  fi
  export COND_DATA=$COND_DATA_2018_PROMPT
  export COND_MC=$COND_MC_2018
  export ERA_ARGS=$ERA_ARGS_2018
  export DATASET_ERA=$DATASET_ERA_2018
  export JSON_FILE=$JSON_FILE_2018
  export YEAR="2018"
  if [[ ! $CMSSW_VERSION =~ ^CMSSW_10_2 ]]; then
    echo "Running $ERA with data GT $COND_DATA requires CMSSW version 102x";
    exit 1;
  fi
else
  echo "Invalid era: $ERA";
fi

export BASE_DIR="$CMSSW_BASE/src/tthAnalysis/NanoAOD"
export JSON_LUMI="$BASE_DIR/data/$JSON_FILE"
export CRAB_CFG="$BASE_DIR/test/crab_cfg.py"

if [ "$JOB_TYPE" != "$TYPE_DATA" ] && \
   [ "$JOB_TYPE" != "$TYPE_MC" ]   && \
   [ "$JOB_TYPE" != "$TYPE_FAST" ] && \
   [ "$JOB_TYPE" != "$TYPE_SYNC" ]; then
  echo "Invalid job type: $JOB_TYPE";
  exit 1;
fi

if [ -z "$DATASET_FILE" ]; then
  export DATASET_FILE="$BASE_DIR/test/datasets/txt/datasets_${JOB_TYPE}_${YEAR}_${DATASET_ERA}.txt";
  read -p "Sure you want to run NanoAOD production on samples defined in $DATASET_FILE? [y/N]" -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi
fi

check_if_exists "$DATASET_FILE"

JOB_TYPE_NAME=$JOB_TYPE
if [ "$JOB_TYPE" == "$TYPE_SYNC" ]; then
  JOB_TYPE=$TYPE_MC;
  GENERATE_CFGS_ONLY=true;
else
  if [ "$NOF_EVENTS" != "-1" ]; then
    echo "You can set the number of events to other value than -1 only if you are running in $TYPE_SYNC mode"
    exit 1;
  fi
fi

if [ -z "$NANOAOD_VER" ]; then
  export NANOAOD_VER="NanoAOD_${ERA}_`date '+%Y%b%d'`";
fi

if [ -z "$YEAR" ]; then
  echo "Year not set";
  exit 1;
fi

generate_cfgs() {
  DO_THX=$1
  if [[ ! -z $DO_THX ]] && [[ $DO_THX = true ]]; then
    PY_DO_THX="True";
    PY_FILENAME=$NANOCFG_TH
  else
    PY_DO_THX="False";
    PY_FILENAME=$NANOCFG_ANY
  fi
  if [ "$JOB_TYPE" == "$TYPE_DATA" ]; then
    TIER="NANOAOD"
    COND=$COND_DATA;
    PY_IS_MC="False";
  else
    COND=$COND_MC;
    TIER="NANOAODSIM";
    PY_IS_MC="True";
  fi

  INPUT_FILE=""
  if [ "$JOB_TYPE_NAME" == "$TYPE_SYNC" ]; then

    INPUT_FILE=$(cat $DATASET_FILE | grep "^/" | awk '{print $6}')
    if [ $(echo $INPUT_FILE | wc -l) != "1" ]; then
      echo "Invalid file: $DATASET_FILE";
      exit 1;
    fi

    if [[ $INPUT_FILE =~ ^/local/ ]] || [[ $INPUT_FILE =~ ^/cms/ ]]; then
      if [[ $(JAVA_HOME="" hdfs dfs -ls $INPUT_FILE | grep $INPUT_FILE | wc -l) == "1" ]]; then
        INPUT_FILE="'file:///hdfs$INPUT_FILE'";
      else
        echo "No such file found on /hdfs: $INPUT_FILE";
        exit 1;
      fi
    elif [[ "$INPUT_FILE" =~ ^/store/ ]]; then
      INPUT_FILE="'root://cms-xrd-global.cern.ch/$INPUT_FILE'";
    else
      echo "Invalid file name: $INPUT_FILE";
      exit 1;
    fi
  fi

  CMSSW_GIT_STATUS=$(git -C $CMSSW_BASE/src log -n1 --format="%D %H %cd")
  NANOAOD_GIT_STATUS=$(git -C $BASE_DIR log -n1 --format="%D %H %cd")
  export CUSTOMISE_COMMANDS="process.MessageLogger.cerr.FwkReport.reportEvery = $REPORT_FREQUENCY\\n\
process.source.fileNames = cms.untracked.vstring($INPUT_FILE)\\n\
#process.source.eventsToProcess = cms.untracked.VEventRange()\\n\
from tthAnalysis.NanoAOD.addVariables import addVariables; addVariables(process, $PY_IS_MC,'$YEAR', $PY_DO_THX)\\n\
from tthAnalysis.NanoAOD.debug import debug; debug(process, dump = False, dumpFile = 'nano.dump', tracer = False, memcheck = False)\\n\
print('CMSSW_VERSION: $CMSSW_VERSION')\\n\
print('CMSSW repo: $CMSSW_GIT_STATUS')\\n\
print('tth-nanoAOD repo: $NANOAOD_GIT_STATUS')\\n\
print('GT: $COND')\\n\
print('era: $ERA_ARGS')\\n"

  export CMSDRIVER_OPTS="nanoAOD --step=NANO --$JOB_TYPE --era=$ERA_ARGS --conditions=$COND --no_exec --fileout=tree.root \
                         --number=$NOF_EVENTS --eventcontent $TIER --datatier $TIER --nThreads=$NTHREADS \
                         --python_filename=$PY_FILENAME"
  if [ "$JOB_TYPE" == "$TYPE_DATA" ]; then
    CMSDRIVER_OPTS="$CMSDRIVER_OPTS --lumiToProcess=$JSON_LUMI";
  fi

  echo "Generating the skeleton configuration file for CRAB $JOB_TYPE jobs: $PY_FILENAME";
  cmsDriver.py $CMSDRIVER_OPTS --customise_commands="$CUSTOMISE_COMMANDS";
}

if [ -z "$NANOCFG_ANY" ]; then
  export NANOCFG_ANY="$BASE_DIR/test/cfgs/nano_${JOB_TYPE_NAME}_${DATASET_ERA}_cfg.py";
  read -p "Sure you want to use this config file: $NANOCFG_ANY? [y/N]" -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi
  if [ ! -d $(dirname $NANOCFG_ANY) ]; then
    mkdir -p $(dirname $NANOCFG_ANY);
  fi
fi
generate_cfgs;
check_if_exists "$NANOCFG_ANY"

if [ "$JOB_TYPE_NAME" == "$TYPE_MC" ]; then
  export NANOCFG_TH="$BASE_DIR/test/cfgs/nano_${JOB_TYPE_NAME}_${DATASET_ERA}_tH_cfg.py";
  generate_cfgs true;
  check_if_exists "$NANOCFG_TH"
fi

if [ $GENERATE_CFGS_ONLY = true ]; then
  exit 0;
fi

if [ "$YEAR" == "2018" ]; then
  echo "Cannot submit jobs for 2018 era, yet (disabled in PAT*Selector* plugins";
  exit 1;
fi

check_if_exists "$JSON_LUMI"

# Saving absolute path
if [[ ! "$DATASET_FILE" =~ ^/ ]]; then
  export DATASET_FILE="$PWD/$DATASET_FILE";
  echo "Full path to the dataset file: $DATASET_FILE";
fi

echo "Checking if crab is available ..."
CRAB_AVAILABLE=$(which crab 2>/dev/null)
if [ -z "$CRAB_AVAILABLE" ]; then
  echo "crab not available! please do: source /cvmfs/cms.cern.ch/crab3/crab.sh"
  exit 1;
fi

echo "Checking if VOMS is available ..."
VOMS_PROXY_AVAILABLE=$(which voms-proxy-info 2>/dev/null)
if [ -z "$VOMS_PROXY_AVAILABLE" ]; then
  echo "VOMS proxy not available! please do: source /cvmfs/grid.cern.ch/glite/etc/profile.d/setup-ui-example.sh";
  exit 1;
fi

echo "Checking if VOMS is open long enough ..."
export MIN_HOURSLEFT=72
export MIN_TIMELEFT=$((3600 * $MIN_HOURSLEFT))
VOMS_PROXY_TIMELEFT=$(voms-proxy-info --timeleft)
if [ "$VOMS_PROXY_TIMELEFT" -lt "$MIN_TIMELEFT" ]; then
  echo "Less than $MIN_HOURSLEFT hours left for the proxy to be open: $VOMS_PROXY_TIMELEFT seconds";
  echo "Please update your proxy: voms-proxy-init -voms cms -valid 192:00";
  exit 1;
fi

export DATASET_PATTERN="^/(.*)/(.*)/[0-9A-Za-z]+$"

if [[ ! "$NANOCFG_ANY" =~ ^/ ]]; then
  export NANOCFG_ANY="$PWD/$NANOCFG_ANY";
  echo "Full path to the $JOB_TYPE cfg file: $NANOCFG_ANY";
fi

if [ "$JOB_TYPE_NAME" == "$TYPE_MC" ]; then
  if [[ ! "$NANOCFG_TH" =~ ^/ ]]; then
    export NANOCFG_TH="$PWD/$NANOCFG_TH";
    echo "Full path to the $JOB_TYPE (tH) cfg file: $NANOCFG_TH";
  fi
fi

read -p "Submitting jobs? [y/N]" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
fi

cat $DATASET_FILE | while read LINE; do
  export DATASET=$(echo $LINE | awk '{print $1}');
  unset DATASET_CATEGORY;
  unset NANOCFG

  export IS_PRIVATE=0;

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

  DATASET_SPLIT=$(echo "$DATASET" | tr '/' ' ')
  DATASET_LEADING_PART=$(echo "$DATASET_SPLIT" | awk '{print $1}')
  DATASET_THIRD_PART=$(echo "$DATASET_SPLIT" | awk '{print $3}')

  if [ "$DATASET_THIRD_PART" == "MINIAOD" ]; then
    echo "Found data sample: $DATASET";
    if [ "$JOB_TYPE" != "$TYPE_DATA" ]; then
      echo "Requested $JOB_TYPE job instead -> aborting";
      exit 1;
    fi
    if [[ "$ERA" == "$ERA_KEY_2018_PROMPT" ]] && [[ ! "$DATASET" =~ PromptReco ]]; then
      echo "$DATASET not valid for $ERA_KEY_2018_PROMPT -> continuing";
      continue;
    elif [[ "$ERA" != "$ERA_KEY_2018_PROMPT" ]] && [[ "$DATASET" =~ PromptReco ]]; then
      echo "$DATASET not valid for $ERA_KEY_2018_PROMPT -> continuing";
      continue;
    fi
  else
    echo "Found MC   sample: $DATASET";
  fi


  if [ "$DATASET_THIRD_PART" == "USER" ]; then
    echo "It's a privately produced sample";
    PRIVATE_DATASET_PATH=$(echo $LINE | awk '{print $6}');
    if [[ "$PRIVATE_DATASET_PATH" != /store/* ]]; then
      echo "The path to private datasets must start with /store";
      exit 1;
    fi
    PRIVATE_DATASET_PATH="/cms${PRIVATE_DATASET_PATH}"
    export PRIVATE_DATASET_FILES=`JAVA_HOME="" hdfs dfs -ls $PRIVATE_DATASET_PATH | grep root$ | awk '{print $8}'`;
    if [ -z "$PRIVATE_DATASET_FILES" ]; then
      echo "No files found in $PRIVATE_DATASET_PATH";
      exit 1;
    fi
    echo "Found the following files in $DATASET:"
    for PRIVATE_DATASET_FILE in $PRIVATE_DATASET_FILES; do
      echo "  $PRIVATE_DATASET_FILE"
    done
  fi

  DATASET_LEADING_PART_UPPERCASE=$(echo $DATASET_LEADING_PART | tr '[:lower:]' '[:upper:]')
  if [[ $DATASET_LEADING_PART_UPPERCASE =~ ^/THQ ]] || [[ $DATASET_LEADING_PART_UPPERCASE =~ ^/THW ]]; then
    export NANOCFG=$NANOCFG_ANY;
  else
    export NANOCFG=$NANOCFG_TH;
  fi
  echo "Using config file: $NANOCFG";

  crab submit $DRYRUN --config="$CRAB_CFG" --wait
done
