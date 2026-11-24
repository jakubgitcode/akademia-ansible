# L6 — Typowe operacje administracyjne

Część A robisz w bloku 1 (25 min), część B w bloku 2 (30 min).

**Scenariusz:** firma ma standard serwera: zestaw narzędzi, aktualne pakiety, działający `cron`, firmowy MOTD
i konfigurację aplikacji. Doprowadź oba hosty do tego standardu.

## Część A — pakiety i usługi (blok 1)

### Krok 1 — Uzupełnij `operacje_pakiety.yml`

Uzupełnij miejsca `# TODO`:

1. Instalacja narzędzi `htop`, `vim`, `curl`, `tree`: moduł `ansible.builtin.apt`, lista w `name`,
   `update_cache` z `cache_valid_time`.
2. Usunięcie `nano` z konfiguracją: `state: absent`, `purge`, `autoremove`.
3. Bezpieczna aktualizacja systemu: `upgrade: safe`.
4. Pakiet `cron` i usługa `cron`: moduł `ansible.builtin.service`, `state: started`, `enabled: true`.

Dwa ostatnie zadania (`stat`, `register`, `when`) są gotowe: przeczytaj je, wrócimy do nich w L7.

Playbook działa od razu: zadania z `TODO` mają zastępczy `debug`. Uruchom go raz przed zmianami, potem uzupełniaj
po jednym zadaniu (zastępczy `debug` usuń) i uruchamiaj po każdej zmianie — tak samo we wszystkich labach dnia 2.

> **Gdzie szukać**
> - `ansible-doc ansible.builtin.apt` — parametry modułu; na końcu **EXAMPLES** z gotowymi zadaniami
>   (`/EXAMPLES` szuka, `q` kończy). Krócej: `ansible-doc -s ansible.builtin.apt` — same parametry.
> - W przeglądarce: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/apt_module.html
>   (w adresie zamień `apt` na nazwę innego modułu: `service`, `lineinfile`, `blockinfile`, `fetch`…).
>
> **Podpowiedzi**
> - Lista pakietów w `name`: `name: [htop, vim, curl, tree]` albo lista YAML z myślnikami pod `name:`.
> - Parametry tak/nie (`update_cache`, `purge`, `autoremove`, `enabled`) zapisuj jako `true` / `false`.
>
> **Co sprawdzić, gdy coś nie działa**
> - `conflicting action statements: ansible.builtin.apt, ansible.builtin.debug` — moduł jest już wpisany,
>   ale w zadaniu został zastępczy `debug`; usuń go (z jego `msg`).
> - `no module/action detected in task` — w zadaniu jest tylko `name:` i komentarze, brakuje modułu.
> - `Unsupported parameters for (ansible.builtin.apt) module: …` — literówka w nazwie parametru albo parametr
>   wcięty nie tam, gdzie trzeba (parametry modułu o 2 spacje głębiej niż nazwa modułu).
> - `-v` pokazuje pełny wynik każdego zadania; `--start-at-task "Usuń nano razem z konfiguracją"` zaczyna od wskazanego.

Dokumentacja modułu w konsoli: `ansible-doc ansible.builtin.apt` (przykłady na końcu: `/EXAMPLES`).

### Krok 2 — Uruchom w bezpiecznej kolejności

```bash
ansible-playbook operacje_pakiety.yml --syntax-check
ansible-playbook operacje_pakiety.yml --check --diff
ansible-playbook operacje_pakiety.yml
```

> Na czystym hoście `--check` zatrzyma się na zadaniu z usługą: `Could not find the requested service cron`.
> To nie błąd w playbooku: w trybie `--check` moduł `apt` niczego nie instaluje, więc usługi `cron` jeszcze nie ma.
> Przejrzyj, co `--check` zdążył pokazać, i uruchom playbook bez `--check`. Więcej o tym w L10.

Aktualizacja systemu przy pierwszym uruchomieniu trwa 1–3 minuty.

Sprawdź wynik poleceniami ad-hoc:

```bash
ansible webservers -m command -a "htop --version"
ansible webservers -m command -a "which nano"            # oczekiwany błąd: rc=1, nano nie ma
ansible webservers -b -m command -a "systemctl is-active cron"
```

### Krok 3 — Drugie uruchomienie

```bash
ansible-playbook operacje_pakiety.yml
```

Oczekiwany wynik: `changed=0` na obu hostach. Wyjątek: zadanie aktualizacji może zgłosić zmianę, jeśli między
uruchomieniami wyszły nowe pakiety.

### Sprawdzenie (część A)
- Czym różni się `state: present` od `state: latest`? Który zapis daje ten sam wynik za tydzień?
- Po co `cache_valid_time`? Co by się działo bez niego przy każdym uruchomieniu?
- Co oznacza `enabled: true` w module `service`, a co `state: started`?

Rozwiązanie: `operacje_pakiety_odpowiedz.yml`.

---

## Część B — pliki konfiguracyjne (blok 2)

### Krok 4 — Uzupełnij `operacje_pliki.yml`

Gotowe zadania przeczytaj:
- MOTD z szablonu `templates/motd.j2` (`template` z `backup: true`) — zajrzyj do szablonu: fakty hosta w pliku;
- konfiguracja początkowa aplikacji (`copy` z `force: false`) — dlaczego `force: false`? Pytanie w „Sprawdzeniu”.

Uzupełnij `# TODO`:
1. `log_level=info` → `log_level=debug`: `ansible.builtin.lineinfile` z `regexp: '^log_level='`.
2. Sekcja monitoringu: `ansible.builtin.blockinfile` z własnym `marker`.
3. Pobranie pliku ze wszystkich hostów do katalogu `pobrane/`: `ansible.builtin.fetch`.

> **Podpowiedzi:** `ansible-doc -s ansible.builtin.lineinfile` (`path`, `regexp`, `line`),
> `ansible-doc -s ansible.builtin.blockinfile` (`path`, `block`, `marker`) i `ansible-doc -s ansible.builtin.fetch`
> (`src`, `dest`). Dwie linie w `block` zapisz blokiem YAML: `block: |` i linie pod spodem, wcięte głębiej.
> Po uruchomieniu sprawdź treść pliku (zadanie „Pokaż końcową konfigurację”): czy `log_level` jest jeden?

```bash
ansible-playbook operacje_pliki.yml --syntax-check
ansible-playbook operacje_pliki.yml
```

> Tu nie zaczynamy od `--check`: na czystym hoście nie ma jeszcze `/etc/szkolenie/app.conf`, a w trybie `--check`
> zadanie `copy` go nie utworzy, więc `lineinfile` skończy się błędem `Destination ... does not exist`.
> Zadania zależne od wcześniejszych zmian mogą w `--check` paść — wrócimy do tego w L10.

Sprawdź:

```bash
ansible webservers -m command -a "cat /etc/motd"
ansible webservers -m command -a "cat /etc/szkolenie/app.conf"
find pobrane/ -type f        # pobrane/<host>/etc/szkolenie/app.conf
```

### Krok 5 — Drugie uruchomienie i ręczna zmiana

```bash
ansible-playbook operacje_pliki.yml                    # changed=0
ansible web01 -b -m lineinfile -a "path=/etc/szkolenie/app.conf regexp=^log_level= line=log_level=info"
ansible-playbook operacje_pliki.yml --check --diff     # Ansible pokazuje, co przywróci
ansible-playbook operacje_pliki.yml                    # web01: changed=1, web02: changed=0
```

Ręczna zmiana na serwerze wraca do stanu z playbooka przy następnym uruchomieniu.

### Sprawdzenie (część B)
- Kiedy `template`, kiedy `lineinfile`, a kiedy `blockinfile`?
- Po co `force: false` w zadaniu `copy` z konfiguracją początkową? (co by się działo z `log_level` przy każdym
  uruchomieniu bez tej opcji?)
- Dlaczego `fetch` zapisuje pliki w `pobrane/<host>/...`, a nie od razu w `pobrane/`?

Rozwiązanie: `operacje_pliki_odpowiedz.yml`.
