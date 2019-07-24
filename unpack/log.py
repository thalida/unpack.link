import os
import sys
import logging
import logstash
import logstash_async.formatter

warning_only_libs = [
    'pika',
    'docker',
    'urllib3',
    'ampq',
    'chardet',
]

for lib in warning_only_libs:
    logging.getLogger(lib).setLevel(logging.WARNING)

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

lsh = logstash.TCPLogstashHandler(os.environ['UNPACK_HOST'], 5959)
logstash_formatter = logstash_async.formatter.LogstashFormatter()
lsh.setFormatter(logstash_formatter)
root_logger.addHandler(lsh)

def handle_excepthook(exctype, value, tb):
    uncaught_logger = logging.getLogger('uncaught')
    message = ''.join(traceback.format_exception(exctype, value, tb))
    uncaught_logger.critical(message)

sys.excepthook = handle_excepthook
