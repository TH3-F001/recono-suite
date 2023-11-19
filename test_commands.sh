#!/bin/bash

# rm -rf /home/neon/Downloads/recono-testing/results/*

# THIS_ENV='/home/neon/Documents/Scripts/recono-suite/venv'
THIS_ENV='/home/neon/.local/pipx/venvs/recono-suite'

source "${THIS_ENV}/bin/activate"

python  /home/neon/Documents/Scripts/recono-suite/recono_sub/command_tester.py

deactivate

  
