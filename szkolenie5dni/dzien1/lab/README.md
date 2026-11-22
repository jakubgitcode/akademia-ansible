# Dzień 1 — laby

Wszystkie laby dnia 1 robisz w tym katalogu. Inventory uzupełnione w L1 służy potem w L2, L4 i L5.

| Lab | Kiedy | Temat | Czas |
|---|---|---|---|
| [L1, część A](L1_srodowisko.md) | organizacja (krok 1) i blok 1 | Ansible w venv, inventory, `ping` | 25 min |
| [L2](L2_adhoc.md) | blok 2 | polecenia ad-hoc, moduły, dokumentacja | 30 min |
| [L3](L3_yaml_jinja.md) | blok 3 | YAML i Jinja2 (lokalnie, bez hostów) | 30 min |
| [L4, część 1](L4_playbook.md) | blok 4 | pierwszy playbook | 35 min |
| [L5](L5_zmienne.md) | blok 5 | zmienne i ich priorytety | 30 min |
| [L4, część 2](L4_playbook.md#część-2--shell-kontra-moduł-własny-playbook-blok-6) | blok 6 | shell kontra moduł; krok 8 (własny playbook) w domu | 20 min |
| [L1, część B](L1_srodowisko.md#część-b--ansiblecfg-i-wersje-dzień-5-blok-7) | **dzień 5**, blok 7 | `ansible.cfg`, przypięta wersja, `source_me.sh` | 7 min |
| [`przyklad_cfg/`](przyklad_cfg/README.md) | dla chętnych (L1 część B, krok 8) | drugi, rozbudowany `ansible.cfg` z inventory, `group_vars` i `host_vars` | — |

## Środowisko

```
Control node : Twój komputer albo maszyna od prowadzącego — tu instalujesz Ansible i wpisujesz polecenia
web01 (dev)  : Ubuntu 24.04, SSH, użytkownik ubuntu z sudo bez hasła
web02 (prod) : jak web01
```

Każdy uczestnik ma własną parę hostów, więc wynik `changed`/`ok` zależy tylko od Ciebie.

Hosty z Dockera (`lab-env`) uruchamia jedno polecenie; prowadzący mógł już to zrobić za Ciebie:

```bash
lab-env/setup.sh      # klucz ~/.ssh/akademia_lab_key, kontenery web01 i web02, test SSH
```

Dane połączenia dla `lab-env`: oba hosty pod adresem `127.0.0.1`, SSH na porcie `2221` (web01) i `2222` (web02),
użytkownik `ubuntu`, klucz `~/.ssh/akademia_lab_key`.

## Gdy coś nie wychodzi

- Rozwiązania są obok zadań: pliki `*_odpowiedz.yml`, katalog `inventory_odpowiedz/`, pliki `*.odpowiedz`.
- Jeśli nie skończysz L1, pracuj dalej na gotowym inventory: `cp inventory_odpowiedz/hosts.yml inventory/hosts.yml`.
- Zatrzymaj się i zawołaj prowadzącego, zanim spędzisz nad jednym błędem więcej niż 5 minut.
