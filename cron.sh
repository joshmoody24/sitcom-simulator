#!/bin/bash
cd ./.venv/bin && source activate && cd ../..
python main.py -q 30 -l 14 -a -d 2>> error.log 1>> output.log
date >> error.log && date >> output.log
