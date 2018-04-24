#!/usr/bin/env python

# Runs nanoAOD Ntuple production with SLURM instead of CRAB

import logging, sys, argparse, os, jinja2, shutil, stat

makefile_template = '''.DEFAULT_GOAL := all
SHELL := /bin/bash

all: sbatch_nanoAOD

.PHONY: clean

clean: {% for entry in file_map.values() %}
\trm -f {{ entry['output_file'] }}
{%- endfor %}

sbatch_nanoAOD:
\t{{ shell_wrapper }}

{% for entry in file_map.values() %}
{{ entry['output_file'] }}: sbatch_nanoAOD
\t:
{% endfor %}
'''

shell_template = '''#!/bin/bash

echo 'Unsetting JAVA_HOME=$JAVA_HOME'
unset JAVA_HOME

echo "Time is: `date`"
echo "Hostname: `hostname`"
echo "Current directory: `pwd`"

EXIT_CODE=0
OUTPUT_FILE="{{ output_file }}"
OUTPUT_BASE=`basename $OUTPUT_FILE`
OUTPUT_DIR="`dirname $OUTPUT_FILE`"

mkdir -p $OUTPUT_DIR

if [[ "$OUTPUT_DIR" =~ ^/hdfs* && ( ! -z $(which hadoop) ) ]]; then
  cp_cmd="hadoop fs -copyFromLocal";
  st_cmd="hadoop fs -stat '%b'";
  OUTPUT_DIR=${OUTPUT_DIR#/hdfs}
else
  cp_cmd=cp;
  st_cmd="stat --printf='%s'"
fi

JOB_DIR="{{ job_dir }}/$SLURM_JOBID"
echo "Creating directory and going to: $JOB_DIR"
mkdir -p $JOB_DIR
cd $JOB_DIR

echo "Starting nanoAOD production at `date`"
cmsRun {{ cfg_file }} &> {{ log_file }}
EXIT_CODE=$?

echo "Finished nanoAOD production at `date` with exit code $EXIT_CODE"

echo "Current directory listing"
ls -l

EXPECTED_OUTPUT_FILE=$JOB_DIR/tree.root

if [ ! -f "$EXPECTED_OUTPUT_FILE" ]; then
  echo "Unable to find the output file $EXPECTED_OUTPUT_FILE";
  EXIT_CODE=1
fi


OUTPUT_FILE_SIZE=$(stat -c '%s' $EXPECTED_OUTPUT_FILE)
if [ -n "$OUTPUT_FILE_SIZE" ] && [ $OUTPUT_FILE_SIZE -ge 1000 ]; then
  echo "$cp_cmd $EXPECTED_OUTPUT_FILE $OUTPUT_DIR/$OUTPUT_BASE"

  CP_RETRIES=0
  COPIED=false
  while [ $CP_RETRIES -lt 3 ]; do
    CP_RETRIES=$[CP_RETRIES + 1];
    $cp_cmd $EXPECTED_OUTPUT_FILE $OUTPUT_DIR/$OUTPUT_BASE

    # add a small delay before stat'ing the file
    sleep 5s

    REMOTE_SIZE=$($st_cmd $OUTPUT_FILE)
    if [ "$REMOTE_SIZE" == "$OUTPUT_FILE_SIZE" ]; then
      COPIED=true
      break;
    else
      continue;
    fi
  done

  if [ ! $COPIED ]; then
    EXIT_CODE=1;
  fi

else
  echo "$EXPECTED_OUTPUT_FILE is broken, will exit with code 1."
  rm $EXPECTED_OUTPUT_FILE
  EXIT_CODE=1
fi

echo "Cleaning up"
cd -
rm -rf $JOB_DIR
exit $EXIT_CODE

'''

shell_wrapper_template ='''#!/bin/bash

OUTPUT_FILES=()
{% for entry in file_map.values() %}
OUTPUT_FILES+=('{{ entry['output_file'] }}')
{%- endfor %}

JOB_IDS=()

{% for entry in file_map.values() %}
if [ ! -f {{ entry['output_file'] }} ]; then
  SBATCH_OUT=`sbatch --mem=1800M --partition=small --output={{ entry['logfile'] }} {{ entry['shell_script'] }}`
  SBATCH_JOBID=`echo "$SBATCH_OUT" | awk '{print $4}'`
  JOB_IDS+=("$SBATCH_JOBID")
  echo "Submitted job $SBATCH_JOBID"
fi
{% endfor %}

JOB_IDS_CAT=`IFS=, ; echo "${JOB_IDS[*]}"`

while true; do
  STILL_ALIVE=`squeue --job "$JOB_IDS_CAT" -h | wc -l`
  if [ "$STILL_ALIVE" != "0" ]; then
    echo "$STILL_ALIVE jobs still left ..."
    sleep 60;
  else
    break;
  fi
done

'''

nano_cfg_additions = '''
process.source.fileNames  = cms.untracked.vstring('file://{{ input_filename }}')
process.source.skipEvents = cms.untracked.uint32({{ skip_events }})
process.maxEvents.input   = cms.untracked.int32({{ max_events }})

'''

if __name__ == '__main__':
  logging.basicConfig(
    stream = sys.stdout,
    level  = logging.INFO,
    format = '%(asctime)s - %(levelname)s: %(message)s'
  )

  class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
      if text.startswith('R|'):
        return text[2:].splitlines()
      return argparse.HelpFormatter._split_lines(self, text, width)

  parser = argparse.ArgumentParser(
    formatter_class = lambda prog: SmartFormatter(prog, max_help_position = 40),
  )
  type_choices = ['data', 'mc']
  parser.add_argument('-i', '--input', dest = 'input', metavar = 'file', required = True, type = str,
                      help = 'R|Input file containing a list of MINIAOD(SIM) or a single ROOT file')
  parser.add_argument('-o', '--output', dest = 'output', metavar = 'path', required = True, type = str,
                      help = 'R|Output directory where the nanoAOD Ntuples will be stored')
  parser.add_argument('-n', '--name', dest = 'name', metavar = 'name', required = True, type = str,
                      help = 'R|Sample name (try to be specific, e.g. SingleElectron_Run2017E_17Nov2017_v1)')
  parser.add_argument('-s', '--script-dir', dest = 'script_dir', metavar = 'path', required = True, type = str,
                      help = 'R|Directory containing config and log files for the SLURM jobs')
  parser.add_argument('-t', '--type', dest = 'type', metavar = 'type', required = True, type = str, choices = type_choices,
                      help = 'R|Sample type; choices: %s' % ', '.join(list(map(lambda choice: "'%s'" % choice, type_choices))))
  parser.add_argument('-m', '--max-events', dest = 'max_events', metavar = 'number', required = False, type = int, default = -1,
                      help = 'R|Maximum number of events to be processed in the file')
  parser.add_argument('-S', '--skip-events', dest = 'skip_events', metavar = 'number', required = False, type = int, default = 0,
                      help = 'R|Number of events to be skipped in the file')
  parser.add_argument('-e', '--era', dest = 'era', metavar = 'era', required = True, type = str, choices = [ '2016', '2017' ],
                      help = 'R|Era')
  parser.add_argument('-v', '--verbose', dest = 'verbose', action = 'store_true', default = False,
                      help = 'R|Enable verbose printout')
  args = parser.parse_args()

  if args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

  infile      = args.input
  outdir      = args.output
  sample_name = args.name
  script_dir  = args.script_dir
  sample_type = args.type
  max_events  = args.max_events
  skip_events = args.skip_events
  era         = args.era

  nano_cfg = os.path.join(
    os.environ['CMSSW_BASE'], 'src', 'tthAnalysis', 'NanoAOD', 'test',
    'nano_cfg_%s_%s.py' % (sample_type, era)
  )

  if not os.path.isfile(nano_cfg):
    raise ValueError("File %s is missing!" % nano_cfg)

  if not os.path.isfile(infile):
    raise ValueError("No such file: %s" % infile)

  # check if the input is valid
  input_files = []
  if infile.lower().endswith('.root'):
    input_files.append(infile)
  else:
    with open(infile, 'r') as f:
      for line in f:
        line_stripped = line.rstrip('\n')
        if not line_stripped:
          # empty line
          continue
        if not line_stripped.endswith('.root'):
          logging.warning('File %s does not appear to be a ROOT file')
          continue
        if not os.path.isfile(line_stripped):
          logging.error('File %s does not exist, skipping')
          continue
        if line_stripped not in input_files:
          # require the input files to be unique
          input_files.append(line_stripped)
        logging.debug('Preparing job for file: %s' % line_stripped)

  # check if the script directory exists, and if not, create it
  if not os.path.isdir(script_dir):
    logging.info('Directory %s does not exist, attempting to create it' % script_dir)
    try:
      os.makedirs(script_dir)
    except IOError as err:
      logging.error('Could not create directory %s because: %s' % (script_dir, err))
      sys.exit(1)
  # now that succeeded, we'll just generate the cfg and log directories silently
  cfg_dir = os.path.join(script_dir, 'cfg')
  log_dir = os.path.join(script_dir, 'log')
  if not os.path.isdir(cfg_dir):
    os.makedirs(cfg_dir)
  if not os.path.isdir(log_dir):
    os.makedirs(log_dir)

  # set the path to the Makefile and the sbatchManager script
  makefile_path = os.path.join(script_dir, 'Makefile_nanoAOD')

  # map the input files to an output file, build the cfg files
  file_map = {}
  for input_file in input_files:
    idx = len(file_map) + 1 # so that the tree indices start from 1 instead of 0
    output_file = os.path.join(
      outdir, sample_name, '%04d' % (idx // 1000), 'tree_%d.root' % idx,
    )
    logging.debug('Mapping input file %s to output file %s' % (input_file, output_file))

    # copy nano_cfg.py to the cfg folder and rename it according to the idx value
    cfg_file = os.path.join(cfg_dir, 'cfg_%d.py' % idx)
    shutil.copyfile(nano_cfg, cfg_file)

    # append a line to the cfg file saying that we want to process current input file
    with open(cfg_file, 'a') as f:
      f.write(jinja2.Template(nano_cfg_additions).render(
        input_filename = input_file,
        max_events     = max_events,
        skip_events    = skip_events,
      ))
    logging.debug('Built config file: %s' % cfg_file)

    # now we want to create a shell script for the job as well
    shell_file = os.path.join(cfg_dir, 'job_%d.sh' % idx)
    with open(shell_file, 'w') as f:
      shell_contents = jinja2.Template(shell_template).render(
        output_file = output_file,
        cfg_file    = cfg_file,
        log_file    = os.path.join(log_dir, 'executable_%d.log' % idx),
        job_dir     = os.path.join(os.path.expanduser('~'), 'jobs', 'nanoAOD'),
      )
      f.write(shell_contents)
    # add executable rights
    st = os.stat(shell_file)
    os.chmod(shell_file, st.st_mode | stat.S_IEXEC)
    logging.debug('Built shell script: %s' % shell_file)

    file_map[input_file] = {
      'output_file'  : output_file,
      'logfile'      : os.path.join(log_dir, 'wrapper_%d.log' % idx),
      'shell_script' : shell_file,
    }

  # now add wrapper to the shell script that keeps the makefile ,,alive''
  shell_wrapper = os.path.join(cfg_dir, 'job_wrapper.sh')
  with open(shell_wrapper, 'w') as f:
    shell_wrapper_contents = jinja2.Template(shell_wrapper_template).render(
      file_map = file_map,
    )
    f.write(shell_wrapper_contents)
  # add executable rights
  st = os.stat(shell_wrapper)
  os.chmod(shell_wrapper, st.st_mode | stat.S_IEXEC)
  logging.debug('Built shell wrapper: %s' % shell_wrapper)

  # generate the makefile
  with open(makefile_path, 'w') as f:
    makefile_contents = jinja2.Template(makefile_template).render(
      file_map      = file_map,
      shell_wrapper = shell_wrapper,
    )
    f.write(makefile_contents)
  logging.info('Wrote the makefile to: %s' % makefile_path)
  logging.info(
    'Run with: make -f %s 2>%s 1>%s' % \
    (makefile_path, os.path.join(script_dir, 'stderr.log'), os.path.join(script_dir, 'stdout.log'))
  )
