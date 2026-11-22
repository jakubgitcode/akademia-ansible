# Drugi przykład ansible.cfg (L1 część B, krok 8)

Pierwszy `ansible.cfg` z L1 (`../ansible.cfg.odpowiedz`) ma trzy linie. Ten jest rozbudowany, w stylu projektów
prowadzącego: każde ustawienie z komentarzem, inventory z `group_vars/` i `host_vars/`, cache faktów.
Hosty są te same co w labie (web01 i web02 z `lab-env`) plus `localhost`.

```
przyklad_cfg/
├── ansible.cfg                 ustawienia projektu (opisane w pliku)
├── pokaz_cfg.yml               playbook do pokazu: grupy, zmienne, fakty z cache
└── inventory/
    ├── hosts.yml               hosty i grupy (to samo w hosts.ini)
    ├── hosts.ini
    ├── group_vars/all.yml      dane połączenia — dlatego hosts.yml jest krótki
    ├── group_vars/webservers.yml
    ├── group_vars/prod.yml     wygrywa z all: web02 ma srodowisko "produkcja"
    └── host_vars/web01.yml     wygrywa z group_vars: web01 ma http_port 8080
```

## Co jest nowe względem pierwszego ansible.cfg

| Ustawienie | Po co |
|---|---|
| `interpreter_python = /usr/bin/python3` | Python na hostach wprost, bez ostrzeżeń (zamiast `ansible_python_interpreter` w inventory) |
| `forks = 10` | 10 hostów naraz zamiast 5 |
| `gathering = smart` + `fact_caching = jsonfile` | fakty zbierane raz na godzinę, potem z plików w `~/.ansible/fakty` |
| `roles_path` | gdzie szukać ról (dzień 3) |
| `callback_result_format = yaml` | wyniki zadań czytelniej niż JSON |
| `host_key_checking = False` | bez pytania o klucz hosta — **tylko w labie** |
| `[inventory] enable_plugins` | które formaty inventory wolno czytać (np. `auto` dla `aws_ec2.yml`) |
| `[diff] context` | ile linii wokół zmiany pokazuje `--diff` |

## Wypróbuj

```bash
cd ~/dzien1/przyklad_cfg
ansible-config dump --only-changed                  # ustawienia ogólne z tego pliku
ansible-config dump --only-changed -t callback      # ustawienia wtyczek: result_format = yaml
ansible-config dump --only-changed -t connection    # pipelining = True
ansible-inventory --graph                           # web01 i web02 są też w grupie monitoring
ansible-inventory --host web02                      # zmienne po połączeniu plików: srodowisko = produkcja
ansible all -m ping                                 # localhost, web01, web02
ansible-playbook pokaz_cfg.yml                      # 1. raz: zadanie "Gathering Facts"
ansible-playbook pokaz_cfg.yml                      # 2. raz: bez "Gathering Facts" — fakty z cache
ls ~/.ansible/fakty                                 # jeden plik JSON na host
ansible-playbook pokaz_cfg.yml --flush-cache        # wymuś ponowne zebranie faktów
```

Inventory w INI zamiast YAML: zmień w `ansible.cfg` linię `inventory = inventory/hosts.ini`
(albo jednorazowo `-i inventory/hosts.ini`). Wynik `ansible-inventory --list` jest ten sam.

> Cache faktów przyspiesza, ale fakty mogą być nieaktualne (np. po zmianie RAM-u albo dodaniu dysku na hoście).
> Po zmianach na hostach uruchom z `--flush-cache` albo skróć `fact_caching_timeout`.
