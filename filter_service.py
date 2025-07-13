# filter_service.py

import logging
from flask import Flask, jsonify
# Importul corect pentru librăria pe care o folosim
from cuckoopy import CuckooFilter 
from database import Database
from log import * # Am adăugat acest import pentru a folosi logger-ul configurat de colegul tău

# --- CONFIGURARE ---
# Acești parametri sunt CRUCIALI.
FILTER_CAPACITY = 2_000_000  # Câte elemente preconizați că veți avea? Ex: 2 milioane
FILTER_FP_RATE = 0.001       # Rata de fals pozitive dorită (0.1%)

# --- Inițializare Globală ---
app = Flask(__name__)

# Inițializarea specifică pentru 'cuckoopy'.
# 'cuckoopy' permite specificarea directă a parametrilor interni, ceea ce oferă un control fin.
# - capacity: Numărul maxim de elemente unice pe care filtrul le poate stoca.
# - error_rate: Probabilitatea de fals pozitive.
# - bucket_size: Câte "amprente" (fingerprints) încap într-o "găleată". 4 este o valoare standard, bună.
# - fingerprint_size: Câți byți să aibă amprenta. Librăria o poate calcula, dar setarea manuală (ex: 2) e ok.
logging.info("Initializing Cuckoo Filter...")
cuckoo_filter = CuckooFilter(
    capacity=FILTER_CAPACITY,
    error_rate=FILTER_FP_RATE,
    bucket_size=4
)
logging.info(f"Cuckoo Filter initialized with capacity={FILTER_CAPACITY}, error_rate={FILTER_FP_RATE}")


def populate_filter_from_db():
    """
    Funcția care citește toate hash-urile din baza de date
    și le introduce în Cuckoo Filter.
    """
    logging.info("Starting to populate Cuckoo Filter from the database...")
    db = Database()
    all_hashes = db.get_all_hashes()  # Metoda scrisă de colegul tău
    
    if not all_hashes:
        logging.warning("Database is empty. No hashes to load into the filter.")
        return

    logging.info(f"Loading {len(all_hashes)} hashes from database into the filter...")
    
    # Inserăm fiecare hash în filtru
    inserted_count = 0
    for file_hash in all_hashes:
        try:
            # Metoda de inserare în 'cuckoopy' se numește .insert()
            if cuckoo_filter.insert(file_hash):
                inserted_count += 1
            else:
                logging.error(f"Failed to insert hash: {file_hash}. The filter is likely full.")
                # Dacă inserarea eșuează, filtrul e plin. Oprim procesul.
                break
        except Exception as e:
            # Prindem orice altă eroare neașteptată
            logging.error(f"An unexpected error occurred while inserting {file_hash}: {e}")
            break
            
    # Metoda de a afla numărul de elemente în 'cuckoopy' este len()
    logging.info(f"Cuckoo Filter populated. Total items successfully inserted: {len(cuckoo_filter)} / {len(all_hashes)}")


# --- Definirea API-ului ---
@app.route('/check/<string:hash_to_check>', methods=['GET'])
def check_hash(hash_to_check):
    """
    Endpoint-ul pe care clientul AV îl va apela.
    Exemplu de apel: GET http://127.0.0.1:5000/check/sha256_hash_aici
    """
    # Metoda de verificare în 'cuckoopy' se numește .contains()
    # Alternativ, se poate folosi sintaxa "pythonică": `if hash_to_check in cuckoo_filter:`
    is_present = cuckoo_filter.contains(hash_to_check)
    
    # Logăm fiecare verificare pentru a vedea activitatea serverului
    logging.debug(f"Checked hash: {hash_to_check} -> Result: {is_present}")
    
    # Returnăm un răspuns JSON standard
    return jsonify({
        'hash': hash_to_check,
        'is_malicious_candidate': is_present  # true sau false
    })


# --- Blocul de pornire ---
if __name__ == '__main__':
    # Folosim logger-ul deja configurat în log.py pentru consistență
    logging.info("Starting Filter Service...")
    
    # 1. Populăm filtrul O SINGURĂ DATĂ, la pornire.
    populate_filter_from_db()
    
    # 2. Pornim serverul web, care va asculta pentru request-uri.
    # host='0.0.0.0' face serverul accesibil din rețea (nu doar de pe localhost)
    logging.info("Starting Flask web server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)