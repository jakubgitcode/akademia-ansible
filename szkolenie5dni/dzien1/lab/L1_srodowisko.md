# L1 — Środowisko pracy

Część A robisz w dniu 1: krok 1 w godzinie organizacyjnej (9:00–10:00), kroki 2–4 w bloku 1 (25 min).
Część B robisz w dniu 5 (blok 7, 7 min), w tym samym katalogu `~/dzien1`.

## Część A — Ansible, inventory, ping (dzień 1)

### Cel
Zainstalować Ansible, opisać w inventory dwa hosty i sprawdzić, że Ansible się z nimi łączy.

### Krok 1 — Ansible w wirtualnym środowisku Pythona (venv)

venv nie zaśmieca systemu i pozwala mieć obok siebie różne wersje Ansible dla różnych projektów.

```bash
python3 -m venv ~/venv-ansible
source ~/venv-ansible/bin/activate

pip install --upgrade pip
pip install ansible

ansible --version
```

Oczekiwany wynik (numery wersji mogą być inne):
```
ansible [core 2.21.6]
  ...
  python version = 3.12.3 ...
```

> Na Pythonie 3.12 (Ubuntu 24.04) dostaniesz ansible-core 2.21, na Pythonie 3.13 i nowszym — 2.22.
> Laby działają na obu wersjach.
>
> Po otwarciu nowego terminala trzeba ponownie wykonać `source ~/venv-ansible/bin/activate`.
> Gdy `python3 -m venv` zgłasza błąd na Ubuntu: `sudo apt install python3-venv`.

### Krok 2 — Uzupełnij inventory

Otwórz `inventory/hosts.yml` i zamień wszystkie `TODO` na dane połączenia
(od prowadzącego albo z [README](README.md#środowisko) dla `lab-env`).

```bash
vi inventory/hosts.yml     # albo otwórz w VS Code
```

Sprawdź strukturę: jakie są grupy i które hosty do nich należą?
```bash
ansible-inventory -i inventory/hosts.yml --graph
ansible-inventory -i inventory/hosts.yml --list
```

### Krok 3 — Przetestuj połączenie

```bash
ansible all -i inventory/hosts.yml -m ping
ansible prod -i inventory/hosts.yml -m ping
ansible web01 -i inventory/hosts.yml -m ping
```

Oczekiwany wynik:
```
web01 | SUCCESS => { ... "ping": "pong" }
web02 | SUCCESS => { ... "ping": "pong" }
```

> `UNREACHABLE` — sprawdź adres, port, użytkownika i ścieżkę do klucza w inventory.
> `-vvv` pokazuje, jak dokładnie Ansible łączy się przez SSH:
> `ansible web01 -i inventory/hosts.yml -m ping -vvv`

### Krok 4 — To samo bez Ansible

Moduł `ping` nie używa sieciowego „pinga”. Loguje się przez SSH i uruchamia na hoście mały program w Pythonie.
Dla porównania zaloguj się ręcznie (dane jak w inventory):

```bash
ssh -i ~/.ssh/akademia_lab_key -p 2221 ubuntu@127.0.0.1 'hostname; python3 --version'
```

### Sprawdzenie (część A)
- Gdzie jest zainstalowany Ansible: na control node czy na hostach? Co musi być na hostach?
- Do jakich grup należy web02?
- Co oznacza `UNREACHABLE`, a co `FAILED`?

Rozwiązanie: `inventory_odpowiedz/hosts.yml`.

---

## Część B — ansible.cfg i wersje (dzień 5, blok 7)

### Cel
Zapisać ustawienia projektu w `ansible.cfg`, przypiąć wersję Ansible i odtwarzać środowisko jednym poleceniem.

### Krok 5 — ansible.cfg: koniec z `-i inventory/hosts.yml`

Utwórz w katalogu labu plik `ansible.cfg`:

```ini
[defaults]
inventory = inventory/hosts.yml
callbacks_enabled = ansible.posix.profile_tasks

[ssh_connection]
pipelining = True
```

```bash
ansible all -m ping                             # bez -i
ansible-config dump --only-changed              # co zmieniliśmy względem domyślnych
ansible-playbook pierwszy_playbook.yml          # na końcu: czasy zadań (profile_tasks)
```

> Na ansible-core 2.22 `ansible-config dump` wypisuje ostrzeżenia `DEPRECATION WARNING` o wtyczkach `tree`
> i `oneline`. To nie Twoja konfiguracja: Ansible ostrzega o wtyczkach, które usunie w wersji 2.23.

> Ansible **pomija** `ansible.cfg` w katalogu zapisywalnym dla wszystkich i wypisuje ostrzeżenie
> `Ansible is being run in a world writable directory`. Dotyczy to np. `/mnt/c` w WSL i folderów współdzielonych
> z maszyną wirtualną. Projekt trzymaj w katalogu domowym Linuksa.

### Krok 6 — Przypnij wersję

```bash
pip freeze | grep -iE '^ansible(-core)?==' > requirements.txt
cat requirements.txt
```

Z tym plikiem każdy (także serwer CI) zainstaluje te same wersje: `pip install -r requirements.txt`.
Aktualizacja Ansible to zmiana numeru w tym pliku, test w nowym venv i dopiero potem przełączenie.

### Krok 7 (jeśli zostanie czas) — source_me.sh

`source_me.sh` tworzy venv w katalogu projektu, instaluje wersje z `requirements.txt` i ustawia zmienne `ANSIBLE_*`
projektu (poziom „zmienna środowiska” z L6 część 0 w dniu 2: wygrywa z `ansible.cfg`, przegrywa z opcjami polecenia).

```bash
deactivate                 # wyjdź z ~/venv-ansible
source source_me.sh        # pierwszy raz: tworzy ./venv i instaluje pakiety (1–2 minuty)
which ansible              # ansible z ./venv projektu
env | grep ^ANSIBLE_       # ANSIBLE_CONFIG i ANSIBLE_CALLBACK_RESULT_FORMAT ze skryptu
ansible-config dump --only-changed -t callback | grep 'env:'   # result_format(env: ANSIBLE_CALLBACK_RESULT_FORMAT) = yaml
deactivate && env | grep ^ANSIBLE_                             # pusto: zmienne projektu znikają razem z venv
```

Otwórz `source_me.sh`: zakomentowane linie (`ANSIBLE_FORKS`, `ANSIBLE_VAULT_PASSWORD_FILE`, `ANSIBLE_KEEP_REMOTE_FILES`)
to ustawienia, które w projekcie warto mieć w jednym miejscu, zamiast pamiętać je przy każdym poleceniu.

### Krok 8 (dla chętnych) — drugi, rozbudowany ansible.cfg

Katalog `przyklad_cfg/` to osobny mały projekt: `ansible.cfg` z opisem każdego ustawienia (forks, cache faktów,
`roles_path`, wynik w YAML, wtyczki inventory) i inventory z `group_vars/` i `host_vars/`. Instrukcja:
[`przyklad_cfg/README.md`](przyklad_cfg/README.md).

```bash
cd przyklad_cfg
ansible-config dump --only-changed     # porównaj z wynikiem z kroku 5
ansible-playbook pokaz_cfg.yml         # uruchom dwa razy: za drugim fakty są z cache
cd ..
```

### Sprawdzenie (część B)
- Skąd Ansible bierze konfigurację i co robi `ansible-config dump --only-changed`?
- Dlaczego wersja Ansible w projekcie powinna być przypięta?
- Jak zaktualizować Ansible bez ryzyka, że zepsujesz działające środowisko?

Rozwiązania: `ansible.cfg.odpowiedz`, `requirements.txt.odpowiedz`.
