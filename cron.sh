#!/bin/bash
cd /var/www/sitcoms.joshmoody.dev/sitcom-simulator-cli/.venv/bin && source activate && cd ../..
python main.py -q 30 -l 20 -a -d
