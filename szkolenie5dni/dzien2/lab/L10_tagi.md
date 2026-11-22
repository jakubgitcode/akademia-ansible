# L10 — Tagi; playbook z asystentem AI (blok 7, 20 min)

## Część A — tagi (10 min)

Przy pracy nad jedną częścią playbooka nie chcesz za każdym razem czekać na całość. Tagi pozwalają uruchomić
tylko wybrane zadania.

### Krok 1 — Oznacz zadania w `wgraj_aplikacje.yml`

| Zadania | Tag |
|---|---|
| instalacja pakietów | `pakiety` |
| katalogi, kod, virtualenv | `kod` |
| szablony, port, `a2ensite`, `a2dissite`, usługa | `konfiguracja` |
| `debug` w `pre_tasks` | `always` (wykonuje się zawsze) |

Zapis przy zadaniu: `tags: [konfiguracja]` (lista — zadanie może mieć kilka tagów).

```bash
ansible-playbook wgraj_aplikacje.yml --list-tags
ansible-playbook wgraj_aplikacje.yml --list-tasks --tags konfiguracja
```

### Krok 2 — Uruchom tylko konfigurację

Zmień wersję na `"2.0"` i uruchom:

```bash
ansible-playbook wgraj_aplikacje.yml --tags konfiguracja
```

Wykonują się: zadanie z `always`, zadania z tagiem `konfiguracja` i powiadomione handlery.
Nie wykonuje się test z `post_tasks` — nie ma tagu. Dopisz mu `tags: [always]` i uruchom ponownie.

```bash
ansible-playbook wgraj_aplikacje.yml --skip-tags pakiety      # wszystko oprócz pakietów
```

### Krok 3 — Zadanie tylko na żądanie: never

Na końcu `tasks` dopisz dwa zadania diagnostyczne z tagami `[never, diagnostyka]`:
odczyt `config.cfg` (`ansible.builtin.command: "cat {{ aplikacja_katalog }}/config.cfg"`, `register`,
`changed_when: false`) i jego wyświetlenie (`ansible.builtin.debug`).

```bash
ansible-playbook wgraj_aplikacje.yml                       # zadań diagnostycznych nie ma
ansible-playbook wgraj_aplikacje.yml --tags diagnostyka    # są
```

### Kiedy tagów NIE używać
- Do sterowania kolejnością wdrożenia („najpierw `--tags pakiety`, potem `--tags konfiguracja`”) — od tego są
  osobne playbooki i role (dzień 3).
- Gdy zadanie z tagiem zależy od zadań bez niego: `--tags konfiguracja` na nowym hoście padnie, bo nie ma Apache.
- Gdy tagów jest tyle, że nikt nie wie, co uruchamia który. Na start wystarczą 2–4 tagi i `never` do diagnostyki.

Rozwiązanie: `wgraj_aplikacje_odpowiedz_tagi.yml`.

## Część B — playbook z asystentem AI (10 min)

**Zadanie:** playbook `usun_aplikacje.yml`, który usuwa aplikację razem z Apache: zatrzymuje usługę `apache2`,
usuwa VirtualHost, pakiety `apache2` i `libapache2-mod-wsgi-py3` (z konfiguracją), katalog aplikacji i logi.

1. Poproś asystenta AI (lub napisz sam). Opisz zadanie, hosty (`webservers`) i ścieżki z `vars` Twojego playbooka.
   Nie wklejaj do zewnętrznych narzędzi haseł, kluczy ani adresów firmowych serwerów.
2. Zanim uruchomisz, sprawdź wynik:
   - pełne nazwy modułów (`ansible.builtin.apt`, nie `apt`);
   - moduły zamiast `shell`/`command` tam, gdzie moduł istnieje (`apt` zamiast `apt-get remove`);
   - `--syntax-check`, potem `--check --diff`;
   - drugie uruchomienie: `changed=0` i bez błędów (np. zatrzymanie usługi, której już nie ma);
   - usługa zatrzymana, zanim zniknie pakiet? (w kontenerach `lab-env` `apt purge` jej nie zatrzyma).
3. Uruchom i sprawdź: `curl http://localhost:8081/` — brak odpowiedzi.
4. Tryb `--check` na hoście bez aplikacji:
   ```bash
   ansible-playbook wgraj_aplikacje.yml --check
   ```
   Zadanie z `lineinfile` kończy się błędem: `/etc/apache2/ports.conf` nie istnieje, bo w trybie `--check`
   moduł `apt` niczego nie zainstalował. `--check` to symulacja, nie gwarancja — zadania zależne od
   wcześniejszych zmian mogą w nim paść.
5. Postaw aplikację z powrotem jednym poleceniem — po to jest automatyzacja:
   ```bash
   ansible-playbook wgraj_aplikacje.yml
   curl http://localhost:8081/
   ```

Porównaj swoją wersję z `usun_aplikacje_odpowiedz.yml`.

## Sprawdzenie
- Czym różnią się `always` i `never`?
- Kiedy wykonują się handlery przy `--tags`?
- Co sprawdzasz w playbooku od asystenta AI, zanim uruchomisz go na serwerach?
