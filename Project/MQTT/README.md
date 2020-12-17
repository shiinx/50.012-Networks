# MQTT

Done using mosquitto & mininet
https://github.com/eclipse/mosquitto

Flow on how we did the testing is in testflow.txt
tl;dr: 
Git clone mosquitto
compile and make mosquitto
sudo ./MQTT.py to start mininet
start broker on h3
subscribe to a topic on h2
start packet capture
publish message
kill tshark

rinse & repeat for different file sizes and QoS

