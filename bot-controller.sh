#!/bin/bash
if [ -f .stop ]; then
	exit
fi

if [ -f chatbot.pid ]; then
	pid=$(<chatbot.pid)
fi
if [ ! -f chatbot.pid ] || ! kill -0 $pid > /dev/null 2>&1; then
	curl "https://api.telegram.org/bot***REMOVED***/sendMessage?chat_id=-1001093943158&text=CONTROLLER%3A%20bot%20is%20offline%2E%20Restarting%2E%2E%2E" &>/dev/null
	nohup ./chatbot.py &>/dev/null &
fi
if [ -f update-members.pid ]; then
	pid=$(<update-members.pid)
fi
if [ ! -f update-members.pid ] || ! kill -0 $pid > /dev/null 2>&1; then
	curl "https://api.telegram.org/bot***REMOVED***/sendMessage?chat_id=-1001093943158&text=CONTROLLER%3A%20update-members%20is%20offline%2E%20Restarting%2E%2E%2E" &>/dev/null
	nohup ./update-members.py &>/dev/null &
fi
