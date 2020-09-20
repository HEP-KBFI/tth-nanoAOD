from CRABClient.UserUtilities import config, getUsernameFromCRIC

import re
import os

def get_env_var(env_var, fail_if_not_exists = True):
  if env_var not in os.environ:
    if fail_if_not_exists:
      raise ValueError("$%s not defined" % env_var)
    else:
      return ''
  return os.environ[env_var]

HOME_SITE     = 'T2_EE_Estonia'
NANOCFG       = get_env_var('NANOCFG')
JSON_LUMI     = get_env_var('JSON_LUMI')
NANOAOD_VER   = get_env_var('NANOAOD_VER')
CHUNK_VER     = get_env_var('CHUNK_VER', False)
WHITELIST     = get_env_var('WHITELIST', False)
PRIVATE_FILES = get_env_var('PRIVATE_DATASET_FILES', False)
PUBLISH       = bool(int(get_env_var('PUBLISH')))
NOF_EVENTS    = int(get_env_var('NOF_EVENTS'))
DO_FILEBASED  = bool(int(get_env_var('FORCE_FILEBASED')))
FILEBASED_NOF = get_env_var('FILEBASED_NOF', False)
NTHREADS      = int(get_env_var('NTHREADS'))

if FILEBASED_NOF:
  FILEBASED_NOF = int(FILEBASED_NOF)
else:
  FILEBASED_NOF = 1
assert(FILEBASED_NOF > 0)

is_private      = bool(int(get_env_var('IS_PRIVATE')))
job_type        = get_env_var('JOB_TYPE')
dataset_name    = get_env_var('DATASET')
dataset_pattern = get_env_var('DATASET_PATTERN')
dataset_match   = re.match(dataset_pattern, dataset_name)
if not dataset_match:
  raise ValueError("Dataset '%s' did not match to pattern '%s'" % (dataset_name, dataset_pattern))

id_head = '{}_{}'.format(NANOAOD_VER, CHUNK_VER) if CHUNK_VER else NANOAOD_VER
id_     = '%s_%s__%s' % (id_head, dataset_match.group(1), dataset_match.group(2))
requestName      = id_
outputDatasetTag = id_
crabUserName = getUsernameFromCRIC()

max_outputDatasetTag_len = 160 - len(crabUserName)
if len(outputDatasetTag) > max_outputDatasetTag_len:
  outputDatasetTag = outputDatasetTag[:max_outputDatasetTag_len]

if len(requestName) > 100:
  requestName_new = requestName[:90] + requestName[-10:]
  print("Changing old request name '{rqname_old}' -> '{rqname_new}'".format(
    rqname_old = requestName,
    rqname_new = requestName_new,
  ))
  requestName = requestName_new

config = config()

config.General.requestName     = requestName
config.General.workArea        = os.path.join(os.path.expanduser('~'), 'crab_projects')
config.General.transferOutputs = True
config.General.transferLogs    = True

config.JobType.pluginName              = 'Analysis'
config.JobType.psetName                = NANOCFG
config.JobType.allowUndistributedCMSSW = True
config.JobType.numCores                = NTHREADS
if NTHREADS > 1:
  config.JobType.maxMemoryMB = 2000 * NTHREADS

if WHITELIST:
  config.Site.whitelist = WHITELIST.split(',')
config.Site.storageSite = HOME_SITE

if is_private:
  config.Data.userInputFiles       = [ 'file:/hdfs{}'.format(path) for path in PRIVATE_FILES.split('\n') ]
  config.Data.outputPrimaryDataset = dataset_match.group(1)
  config.Data.splitting            = 'FileBased'
  config.Data.unitsPerJob          = 1
  config.Site.whitelist            = [ HOME_SITE ]
else:
  if DO_FILEBASED:
    config.Data.splitting   = 'FileBased'
    config.Data.unitsPerJob = FILEBASED_NOF
  else:
    config.Data.splitting   = 'EventAwareLumiBased'
    config.Data.unitsPerJob = NOF_EVENTS

  config.Data.inputDataset = dataset_name
  config.Data.inputDBS     = 'global'

config.Data.outLFNDirBase             = '/store/user/%s/%s' % (crabUserName, NANOAOD_VER)
config.Data.publication               = PUBLISH
config.Data.outputDatasetTag          = outputDatasetTag
config.Data.allowNonValidInputDataset = True

if job_type == "data":
  config.Data.lumiMask = JSON_LUMI