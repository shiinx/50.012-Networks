#!/bin/bash 
echo "Use http://localhost:8888/queue.png to see the figure on your browser"
python3 -m http.server 8888 --bind 127.0.0.1
