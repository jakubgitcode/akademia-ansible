# L2 — Polecenia ad-hoc i moduły (blok 2, 30 min)

## Cel
Wykonać na hostach pojedyncze operacje modułami Ansible, znaleźć opis modułu w dokumentacji
i zobaczyć idempotencję: drugie wykonanie tej samej operacji niczego nie zmienia.

Za pomocą Ansible możemy uruchamiać pojedyncze komendy lub całe plany wykonania w formie playbooków.
Spróbujmy dla nabrania wprawy wykonać kilka operacji popularnymi modułami z poziomu konsoli.
Może wydawać się to mało przydatne, jednak często proste rzeczy okazują się użyteczne!

Schemat polecenia:
```
ansible <hosty lub grupa> -i <inventory> -m <moduł> -a "<argumenty modułu>" [--become]
```

> W poleceniach ad-hoc wystarcza krótka nazwa modułu (`-m file`). W playbookach piszemy pełną (`ansible.builtin.file`).

---

## Krok 1 — command, shell, raw

```bash
ansible webservers -i inventory/hosts.yml -m command -a "uptime"
ansible webservers -i inventory/hosts.yml -m shell -a "date; whoami; df -h /"
ansible webservers -i inventory/hosts.yml -m command -a "date; whoami; df -h /"
```

Ostatnie polecenie się nie wykona. `command` uruchamia jeden program bez powłoki: nie rozumie `;`, `|`, `>`
ani zmiennych `$...`, za to jest bezpieczniejszy. `shell` przekazuje całe polecenie do powłoki na hoście.

```bash
ansible webservers -i inventory/hosts.yml -m raw -a "ps ux"
```

`raw` wysyła polecenie przez SSH bez Pythona na hoście; przydaje się np. do instalacji Pythona na nowym serwerze.

## Krok 2 — Fakty: co Ansible wie o hostach

```bash
ansible all -i inventory/hosts.yml -m setup -a "filter=ansible_distribution*"
ansible all -i inventory/hosts.yml -m setup -a "filter=ansible_memtotal_mb"
```

## Krok 3 — Dokumentacja modułu

Chcemy utworzyć katalog. Wyszukaj w internecie „ansible create directory” — powinieneś trafić na dokumentację
modułu `ansible.builtin.file`. Ten sam opis masz w konsoli:

```bash
ansible-doc ansible.builtin.file          # pełny opis; szukaj parametrów path i state (/ w less)
ansible-doc -s ansible.builtin.file       # skrócona lista parametrów
ansible-doc -l ansible.builtin           # lista modułów jednej kolekcji
```

> Samo `ansible-doc -l` (wszystkie kolekcje) kończy się dziś błędem
> `'_AnsibleTaggedDict' object has no attribute 'strip'`. Powód: kolekcja `google.cloud` w pakiecie `ansible`
> 14.6 i 15.0 (stan na 18.11.2026). Lista dla wybranej kolekcji działa.

## Krok 4 — Moduł file i idempotencja

```bash
ansible webservers -i inventory/hosts.yml -m file -a "path=/tmp/akademia state=directory mode=0755"
```

Uruchom **to samo polecenie drugi raz**. Za pierwszym razem: `CHANGED` (żółty). Za drugim: `SUCCESS` (zielony),
`"changed": false`. Moduł sprawdził stan i nic nie zrobił, bo katalog już jest. To jest idempotencja.

## Krok 5 — Cudzysłowy: gdzie rozwija się zmienna

```bash
ansible webservers -i inventory/hosts.yml -m shell -a 'echo "$USER na $(hostname)"'
ansible webservers -i inventory/hosts.yml -m shell -a "echo $USER na $(hostname)"
```

Wynik jest różny:
- `'...'` — przekazujemy `$USER` jako tekst; rozwija go powłoka na hoście docelowym (np. `ubuntu na web01`);
- `"..."` — `$USER` i `$(hostname)` rozwija Twoja powłoka, zanim uruchomi się Ansible; oba hosty wypiszą
  dane **Twojego** komputera.

Sposób Ansible: zmienna przekazana przez `-e` (extra vars) i wstawiona szablonem Jinja2.
Utwórz katalog z własnym imieniem w nazwie:

```bash
ansible webservers -i inventory/hosts.yml -m file \
  -a "path=/tmp/akademia/stworz_mnie_{{ moj_user }} state=directory" -e moj_user=TWOJE_IMIE
ansible webservers -i inventory/hosts.yml -m command -a "ls /tmp/akademia"
```

## Krok 6 — copy, apt i become

```bash
ansible webservers -i inventory/hosts.yml -m copy \
  -a "content='Zarzadzane przez Ansible' dest=/tmp/akademia/info.txt"

# instalacja pakietu wymaga uprawnień administratora — bez --become dostaniesz błąd:
ansible webservers -i inventory/hosts.yml -m apt -a "name=tree update_cache=true cache_valid_time=3600"
ansible webservers -i inventory/hosts.yml -m apt -a "name=tree update_cache=true cache_valid_time=3600" --become
```

Uruchom instalację z `--become` drugi raz. Jaki jest status?

## Krok 7 (bonus) — sprawdź przed zmianą

```bash
ansible webservers -i inventory/hosts.yml -m copy \
  -a "content='Nowa tresc' dest=/tmp/akademia/info.txt" --check --diff
ansible webservers -i inventory/hosts.yml -m command -a "cat /tmp/akademia/info.txt"
```

`--check` niczego nie zmienia na hostach, `--diff` pokazuje, co by się zmieniło.

---

## Sprawdzenie
- Czym różnią się `command`, `shell` i `raw`? Którego używasz domyślnie?
- Co robi flaga `--become`?
- Jaka jest dystrybucja systemu na hostach i skąd to wiesz bez logowania się na nie?
- Dlaczego przy drugim uruchomieniu `file` i `apt` dostajesz `SUCCESS`, a nie `CHANGED`?
- Którą wersję cudzysłowów wybierzesz, żeby `$USER` oznaczał użytkownika na hoście docelowym?
