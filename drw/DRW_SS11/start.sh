#!/bin/bash
wine drwupsrv.exe -c download -s 90 --zones=drwzones.xml --repo-dir repo --key-dir=. --data-dir=. --log-dir=. --verbosity debug
