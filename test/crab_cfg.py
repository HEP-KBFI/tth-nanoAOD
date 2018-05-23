from CRABClient.UserUtilities import config, getUsernameFromSiteDB

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
NANOCFG_DATA  = get_env_var('NANOCFG_DATA')
NANOCFG_MC    = get_env_var('NANOCFG_MC')
JSON_LUMI     = get_env_var('JSON_LUMI')
NANOAOD_VER   = get_env_var('NANOAOD_VER')
WHITELIST     = get_env_var('WHITELIST', False)
PRIVATE_FILES = get_env_var('PRIVATE_DATASET_FILES', False)

is_private      = bool(int(get_env_var('IS_PRIVATE')))
is_data         = bool(int(get_env_var('IS_DATA')))
dataset_name    = get_env_var('DATASET')
dataset_pattern = get_env_var('DATASET_PATTERN')
dataset_match   = re.match(dataset_pattern, dataset_name)
if not dataset_match:
  raise ValueError("Dataset '%s' did not match to pattern '%s'" % (dataset_name, dataset_pattern))

id_ = '%s_%s__%s' % (NANOAOD_VER, dataset_match.group(1), dataset_match.group(2))
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

if WHITELIST:
  config.Site.whitelist = WHITELIST.split(',')
config.Site.storageSite = HOME_SITE

if is_private:
  config.Data.userInputFiles       = PRIVATE_FILES.split()
  config.Data.outputPrimaryDataset = dataset_match.group(1)
  config.Data.splitting            = 'FileBased'
  config.Data.unitsPerJob          = 1
  config.Data.outLFNDirBase        = '/store/user/%s/%s' % (getUsernameFromSiteDB(), NANOAOD_VER)
  config.Data.publication          = False
  config.Data.outputDatasetTag     = outputDatasetTag
  config.Site.whitelist            = [ HOME_SITE ]
else:
  config.Data.inputDataset     = dataset_name
  config.Data.inputDBS         = 'global'
  config.Data.splitting        = 'EventAwareLumiBased'
  config.Data.unitsPerJob      = 50000
  config.Data.outLFNDirBase    = '/store/user/%s/%s' % (getUsernameFromSiteDB(), NANOAOD_VER)
  config.Data.publication      = False
  config.Data.outputDatasetTag = outputDatasetTag

config.Data.allowNonValidInputDataset = True

if is_data:
  config.Data.lumiMask = JSON_LUMI
