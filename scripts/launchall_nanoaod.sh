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

export DATASET_PATTERN="^/(.*)/(.*)/[0-9A-Za-z]+$"

is_valid_dataset() {
  DATASET_CANDIDATE=$1;

  if [ -z "$DATASET_CANDIDATE" ]; then
    return 0; # it's an empty line, skip silently
  fi

  if [[ "${DATASET_CANDIDATE:0:1}" == "#" ]]; then
    return 0; # it's a comment
  fi

  if [[ ! "$DATASET_CANDIDATE" =~ $DATASET_PATTERN ]]; then
    echo "Not a valid sample: '$DATASET_CANDIDATE'";
    return 0;
  fi

  return 1;
}

export NOF_EVENTS=100000
export NOF_CMSDRIVER_EVENTS="-1"
export REPORT_FREQUENCY=1000
export NTHREADS=1

GENERATE_CFGS_ONLY=false
DRYRUN=""
export DATASET_FILE=""
export JOB_TYPE=""
export PUBLISH=1
export CFG_LABEL_STR=""

TYPE_DATA="data"
TYPE_MC="mc"
TYPE_FAST="fast"
TYPE_SYNC="sync"

show_help() {
  THIS_SCRIPT=$0;
  echo -ne "Usage: $(basename $THIS_SCRIPT) -e <era>  -j <type> [-d] [-g] [-f <dataset file>] [-v version] [-w whitelist = ''] " 1>&2;
  echo -ne "[-n <job events = $NOF_EVENTS>] [-N <cfg events = $NOF_CMSDRIVER_EVENTS>] [-r <frequency = $REPORT_FREQUENCY>] " 1>&2;
  echo     "[-t <threads = $NTHREADS>] [ -p <publish: 0|1 = $PUBLISH> ] [ -s <label> = '' ]" 1>&2;
  echo "Available eras: $ERA_KEY_2016_v2, $ERA_KEY_2016_v3, $ERA_KEY_2017_v1, $ERA_KEY_2017_v2, $ERA_KEY_2018, $ERA_KEY_2018_PROMPT" 1>&2;
  echo "Available job types: $TYPE_DATA, $TYPE_MC, $TYPE_FAST, $TYPE_SYNC"
  exit 0;
}

while getopts "h?dgf:j:e:v:w:n:N:r:t:p:s:" opt; do
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
  N) export NOF_CMSDRIVER_EVENTS=${OPTARG}
     ;;
  r) export REPORT_FREQUENCY=${OPTARG}
     ;;
  t) export NTHREADS=${OPTARG}
     ;;
  p) export PUBLISH=${OPTARG}
     ;;
  s) export CFG_LABEL_STR=${OPTARG}
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

if [[ $PUBLISH != "0" ]] && [[ $PUBLISH != "1" ]]; then
  echo "Invalid value for the publish option: $PUBLISH";
  exit 1;
fi

if ! [[ $NOF_EVENTS =~ ^[0-9]+$ ]] || [[ $NOF_EVENTS == "0" ]]; then
  echo "Option -n not a valid number: $NOF_EVENTS";
  exit 1;
fi

if (! [[ $NOF_CMSDRIVER_EVENTS =~ ^[0-9]+$ ]] && [[ $NOF_CMSDRIVER_EVENTS != "-1" ]]) || [[ $NOF_CMSDRIVER_EVENTS == "0" ]]; then
  echo "Option -N not a valid number: $NOF_CMSDRIVER_EVENTS";
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
export FILEBLOCK_LIST="$BASE_DIR/test/datasets_fileblock_err.txt"

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
check_if_exists "$FILEBLOCK_LIST"

declare -A FILEBLOCK_ARR
while read -r LINE; do
  read -ra LINEARR <<<"$LINE";
  FILEBLOCK_ARR["${LINEARR[0]}"]="${LINEARR[1]}";
done < "$FILEBLOCK_LIST"
echo "Found ${#FILEBLOCK_ARR[@]} datasets with fileblock errors"

MAX_NOF_JOBS=1
declare -A DATASET_ARR
while read LINE; do
  DATASET_CANDIDATE=$(echo $LINE | awk '{print $1}');

  is_valid_dataset ${DATASET_CANDIDATE};
  if [[ $? != "1" ]]; then
    continue;
  fi

  DATASET_SPLIT=$(echo "$DATASET_CANDIDATE" | tr '/' ' ');
  DATASET_SECOND_PART=$(echo "$DATASET_SPLIT" | awk '{print $2}');
  DATASET_THIRD_PART=$(echo "$DATASET_SPLIT" | awk '{print $3}');

  if ( [[ "$JOB_TYPE" == "$TYPE_MC" ]] || [[ "$JOB_TYPE" == "$TYPE_SYNC" ]] ) && [[ "$DATASET_THIRD_PART" != "USER" ]]; then
    DATASET_CAMPAIGN=$(echo "$DATASET_SECOND_PART" | tr '-' ' ' | awk '{print $1}');
    if [ "$DATASET_CAMPAIGN" != "$DATASET_ERA" ]; then
      echo "Invalid era detected in $DATASET_CANDIDATE: $DATASET_CAMPAIGN (expected ${DATASET_ERA})";
      exit 1;
    fi
  fi

  if [ ${FILEBLOCK_ARR[$DATASET_CANDIDATE]} ]; then
    MAX_EVENTS=${FILEBLOCK_ARR[$DATASET_CANDIDATE]};
    NOF_JOBS=$(( MAX_EVENTS%NOF_EVENTS ? MAX_EVENTS/NOF_EVENTS+1 : MAX_EVENTS/NOF_EVENTS ));
    DATASET_ARR["$DATASET_CANDIDATE"]=$NOF_JOBS;
    MAX_NOF_JOBS=$(( MAX_NOF_JOBS > NOF_JOBS ? MAX_NOF_JOBS : NOF_JOBS ));
  fi
done <<< "$(cat $DATASET_FILE)"

echo "Found maximum number of jobs over all datasets that have file block issues: $MAX_NOF_JOBS"

JOB_TYPE_NAME=$JOB_TYPE
if [ "$JOB_TYPE" == "$TYPE_SYNC" ]; then
  JOB_TYPE=$TYPE_MC;
  GENERATE_CFGS_ONLY=true;
else
  if [ "$NOF_CMSDRIVER_EVENTS" != "-1" ]; then
    echo "You can set the number of events to other value than -1 only if you are running in $TYPE_SYNC mode"
    exit 1;
  fi
fi

if [ -z "$NANOAOD_VER" ]; then
  export NANOAOD_VER="${ERA}_`date '+%Y%b%d'`";
  echo "Set version to: $NANOAOD_VER"
fi

if [ -z "$YEAR" ]; then
  echo "Year not set";
  exit 1;
fi

generate_cfgs() {
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
    elif [ -f "$INPUT_FILE" ]; then
      INPUT_FILE="'file://$INPUT_FILE'";
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
from tthAnalysis.NanoAOD.addVariables import addVariables; addVariables(process, $PY_IS_MC,'$YEAR')\\n\
from tthAnalysis.NanoAOD.debug import debug; debug(process, dump = False, dumpFile = 'nano.dump', tracer = False, memcheck = False, timing = False)\\n\
print('CMSSW_VERSION: $CMSSW_VERSION')\\n\
print('CMSSW repo: $CMSSW_GIT_STATUS')\\n\
print('tth-nanoAOD repo: $NANOAOD_GIT_STATUS')\\n\
print('GT: $COND')\\n\
print('era: $ERA_ARGS')\\n"

  if [ -n "$1" ]; then
    echo "Generating cfg file for chunk #$1 with split size $NOF_EVENTS";
    CHUNK_IDX_CUR=$1;
    NOF_SKIP=$(( (CHUNK_IDX_CUR-1) * NOF_EVENTS ));
    CHUNK_COMMANDS="process.source.skipEvents=cms.untracked.uint32($NOF_SKIP)\\n";
    export CUSTOMISE_COMMANDS="${CUSTOMISE_COMMANDS}${CHUNK_COMMANDS}";
    export NOF_CFG_EVENTS=$NOF_EVENTS;
  else
    export NOF_CFG_EVENTS=$NOF_CMSDRIVER_EVENTS;
  fi

  export CMSDRIVER_OPTS="nanoAOD --step=NANO --$JOB_TYPE --era=$ERA_ARGS --conditions=$COND --no_exec --fileout=tree.root \
                         --number=$NOF_CFG_EVENTS --eventcontent $TIER --datatier $TIER --nThreads=$NTHREADS \
                         --python_filename=$NANOCFG"
  if [ "$JOB_TYPE" == "$TYPE_DATA" ]; then
    CMSDRIVER_OPTS="$CMSDRIVER_OPTS --lumiToProcess=$JSON_LUMI";
  fi

  echo "Generating the skeleton configuration file for CRAB $JOB_TYPE jobs: $NANOCFG";
  cmsDriver.py $CMSDRIVER_OPTS --customise_commands="$CUSTOMISE_COMMANDS";
}

get_cfg_name() {
  if [ -z "$CFG_LABEL_STR" ]; then
    CFG_PREFIX="${JOB_TYPE_NAME}";
  else
    CFG_PREFIX="${CFG_LABEL_STR}_${JOB_TYPE_NAME}";
  fi
  if [ -n "$1" ]; then
    echo "$BASE_DIR/test/cfgs/nano_${CFG_PREFIX}_${DATASET_ERA}_chunk_${NOF_EVENTS}_part_${1}_cfg.py";
  else
    echo "$BASE_DIR/test/cfgs/nano_${CFG_PREFIX}_${DATASET_ERA}_cfg.py";
  fi
}

if [ -z "$NANOCFG" ]; then
  export NANOCFG=$(get_cfg_name);

  read -p "Sure you want to use this config file: $NANOCFG? [y/N]" -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi

  if [ ! -d $(dirname $NANOCFG) ]; then
    mkdir -p $(dirname $NANOCFG);
  fi
fi
generate_cfgs;
check_if_exists "$NANOCFG"

if (( MAX_NOF_JOBS > 1 )); then
  for CHUNK_IDX in $(seq 1 $MAX_NOF_JOBS); do
    export NANOCFG=$(get_cfg_name $CHUNK_IDX);

    read -p "Sure you want to generate config file: $NANOCFG? [y/N]" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
    fi

    generate_cfgs $CHUNK_IDX;
    check_if_exists "$NANOCFG";
  done
fi

if [ $GENERATE_CFGS_ONLY = true ]; then
  exit 0;
fi

if [ "$YEAR" == "2018" ]; then
  echo "Cannot submit jobs for 2018 era, yet (update in PAT*Selector* plugins)";
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

if [[ ! "$NANOCFG" =~ ^/ ]]; then
  export NANOCFG="$PWD/$NANOCFG";
  echo "Full path to the $JOB_TYPE cfg file: $NANOCFG";
fi

read -p "Submitting jobs? [y/N]" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
fi

while read LINE; do
  export DATASET=$(echo $LINE | awk '{print $1}');
  unset DATASET_CATEGORY;
  unset NANOCFG;
  unset CHUNK_VER;
  unset FORCE_FILEBASED;

  export IS_PRIVATE=0;

  is_valid_dataset ${DATASET};
  if [[ $? != "1" ]]; then
    continue;
  fi

  export DATASET_CATEGORY="${BASH_REMATCH[1]}";

  if [ -z "$DATASET_CATEGORY" ]; then
    echo "Could not find the dataset category for: '$DATASET'";
    continue;
  fi

  DATASET_SPLIT=$(echo "$DATASET" | tr '/' ' ')
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

  if [ ${DATASET_ARR["$DATASET"]} ]; then
    NOF_CHUNKS=${DATASET_ARR["$DATASET"]};
    if (( NOF_CHUNKS > 1 )); then
      for CHUNK_IDX in $(seq 1 $NOF_CHUNKS); do
        export FORCE_FILEBASED=1;
        export NANOCFG=$(get_cfg_name $CHUNK_IDX);
        export CHUNK_VER="CHUNK${CHUNK_IDX}"
        echo "Using config file: $NANOCFG";

        crab submit $DRYRUN --config="$CRAB_CFG" --wait
      done
    else
      export FORCE_FILEBASED=1;
      export NANOCFG=$(get_cfg_name);
      echo "Using config file: $NANOCFG";

      crab submit $DRYRUN --config="$CRAB_CFG" --wait
    fi
  else
    export FORCE_FILEBASED=0;
    export NANOCFG=$(get_cfg_name);
    echo "Using config file: $NANOCFG";

    crab submit $DRYRUN --config="$CRAB_CFG" --wait
  fi
done <<< "$(cat $DATASET_FILE)"
