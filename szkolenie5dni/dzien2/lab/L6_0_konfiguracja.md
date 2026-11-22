# L6, część 0 — skąd Ansible bierze ustawienia (blok 1, 7 minut)

Od dziś piszesz polecenia bez `-i inventory/hosts.yml`, bo ten katalog ma `ansible.cfg`. To jeden z kilku poziomów,
z których Ansible bierze nastawy. Od najsłabszego do najsilniejszego:

| Poziom | Przykład | Rodzaj |
|---|---|---|
| 1. `ansible.cfg` | `inventory = inventory/hosts.yml` | ustawienie |
| 2. zmienna środowiska `ANSIBLE_*` | `ANSIBLE_INVENTORY=…`, `ANSIBLE_REMOTE_USER=…` | ustawienie |
| 3. opcja polecenia | `-i`, `-u`, `-f` | ustawienie |
| 4. słowo kluczowe w playbooku | `remote_user:` w play | ustawienie |
| 5. zmienna | `ansible_user` w inventory, `group_vars`, `vars:` (kolejność między nimi: L5) | zmienna |
| 6. `-e` | `-e ansible_user=…` | zmienna, wygrywa ze wszystkim |

Cała tabela w dokumentacji: „Controlling how Ansible behaves: precedence rules”.

Zmienne środowiska podajesz tu **przed poleceniem** (`ZMIENNA=wartość polecenie`): działają tylko na to jedno polecenie.
`export ZMIENNA=wartość` zostaje w terminalu do jego zamknięcia albo `unset ZMIENNA`. Tak działa `source_me.sh`
z dnia 5.

### Krok 1 — plik

```bash
cd ~/dzien2
ansible-config dump --only-changed
```

W nawiasie jest źródło: `DEFAULT_HOST_LIST(/home/kursant/dzien2/ansible.cfg) = [...]`. Pierwsza linia,
`CONFIG_FILE()`, mówi, który `ansible.cfg` Ansible wczytał. Wczytuje tylko jeden: z `ANSIBLE_CONFIG`, z bieżącego
katalogu, `~/.ansible.cfg` albo `/etc/ansible/ansible.cfg` — pierwszy znaleziony.

### Krok 2 — zmienna środowiska wygrywa z plikiem

```bash
ANSIBLE_PIPELINING=False ansible-config dump --only-changed | grep PIPELINING
ANSIBLE_INVENTORY=nieistnieje.yml ansible all -m ping
```

Pierwsze: `ANSIBLE_PIPELINING(env: ANSIBLE_PIPELINING) = False`, choć `ansible.cfg` ma `pipelining = True`.
Drugie: `provided hosts list is empty` — inventory z pliku zostało zastąpione nieistniejącym.

### Krok 3 — opcja polecenia wygrywa ze zmienną środowiska

```bash
ANSIBLE_INVENTORY=nieistnieje.yml ansible all -i inventory/hosts.yml -m ping
```

Dwa razy `SUCCESS`.

### Krok 4 — zmienna wygrywa z opcją polecenia

```bash
ansible web01 -m ansible.builtin.command -a whoami -u root
ANSIBLE_REMOTE_USER=root ansible web01 -m ansible.builtin.command -a whoami
ansible-inventory --host web01 | grep ansible_user
```

Oba razy `ubuntu`, nie `root`: `ansible_user: ubuntu` z inventory jest zmienną i wygrywa z `-u` i z `ANSIBLE_REMOTE_USER`.
To częsta pułapka: „podałem `-u`, a Ansible łączy się jako ktoś inny”.

### Krok 5 — `-e` wygrywa ze wszystkim

```bash
ansible web01 -m ansible.builtin.ping -e ansible_user=root
```

`UNREACHABLE` i `Permission denied`: tym razem Ansible naprawdę łączy się jako `root`, a root nie ma na hostach
labu Twojego klucza.

### Sprawdzenie
- Jak sprawdzisz, skąd pochodzi wartość ustawienia? (`ansible-config dump --only-changed`, źródło w nawiasie)
- Kolega mówi: „dałem `-u admin`, a Ansible wciąż łączy się jako `ubuntu`”. Co mu odpowiesz?
- Dlaczego `-e` w poleceniu bywa niebezpieczne w playbookach używanych przez zespół?

Wrócisz do tego w dniu 4 (`ANSIBLE_KEEP_REMOTE_FILES` przy debugowaniu modułu) i w dniu 5 (`source_me.sh` ustawia
zmienne `ANSIBLE_*` dla całego projektu).
