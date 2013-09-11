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
cp /usr/share/ooni/ooniprobe.conf.sample ~/.ooni/ooniprobe.conf

cd /ooni/inputs/
make lists 2>&1 > /dev/null

# https://code.google.com/p/pypcap/issues/detail?id=27
# pip install pydnet pypcap

/opt/ooni-probe/bin/oonid
echo "You may now visit http://localhost:8042/ to start running some ooniprobe tests"
echo ""
echo "Or if you are a bit more h4x0r you can ssh into the box and use the ooniprobe CLI"
echo "Login using 'vagrant ssh', and dont forget to run ooniprobe as root."
echo "First run: 'sudo su; cd /usr/share/ooni; ./bin/ooniprobe -i decks/before_i_commit.testdeck'"
