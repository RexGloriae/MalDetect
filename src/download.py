from bs4 import BeautifulSoup
import requests
import os
import zipfile
from log import *

MALBAZAAR = 'https://datalake.abuse.ch/malware-bazaar/hourly/'
OUTPUT = 'assets/'
MANIFEST = 'manifest'
ZIP_MANIFEST = 'zip_manifest'

class MalwareBazaar:
    def __init__(self):
        os.makedirs(OUTPUT, exist_ok=True)
        self.manifest = self.load_manifest()
        self.zip_manifest = self.load_zip_manifest()

    def scrape(self):
        logging.info("Scraping Malware Bazaar...")
        response = requests.get(MALBAZAAR)
        soup = BeautifulSoup(response.text, 'html.parser')
        zip_links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.endswith('.zip'):
                logging.info(f"Found archive: {href}")
                zip_links.append(MALBAZAAR + href)
        return zip_links

    
    def load_manifest(self):
        logging.info("Loading manifest...")
        entries = set()
        if os.path.exists(MANIFEST):
            with open(MANIFEST, 'r') as f:
                for line in f:
                    entries.add(line.strip())
        return entries

    def load_zip_manifest(self):
        logging.info("Loading ZIP manifest...")
        entries = set()
        if os.path.exists(ZIP_MANIFEST):
            with open(ZIP_MANIFEST, 'r') as f:
                for line in f:
                    entries.add(line.strip())
        return entries

    def save_manifest(self):
        logging.info("Saving manifest...")
        with open(MANIFEST, 'w') as f:
            for line in sorted(self.manifest):
                f.write(line + '\n')
    
    def save_zip_manifest(self):
        logging.info("Saving ZIP manifest...")
        with open(ZIP_MANIFEST, 'w') as f:
            for line in sorted(self.zip_manifest):
                f.write(line + '\n')
    
    def download_zip(self, url, dest):
        logging.info(f"Downloading ZIP archive: {url}...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_len = int(r.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192
            bar_len = 40

            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded+=len(chunk)

                        if total_len:
                            done = int(bar_len * downloaded / total_len)
                            progress_bar = '#' * done + '-' * (bar_len - done)
                            percent = (downloaded / total_len) * 100
                            print(f"\r[{progress_bar}] {percent:.1f}%", end='', flush=True)
            print()
            logging.info(f"Saved ZIP to {dest}...")
    
    def proccess_zip(self, zip_path):
        logging.info(f"Proccessing {zip_path}...")
        try:
            with zipfile.ZipFile(zip_path) as z:
                for sample in z.namelist():
                    if sample in self.manifest:
                        logging.info(f"Skipping known sample: {sample}...")
                        continue
                    print(f"Extracting {sample}...")
                    z.extract(sample, path=OUTPUT, pwd=b'infected')
                    self.manifest.add(sample)
        except zipfile.BadZipFile as e:
            logging.error(f"{e}...")
        except RuntimeError as e:
            logging.error(f"{e}...")

        os.remove(zip_path)

    def run(self):
        links = self.scrape()
        for url in links:
            zip_name = url.split('/')[-1]
            zip_path = os.path.join(OUTPUT, zip_name)

            if zip_name in self.zip_manifest:
                logging.info(f"Skipping already proccessed ZIP: {zip_name}...")
                continue

            if not os.path.exists(zip_path):
                self.download_zip(url, zip_path)
            else:
                logging.info(f"Skipping already downloaded ZIP: {zip_name}...")

            self.proccess_zip(zip_path)
        
        self.save_manifest()

    
if __name__ == "__main__":
    scraper = MalwareBazaar()
    scraper.run()
