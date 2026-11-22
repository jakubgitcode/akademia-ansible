# Dzień 4 — laby

Punkt startu: projekt z dnia 3 (role `aplikacja` i `loadbalancer`, `site.yml`, inventory warstw). Dziś robimy z niego
projekt, który da się bezpiecznie utrzymywać: dwa środowiska, sekrety w vault, diagnostyka i kontrolowane zmiany.

```
prod: web01 (load balancer + baza) → web02, web03 (aplikacja)     http://localhost:8081
dev:  web04 — cała aplikacja na jednym hoście                      http://localhost:8084
```

| Lab | Kiedy | Temat | Czas |
|---|---|---|---|
| [L15, część A](L15_srodowiska.md) | blok 1 | inventory per środowisko: dev na web04 | 25 min |
| [L15, część B](L15_srodowiska.md#część-b--gdzie-trzymać-zmienne-inventory-dynamiczne-blok-2) | blok 2 | gdzie trzymać zmienne; inventory dynamiczne i hybrydowe | 35 min |
| [L16](L16_vault.md) | blok 3 | ansible-vault: hasła dev i prod, `no_log`, rotacja hasła | 35 min |
| [L17](L17_diagnostyka.md) | blok 4 | pięć błędów do znalezienia; moduł od środka | 35 min |
| [L18, część A](L18_sterowanie.md) | blok 5 | `changed_when`, `failed_when`, `until`, `assert`, `block`/`rescue` | 35 min |
| [L18, część B](L18_sterowanie.md#część-b--restart-bez-przerwy-w-działaniu-blok-6) | blok 6 | restart po jednym węźle: `serial` | 35 min |
| [L18, część C](L18_sterowanie.md#część-c--throttle-i-restart-w-handlerze-blok-7) | blok 7 | `throttle` a restart w handlerze z pętlą | 15 min |

## Środowisko

Od dziś cztery hosty: doszedł **web04** (SSH na porcie 2224, strona na `http://localhost:8084`).

```bash
source ~/venv-ansible/bin/activate
cd ~/dzien4                             # albo: cd szkolenie5dni/dzien4/lab
ansible-galaxy install -r requirements.yml
ansible all -m ping                     # na start: prod (web01–web03)
ansible-playbook site.yml               # stan z dnia 3: changed=0
```

> web04 nie odpowiada? `cd ~/lab-env && ./setup.sh` (pozostałe hosty zostają bez zmian).

## Gdy coś nie wychodzi

- Rozwiązanie to kompletny projekt w `odpowiedz/` (stan na koniec dnia). Hasła do jego plików vault:
  dev `dev-szkolenie`, prod `prod-szkolenie` (L16, krok 3).
- Zatrzymaj się i zawołaj prowadzącego, zanim spędzisz nad jednym błędem więcej niż 5 minut.
