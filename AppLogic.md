# Pasul 1
Se rulează comanda `python download.py` pentru colectarea datele necesare pentru popularea bazei de date
# Pasul 2
Se rulează comanda `python filter_service.py` 

Se va putea vedea în consolă log-uri care arată că se inițializează filtrul, se încarcă hash-urile din DB și apoi pornește serverul web.
# Pasul 3
**Simularea unui client AV**
- Ia un hash care știi că a fost descărcat în `malware.db`.
    *   Deschide o nouă fereastră de terminal și folosește `curl` pentru a testa API-ul:
    ```bash
    # Presupunând că hash-ul 'aabbcc...' ESTE în baza de date
    curl http://127.0.0.1:5000/check/aabbcc...
    # Răspuns așteptat: {"hash":"aabbcc...","is_malicious_candidate":true}

    # Test cu un hash care sigur NU este în baza de date
    curl http://127.0.0.1:5000/check/acesta_este_un_test_12345
    # Răspuns așteptat: {"hash":"acesta_este_un_test_12345","is_malicious_candidate":false}
    ```
