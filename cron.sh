#!/bin/bash
cd /var/www/sitcoms.joshmoody.dev/sitcom-simulator-cli/.venv/bin && source activate && cd ../..
python main.py -q 30 -l 15 -a -d 2>> error.log 1>> output.log
date >> error.log && date >> output.log
