# L16 — Sekrety: ansible-vault (blok 3, 35 min)

**Problem:** hasła do bazy leżą jawnym tekstem w plikach, które trafią do repozytorium. Każdy, kto ma dostęp do gita,
zna hasło do bazy produkcyjnej.

## Krok 1 — Gdzie są sekrety

```bash
grep -rn "haslo" inventories group_vars
```

## Krok 2 — Wzorzec: jawny odnośnik, zaszyfrowana wartość

W każdym środowisku zamień plik `group_vars/all.yml` na katalog — Ansible wczytuje wszystkie pliki z katalogu grupy:

```bash
for e in dev prod; do
  mkdir inventories/$e/group_vars/all
  mv inventories/$e/group_vars/all.yml inventories/$e/group_vars/all/main.yml
done
```

W `main.yml` każdego środowiska zamień wartości haseł na odnośniki:

```yaml
db_haslo: "{{ vault_db_haslo }}"
db_haslo_root: "{{ vault_db_haslo_root }}"
```

Obok utwórz `vault.yml` z prawdziwymi wartościami (tymi samymi co dotąd — po zaszyfrowaniu nic się nie zmieni na serwerach):

```yaml
---
vault_db_haslo: "…"
vault_db_haslo_root: "…"
```

Dlaczego dwie zmienne: `grep db_haslo` dalej znajdzie, skąd bierze się hasło, choć sama wartość jest zaszyfrowana.

## Krok 3 — Hasła do vault, poza repozytorium

```bash
echo 'dev-szkolenie'  > ~/.vault_dev
echo 'prod-szkolenie' > ~/.vault_prod
chmod 600 ~/.vault_dev ~/.vault_prod
```

> Plik z hasłem nie może być wykonywalny — Ansible uruchomiłby go jak skrypt zwracający hasło.

## Krok 4 — Szyfrowanie: osobne hasło dla każdego środowiska

```bash
ansible-vault encrypt --vault-id dev@~/.vault_dev   inventories/dev/group_vars/all/vault.yml
ansible-vault encrypt --vault-id prod@~/.vault_prod inventories/prod/group_vars/all/vault.yml
head -1 inventories/dev/group_vars/all/vault.yml     # $ANSIBLE_VAULT;1.2;AES256;dev
```

Etykieta (`dev`, `prod`) mówi Ansible, którym hasłem otworzyć plik.

## Krok 5 — Dev z hasłem z ansible.cfg

```bash
ansible-playbook site.yml --check        # błąd: no vault secrets found — Ansible nie zna hasła
```

W `ansible.cfg`, w sekcji `[defaults]`, dopisz:

```ini
vault_identity_list = dev@~/.vault_dev
```

```bash
ansible-playbook site.yml                                    # changed=0 — te same hasła, tylko zaszyfrowane
ansible-vault view inventories/dev/group_vars/all/vault.yml  # podgląd bez odszyfrowania pliku na dysku
```

## Krok 6 — Prod tylko z hasłem prod

```bash
ansible-playbook -i inventories/prod site.yml --check                                   # błąd: brak hasła prod
ansible-playbook -i inventories/prod site.yml --check --vault-id prod@~/.vault_prod     # zmiana tylko w pip (L15, krok 7)
ansible-playbook -i inventories/prod site.yml --check --vault-id prod@prompt            # albo hasło wpisane ręcznie
```

Tak wygląda podział w firmie: hasło dev zna zespół, hasło prod — tylko CI albo AWX (dzień 5).

## Krok 7 — Przeciek: hasło w wyniku

Sprawdź, co zobaczyłby ktoś, kto czyta log wdrożenia (zmiana hasła tylko na próbę, bez zmian na serwerach):

```bash
ansible-playbook site.yml --check --diff -e vault_db_haslo=Podglad-Hasla-123 | grep -n Podglad-Hasla-123
```

Na ansible-core 2.21 (Python 3.12, Ubuntu 24.04) hasło jest w wyniku dwa razy: w różnicy pliku `config.cfg` (`--diff`)
i w opisie pętli roli MySQL, która wypisuje każdego użytkownika z hasłem. Logi CI i AWX czyta więcej osób niż vault.

Na ansible-core 2.22 zobaczysz `'password': '$REDACTED$'`, a zmianę `config.cfg` bez treści: nowa wersja sama ukrywa
wartości przekazane do parametrów-haseł modułów. Nie polegaj na tym — starsze wersje (i wiele środowisk w firmach)
tego nie robią, a hasło wypisane np. przez `debug` albo zapisane w pliku czytelnym dla wszystkich nadal wycieka.

## Krok 8 — Poprawki

1. W `roles/aplikacja/tasks/main.yml`, w zadaniu „Wgraj konfigurację aplikacji”:
   - `diff: false` (poziom zadania, obok `notify`) — Ansible zgłosi zmianę pliku bez pokazywania treści;
   - `owner: root`, `group: www-data`, `mode: '0640'` — plik z hasłem czyta tylko root i Apache.
2. W `group_vars/databases.yml` dopisz `mysql_hide_passwords: true` — rola MySQL włącza wtedy `no_log` dla użytkowników.

```bash
ansible-playbook site.yml --check --diff -e vault_db_haslo=Podglad-Hasla-123 | grep -c Podglad-Hasla-123   # 0
ansible-playbook site.yml
ansible web04 -b -m command -a "stat -c '%a %U %G' /var/www/naszaaplikacja/config.cfg"     # 640 root www-data
```

> `no_log: true` ukrywa cały wynik zadania, także komunikat błędu. Używaj go tam, gdzie wynik zawiera sekret,
> a do diagnozy włączaj chwilowo (np. zmienną, jak `mysql_hide_passwords` w roli z Galaxy).

## Krok 9 — Rotacja hasła

```bash
ansible-vault edit inventories/dev/group_vars/all/vault.yml     # vault_db_haslo: "Dev-Baza-2026-v2"
ansible-playbook site.yml --diff                                # nowe hasło nie pojawia się w wyniku
curl -s http://localhost:8084/ | grep -o 'Baza danych: [^<]*'    # połączona — baza i aplikacja mają nowe hasło
```

Jedno uruchomienie zmieniło hasło użytkownika w MySQL i w konfiguracji aplikacji, a handler zrestartował Apache.

## Krok 10 — encrypt_string: pojedyncza wartość

```bash
ansible-vault encrypt_string --encrypt-vault-id dev 'tajny-klucz' --name vault_klucz_api
```

Hasło dev Ansible bierze z `vault_identity_list`; `--encrypt-vault-id dev` mówi, którym hasłem szyfrować.
Wynik (`vault_klucz_api: !vault | …`) można wkleić do zwykłego, jawnego pliku YAML. Wygodne dla jednej wartości;
przy wielu sekretach czytelniejszy jest osobny `vault.yml`.

## Krok 11 — Prod w labie bez wpisywania hasła

W labie oba hasła są na Twojej maszynie, więc dopisz prod w `ansible.cfg`:

```ini
vault_identity_list = dev@~/.vault_dev, prod@~/.vault_prod
```

```bash
ansible-playbook -i inventories/prod site.yml        # poprawki z kroku 8 także na prod
```

## Dodatkowe — zmiany w plikach vault w gicie

`git diff` na zaszyfrowanym pliku pokazuje szyfrogram. Git może go odszyfrować przy porównaniu:

```bash
git init
echo '**/vault.yml diff=ansible-vault' > .gitattributes
git config diff.ansible-vault.textconv "ansible-vault view"
git add -A && git commit -m start          # wcześniej: git config user.name / user.email
ansible-vault edit inventories/dev/group_vars/all/vault.yml
git diff                                   # widać odszyfrowaną zmianę
```

`.gitignore` w labie pomija `galaxy/` i pliki `.vault*`.

Gotowy przykład z historią zmian: `~/akademia-ansible/pokaz_vault/` (repozytorium szkolenia) — plik zaszyfrowany
w całości hasłem szkolenia i `git log -p` z odszyfrowaną różnicą; instrukcja w `README.md` tego katalogu.

## Sprawdzenie
- Dlaczego dwie zmienne (`db_haslo` i `vault_db_haslo`) zamiast jednej zaszyfrowanej?
- Czym różni się `ansible-vault encrypt` od `encrypt_string`?
- Kto w Twojej firmie powinien znać hasło vault prod?
- Gdzie poza plikami vault wyciekają sekrety? (wynik `--diff`, pętle, `-v`, uprawnienia plików na serwerze)
- Systemy zewnętrzne: kiedy HashiCorp Vault, AWS Secrets Manager albo CyberArk zamiast ansible-vault?

Rozwiązanie: `odpowiedz/inventories/*/group_vars/all/`, `odpowiedz/group_vars/databases.yml`,
`odpowiedz/roles/aplikacja/tasks/main.yml`, `odpowiedz/ansible.cfg`.
