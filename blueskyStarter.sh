#!/bin/bash

export CONDA_ACTIVATE=/APSshare/miniconda/x86_64/bin/activate
export CONDA_ENVIRONMENT=bluesky_2021_1
# bluesky

export IPYTHON_PROFILE=bluesky
export IPYTHONDIR=/home/beams8/USER2IDD/.ipython-bluesky

export OPTIONS=""
export OPTIONS="${OPTIONS} --profile=${IPYTHON_PROFILE}"
export OPTIONS="${OPTIONS} --ipython-dir=${IPYTHONDIR}"
export OPTIONS="${OPTIONS} --IPCompleter.use_jedi=False"
export OPTIONS="${OPTIONS} --InteractiveShellApp.hide_initial_ns=False"

source ${CONDA_ACTIVATE} ${CONDA_ENVIRONMENT}
ipython ${OPTIONS}
