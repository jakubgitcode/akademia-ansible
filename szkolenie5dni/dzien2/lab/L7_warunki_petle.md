# L7 — Warunki, pętle, register, set_fact (blok 3, 30 min)

**Scenariusz:** web01 to środowisko **dev**, web02 to **prod**. Ten sam playbook konfiguruje oba hosty;
różnice opisują wyłącznie zmienne w `inventory/group_vars/`.

Kroki 1–3 są obowiązkowe, krok 4 — jeśli zdążysz (inaczej w domu).

## Krok 1 — Zmienne środowisk

1. Obejrzyj `inventory/group_vars/all.yml` (wspólne wartości domyślne) i `inventory/group_vars/dev.yml`.
2. Uzupełnij `inventory/group_vars/prod.yml` według `TODO` w pliku.

Sprawdź, co dostanie każdy host, zanim cokolwiek uruchomisz:

```bash
ansible-inventory --host web01
ansible-inventory --host web02
```

## Krok 2 — Pętle: `petle.yml`

Uzupełnij `# TODO`:
1. Katalogi z listy `katalogi_aplikacji`: `ansible.builtin.file` z `loop`.
2. Użytkownicy z listy słowników `uzytkownicy_aplikacji` (`item.name`, `item.comment`, `item.shell`), tylko aktywni
   (`when: item.aktywny | bool`), z czytelnym logiem (`loop_control: label`).
3. Raport brakujących plików: pętla po `konfigi.results`, warunek `not item.stat.exists`.

```bash
ansible-playbook petle.yml --syntax-check
ansible-playbook petle.yml
ansible webservers -m command -a "ls /opt/sklep"
ansible webservers -m command -a "id deploy"
ansible webservers -m command -a "id stazysta"      # oczekiwany błąd: tego użytkownika nie ma
```

## Krok 3 — Warunki, register i set_fact: `warunki.yml`

Uzupełnij `# TODO`:
1. `ncdu` tylko na rodzinie Debian (`ansible_facts.os_family`).
2. Komunikat trybu debug, gdy `app_debug` jest prawdą (`| default(false) | bool`).
3. Plik `PRODUKCJA` tylko na hostach z grupy `prod` (`group_names`).
4. Ostrzeżenie o małej ilości RAM na produkcji: **lista warunków** (wszystkie muszą być spełnione).
5. `set_fact`: dwie własne zmienne hosta wyliczone z `register` i faktów.

```bash
ansible-playbook warunki.yml
```

Przeanalizuj wynik: które zadania mają `skipping` na web01, a które na web02 — i dlaczego?

## Krok 4 (jeśli zdążysz) — Konfiguracja per środowisko: `konfiguracja_srodowisk.yml`

1. `/etc/szkolenie/app_env.conf` ze wspólnego szablonu `templates/app_env.conf.j2` (obejrzyj `default()`
   i `ternary()`).
2. Flaga kopii zapasowej tylko na produkcji.

```bash
ansible-playbook konfiguracja_srodowisk.yml
ansible webservers -m command -a "cat /etc/szkolenie/app_env.conf"
```

Priorytety zmiennych w praktyce (dzień 1, L5):

```bash
ansible-playbook konfiguracja_srodowisk.yml -e app_port=9999      # -e wygrywa ze wszystkim
ansible webservers -m command -a "grep port /etc/szkolenie/app_env.conf"
ansible-playbook konfiguracja_srodowisk.yml                       # powrót do wartości z inventory
```

## Krok 5 — Idempotencja

Uruchom każdy playbook drugi raz — oczekiwany wynik: `changed=0`.

## Sprawdzenie
- Skąd web02 „wie”, że jest produkcją? (dwie odpowiedzi: grupa i zmienna)
- Dlaczego `when: app_debug` bez `| bool` to pułapka? (podpowiedź: `-e app_debug=false` daje napis `"false"`;
  ansible-core 2.19+ zatrzyma się błędem „Conditionals must have a boolean result”, starsze wersje uznawały go za prawdę)
- Co zawiera `item.item` w pętli po `wynik.results`?
- Czym różni się zmienna z `register` od zmiennej z `set_fact`? Jak długo żyją?

Rozwiązania: `petle_odpowiedz.yml`, `warunki_odpowiedz.yml`, `konfiguracja_srodowisk_odpowiedz.yml`,
`inventory/group_vars/prod_odpowiedz.yml`.
