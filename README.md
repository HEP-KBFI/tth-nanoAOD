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
echo -e 'PhysicsTools/NanoAOD/*\n' > .git/info/sparse-checkout
git remote add origin https://github.com/HEP-KBFI/cmssw.git
git fetch origin
git checkout master-102x
git pull
```

Retrieve preliminary scale and smearing uncertainties of electron energies for 2018 era:

```bash
mkdir -p $CMSSW_BASE/src/EgammaAnalysis/ElectronTools/data
cd $_
git init
git config core.sparseCheckout true
echo -e 'ScalesSmearings/Run2018_Step2Closure_CoarseEtaR9Gain_*.dat\n' > .git/info/sparse-checkout
git remote add origin https://github.com/cms-egamma/EgammaAnalysis-ElectronTools.git
git fetch origin
git checkout ScalesSmearing2018_Dev
git pull
```
