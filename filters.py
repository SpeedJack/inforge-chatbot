from telegram.ext import BaseFilter
from memoized import memoized
from db import is_registered

@memoized(timeout=24*60*60)
def _get_admin_ids(bot, chat_id):
	return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

class FilterAdmin(BaseFilter):
	def __init__(self, bot):
		self.bot = bot

	def filter(self, message):
		return (message.from_user.id
				in _get_admin_ids(self.bot, message.chat_id))

class FilterAddedBot(BaseFilter):
	def filter(self, message):
		for u in message.new_chat_members:
			if u.username and u.username[-3:].lower() == "bot":
				return True
		if message.new_chat_member is not None:
			username = message.new_chat_member.username
			if username and username[-3:].lower() == "bot":
				return True
		return False
filter_added_bot = FilterAddedBot()

class FilterRegistered(BaseFilter):
	def filter(self, message):
		return is_registered(message.from_user.id, message.chat_id)
filter_registered = FilterRegistered()

#class FilterBanned(BaseFilter):
#	def filter(self, message):
#		return is_banned(message.from_user.id, message.chat_id)
#filter_banned = FilterBanned()

__all__ = ["FilterAdmin", "filter_added_bot", "filter_registered"]
