#!/bin/bash
cd /home/pi/PTP-Test-Scripts/ADMD || exit 1

# Make sure the repo exists
if [ -d .git ]; then
    echo "Updating repo..."
    /usr/bin/git reset --hard HEAD
    /usr/bin/git pull --rebase
else
    echo "Not a git repo in $(pwd)"
fi