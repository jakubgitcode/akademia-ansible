# Dzień 3 — laby

Dziś aplikacja z dnia 2 staje się projektem wielowarstwowym:

```
klient ──► web01: load balancer (nginx, :80) ──► web02, web03: aplikacja (Apache) ──► web01: baza (MySQL)
           http://localhost:8081                  http://localhost:8082, :8083
```

| Lab | Kiedy | Temat | Czas |
|---|---|---|---|
| [L11, część A](L11_role.md) | blok 1 | playbook z dnia 2 → rola `aplikacja` | 25 min |
| [L11, część B](L11_role.md#część-b--rola-w-siteyml-blok-2) | blok 2 | `site.yml` z rolą, `defaults` a `vars`, `import_role` a `include_role` | 35 min |
| [L12](L12_galaxy.md) | blok 3 | Galaxy i kolekcje, przypięte wersje | 30 min |
| [L13](L13_baza.md) | bloki 4 i 5 | baza danych z roli z Galaxy, spięcie przez `hostvars` | 35 + 35 min |
| [L14](L14_balanser.md) | bloki 6 i 7 | load balancer, skalowanie na trzeci host, diagnoza warstwami | 35 + 15 min |

## Środowisko

Od dziś trzy hosty: doszedł **web03** (SSH na porcie 2223, strona na `http://localhost:8083`).
Inventory dnia 3 (`inventory/hosts.yml`) dzieli hosty na **warstwy**, nie na środowiska:
`loadbalancers` i `databases` to web01, `appservers` to web02 (web03 dołączy w L14).

```bash
source ~/venv-ansible/bin/activate
cd ~/dzien3                             # albo: cd szkolenie5dni/dzien3/lab
ansible all -m ping                     # 3 × SUCCESS
ansible-inventory --graph
```

> web03 nie odpowiada? Hosty uruchomiono przed dodaniem web03: `cd ~/lab-env && ./setup.sh`
> (web01 i web02 zostają bez zmian).

## Gdy coś nie wychodzi

- Rozwiązanie to kompletny projekt w katalogu `odpowiedz/` (stan po L14). Uruchamiasz go z tego katalogu:
  `cd odpowiedz && ansible-playbook site.yml`.
- Pliki do porównania: rola `odpowiedz/roles/aplikacja/`, zmienne `odpowiedz/inventory/group_vars/`,
  szablon load balancera `odpowiedz/roles/loadbalancer/templates/`.
- Zatrzymaj się i zawołaj prowadzącego, zanim spędzisz nad jednym błędem więcej niż 5 minut.
