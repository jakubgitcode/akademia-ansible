# L11 — Playbook z dnia 2 zamieniamy w rolę

Część A robisz w bloku 1 (25 min), część B w bloku 2 (35 min).

**Po co:** playbook `wgraj_aplikacje.yml` działa, ale wszystko jest w jednym pliku: zadania, zmienne, handlery,
a szablony i kod leżą obok. Rola to ta sama treść ułożona w standardowe katalogi — da się ją użyć w wielu
playbookach, przekazać innemu zespołowi albo opublikować w Galaxy.

**Zasada refaktoryzacji:** po przeróbce wynik na serwerze ma być identyczny. Dowód: uruchomienie roli na hoście
postawionym starym playbookiem daje `changed=0`.

## Część A — z playbooka do katalogów roli (blok 1)

### Krok 1 — Punkt startu

`wgraj_aplikacje.yml` to rozwiązanie z dnia 2; zmieniło się tylko `hosts: appservers` (warstwa aplikacji
w nowym inventory). Szablony są w `templates/`, kod aplikacji w `naszaaplikacja/`.

```bash
ansible-inventory --graph
ansible-playbook wgraj_aplikacje.yml
curl http://localhost:8082/
```

Po tym uruchomieniu web02 jest w stanie wzorcowym — do niego porównamy rolę.

> Chcesz pracować na swoim playbooku z dnia 2? Skopiuj go tu razem z szablonami (zmień `hosts:` na `appservers`).

### Krok 2 — Szkielet roli

```bash
ansible-galaxy role init roles/aplikacja
tree roles/aplikacja
```

| Katalog | Co trafia | Z którego miejsca playbooka |
|---|---|---|
| `tasks/main.yml` | lista zadań | sekcja `tasks:` |
| `handlers/main.yml` | handlery | sekcja `handlers:` |
| `templates/` | szablony Jinja2 | katalog `templates/` |
| `files/` | pliki kopiowane bez zmian | katalog `naszaaplikacja/` (kod aplikacji) |
| `defaults/main.yml` | **parametry** roli — łatwo je nadpisać | sekcja `vars:` |
| `vars/main.yml` | **stałe** roli — wygrywają z inventory | (nowe) lista pakietów |
| `meta/main.yml` | opis roli, zależności | (nowe) |

Katalogu `tests/` nie potrzebujemy — możesz go usunąć.

### Krok 3 — Zadania i handlery

1. Do `roles/aplikacja/tasks/main.yml` skopiuj **zawartość** sekcji `tasks:` z `wgraj_aplikacje.yml`
   (same zadania, bez `- name: Wdrożenie…`, `hosts:` i `tasks:`) i przesuń je w lewo o 4 spacje — w pliku roli
   zadania zaczynają się od pierwszej kolumny.
2. Do `roles/aplikacja/handlers/main.yml` — tak samo zawartość sekcji `handlers:`.

W edytorze `vi`: zaznacz linie (`V`, strzałki) i `<` przesuwa o jeden poziom wcięcia.

### Krok 4 — Szablony, kod, zmienne

```bash
cp templates/config.cfg.j2 templates/naszaaplikacja.conf.j2 templates/naszaaplikacja.wsgi.j2 roles/aplikacja/templates/
cp -r naszaaplikacja roles/aplikacja/files/
```

1. W zadaniach `template` zmień `src: templates/config.cfg.j2` na `src: config.cfg.j2` (i tak dla trzech szablonów):
   rola szuka szablonów we własnym katalogu `templates/`. `src: naszaaplikacja/` w zadaniu `copy` zostaje —
   rola szuka plików w `files/`.
2. Do `roles/aplikacja/defaults/main.yml` przenieś zmienne z sekcji `vars:` playbooka.
3. Do `roles/aplikacja/vars/main.yml` wpisz listę pakietów jako `aplikacja_pakiety` i w zadaniu `apt` użyj
   `name: "{{ aplikacja_pakiety }}"`.

Wszystkie zmienne roli zaczynają się od `aplikacja_` — nazwy roli. Dzięki temu nie zderzą się ze zmiennymi
innych ról w tym samym playu.

## Część B — rola w site.yml (blok 2)

### Krok 5 — site.yml

Otwórz `site.yml`. To główny playbook projektu: dziś dojdą do niego trzy warstwy.

1. Przenieś `pre_tasks` i `post_tasks` z `wgraj_aplikacje.yml` do playa „Warstwa aplikacji”.
2. Zamień `roles: []` na:
   ```yaml
     roles:
       - aplikacja
   ```

```bash
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml --list-tasks     # zadania roli z prefiksem „aplikacja :”
```

### Krok 6 — Dowód refaktoryzacji: changed=0

```bash
ansible-playbook site.yml
```

Oczekiwany wynik: `changed=0`. Każda zmiana oznacza, że rola robi coś inaczej niż playbook — sprawdź
`--check --diff`, co dokładnie, i popraw rolę.

Typowe przyczyny: zostało `src: templates/…` w zadaniu `template` (błąd „Could not find or access”),
zmienna z literówką w `defaults/main.yml`, brak pliku w `files/naszaaplikacja/`.

### Krok 7 — Parametry: defaults kontra group_vars kontra vars

1. W `inventory/group_vars/appservers.yml` wpisz `aplikacja_nazwa: "Nasza aplikacja — produkcja"` i uruchom
   `site.yml`. Nowa nazwa jest na stronie: **group_vars wygrywa z `defaults/` roli**.
2. Pułapka: dopisz `aplikacja_nazwa: "Nazwa z vars roli"` na końcu `roles/aplikacja/vars/main.yml` i uruchom.
   Strona pokazuje nazwę z `vars/`: **`vars/` roli wygrywa z group_vars**.
3. Usuń tę linię z `vars/main.yml` i uruchom ponownie.

Wniosek: parametry, które ktoś ma zmieniać, trzymaj w `defaults/`; w `vars/` tylko to, czego nie wolno nadpisać.

### Krok 8 — import_role kontra include_role

`import_include.yml` używa roli na dwa sposoby. Nie uruchamiaj go — porównaj:

```bash
ansible-playbook import_include.yml --list-tasks
ansible-playbook import_include.yml --list-tags
```

| | `import_role` (i `roles:`) | `include_role` |
|---|---|---|
| kiedy Ansible wczytuje rolę | przed uruchomieniem | w trakcie, gdy dojdzie do zadania |
| `--list-tasks`, `--list-tags` | widać zadania i tagi roli | widać tylko zadanie `include_role` |
| `when` na zadaniu z rolą | dopisany do każdego zadania roli | sprawdzany raz: wczytać rolę czy nie |
| pętla (`loop`) | niemożliwa | możliwa — rola kilka razy z różnymi parametrami |

### Krok 9 (jeśli zdążysz) — opis roli

Uzupełnij `roles/aplikacja/meta/main.yml` (`author`, `description`, `platforms`: Ubuntu `noble`)
i `README.md` roli: co robi, jakie ma parametry. Wzór: `odpowiedz/roles/aplikacja/`.

## Sprawdzenie
- Czym różni się `defaults/` od `vars/` w roli? Gdzie trzymasz port aplikacji, a gdzie listę pakietów?
- Skąd rola wie, gdzie szukać `config.cfg.j2` i katalogu `naszaaplikacja/`?
- Dlaczego `changed=0` po przeróbce jest dobrym testem?
- Kiedy `include_role` zamiast `import_role`?

Rozwiązanie: `odpowiedz/roles/aplikacja/`, play „Warstwa aplikacji” w `odpowiedz/site.yml`.
