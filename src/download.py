import requests
from log import *
from secret.key import MALSHARE_API
import time
from database import *

MALBAZAAR = 'https://bazaar.abuse.ch/export/txt/sha256/recent/'
MALSHARE = f'https://malshare.com/api.php?api_key={MALSHARE_API}&action=getlist'

def resolve_hashes(hashes):
    new = 0
    for hash in hashes:
        if Database().exists(hash) is False:
            logging.info(f"Adding to database a new hash: {hash}...")
            new = new + 1
            Database().save(hash)
        else:
            logging.info(f"Skipping known hash: {hash}...")
    return new

class MalwareBazaar:
    def __init__(self):
        self.response = requests.get(MALBAZAAR)
        self.response.raise_for_status()

    def get_hashes(self):
        lines = self.response.text.splitlines()
        hashes = [line.strip() for line in lines if line and not line.startswith("#")]
        return hashes
    
    def scrape(self):
        logging.info(f"Getting malware hashes from {MALBAZAAR}...")
        hashes = self.get_hashes()
        logging.info(f"Fetched {len(hashes)} hashes...")
        new = resolve_hashes(hashes)
        logging.info(f"A total of {new} new hashes has been added from Malware Bazaar...")

class MalShare:
    def __init__(self):
        self.response = requests.get(MALSHARE)
        self.response.raise_for_status()
    
    def get_hashes(self):
        data = self.response.json()
        hashes = [entry['sha256'] for entry in data]
        return hashes

    def scrape(self):
        logging.info(f"Getting malware hashes from {MALSHARE}...")
        hashes = self.get_hashes()
        logging.info(f"Fetched {len(hashes)} hasshes...")
        new = resolve_hashes(hashes)
        logging.info(f"A total of {new} new hashes has been added from MalShare...")
    
if __name__ == "__main__":
    while True:
        for remaining in range(60, 0, -1):
            scraper = MalwareBazaar()
            scraper.scrape()
            scraper = MalShare()
            scraper.scrape()
            print(f"\r[ETA] Time until next download: {remaining} minutes...", end='', flush=True)
            time.sleep(60)
        