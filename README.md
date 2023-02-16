1. Add agent key in dir
2. Add params in .env such as .env.sample

Exec in docker:
- `docker build -t bvs:06 .`
- `docker run --rm -v /bases:/BvsUpdater/bases --name bvsc -it bvs:06` (use `-d` for detach)
(for debug `docker exec -it bvsc /bin/bash`)

Exec in host:
- `chmod +x init.sh && ./init.sh`
- `cd ./BvsUpdater && ./main.py`

You may add service:
- `cp bvsupdater.service /etc/systemd/system`
- `systemctl enable bvsupdater`
- `systemctl start bvsupdater`
- `systemctl status bvsupdater`
