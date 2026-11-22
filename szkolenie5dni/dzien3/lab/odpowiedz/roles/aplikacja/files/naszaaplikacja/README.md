# naszaaplikacja

Przykładowa aplikacja w Pythonie (Flask). Strona główna pokazuje nazwę, środowisko, wersję i serwer;
`/health` odpowiada `OK` (dla monitoringu i load balancera).

## Uruchomienie u dewelopera

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp config.cfg.example config.cfg
venv/bin/python aplikacja.py          # http://localhost:5081/
```

## Wdrożenie na serwerze: Ubuntu 24.04, Apache z mod_wsgi

Przykładowe ścieżki: aplikacja w `/var/www/szkolenie.pl/aplikacja`, logi w `/var/www/szkolenie.pl/logs`, port 5081.

1. Pakiety: `apt install apache2 libapache2-mod-wsgi-py3 python3-venv`
2. Katalog aplikacji i katalog na logi (właściciel katalogu logów: `www-data`).
3. Kod aplikacji (zawartość tego katalogu) do katalogu aplikacji.
4. virtualenv w podkatalogu `venv` katalogu aplikacji i zależności:
   `python3 -m venv venv && venv/bin/pip install -r requirements.txt`
5. Konfiguracja aplikacji: `config.cfg` obok `aplikacja.py` (wzór: `config.cfg.example`).
6. Punkt wejścia WSGI: `naszaaplikacja.wsgi` w katalogu aplikacji (wzór: `naszaaplikacja.wsgi.example`).
7. VirtualHost: `/etc/apache2/sites-available/naszaaplikacja.conf` (wzór: `naszaaplikacja.apache.conf.example`).
8. Port: w `/etc/apache2/ports.conf` linia `Listen <port>`.
9. Włączenie strony: `a2ensite naszaaplikacja`. Gdy aplikacja działa na porcie 80, wyłącz domyślną stronę
   Apache: `a2dissite 000-default`.
10. `systemctl restart apache2`

Aplikacja czyta `config.cfg` przy starcie: po każdej zmianie konfiguracji trzeba zrestartować Apache.

Sprawdzenie: `curl http://localhost:5081/` i `curl http://localhost:5081/health` (odpowiedź `OK`).
