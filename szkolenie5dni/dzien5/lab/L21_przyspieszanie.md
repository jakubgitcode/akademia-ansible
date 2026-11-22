# L21 — Lookupy, delegacja, async; przyspieszanie (blok 6, 35 min)

Pracujesz w `projekt/`.

## Część A — lookupy, delegacja, async (15 min)

```bash
cd ~/dzien5/projekt
time ansible-playbook ciekawostki.yml
cat wdrozenia.log
```

Przeczytaj `ciekawostki.yml` i znajdź odpowiedzi:
- `lookup('ansible.builtin.pipe', 'hostname')` zwraca nazwę Twojej maszyny, nie web04. Dlaczego?
  (lookup wykonuje się na control node; w AWX — w kontenerze zadania)
- `query()` zwraca listę, `lookup()` — napis. Kiedy które?
- `delegate_to: localhost` + `run_once`: jeden wpis w `wdrozenia.log`, choć play dotyczy grupy.
- `async` + `poll: 0`: długie zadanie działa w tle, a w tym czasie wykonuje się następne. Całość trwa ok. 15 sekund,
  nie 30. Zmień `poll: 0` na `poll: 5` i porównaj `time`.

## Część B — przyspieszanie (20 min)

Mierz na prod (trzy hosty). Każde polecenie uruchom i zapisz czas.

### Krok 1 — Gdzie ucieka czas

```bash
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.profile_tasks ansible-playbook -i inventories/prod site.yml
```

Na końcu: najwolniejsze zadania. Zwykle: zbieranie faktów, `apt` i `pip`.

### Krok 2 — pipelining i forks

```bash
time ANSIBLE_PIPELINING=0 ansible-playbook -i inventories/prod site.yml     # bez pipelining (domyślne Ansible)
time ansible-playbook -i inventories/prod site.yml                          # z pipelining (nasz ansible.cfg)
time ansible-playbook -i inventories/prod site.yml -f 1                     # jeden host naraz
```

`pipelining` przesyła moduł przez już otwarte połączenie SSH zamiast kopiować plik. `forks` (domyślnie 5) to liczba
hostów obsługiwanych równolegle — przy setkach hostów podnosisz ją do 20–50.

### Krok 3 — Pamięć podręczna faktów

W `ansible.cfg`, w `[defaults]`, dopisz:

```ini
gathering = smart
fact_caching = jsonfile
fact_caching_connection = .fakty
fact_caching_timeout = 3600
```

```bash
time ansible-playbook -i inventories/prod site.yml      # zbiera fakty i zapisuje w .fakty/
time ansible-playbook -i inventories/prod site.yml      # bierze fakty z .fakty/
ls .fakty/           # pliki z przedrostkiem, np. s1_web02
```

Przy okazji: z pamięcią faktów `--limit appservers` zna fakty bazy z poprzedniego uruchomienia (dzień 3, L13, krok 9).
W firmie zamiast plików: Redis, wspólny dla zespołu albo AWX.

### Krok 4 — mitogen

```bash
pip install mitogen==0.3.55
STRAT=$(python3 -c "import ansible_mitogen, os; print(os.path.join(os.path.dirname(ansible_mitogen.__file__), 'plugins', 'strategy'))")
time ANSIBLE_STRATEGY_PLUGINS=$STRAT ANSIBLE_STRATEGY=mitogen_linear ANSIBLE_HOST_KEY_CHECKING=False \
  ansible-playbook -i inventories/prod site.yml
```

`ANSIBLE_HOST_KEY_CHECKING=False`: mitogen sprawdza klucze hostów po swojemu, a kontenery labowe dostają nowe klucze
przy każdym starcie (bez tej zmiennej: `UNREACHABLE … mismatching host key`). Na prawdziwych serwerach jej nie używaj.

mitogen utrzymuje na hoście proces Pythona i wykonuje w nim moduły bez ponownego uruchamiania interpretera.
Zysk jest największy przy wielu krótkich zadaniach i dalekich hostach. W teście tych labów (GitHub Actions, prod na trzech
kontenerach) `site.yml` skrócił się z ok. 38 do 22 sekund; `pipelining` dał ok. 3 sekundy, `forks` przy trzech hostach — niewiele. Sprawdzaj zgodność z wersją ansible-core przed aktualizacją (wydania mitogen goni za ansible-core).

### Krok 5 — Porównanie

Zapisz czasy w tabeli i porównaj z sąsiadem. Co z tego zastosujesz w swoim projekcie od jutra?

## Sprawdzenie
- Gdzie wykonuje się lookup, a gdzie moduł?
- Kiedy `async`, a kiedy po prostu więcej `forks`?
- Dlaczego `pipelining` nie jest domyślnie włączony? (podpowiedź: `requiretty` w sudoers na starszych systemach)
- Co daje pamięć podręczna faktów poza szybkością?
