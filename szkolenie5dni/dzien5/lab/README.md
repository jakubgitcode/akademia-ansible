# Dzień 5 — laby

Projekt z dnia 4 (`projekt/`) trafia do AWX, dostaje kontrolę jakości (ansible-lint, Molecule) i przyspieszamy go.
Na koniec pokaz Windows i — dla chętnych — własny moduł.

| Lab | Kiedy | Temat | Czas |
|---|---|---|---|
| [L19, część A](L19_awx.md) | blok 1 | AWX: poświadczenia, projekt z gita, inventory | 25 min |
| [L19, część B](L19_awx.md#część-b--szablon-ankieta-uprawnienia-blok-2) | blok 2 | szablon zadania, ankieta, harmonogram, uprawnienia | 35 min |
| [L19, część C](L19_awx.md#część-c--awx-jako-kod-blok-3) | blok 3 | AWX jako kod: kolekcja `awx.awx` | 30 min |
| [L20](L20_jakosc.md) | bloki 4 i 5 | ansible-lint (`--fix`), Molecule, test w CI | 35 + 35 min |
| [L21](L21_przyspieszanie.md) | blok 6 | lookupy, delegacja, `async`; przyspieszanie | 35 min |
| L1, część B: `~/dzien1/L1_srodowisko.md` (w repozytorium `dzien1/lab/`) | blok 7, w `~/dzien1` | `ansible.cfg`, przypięta wersja, `source_me.sh` | 7 min |
| [L22 (opcja)](L22_modul.md) | w domu | własny moduł | 10 min |

## Środowisko

```bash
source ~/venv-ansible/bin/activate
cd ~/dzien5/projekt                      # albo: cd szkolenie5dni/dzien5/lab/projekt
export ANSIBLE_VAULT_IDENTITY_LIST=dev@~/.vault_dev,prod@~/.vault_prod   # hasła vault z dnia 4 (dopisz do ~/.bashrc)
ansible-galaxy install -r requirements.yml
ansible-playbook site.yml                          # dev: changed=0
ansible-playbook -i inventories/prod site.yml      # prod: changed=0
```

`projekt/` to rozwiązanie dnia 4 ze zmianami pod AWX:
- hasła vault nie są w `ansible.cfg` (AWX nie ma Twoich plików z hasłami), tylko w zmiennej środowiskowej;
- `inventories/awx/` — prod widziany z AWX: adres maszyny w zmiennej `lab_adres`, hasła zaszyfrowane pojedynczo
  (`encrypt_string`), bo AWX importuje inventory bez hasła vault;
- `roles/requirements.yml` i `collections/requirements.yml` — tam AWX szuka zależności z Galaxy.

Rozwiązania: `odpowiedz/` (AWX jako kod, poprawiony stary playbook, test Molecule).
