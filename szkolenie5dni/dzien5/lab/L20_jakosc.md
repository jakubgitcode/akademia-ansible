# L20 — Jakość: ansible-lint, Molecule, test w CI

Część A w bloku 4 (35 min), część B w bloku 5 (35 min).

```bash
cd ~/dzien5
pip install -r jakosc/requirements.txt        # ansible-lint, molecule, molecule-plugins[docker] (1–2 minuty)
```

## Część A — ansible-lint (blok 4)

### Krok 1 — Twój projekt

```bash
cd projekt && ansible-lint --offline --exclude galaxy; cd ..
```

Oczekiwany wynik: `Passed … profile was 'production'`. Rozwiązania z dni 1–4 pisaliśmy tak, żeby przechodziły
najostrzejszy profil.

### Krok 2 — Stary playbook

`jakosc/stary_playbook.yml` działa, ale jest napisany tak, jak wiele playbooków sprzed kilku lat.

```bash
ansible-lint --offline jakosc/stary_playbook.yml
```

Około 20 uwag. Każda ma nazwę reguły (np. `fqcn[action-core]`, `no-changed-when`) — opis: `ansible-lint -L`
albo dokumentacja ansible-lint.

### Krok 3 — Poprawki automatyczne

```bash
cp jakosc/stary_playbook.yml /tmp/przed.yml
ansible-lint --offline --fix jakosc/stary_playbook.yml
diff /tmp/przed.yml jakosc/stary_playbook.yml
```

`--fix` poprawia to, co da się zmienić bez myślenia: pełne nazwy modułów, zapis `klucz=wartość` na YAML, `yes` na
`true`, wielkie litery w nazwach. Przejrzyj zmiany: `mode: "644"` i `update_cache: "yes"` jako napisy — działają,
ale czy tak byś to zapisał?

### Krok 4 — Poprawki ręczne

Zostało kilka uwag, których narzędzie nie poprawi, bo wymagają decyzji:

| Reguła | Decyzja |
|---|---|
| `package-latest` | `present` czy świadomie `latest`? |
| `command-instead-of-module` | `ansible.builtin.service` zamiast `service cron restart` |
| `no-changed-when` | czy to zadanie coś zmienia? |
| `risky-shell-pipe` | `set -o pipefail` — błąd `df` nie może zginąć w potoku |
| `name[play]`, `name[missing]` | nazwy playa i zadań |

Popraw, aż `ansible-lint` pokaże `profile was 'production'`. Rozwiązanie: `odpowiedz/stary_playbook.yml`.

> Gdy reguła nie pasuje do sytuacji: `# noqa: nazwa-reguły` przy zadaniu z komentarzem dlaczego — tak jak
> `run-once[task]` w `site.yml` z dnia 3.

## Część B — Molecule: test roli w kontenerze (blok 5)

### Krok 5 — Scenariusz

```bash
cd projekt/roles/aplikacja
ls molecule/default
```

- `molecule.yml` — kontener z Ubuntu 24.04 i systemd (obraz przygotowany do testów ról), sterownik Docker;
- `converge.yml` — wdraża rolę z wartościami domyślnymi;
- `verify.yml` — sprawdza wynik.

### Krok 6 — Pierwsze uruchomienie

```bash
molecule create && molecule converge          # kontener + rola (pierwszy raz 2–3 minuty)
molecule login                                # jesteś w kontenerze: curl -s localhost/health; exit
molecule idempotence                          # drugie uruchomienie roli: musi dać changed=0
```

### Krok 7 — Sprawdzenia

Uzupełnij dwa `TODO` w `molecule/default/verify.yml`: strona główna z nazwą aplikacji; `config.cfg` z uprawnieniami
`0640` i grupą `www-data` (zabezpieczenie z dnia 4 — test pilnuje, żeby nikt go nie cofnął).

```bash
molecule verify
```

### Krok 8 — Cały cykl

```bash
molecule test        # destroy → create → converge → idempotence → verify → destroy
cd ../../..
```

Zepsuj coś w roli (np. `mode: '0644'` przy `config.cfg`) i uruchom `molecule test` — test to wychwyci. Przywróć.

### Krok 9 — Test w CI (do przeczytania)

`jakosc/ci.PRZYKLAD.yml`: przy każdej zmianie w repozytorium GitHub Actions uruchamia `ansible-lint` i `molecule test`.
Tak testujemy laby tego szkolenia: każda zmiana i co tydzień nowa wersja Ansible przechodzi wszystkie dni krok po kroku.

## Sprawdzenie
- Co poprawia `--fix`, a czego nie poprawi nigdy?
- Co sprawdza krok `idempotence` w Molecule?
- Czym test w Molecule różni się od uruchomienia roli na web02?
- Co powinno blokować scalenie zmiany: lint, Molecule, oba?

Rozwiązania: `odpowiedz/stary_playbook.yml`, `odpowiedz/molecule/verify.yml`.
