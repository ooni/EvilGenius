sudo apt-get install -y git
cd /opt/
git clone https://github.com/TheTorProject/ooni-probe.git
cd /opt/ooni-probe

export USE_VIRTUALENV=0
./setup-dependencies.sh -y
python setup.py install

cd /usr/share/ooni/
echo "[+] Building geoip stuff.."
make geoip 2>&1 > /dev/null

mkdir -p ~/.ooni
cp /scripts/ooniprobe.conf /opt/ooni-probe/

cd /ooni/inputs/
make lists 2>&1 > /dev/null

# https://code.google.com/p/pypcap/issues/detail?id=27
# pip install pydnet pypcap
