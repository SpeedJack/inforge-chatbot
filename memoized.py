import logging
import time

import log
logger = logging.getLogger(__name__)

_last_collect = time.time()

class memoized(object):
	_caches = {}
	_timeouts = {}

	def __init__(self, timeout=60, refresh_on_access=False):
		self.timeout = timeout
		self.refresh_on_access = refresh_on_access

#	def purge(self):
#		for func in self._caches:
#			self._caches[func] = {}

	def collect(self):
		for func in self._caches:
			cache = {}
			for key in self._caches[func]:
				if (time.time() - self._caches[func][key][1]) < self._timeouts[func]:
					cache[key] = self._caches[func][key]
			self._caches[func] = cache

	def __call__(self, f):
		self.cache = self._caches[f] = {}
		self._timeouts[f] = self.timeout

		def func(*args, **kwargs):
			nc = kwargs.pop("no_cache", False)
			kw = sorted(kwargs.items())
			key = (args, tuple(kw))
			try:
				v = self.cache[key]
				if nc or ((time.time() - v[1]) > self.timeout):
					raise KeyError
			except KeyError:
				logger.debug("NOT IN CACHE: function name:'" + f.__name__ +
						"'; args:'" + repr(key[0]) +
						"'; kwargs:'" + repr(key[1]) + "'")
				v = self.cache[key] = f(*args,**kwargs), time.time()
			else:
				logger.debug("CACHE: function name:'" + f.__name__ +
						"'; args:'" + repr(key[0]) +
						"'; kwargs:'" + repr(key[1]) +
						"'; value:'" + repr(v[0]) + "'")
				if self.refresh_on_access:
					self.cache[key] = self.cache[key][0], time.time()
			return v[0]
		func.func_name = f.__name__

		return func

def memoized_collect(collect_time=60*60):
	global _last_collect
	now = time.time()
	if now - _last_collect > collect_time:
		logger.info("Collecting old memoized data...")
		memoized().collect()
		_last_collect = now
