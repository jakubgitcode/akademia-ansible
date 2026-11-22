# Rola aplikacja

Instaluje aplikację `naszaaplikacja` (Flask) pod Apache z mod_wsgi, w virtualenv. Ubuntu 24.04.

Parametry: `defaults/main.yml` (katalogi, port, nazwa, wersja, opcjonalnie dane bazy `aplikacja_baza_*`).
Tagi: `pakiety`, `kod`, `konfiguracja`; `diagnostyka` (tylko na żądanie) pokazuje `config.cfg`.

```yaml
- hosts: appservers
  become: true
  roles:
    - aplikacja
```
