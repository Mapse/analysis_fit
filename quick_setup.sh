if [[ $_ == $0 ]]; then  
  echo "This script is meant to be sourced:"
  echo "  source $0"
  exit 0
fi

conda deactivate ; conda deactivate 

# activate if CMSSW Needed:
# cmsenv
###########################

conda activate OniaOpenCharmRun2ULenv
voms-proxy-init --rfc --voms cms
