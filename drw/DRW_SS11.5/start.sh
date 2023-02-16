#!/bin/bash
wine drwupsrv.exe -c download -s 90 --zones=drwzones.xml --repo-dir=repo --key-file=agent.key --data-dir=. --log-dir=. --verbosity debug | cat
