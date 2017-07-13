#!/usr/bin/env python3

import sys
import telegram
from config import BOT_TOKEN

group = -1001055827794 # Test group: -1001093943158

if __name__ == "__main__":
	if sys.argv[1:] is not None and sys.argv[1:] and sys.argv[1:] != "":
		message = " ".join(sys.argv[1:])
		print("Sending:", message)
		bot = telegram.Bot(token=BOT_TOKEN)
		bot.send_message(chat_id=group,
				text=message,
				parse_mode=telegram.ParseMode.MARKDOWN)
	else:
		print("Specifica un messaggio come parametro!")
