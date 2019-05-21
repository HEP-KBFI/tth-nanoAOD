# tth-nanoAOD
Code and config files specific to ttH with H->tautau analysis that is run during nanoAOD production

## Requirements

Set up CMSSW 102x

```bash
export SCRAM_ARCH=slc6_amd64_gcc700
cmsrel CMSSW_10_2_10
cd $_/src/
cmsenv

git init
git config core.sparseCheckout true
echo -e 'PhysicsTools/NanoAOD/*\nDataFormats/MuonDetId/*\nRecoTauTag/RecoTau/*\n' > .git/info/sparse-checkout
git remote add origin https://github.com/HEP-KBFI/cmssw.git
git fetch origin
git checkout deepTauV2
git pull
```
