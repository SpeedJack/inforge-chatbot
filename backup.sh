#!/bin/bash
# cronjob: 55 4 * * *
rsync -u chatbot.db backup.db
