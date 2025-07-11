import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs('logs', exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))

file = RotatingFileHandler(
    'logs/entry.log',
    maxBytes=5*1024*1024,
    backupCount=3
)
file.setLevel(logging.DEBUG)
file.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))

logger.addHandler(console)
logger.addHandler(file) 