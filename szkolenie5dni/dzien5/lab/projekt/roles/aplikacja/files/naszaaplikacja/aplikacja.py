"""naszaaplikacja — przykładowa aplikacja (Flask) do ćwiczeń z wdrażania."""
import configparser
import html
import os
import socket

from flask import Flask

KATALOG = os.path.dirname(os.path.abspath(__file__))


def wczytaj_konfiguracje():
    """config.cfg obok aplikacji; bez niego aplikacja startuje z przykładową konfiguracją."""
    config = configparser.ConfigParser()
    if not config.read(os.path.join(KATALOG, "config.cfg"), encoding="utf-8"):
        config.read(os.path.join(KATALOG, "config.cfg.example"), encoding="utf-8")
    return config


# Konfigurację czytamy RAZ, przy starcie procesu. Zmiana config.cfg działa dopiero po restarcie Apache.
KONFIGURACJA = wczytaj_konfiguracje()
app = Flask(__name__)


def stan_bazy():
    if not KONFIGURACJA.has_section("baza"):
        return "nie skonfigurowana"
    baza = KONFIGURACJA["baza"]
    try:
        import pymysql

        polaczenie = pymysql.connect(
            host=baza["host"],
            user=baza["uzytkownik"],
            password=baza["haslo"],
            database=baza["nazwa"],
            connect_timeout=3,
        )
        polaczenie.close()
        return "połączona z " + baza["host"]
    except Exception as blad:  # pokazujemy błąd na stronie: to aplikacja do ćwiczeń
        return "BŁĄD: " + str(blad)


@app.route("/")
def strona_glowna():
    c = KONFIGURACJA["config"]
    wiersze = {
        "Środowisko": c.get("srodowisko", "nieznane"),
        "Wersja": c.get("wersja", "?"),
        "Serwer": socket.gethostname(),
        "Baza danych": stan_bazy(),
    }
    lista = "".join(f"<li>{k}: {html.escape(v)}</li>" for k, v in wiersze.items())
    nazwa = html.escape(c.get("nazwa", "naszaaplikacja"))
    return (
        '<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8">'
        f"<title>{nazwa}</title></head><body><h1>{nazwa}</h1><ul>{lista}</ul></body></html>\n"
    )


@app.route("/health")
def zdrowie():
    """Sprawdzenie dla monitoringu i load balancera."""
    return "OK\n"


if __name__ == "__main__":
    # Tryb deweloperski (bez Apache): venv/bin/python aplikacja.py
    app.run(host="0.0.0.0", port=KONFIGURACJA["config"].getint("port", 5081))
