#!/bin/bash

show_help() {
  echo "Usage: $0 -d <dataset>  [-n <max_lumis>]" 1>&2;
  exit 0;
}

VERBOSE=false
DATASET=""
MAX_LUMIS=100000

while getopts "h?vd:n:" opt; do
  case "${opt}" in
  h|\?) show_help
        ;;
  v) VERBOSE=true
     ;;
  d) DATASET=${OPTARG}
     ;;
  n) export MAX_LUMIS=${OPTARG}
     ;;
  esac
done

if [ -z "$DATASET" ]; then
  echo "Required option: -d <dataset>";
  exit 1;
fi

DATASET_NAME=$(dasgoclient -query="dataset dataset=$DATASET")
if [ "$DATASET_NAME" != "$DATASET" ]; then
  echo "Invalid dataset: $DATASET";
  exit 1;
fi

NOF_FILES=$(dasgoclient -query="dataset dataset=$DATASET | grep dataset.num_file" -unique | grep -v "^\[")
NOF_EVENTS=$(dasgoclient -query="dataset dataset=$DATASET | grep dataset.nevents" -unique | grep -v "^\[")
EVENTS_PER_FILE=$(python -c "print($NOF_EVENTS/$NOF_FILES)")

LARGEST_FILE_LINE=$(dasgoclient -query="file dataset=$DATASET | grep file.name | grep file.nevents" | sort -nr -k2 | head -n1)
LARGEST_FILE_NAME=$(echo $LARGEST_FILE_LINE | awk '{print $1}')
LARGEST_FILE_EVENTS=$(echo $LARGEST_FILE_LINE | awk '{print $2}')

echo "Number of files: $NOF_FILES"
echo "Number of events: $NOF_EVENTS"
echo "Average number of events per file: $EVENTS_PER_FILE"
echo "Largest file $LARGEST_FILE_NAME contains $LARGEST_FILE_EVENTS events"

BLOCKS=$(dasgoclient -query="block dataset=$DATASET" 2>/dev/null)
BAD_BLOCKS=0
NOF_BLOCKS=0
for BLOCK in $BLOCKS; do
  NOF_BLOCKS=$((NOF_BLOCKS+1))
  LUMIS=$(dasgoclient -query="lumi block=$BLOCK" 2>/dev/null);
  NOF_LUMIS_SUM=0
  for LUMI in $LUMIS; do
    NOF_LUMIS=$(echo "$LUMI" | tr -cd ',' | wc -c);
    NOF_LUMIS=$((NOF_LUMIS+1));
    NOF_LUMIS_SUM=$((NOF_LUMIS_SUM+NOF_LUMIS));
  done

  if [ "$NOF_LUMIS_SUM" -gt "$MAX_LUMIS" ]; then
    echo "ERROR: found $NOF_LUMIS_SUM > $MAX_LUMIS lumis in block $BLOCK";
    BAD_BLOCKS=$((BAD_BLOCKS+1))
  elif [ $VERBOSE = true ]; then
    echo "Found $NOF_LUMIS_SUM lumis in block $BLOCK";
  fi
done

if [ "$BAD_BLOCKS" -gt "0" ]; then
  echo -n "Dataset $DATASET is NOT compatible with EventAwareLumiBased splitting as it has "
  echo    "$BAD_BLOCKS blocks (out of $NOF_BLOCKS blocks) containing more than $MAX_LUMIS lumis";
else
  echo "Dataset $DATASET is compatible with EventAwareLumiBased splitting";
fi
