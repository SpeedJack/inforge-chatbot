#!/bin/bash
touch .stop
if [ -f chatbot.pid ]; then
	kill $(<chatbot.pid)
fi
if [ -f update-members.pid ]; then
	kill $(<update-members.pid)
fi
