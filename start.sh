#!/bin/bash
if [ ! -f .stop ]; then
	echo "File '.stop' is NOT present (bot is already started). To force execution, create (touch) the '.stop' file. Exiting..."
	exit
fi

nohup ./chatbot.py &>/dev/null &
nohup ./update-members.py &>/dev/null &
rm ".stop" &>/dev/null
