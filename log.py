import logging
from config import LOG_LEVEL, LOG_FILE

numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
if not isinstance(numeric_level, int):
	raise ValueError("Invalid log level: %s" % loglevel)
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
if LOG_FILE is not None and LOG_FILE != "":
	logging.basicConfig(format=log_format, filename=LOG_FILE,
			level=numeric_level)
else:
	logging.basicConfig(format=log_format, level=numeric_level)
