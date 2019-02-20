#!/bin/bash

# DO NOT SOURCE! IT MAY KILL YOUR SHELL!

# GT choices based on: https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable

export JSON_FILE_2016="Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt"
export JSON_FILE_2017="Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt"
export JSON_FILE_2018="" #TBA

export COND_DATA_2016_v2="80X_dataRun2_2016LegacyRepro_v4"
export COND_MC_2016_v2="80X_mcRun2_asymptotic_2016_TrancheIV_v8"
export ERA_ARGS_2016_v2="Run2_2016,run2_miniAOD_80XLegacy"
export ERA_KEY_2016_v2="2016v2"
export DATASET_ERA_2016_v2="RunIISummer16MiniAODv2"

export COND_DATA_2016_v3="94X_dataRun2_v10"
export COND_MC_2016_v3="94X_mcRun2_asymptotic_v3"
export ERA_ARGS_2016_v3="Run2_2016,run2_nanoAOD_94X2016"
export ERA_KEY_2016_v3="2016v3"
export DATASET_ERA_2016_v3="RunIISummer16MiniAODv3"

# these GTs were taken from previous iteration of the analysis; no recommendation found!
export COND_DATA_2017_v1="94X_dataRun2_v6"
export COND_MC_2017_v1="94X_mc2017_realistic_v14"
export ERA_ARGS_2017_v1="Run2_2017,run2_nanoAOD_94XMiniAODv1"
export ERA_KEY_2017_v1="2017v1"
export DATASET_ERA_2017_v1="RunIIFall17MiniAOD"

export COND_DATA_2017_v2="94X_dataRun2_v11"
export COND_MC_2017_v2="94X_mc2017_realistic_v17"
export ERA_ARGS_2017_v2="Run2_2017,run2_nanoAOD_94XMiniAODv2"
export ERA_KEY_2017_v2="2017v2"
export DATASET_ERA_2017_v2="RunIIFall17MiniAODv2"

export COND_DATA_2018="102X_dataRun2_Sep2018Rereco_v1"
export COND_MC_2018="102X_upgrade2018_realistic_v12"
export ERA_ARGS_2018="Run2_2018"
export ERA_KEY_2018="2018"
export DATASET_ERA_2018="RunIIAutumn18MiniAOD"

OPTIND=1 # reset in case getopts has been used previously in the shell

GENERATE_CFGS_ONLY=false
DRYRUN=""
export DATASET_FILE=""
export NANOCFG=""
export JOB_TYPE=""

TYPE_DATA="data"
TYPE_MC="mc"
TYPE_FAST="fast"

show_help() {
  echo "Usage: $0 -e <era>  -j <type> [-d] [-g] [-f <dataset file>] [-c <cfg>] [-v version] [-w whitelist]" 1>&2;
  echo "Available eras: $ERA_KEY_2016_v2, $ERA_KEY_2016_v3, $ERA_KEY_2017_v1, $ERA_KEY_2017_v2, $ERA_KEY_2018" 1>&2;
  echo "Available job types: $TYPE_DATA, $TYPE_MC, $TYPE_FAST"
  exit 0;
}

while getopts "h?dgf:c:j:e:v:w:p:" opt; do
  case "${opt}" in
  h|\?) show_help
        ;;
  f) export DATASET_FILE=${OPTARG}
     ;;
  d) DRYRUN="--dryrun"
     ;;
  c) export NANOCFG=${OPTARG}
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
elif [ "$ERA" == "$ERA_KEY_2016_v3" ]; then
  export COND_DATA=$COND_DATA_2016_v3
  export COND_MC=$COND_MC_2016_v3
  export ERA_ARGS=$ERA_ARGS_2016_v3
  export DATASET_ERA=$DATASET_ERA_2016_v3
  export JSON_FILE=$JSON_FILE_2016
  export YEAR="2016"
elif [ "$ERA" == "$ERA_KEY_2017_v1" ]; then
  export COND_DATA=$COND_DATA_2017_v1
  export COND_MC=$COND_MC_2017_v1
  export ERA_ARGS=$ERA_ARGS_2017_v1
  export DATASET_ERA=$DATASET_ERA_2017_v1
  export JSON_FILE=$JSON_FILE_2017
  export YEAR="2017"
elif [ "$ERA" == "$ERA_KEY_2017_v2" ]; then
  export COND_DATA=$COND_DATA_2017_v2
  export COND_MC=$COND_MC_2017_v2
  export ERA_ARGS=$ERA_ARGS_2017_v2
  export DATASET_ERA=$DATASET_ERA_2017_v2
  export JSON_FILE=$JSON_FILE_2017
  export YEAR="2017"
elif [ "$ERA" == "$ERA_KEY_2018" ]; then
  export COND_DATA=$COND_DATA_2018
  export COND_MC=$COND_MC_2018
  export ERA_ARGS=$ERA_ARGS_2018
  export DATASET_ERA=$DATASET_ERA_2018
  export JSON_FILE=$JSON_FILE_2018
  export YEAR="2018"
  echo "Era $ERA yet not supported";
  exit 1;
else
  echo "Invalid era: $ERA";
fi

export BASE_DIR="$CMSSW_BASE/src/tthAnalysis/NanoAOD"
export JSON_LUMI="$BASE_DIR/data/$JSON_FILE"
export CRAB_CFG="$BASE_DIR/test/crab_cfg.py"

if [ "$JOB_TYPE" != "$TYPE_DATA" ] && [ "$JOB_TYPE" != "$TYPE_MC" ] && [ "$JOB_TYPE" != "$TYPE_FAST" ]; then
  echo "Invalid job type: $JOB_TYPE";
  exit 1;
fi

if [ -z "$DATASET_FILE" ]; then
  export DATASET_FILE="$BASE_DIR/test/datasets/txt/datasets_${JOB_TYPE}_${YEAR}_${DATASET_ERA}.txt";
  read -p "Sure you want to run NanoAOD production on samples defined in $DATASET_FILE? " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi
fi

check_if_exists "$DATASET_FILE"

if [ -z "$NANOAOD_VER" ]; then
  export NANOAOD_VER="NanoAOD_${ERA}_`date '+%Y%b%d'`";
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

  export CUSTOMISE_COMMANDS="process.MessageLogger.cerr.FwkReport.reportEvery = 1000\\n\
process.source.fileNames = cms.untracked.vstring()\\n\
#process.source.eventsToProcess = cms.untracked.VEventRange()\\n\
from tthAnalysis.NanoAOD.addVariables import addVariables; addVariables(process)\\n\
from tthAnalysis.NanoAOD.addJetSubstructureObservables import addJetSubstructureObservables; addJetSubstructureObservables(process)\\n\
from tthAnalysis.NanoAOD.addLeptonSubtractedAK8Jets import addLeptonSubtractedAK8Jets; addLeptonSubtractedAK8Jets(process, $PY_IS_MC,'$YEAR')\\n\
from tthAnalysis.NanoAOD.debug import debug; debug(process, dump = False, dumpFile = 'nano.dump', tracer = False, memcheck = False)\\n"

  export CMSDRIVER_OPTS="nanoAOD --step=NANO --$JOB_TYPE --era=$ERA_ARGS --conditions=$COND --no_exec --fileout=tree.root \
                         --number=-1 --eventcontent $TIER --datatier $TIER --python_filename=$NANOCFG"
  if [ "$JOB_TYPE" == "$TYPE_DATA" ]; then
    CMSDRIVER_OPTS="$CMSDRIVER_OPTS --lumiToProcess=$JSON_LUMI";
  fi

  echo "Generating the skeleton configuration file for CRAB $JOB_TYPE jobs: $NANOCFG";
  cmsDriver.py $CMSDRIVER_OPTS --customise_commands="$CUSTOMISE_COMMANDS";
}

if [ -z "$NANOCFG" ]; then
  export NANOCFG="$BASE_DIR/test/cfgs/nano_${JOB_TYPE}_${DATASET_ERA}_cfg.py";
  read -p "Sure you want to use this config file: $NANOCFG? " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    [[ "$0" = "$BASH_SOURCE" ]] && exit 1 || return 1
  fi
  if [ ! -d $(dirname $NANOCFG) ]; then
    mkdir -p $(dirname $NANOCFG);
  fi
fi
generate_cfgs;
if [ $GENERATE_CFGS_ONLY = true ]; then
  exit 0;
fi

check_if_exists "$NANOCFG"
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

if [[ ! "$NANOCFG" =~ ^/ ]]; then
  export NANOCFG="$PWD/$NANOCFG";
  echo "Full path to the $JOB_TYPE cfg file: $NANOCFG";
fi

echo "Submitting jobs ..."
cat $DATASET_FILE | while read LINE; do
  export DATASET=$(echo $LINE | awk '{print $1}');
  unset DATASET_CATEGORY;

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
  else
    echo "Found MC   sample: $DATASET";
  fi


  if [ "$DATASET_THIRD_PART" == "USER" ]; then
    echo "It's a privately produced sample";
    PRIVATE_DATASET_PATH=$(echo $LINE | awk '{print $6}');
    if [[ "$PRIVATE_DATASET_PATH" != /cms/* ]]; then
      echo "The path to private datasets must start with /cms";
      exit 1;
    fi
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

  crab submit $DRYRUN --config="$CRAB_CFG" --wait
done
