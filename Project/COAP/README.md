# COAP

Done using libcoap & mininet
https://github.com/obgm/libcoap

Flow on how we did the testing is in testflow.txt
tl;dr: 
Git clone libcoap
compile and make libcoap
sudo ./COAP.py to start mininet
start coap server
start packet capture
send file
kill tshark

rinse & repeat for different file sizes

