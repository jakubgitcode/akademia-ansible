# L4 — Playbook

Część 1 po obiedzie (blok 4, 35 min), część 2 na koniec dnia (blok 6, 20 min: kroki 5–7; krok 8 to zadanie domowe).

Playbooki, podobnie jak skrypty, zapewniają jednakowe wykonanie zadań przy każdym przebiegu.
Dodatkowo pozwalają zdefiniować szereg zmiennych i parametrów przydatnych do efektywnego użycia Ansible.

> W playbooku moduły zapisujemy pełną nazwą (FQCN), np. `ansible.builtin.file`. Dzięki temu wiadomo,
> z której kolekcji pochodzi moduł, a dokumentację znajdziesz poleceniem `ansible-doc ansible.builtin.file`.

---

## Część 1 — pierwszy playbook (blok 4)

### Krok 1 — Uzupełnij playbook

Otwórz `pierwszy_playbook.yml` i uzupełnij miejsca oznaczone `# TODO`.

Playbook działa od razu: zadania do uzupełnienia mają na razie zastępczy `debug` z napisem `TODO`.
Uruchom go przed zmianami, potem uzupełniaj po jednym zadaniu (zastępczy `debug` usuń) i uruchamiaj po każdej zmianie:

```bash
ansible-playbook -i inventory/hosts.yml pierwszy_playbook.yml
```

> **Gdzie szukać**
> - `ansible-doc ansible.builtin.file` — opis modułu i jego parametrów; na końcu sekcja **EXAMPLES**
>   z gotowymi zadaniami (w przeglądarce pomocy: `/EXAMPLES` szuka, `q` kończy).
> - `ansible-doc -s ansible.builtin.file` — tylko lista parametrów w postaci zadania do skopiowania.
> - `ansible-doc -l | grep -i ping` — jaki moduł robi to, czego szukam.
> - To samo w przeglądarce: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/index.html
>
> **Podpowiedzi do TODO**
> - Zmienna w `vars:` to para `nazwa: wartość`, wcięta jak `katalog_lab`.
> - `ping` bez parametrów zapisujesz jako `ansible.builtin.ping:` (dwukropek, nic po nim).
> - Wartość zmiennej w tekście: `"{{ powitanie }}"` — w YAML-u w cudzysłowie, gdy wartość zaczyna się od `{{`.
>   W `debug` jest parametr `msg` (tekst) albo `var` (sama nazwa zmiennej, bez `{{ }}`).
> - `file`: parametry `path`, `state`, `mode`; uprawnienia w cudzysłowie (`'0755'`), inaczej YAML zrobi z nich liczbę.
> - Wizytówka: nazwy faktów z TODO wstaw tak samo jak w zadaniu „Przedstaw hosta”.
>
> **Co sprawdzić, gdy coś nie działa**
> - `no module/action detected in task` — w zadaniu jest tylko `name:`, brakuje modułu.
> - `mapping values are not allowed here` / `could not find expected ':'` — wcięcia albo brakujący dwukropek
>   (linia i kolumna są w komunikacie; wcinaj spacjami, nie tabulatorem).
> - `Destination directory /tmp/akademia does not exist` (wizytówka) — najpierw uzupełnij zadanie z katalogiem.
> - Dodaj `-v`, żeby zobaczyć pełny wynik każdego zadania.

### Krok 2 — Sprawdź składnię

```bash
ansible-playbook -i inventory/hosts.yml pierwszy_playbook.yml --syntax-check
```

### Krok 3 — Symulacja, potem uruchomienie

```bash
ansible-playbook -i inventory/hosts.yml pierwszy_playbook.yml --check --diff
ansible-playbook -i inventory/hosts.yml pierwszy_playbook.yml
```

`--check` niczego nie zmienia, `--diff` pokazuje, co by się zmieniło (np. treść pliku `wizytowka.txt`).

### Krok 4 — Idempotencja

```bash
ansible-playbook -i inventory/hosts.yml pierwszy_playbook.yml
```

Porównaj `PLAY RECAP` z pierwszym uruchomieniem: oczekujemy `changed=0`.
Zmień tekst powitania albo treść wizytówki i uruchom jeszcze raz — ile zadań jest teraz `changed`?

### Sprawdzenie (część 1)
- Czym różni się polecenie ad-hoc od playbooka?
- Z jakich części składa się play: gdzie są hosty, zmienne, zadania?
- Po czym poznajesz, że playbook jest idempotentny?
- Dlaczego zadanie z `uptime` ma `changed_when: false`?

Rozwiązanie: `pierwszy_playbook_odpowiedz.yml`.

---

## Część 2 — shell kontra moduł, własny playbook (blok 6)

### Krok 5 — Pakiety w pierwszym playbooku

Dopisz na końcu `pierwszy_playbook.yml` zadanie, które zainstaluje pakiety `tree` i `jq` modułem
`ansible.builtin.apt`. Uprawnienia administratora daj tylko temu zadaniu (`become: true` na poziomie zadania).
Uruchom playbook dwa razy.

> Podpowiedź: `ansible-doc ansible.builtin.apt` — parametry `name` (może być listą), `state`,
> `update_cache`, `cache_valid_time`.

### Krok 6 — Shell kontra moduł

`shell_kontra_modul.yml` instaluje pakiet `cowsay` dwa razy: poleceniem `apt-get` przez shell i modułem `apt`.

```bash
ansible-playbook -i inventory/hosts.yml shell_kontra_modul.yml --check
ansible-playbook -i inventory/hosts.yml shell_kontra_modul.yml
ansible-playbook -i inventory/hosts.yml shell_kontra_modul.yml
```

Porównaj oba zadania:
- co zrobił każdy z nich w trybie `--check`?
- jaki status ma każdy z nich przy drugim uruchomieniu i dlaczego?

### Krok 7 — creates: polecenie, które wykona się tylko raz

Nie dla każdej operacji jest moduł. Wtedy zostaje `command` albo `shell` — i parametr `creates`.
Dopisz w `shell_kontra_modul.yml` zadanie (TODO na końcu pliku), które wygeneruje klucz SSH:

```bash
ssh-keygen -q -N '' -f /tmp/akademia/klucz
```

Użyj `creates: /tmp/akademia/klucz`. Jeśli ten plik istnieje, zadanie zostanie pominięte
(to forma semafora dla zadania realizowanego za pomocą pliku). Uruchom playbook dwa razy.

Spraw tym samym parametrem, żeby zadanie instalujące `cowsay` przez shell przestało zgłaszać zmianę.
Po zmianach drugie uruchomienie ma dać `changed=0`.

> **Gdzie szukać:** `ansible-doc ansible.builtin.command` — parametr `creates` i przykłady w EXAMPLES.
> Najczytelniej zapisać polecenie i warunek jako dwa parametry modułu: `cmd: ...` i `creates: ...`.
> Jaki plik tworzy instalacja `cowsay`? Sprawdź: `ansible web01 -i inventory/hosts.yml -m shell -a "dpkg -L cowsay | grep games/"`.

### Krok 8 — Własny playbook od zera

Napisz samodzielnie nowy playbook `moj_pierwszy_playbook.yml`, który na hostach z grupy `webservers` utworzy
plik `/tmp/host_is_ready` o treści `OK`.

Zadanie to można zrealizować na kilka sposobów:
- za pomocą modułu `shell` i komend bash (np. `echo`),
- za pomocą modułu `template`,
- za pomocą modułu `copy` + `content`,
- za pomocą modułu `copy` (wymaga uprzedniego przygotowania pliku),
- `lineinfile`.

Polecam użycie modułu `template` (szablon zapisz w `templates/`).

> **Jak zacząć:** skopiuj nagłówek play z `pierwszy_playbook.yml` (`- name:`, `hosts:`, `tasks:`), zmień `hosts`
> i dopisz jedno zadanie. Szablon `templates/host_is_ready.j2` to zwykły plik tekstowy z treścią `OK`;
> parametry modułu: `ansible-doc -s ansible.builtin.template` (`src`, `dest`).

Sprawdź wynik:

```bash
ansible-playbook -i inventory/hosts.yml moj_pierwszy_playbook.yml --syntax-check
ansible-playbook -i inventory/hosts.yml moj_pierwszy_playbook.yml
ansible webservers -i inventory/hosts.yml -m command -a "cat /tmp/host_is_ready"
```

### Sprawdzenie (część 2)
- Dlaczego zadanie z `shell` zgłasza zmianę przy każdym uruchomieniu?
- Co `--check` robi z zadaniami `shell` i `command`?
- Kiedy `command` z `creates` jest w porządku, a kiedy lepiej poszukać modułu?
- Które z pięciu sposobów z kroku 8 są idempotentne?

## Odpowiedzi
- `pierwszy_playbook_odpowiedz.yml` (z krokiem 5)
- `shell_kontra_modul_odpowiedz.yml`
- `moj_pierwszy_playbook_odpowiedz.yml` i `templates/host_is_ready_odpowiedz.j2`
