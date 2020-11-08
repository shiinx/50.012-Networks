# 50.012 
# install mininet and supporting libraries
sudo apt -y install mininet
# install curl package for pip3.4 installation
sudo apt-get install curl
# install pip3.4
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.4 get-pip.py
# install matplotlib package for lab4 plotting figures
# if occur 'cannot uninstall six', try adding the flags --ignore-installed six
# sudo pip3.4 install matplotlib --ignore-installed six
sudo pip3.4 install matplotlib
