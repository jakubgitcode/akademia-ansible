# L13 — Baza danych z roli z Galaxy i spięcie warstw

Część 1 robisz w bloku 4 (35 min), część 2 w bloku 5 (35 min).

**Cel:** MySQL na web01 z roli `geerlingguy.mysql`, a aplikacja na web02 łączy się z nią. Adresu bazy nigdzie
nie wpisujesz — aplikacja odczytuje go z inventory i faktów hosta bazy.

## Część 1 — warstwa bazy danych (blok 4)

### Krok 1 — web01 zmienia rolę

W dniu 2 web01 był serwerem aplikacji (Apache na porcie 80). Dziś to baza i load balancer, więc usuwamy z niego
aplikację gotowym playbookiem:

```bash
ansible-playbook porzadki_web01.yml
curl http://localhost:8081/          # brak odpowiedzi — na web01 nic już nie działa na porcie 80
```

Zwróć uwagę na `hosts: all:!appservers` — wzorzec „wszystkie hosty oprócz grupy appservers”.

### Krok 2 — Gdzie trzymać zmienne bazy

Otwórz `inventory/group_vars/all.yml`: nazwa bazy, użytkownik i hasło są tam, bo potrzebują ich **dwie** warstwy:
baza (tworzy bazę i użytkownika) i aplikacja (łączy się z bazą).

### Krok 3 — Parametry roli: group_vars/databases.yml

Uzupełnij `inventory/group_vars/databases.yml` według `TODO` w pliku. Nazwy zmiennych i format list znalazłeś
w L12 (`README.md` i `defaults/main.yml` roli). Wartości bazy i użytkownika bierz ze zmiennych z `all.yml`:

```yaml
mysql_databases:
  - name: "{{ db_nazwa }}"
```

> Hasło roota jawnym tekstem jest tu tylko na czas ćwiczenia — w dniu 4 przeniesiemy hasła do ansible-vault.

### Krok 4 — Play warstwy bazy w site.yml

Na początku `site.yml`, **przed** playem aplikacji, dopisz:

```yaml
- name: Warstwa bazy danych
  hosts: databases
  become: true
  roles:
    - geerlingguy.mysql
```

Kolejność playów to kolejność warstw: baza musi działać, zanim aplikacja zacznie się z nią łączyć.

### Krok 5 — Uruchom

```bash
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml
ansible databases -b -m command -a "mysql -e 'SHOW DATABASES'"      # jest baza naszaaplikacja
```

Pierwsze uruchomienie trwa kilka minut (instalacja MySQL). Przeczytaj ostrzeżenia `DEPRECATION WARNING`:
to przeniesienie modułów `community.mysql` → `ansible.mysql` z L12, nie błąd w Twoim kodzie.

### Krok 6 — Drugie uruchomienie

```bash
ansible-playbook site.yml          # changed=0 — także rola z Galaxy jest idempotentna
```

---

## Część 2 — spięcie aplikacji z bazą (blok 5)

### Krok 7 — Rola aplikacja dostaje parametry bazy

Aplikacja czyta dane bazy z sekcji `[baza]` w `config.cfg` (`naszaaplikacja/config.cfg.example`). Rola ma być
ogólna: nie wie nic o Twoim inventory, dostaje tylko parametry.

1. W `roles/aplikacja/defaults/main.yml` dodaj cztery parametry z pustymi wartościami:
   `aplikacja_baza_host`, `aplikacja_baza_nazwa`, `aplikacja_baza_uzytkownik`, `aplikacja_baza_haslo`.
2. Na końcu `roles/aplikacja/templates/config.cfg.j2` dopisz sekcję wstawianą tylko wtedy, gdy host bazy jest podany:

   ```jinja
   {% if aplikacja_baza_host %}

   [baza]
   host = {{ aplikacja_baza_host }}
   uzytkownik = {{ aplikacja_baza_uzytkownik }}
   haslo = {{ aplikacja_baza_haslo }}
   nazwa = {{ aplikacja_baza_nazwa }}
   {% endif %}
   ```

3. Uruchom `site.yml`: `changed=0`. Parametry są puste, więc plik się nie zmienił.

### Krok 8 — Spięcie w inventory: hostvars i groups

W `inventory/group_vars/appservers.yml` dopisz:

```yaml
aplikacja_baza_host: "{{ hostvars[groups['databases'][0]].ansible_facts.default_ipv4.address }}"
aplikacja_baza_nazwa: "{{ db_nazwa }}"
aplikacja_baza_uzytkownik: "{{ db_uzytkownik }}"
aplikacja_baza_haslo: "{{ db_haslo }}"
```

Czytaj od środka: `groups['databases'][0]` — pierwszy host z grupy databases (web01); `hostvars[…]` — jego
zmienne; `.ansible_facts.default_ipv4.address` — jego adres IP z faktów zebranych w playu bazy.

```bash
ansible-playbook site.yml
curl http://localhost:8082/          # Baza danych: połączona z 172.…
```

Zmienia się tylko `config.cfg` na web02, a handler restartuje Apache.

### Krok 9 — Pułapka: --limit i brak faktów

```bash
ansible-playbook site.yml --limit appservers
```

Błąd: `… has no attribute 'default_ipv4'`. Z `--limit appservers` play bazy się nie wykonuje, więc Ansible nie zebrał
faktów web01 i nie zna jego adresu.

Rozwiązanie: w playu aplikacji, w `pre_tasks` (jako pierwsze zadanie), zbierz fakty hostów bazy jawnie:

```yaml
    - name: Zbierz fakty hostów bazy danych
      ansible.builtin.setup:
      delegate_to: "{{ item }}"         # wykonaj na hoście bazy…
      delegate_facts: true              # …i zapisz fakty jako fakty TEGO hosta, nie web02
      loop: "{{ groups['databases'] }}"
      run_once: true                    # raz, a nie osobno dla każdego serwera aplikacji
      tags: [always]
```

```bash
ansible-playbook site.yml --limit appservers      # działa, changed=0
```

## Sprawdzenie
- Dlaczego dane bazy są w `group_vars/all.yml`, a parametry roli MySQL w `group_vars/databases.yml`?
- Skąd aplikacja zna adres bazy? Co zmienisz, gdy baza przeniesie się na inny host?
- Dlaczego rola `aplikacja` nie odwołuje się sama do `groups['databases']`?
- Po co `delegate_facts: true`? Co by się stało bez tego?

Rozwiązanie: `odpowiedz/inventory/group_vars/databases.yml` i `appservers.yml`, `odpowiedz/site.yml`,
`odpowiedz/roles/aplikacja/templates/config.cfg.j2`.
