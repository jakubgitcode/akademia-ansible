# L8 — Wdrożenie aplikacji jednym playbookiem

Część 1 robisz w bloku 4 (35 min), część 2 w bloku 5 (35 min).

**Scenariusz:** deweloperzy dostarczają aplikację `naszaaplikacja` (katalog `naszaaplikacja/`: kod,
`requirements.txt`, przykładowe pliki konfiguracyjne i instrukcja `README.md`). Aplikacja ma działać na obu hostach
pod Apache z modułem WSGI. Nowe wersje będą przychodzić często, więc instalację opisujemy playbookiem,
a nie robimy ręcznie.

Prowadzący pokazał aplikację uruchomioną u dewelopera i kroki instalacji z `README.md`. Twój playbook robi te kroki
na obu hostach.

## Część 1 — pakiety, kod, virtualenv (blok 4)

### Krok 1 — Przeczytaj instrukcję dewelopera

```bash
cat naszaaplikacja/README.md
ls naszaaplikacja/
```

Otwórz `wgraj_aplikacje.yml`. Zadania są w tej samej kolejności co kroki instrukcji; parametry wdrożenia
(katalogi, port, nazwa, wersja) są w sekcji `vars`.

Po każdym kroku uruchamiaj playbook. Zadania, do których jeszcze nie doszedłeś, tylko wypisują
`TODO — krok N` (moduł `debug`): w każdym kroku zamieniasz `debug` na właściwy moduł.

```bash
ansible-playbook wgraj_aplikacje.yml       # na start: same komunikaty TODO, changed=0
```

> **Gdzie szukać:** w każdym kroku `ansible-doc -s <moduł>` (parametry) i `ansible-doc <moduł>` → `/EXAMPLES`.
> Typowe błędy (`conflicting action statements`, `Unsupported parameters`) i co z nimi zrobić — ramka w L6, krok 1.

### Krok 2 — Pakiety

`ansible.builtin.apt` z **listą** pakietów w `name`: `apache2`, `libapache2-mod-wsgi-py3`, `python3-venv`
i `python3-packaging`.

> Dokumentacja modułu `apt`: przy liście pakietów lepiej podać ją w `name` niż użyć `loop` —
> jedno wywołanie apt zamiast czterech.
>
> `python3-packaging` nie jest potrzebny aplikacji. Potrzebuje go moduł `ansible.builtin.pip` (krok 5), który działa
> na hoście w systemowym Pythonie — zobacz sekcję „Requirements” w `ansible-doc ansible.builtin.pip`. Bez tego
> pakietu krok 5 kończy się błędem `Failed to import the required Python library (packaging)`.

```bash
ansible-playbook wgraj_aplikacje.yml
ansible webservers -m command -a "dpkg -l apache2"      # ii  apache2 … — zainstalowany
```

Czy Apache działa i co pokazuje, sprawdzisz w kroku 10.

### Krok 3 — Katalogi

Katalog aplikacji i katalog logów (`owner`/`group`: `www-data`).

### Krok 4 — Kod aplikacji

`ansible.builtin.copy` z `src: naszaaplikacja/`. Ukośnik na końcu ma znaczenie:
- `src: naszaaplikacja/` kopiuje **zawartość** katalogu do `dest`;
- `src: naszaaplikacja` kopiuje **katalog** — powstałby `/var/www/naszaaplikacja/naszaaplikacja/`.

```bash
ansible-playbook wgraj_aplikacje.yml
ansible webservers -m command -a "ls /var/www/naszaaplikacja"
```

### Krok 5 — virtualenv i zależności

`ansible.builtin.pip` z `requirements` i `virtualenv` (przykłady: `ansible-doc ansible.builtin.pip`, `/EXAMPLES`).

```bash
ansible-playbook wgraj_aplikacje.yml
ansible webservers -m command -a "/var/www/naszaaplikacja/venv/bin/pip list"     # Flask, PyMySQL
```

### Krok 6 — Drugie uruchomienie

```bash
ansible-playbook wgraj_aplikacje.yml        # changed=0
```

Kod, pakiety i biblioteki są na hostach. Apache jeszcze nie wie o aplikacji — to część 2.

---

## Część 2 — konfiguracja i uruchomienie (blok 5)

### Krok 7 — Konfiguracja aplikacji z szablonu

Przykład dewelopera zamieniamy w szablon:

```bash
cp naszaaplikacja/config.cfg.example templates/config.cfg.j2
```

W `templates/config.cfg.j2` zamień wartości na zmienne:

| Było | Ma być |
|---|---|
| `nazwa = Nasza aplikacja` | `nazwa = {{ aplikacja_nazwa }}` |
| `srodowisko = deweloperskie` | `srodowisko = {{ srodowisko \| default('nieznane') }}` (zmienna z `group_vars`, L7) |
| `wersja = 1.0` | `wersja = {{ aplikacja_wersja }}` |
| `port = 5081` | `port = {{ aplikacja_port }}` |

Komentarze o bazie danych możesz usunąć (baza będzie w dniu 3). Uzupełnij zadanie „Wgraj konfigurację aplikacji”.

### Krok 8 — WSGI i VirtualHost z szablonów

```bash
cp naszaaplikacja/naszaaplikacja.wsgi.example        templates/naszaaplikacja.wsgi.j2
cp naszaaplikacja/naszaaplikacja.apache.conf.example templates/naszaaplikacja.conf.j2
```

W obu szablonach zamień ścieżki i port z przykładu dewelopera na zmienne:

| W przykładzie | Zmienna |
|---|---|
| `/var/www/szkolenie.pl/aplikacja` | `{{ aplikacja_katalog }}` |
| `/var/www/szkolenie.pl/logs` | `{{ aplikacja_log_dir }}` |
| `5081` | `{{ aplikacja_port }}` |

Sprawdź, czy nic nie zostało: `grep -n "szkolenie.pl/\|5081" templates/*.j2` — nie powinno nic wypisać
(nazwa serwera `naszaaplikacja.szkolenie.pl` może zostać).

Uzupełnij dwa zadania `template`.

### Krok 9 — Port nasłuchu

`ansible.builtin.lineinfile` w `/etc/apache2/ports.conf`. Dla portu 80 nic się nie zmieni (taka linia już jest),
ale ten sam playbook przestawi Apache na inny port, gdy zmienisz `aplikacja_port` — przyda się w dniu 3.

### Krok 10 — Włączenie strony i restart

- `a2ensite` nie ma modułu w `ansible.builtin`: `ansible.builtin.command` z `creates`
  (wzór: gotowe zadanie `a2dissite` z `removes` tuż pod nim).
- Restart Apache: `ansible.builtin.service`, `state: restarted`.

```bash
ansible-playbook wgraj_aplikacje.yml --check --diff     # przejrzyj zmiany w plikach konfiguracyjnych
ansible-playbook wgraj_aplikacje.yml
curl http://localhost:8081/
curl http://localhost:8082/
curl http://localhost:8081/health                         # OK
```

Oczekiwany wynik: strona „Nasza aplikacja” na obu hostach; web01 pokazuje `Środowisko: dev`, web02 `Środowisko: prod`
(jeśli w L7 uzupełniłeś `prod.yml`; inaczej `nieznane`).

### Krok 11 — Drugie uruchomienie

```bash
ansible-playbook wgraj_aplikacje.yml
```

Każdy host ma `changed=1`, choć nic się nie zmieniło: restart Apache wykonuje się zawsze. Zanotuj to — w L9
naprawimy to handlerem.

## Dodatkowe (gdy skończysz wcześniej)

- Trzy zadania `template` zastąp jednym z `loop` po liście słowników `src`/`dest` (pomysł z oryginalnego LAB 5).
- Strona nie działa? Logi aplikacji: `ansible web01 -b -m command -a "tail -20 /var/log/naszaaplikacja/error.log"`.
  Typowe przyczyny: literówka w ścieżce w szablonie, brak `venv` (krok 5), zostawiona domyślna strona Apache.

## Sprawdzenie
- Dlaczego kod kopiujemy modułem `copy`, a konfigurację generujemy modułem `template`?
- Po co `creates` w zadaniu z `a2ensite`? Co pokaże drugie uruchomienie bez niego?
- Gdzie są parametry wdrożenia i co trzeba zmienić, żeby aplikacja działała w innym katalogu?
- Dlaczego zmiana w `config.cfg` wymaga restartu Apache? (`naszaaplikacja/README.md`, ostatni akapit)

Rozwiązanie: `wgraj_aplikacje_odpowiedz.yml` i szablony w `templates/odpowiedz/`.
