import logging
from logging.handlers import TimedRotatingFileHandler
import os

os.makedirs('logs', exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

file = TimedRotatingFileHandler(
    'logs/entry.log',
    when='H',
    interval=1,
    backupCount=3
)
file.setLevel(logging.DEBUG)
file.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

logger.addHandler(console)
logger.addHandler(file) 