# L15 — Wiele środowisk

Część A robisz w bloku 1 (25 min), część B w bloku 2 (35 min).

**Cel:** ten sam `site.yml` i te same role stawiają dwa różne środowiska. Prod to trzy hosty z dnia 3,
dev to cała aplikacja na jednym hoście web04. Różnice opisują tylko zmienne.

## Część A — inventory per środowisko (blok 1)

### Krok 1 — Prod to dotychczasowe inventory

```bash
mkdir -p inventories
mv inventory inventories/prod
ansible-inventory -i inventories/prod --graph
```

### Krok 2 — Domyślnie dev

W `ansible.cfg` zmień linię `inventory`:

```ini
inventory = inventories/dev
```

Bez `-i` pracujesz na dev. Prod tylko jawnie: `-i inventories/prod`. Pomyłka kosztuje wtedy co najwyżej dev.

### Krok 3 — Hosty dev

Utwórz `inventories/dev/hosts.yml`: web04 (`ansible_port: 2224`, reszta połączenia jak w prod) we wszystkich trzech
grupach — `loadbalancers`, `databases`, `appservers`. Wzór układu: `inventories/prod/hosts.yml`.

```bash
ansible-inventory --graph          # bez -i: dev
```

### Krok 4 — Zmienne dev

```bash
mkdir -p inventories/dev/group_vars
cp inventories/prod/group_vars/*.yml inventories/dev/group_vars/
```

Zmień w kopiach:

| Plik | Zmienna | Dev |
|---|---|---|
| `all.yml` | `srodowisko` | `dev` |
| `all.yml` | `db_haslo` | inne niż w prod, np. `Dev-Baza-2026` |
| `all.yml` (dopisz) | `aplikacja_port` | `8080` — port 80 zajmie nginx na tym samym hoście |
| `all.yml` (dopisz) | `loadbalancer_port_backendow` | `"{{ aplikacja_port }}"` |
| `appservers.yml` | `aplikacja_nazwa` | `Nasza aplikacja — DEV` |
| `databases.yml` | `mysql_root_password` | inne niż w prod, np. `Dev-Root-2026` |

### Krok 5 — Połączenie

```bash
ansible all -m ping                # web04 | SUCCESS
```

### Krok 6 — Dev od zera

```bash
ansible-playbook site.yml
curl http://localhost:8084/        # Nasza aplikacja — DEV, Środowisko: dev, Serwer: web04, baza połączona
ansible-playbook site.yml          # changed=0
```

Ten sam kod, który w prod rozkłada aplikację na trzy hosty, tu stawia wszystko na jednym — z innym portem aplikacji.

### Krok 7 — Prod bez zmian

```bash
ansible-playbook -i inventories/prod site.yml --check
```

Zmiana tylko w zadaniu „Utwórz virtualenv i zainstaluj zależności” i w powiadomionym restarcie. To ograniczenie modułu
`pip`: z plikiem `requirements` w trybie `--check` zawsze zgłasza zmianę, bo nie umie tego sprawdzić bez instalacji
(L17: `--check` to symulacja, nie gwarancja). Pozostałe zadania: `ok` — przeniesienie plików niczego nie zmieniło.

## Część B — gdzie trzymać zmienne; inventory dynamiczne (blok 2)

### Krok 8 — Wspólne zmienne obok playbooka

Spięcie aplikacji z bazą i parametry roli MySQL są w obu środowiskach identyczne. Zamiast trzymać je dwa razy,
przenieś je do katalogu `group_vars/` **obok `site.yml`** — Ansible wczytuje go dla każdego inventory.

1. `mkdir group_vars`
2. Z `inventories/*/group_vars/appservers.yml` przenieś cztery zmienne `aplikacja_baza_*` do `group_vars/appservers.yml`
   (jeden raz). W inventory zostaje tylko `aplikacja_nazwa`.
3. W każdym `inventories/*/group_vars/all.yml` dopisz `db_haslo_root:` z wartością `mysql_root_password` tego środowiska.
4. Plik `databases.yml` przenieś z `inventories/prod/group_vars/` do `group_vars/` i zmień w nim
   `mysql_root_password: "{{ db_haslo_root }}"`. Usuń `inventories/dev/group_vars/databases.yml`.

```bash
ansible-playbook site.yml                                   # dev: changed=0
ansible-playbook -i inventories/prod site.yml --check       # prod: zmiana tylko w pip, jak w kroku 7
```

### Krok 9 — Pułapka: kto wygrywa

Dopisz na końcu `group_vars/appservers.yml` (tego obok playbooka): `aplikacja_nazwa: "Nazwa z group_vars obok playbooka"`.

```bash
ansible-playbook site.yml && curl -s http://localhost:8084/ | grep -o '<h1>.*</h1>'
```

Strona dev pokazuje nazwę z `group_vars` obok playbooka, nie z `inventories/dev`: **group_vars obok playbooka wygrywa
z group_vars w inventory**. Usuń tę linię i uruchom ponownie.

Zasada: obok playbooka tylko to, czego środowiska nie zmieniają; wartości środowisk — w `inventories/<środowisko>/`.

### Krok 10 — Inventory dynamiczne: skrypt

`dynamiczne/kontenery.py` pyta Dockera, które hosty labowe działają, i zwraca je w formacie JSON.
W firmie w tym miejscu jest zapytanie do API chmury albo CMDB.

```bash
ansible-inventory -i dynamiczne/kontenery.py --list    # ostrzeżenie: Unable to parse — skrypt nie jest wykonywalny
chmod +x dynamiczne/kontenery.py
dynamiczne/kontenery.py --list                         # sam skrypt: JSON z hostami i ich zmiennymi
ansible -i dynamiczne/kontenery.py all -m ping         # 4 × SUCCESS
```

Skrypt inventory musi być wykonywalny — inaczej Ansible próbuje czytać go jak plik INI.

### Krok 11 — Inventory hybrydowe

`dynamiczne/grupy.yml` dokłada grupy do hostów ze skryptu. Uzupełnij `TODO`: grupa `monitorowane` z web02 i web04.

```bash
ansible-inventory -i dynamiczne/ --graph               # cały katalog: skrypt + plik statyczny
ansible -i dynamiczne/ monitorowane -m ping
```

Przeczytaj też `przyklady/aws_ec2.yml`: wtyczka inventory, która pobiera maszyny kursantów tego szkolenia z AWS
(filtry po tagach, grupy z tagów). Nie uruchamiamy — wymaga konta AWS.

### Krok 12 — Pułapka: dwa inventory naraz

```bash
ansible-inventory -i inventories/dev -i inventories/prod --graph appservers
```

Kilka `-i` Ansible łączy w jedno inventory: `site.yml` uruchomiony tak zmieniłby dev i prod naraz.

## Sprawdzenie
- Co musisz zmienić, żeby dodać środowisko `test`?
- Dlaczego domyślnym inventory jest dev, a nie prod?
- Kiedy zmienna trafia do `group_vars` obok playbooka, a kiedy do `inventories/<środowisko>/group_vars`?
- Co łączy, a co różni inventory statyczne, dynamiczne i hybrydowe?

Rozwiązanie: `odpowiedz/inventories/`, `odpowiedz/group_vars/`, `odpowiedz/dynamiczne/grupy.yml`
(w rozwiązaniu jest już stan po L16: `group_vars/all/` jako katalog z plikiem vault).
