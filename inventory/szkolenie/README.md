# Hosty w chmurze (zapasowe i do rozwiązań)

Laby robisz na hostach w Dockerze (`lab-env`, web01–web04 na Twojej maszynie). Gdy coś w nich nie działa albo
prowadzący pokazuje rozwiązanie, te same laby działają na maszynach z Ubuntu 24.04 w chmurze. Mają te same nazwy
(web01–web04), więc wystarczy dodać **drugie `-i`** — inventory labu daje grupy i zmienne, ten katalog daje adresy.

| Plik | Hosty | Kiedy |
|---|---|---|
| `dni1-2.yml` | web01, web02 | dni 1–2 |
| `prod.yml` | web01 (load balancer + baza), web02, web03 (aplikacja) | dni 3–5, środowisko prod |
| `dev.yml` | web04 (cała aplikacja na jednym hoście) | dzień 4, środowisko dev |
| `awaria.yml` | `nieistniejehost` w grupie `apache` | pokaz: jak wygląda host, który nie odpowiada |
| `host_vars/` | adresy i dane połączenia web01–web04 | — |
| `klucz_chmura.vault` | klucz SSH do web01–web04 w chmurze, zaszyfrowany (vault id `szkolenie`) | raz, niżej |
| `klucz_chmura.pub` | ten sam klucz, część publiczna (na maszynach) | — |

## Raz: klucz SSH do maszyn w chmurze

Klucz leży w repozytorium zaszyfrowany (`klucz_chmura.vault`, vault id `szkolenie`); hasło vault dostajesz na sali
i zapisujesz w `~/.vault_szkolenie` (instrukcja: `pokaz_vault/README.md`).

Potrzebujesz `ansible-vault`, czyli aktywnego venv z Ansible (L1).

```bash
cd ~/akademia-ansible        # tu, nie w katalogu labu: ansible.cfg labu dnia 4 szuka haseł dev i prod
ansible-vault decrypt --vault-id szkolenie@~/.vault_szkolenie \
  --output ~/.ssh/akademia_chmura inventory/szkolenie/klucz_chmura.vault
chmod 600 ~/.ssh/akademia_chmura
ansible chmura -i inventory/szkolenie/prod.yml -i inventory/szkolenie/dev.yml -m ping
```

Po `git pull` z nowym kluczem (każde szkolenie ma własny) powtórz `decrypt`.

## Użycie

```bash
# dzień 2 (w katalogu ~/dzien2)
ansible-playbook -i inventory -i ~/akademia-ansible/inventory/szkolenie/dni1-2.yml wgraj_aplikacje_odpowiedz.yml
# dzień 3 (rozwiązanie)
cd ~/dzien3/odpowiedz && ansible-playbook -i inventory -i ~/akademia-ansible/inventory/szkolenie/prod.yml site.yml
# dzień 4
ansible-playbook -i inventories/prod -i ~/akademia-ansible/inventory/szkolenie/prod.yml site.yml
ansible-playbook -i inventories/dev  -i ~/akademia-ansible/inventory/szkolenie/dev.yml  site.yml
# same hosty w chmurze
ansible chmura -i ~/akademia-ansible/inventory/szkolenie/prod.yml -i ~/akademia-ansible/inventory/szkolenie/dev.yml -m ping
```

Adresy w `host_vars/` są prywatne: zapasowe hosty są w tej samej sieci co Twoja maszyna szkoleniowa i tylko z niej
są osiągalne (z laptopa nie). Prowadzący wpisuje je na początku szkolenia; pobierasz je przez
`cd ~/akademia-ansible && git pull`.

Różnice względem kontenerów:
- strony WWW są pod adresem maszyny: `http://<adres web01>/` zamiast `http://localhost:8081`;
  dev (web04): `http://<adres web04>/`;
- to **wspólne** maszyny: jeśli kilka osób uruchomi playbook naraz, nadpiszą sobie konfigurację — uzgadniaj
  z prowadzącym, kto z nich korzysta.
