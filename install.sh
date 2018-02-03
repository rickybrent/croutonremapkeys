#!/bin/bash
if [ "$(id -u)" != "0" ]; then
  exec sudo "$0" "$@"
fi
apt-get install python3-venv
python3 -m venv /opt/croutonremapkeys
source /opt/croutonremapkeys/bin/activate
cd /opt/croutonremapkeys
git clone https://github.com/rickybrent/evdevremapkeys.git
git clone https://github.com/rickybrent/croutonremapkeys.git
pip install -r evdevremapkeys/requirements.txt
pip install -r croutonremapkeys/requirements.txt
cd evdevremapkeys
./setup.py install
CMD='/opt/croutonremapkeys/bin/python /opt/croutonremapkeys/croutonremapkeys/croutonremapkeys.py >> /var/log/croutonremapkeys 2>&1 &'
echo "ready!"
# Remove the line (if present), then add the line to rc.local:
awk '!/^\/opt\/croutonremapkeys/' /etc/rc.local > /tmp/rc.local
awk -vpattern="^exit 0" -vcmd="$CMD" '$0 ~ pattern {print cmd; print; next} 1' /tmp/rc.local > /etc/rc.local

