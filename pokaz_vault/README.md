# Pokaz: ansible-vault w publicznym repozytorium

`vault.yml` jest zaszyfrowany **w całości** (vault id `szkolenie`), `zmienne.yml` obok jest jawny i tylko wskazuje
na wartości z vault. Hasło vault szkolenia dostajesz od prowadzącego na sali.

## Raz: hasło vault

```bash
read -rs -p "Hasło vault szkolenia: " h && printf '%s\n' "$h" > ~/.vault_szkolenie && chmod 600 ~/.vault_szkolenie; unset h; echo
```

Plik z hasłem nie może być wykonywalny — Ansible uruchomiłby go jak skrypt zwracający hasło.

## Odczyt i uruchomienie

```bash
cd ~/akademia-ansible/pokaz_vault        # ansible.cfg w tym katalogu wskazuje ~/.vault_szkolenie
head -1 vault.yml                        # $ANSIBLE_VAULT;1.2;AES256;szkolenie — etykieta mówi, którym hasłem otworzyć
ansible-vault view vault.yml
ansible-playbook pokaz.yml               # sekrety użyte, ale niewypisane
```

## git diff i git log na zaszyfrowanych plikach

Zwykły `git log -p` pokazuje przy zmianie pliku vault tylko zmieniony szyfrogram — nie wiadomo, co się zmieniło.
`.gitattributes` w repozytorium oznacza pliki vault jako `diff=ansible-vault`; wystarczy powiedzieć gitowi, czym je
odszyfrować przy porównaniu:

```bash
cd ~/akademia-ansible
git config diff.ansible-vault.textconv pokaz_vault/git-vault-view.sh    # ansible-vault view z hasłem szkolenia
git log -p pokaz_vault/vault.yml         # historia zmian sekretów, odszyfrowana
```

Własna zmiana:

```bash
cd ~/akademia-ansible/pokaz_vault
ansible-vault edit vault.yml             # np. nowy użytkownik albo zmiana vault_api_token
git diff                                 # odszyfrowana różnica: widać, który sekret się zmienił
git checkout vault.yml                   # cofnij — to repozytorium prowadzącego
```

Skrypt wywołuje `ansible-vault`, więc git musi go widzieć w PATH (aktywny venv z L1). Wersje zaszyfrowane hasłem
poprzedniego szkolenia mają w historii opis zamiast treści.

Bez `git config` (albo bez hasła) `git diff` pokazuje szyfrogram — tak widzi plik każdy spoza szkolenia.

> Uwaga: odszyfrowana różnica trafia na ekran. Nie wklejaj jej do zgłoszeń ani czatów.
