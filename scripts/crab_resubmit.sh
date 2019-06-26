#!/bin/bash

ARGC=$#
ARGV=($@)

DIR_IDX=-1
for (( j=0; j<ARGC; j++ )); do
  if [[ ${ARGV[j]} == "-d" ]]; then
    DIR_IDX=$(( j + 1 ));
    break;
  fi
done

if (( DIR_IDX >= 0 )); then
  CRABDIR=${ARGV[DIR_IDX]};
fi

if [ -z $CRABDIR ]; then
  echo "Unable to parse crab directory name from command line arguments";
  exit 1;
fi

if [ ! -d $CRABDIR ]; then
  echo "No such directory: $CRABDIR";
  exit 1;
fi

CRAB_LOGFILE=$CRABDIR/crab.log
if [ ! -f $CRAB_LOGFILE ]; then
  echo "Not a valid CRAB directory: $CRABDIR";
  exit 1;
fi

DIR_BASENAME=$(basename $CRABDIR)
if [[ $DIR_BASENAME =~ "CHUNK" ]] && [[ ! $DIR_BASENAME =~ "CHUNK1" ]]; then
  JOBIDS=$(crab status -d $CRABDIR --json | grep "^{" | parse_crab_errors.py | grep -v 60302 | awk '{print $2}' | tr '\n' ',' | sed 's/,$//g');
  crab resubmit $* --jobids=$JOBIDS;
else
  crab resubmit $*;
fi
