from CRABClient.UserUtilities import config, getUsernameFromSiteDB

import re
import os

def get_env_var(env_var):
  if env_var not in os.environ:
    raise ValueError("$%s not defined" % env_var)
  return os.environ[env_var]

if 'JOB_PREFIX' not in os.environ:
  raise ValueError("$JOB_PREFIX not defined")

PREFIX = get_env_var('JOB_PREFIX')

NANOCFG_DATA = get_env_var('NANOCFG_DATA')
NANOCFG_MC   = get_env_var('NANOCFG_MC')
JSON_LUMI    = get_env_var('JSON_LUMI')

is_data         = bool(int(get_env_var('IS_DATA')))
dataset_name    = get_env_var('DATASET')
dataset_pattern = get_env_var('DATASET_PATTERN')
dataset_match   = re.match(dataset_pattern, dataset_name)
if not dataset_match:
  raise ValueError("Dataset '%s' did not match to pattern '%s'" % (dataset_name, dataset_pattern))

id_ = '%s_%s__%s' % (PREFIX, dataset_match.group(1), dataset_match.group(2))
requestName      = id_
outputDatasetTag = id_

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

config.JobType.pluginName = 'Analysis'
config.JobType.psetName   = NANOCFG_DATA if is_data else NANOCFG_MC

config.Data.inputDataset     = dataset_name
config.Data.inputDBS         = 'global'
config.Data.splitting        = 'EventAwareLumiBased'
config.Data.unitsPerJob      = 50000
config.Data.outLFNDirBase    = '/store/user/%s/NanoAOD_2017_v2' % getUsernameFromSiteDB()
config.Data.publication      = False
config.Data.outputDatasetTag = outputDatasetTag

config.Data.allowNonValidInputDataset = True

if is_data:
  config.Data.lumiMask = JSON_LUMI

config.Site.storageSite = 'T2_EE_Estonia'