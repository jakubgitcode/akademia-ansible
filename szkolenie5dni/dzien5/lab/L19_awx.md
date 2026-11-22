# L19 — AWX

Część A w bloku 1 (25 min), część B w bloku 2 (35 min), część C w bloku 3 (30 min).

**Po co:** dotąd projekt uruchamiałeś z własnej maszyny, z hasłami w plikach w katalogu domowym. W AWX projekt
pobiera się z gita, hasła są w poświadczeniach (nikt ich nie widzi), wdrożenie to przycisk albo harmonogram,
a uprawnienia mówią, kto może uruchomić prod.

| Twój projekt | AWX |
|---|---|
| repozytorium z `site.yml` i rolami | **Project** (synchronizacja z gita) |
| `inventories/prod/hosts.yml` | **Inventory** (źródło: plik z projektu) |
| klucz SSH, hasło vault prod | **Credentials** (Machine, Vault) |
| `ansible-playbook -i … site.yml` | **Job Template** (Launch) |
| `-e aplikacja_wersja=1.1` | **Survey** (ankieta przy uruchomieniu) |
| „kto może wdrożyć na prod” | **RBAC**: uprawnienie Execute |

Od prowadzącego dostajesz: adres AWX, użytkownika i hasło, swoją organizację, adres repozytorium projektu.
Nazwy obiektów zaczynaj od swojego użytkownika (np. `kursant01-…`).

## Część A — poświadczenia, projekt, inventory (blok 1)

### Krok 1 — Adres Twojej maszyny widziany z AWX

AWX łączy się z hostami web01–web03 przez sieć, na porty 2221–2223 Twojej maszyny (nie przez `127.0.0.1`):

```bash
hostname -I | cut -d' ' -f1          # np. 10.42.1.23 — zapisz
```

### Krok 2 — Poświadczenia (Resources → Credentials → Add)

1. **Machine** `kursant01-lab`: Username `ubuntu`, SSH Private Key — wklej treść `cat ~/.ssh/akademia_lab_key`.
2. **Vault** `kursant01-vault-prod`: Vault Password `prod-szkolenie`, Vault Identifier `prod`.

Po zapisaniu nikt (także Ty) nie zobaczy już klucza ani hasła — AWX tylko ich używa.

### Krok 3 — Projekt (Resources → Projects → Add)

`kursant01-projekt`: Source Control Type **Git**, URL od prowadzącego, gałąź `main`, zaznacz **Update Revision on Launch**.
Po zapisaniu AWX pobiera repozytorium i instaluje zależności z `roles/requirements.yml` i `collections/requirements.yml`.
Status synchronizacji: zielony.

### Krok 4 — Inventory z pliku w projekcie (Resources → Inventories → Add inventory)

1. `kursant01-prod`, w **Variables**: `lab_adres: 10.42.1.23` (adres z kroku 1).
2. Zakładka **Sources** → Add: Source **Sourced from a Project**, projekt `kursant01-projekt`,
   Inventory file `inventories/awx/hosts.yml`, zaznacz **Update on launch**. Zapisz i **Sync**.
3. Zakładki **Hosts** i **Groups**: web01–web03 i grupy warstw z pliku.

Zajrzyj do `projekt/inventories/awx/`: `ansible_host: "{{ lab_adres }}"`, a hasła w `group_vars/all.yml` są zaszyfrowane
pojedynczo (`!vault |`). AWX importuje je bez hasła i odszyfruje dopiero w zadaniu, poświadczeniem z kroku 2.

## Część B — szablon, ankieta, uprawnienia (blok 2)

### Krok 5 — Szablon zadania (Resources → Templates → Add job template)

`kursant01-site-prod`: Inventory `kursant01-prod`, Project `kursant01-projekt`, Playbook `site.yml`,
Credentials: `kursant01-lab` i `kursant01-vault-prod`. Zapisz → **Launch**.

Wynik zadania wygląda jak w Twoim terminalu. Oczekiwany `changed=0` — AWX uruchomił ten sam kod na tych samych hostach.

### Krok 6 — Ankieta (zakładka Survey szablonu)

Pytanie „Wersja aplikacji”, zmienna `aplikacja_wersja`, typ Text, domyślnie `1.0`. Włącz ankietę (**Survey Enabled**).
**Launch** z wersją `1.1`, potem:

```bash
curl -s http://localhost:8081/ | grep -o 'Wersja: [^<]*'      # 1.1
```

Odpowiedź z ankiety trafia do zadania jako `-e` — wygrywa ze wszystkimi zmiennymi.

### Krok 7 — Harmonogram (zakładka Schedules szablonu)

Codziennie o 6:00, a w szablonie (albo w osobnym) **Job Type: Check** — co rano raport, czy serwery odbiegają od kodu
(dryf, dzień 3). Nie musisz czekać do rana: zobacz, jak wygląda lista zaplanowanych uruchomień.

### Krok 8 — Uprawnienia (zakładka Access szablonu)

Dodaj koledze z sąsiedniego stanowiska rolę **Execute** na swoim szablonie. Niech uruchomi Twój szablon —
i spróbuje go edytować (nie może). Tak wygląda „operator wdraża, nie zmienia”.

### Krok 9 (jeśli zdążysz) — Powiadomienia

Administration → Notifications: typ Webhook albo Email (jeśli prowadzący skonfigurował serwer poczty), podepnij
do szablonu na „Failure”. Uruchom szablon z ankietą `aplikacja_wersja` = cokolwiek i zepsuj połączenie
(np. zły `lab_adres` w inventory) — przyjdzie powiadomienie.

## Część C — AWX jako kod (blok 3)

Wszystko, co klikałeś, można opisać playbookiem i trzymać w gicie: przegląd zmian, historia, odtworzenie AWX od zera.

### Krok 10 — Kolekcja awx.awx i token

```bash
cd ~/dzien5                                          # katalog nad projekt/
ansible-galaxy collection install -r awx/requirements.yml -p awx/kolekcje
cp awx/moje.yml.przyklad awx/moje.yml
```

W AWX: kliknij swojego użytkownika → **Tokens** → Add, zakres **Write**. Wpisz token i pozostałe dane w `awx/moje.yml`.

### Krok 11 — Uzupełnij i uruchom

`awx/awx_jako_kod.yml` tworzy poświadczenia, projekt, inventory ze źródłem — z przyrostkiem `-kod`, żeby nie nadpisać
obiektów z części A i B. Uzupełnij dwa `TODO`: szablon z ankietą (`awx.awx.job_template`) i uruchomienie
(`awx.awx.job_launch`). Przykłady: `ANSIBLE_COLLECTIONS_PATH=awx/kolekcje ansible-doc awx.awx.job_template`.

```bash
ANSIBLE_COLLECTIONS_PATH=awx/kolekcje ansible-playbook awx/awx_jako_kod.yml
curl -s http://localhost:8081/ | grep -o 'Wersja: [^<]*'      # 1.2 — ustawione z kodu przez AWX
```

Uruchom drugi raz: `changed=0` także dla obiektów AWX (poza uruchomieniem zadania).

### Krok 12 — Wróć do wersji z kodu

Launch szablonu `kursant01-site-prod` z ankietą `1.0` (albo `ansible-playbook -i inventories/prod site.yml`).

## Execution environments (omówienie)

AWX uruchamia zadania w kontenerach — **execution environments** (EE): obraz z ansible-core, kolekcjami i bibliotekami
Pythona. Własny EE budujesz `ansible-builder` z pliku `execution-environment.yml`, a lokalnie uruchamiasz playbook
w tym samym EE przez `ansible-navigator run site.yml --eei <obraz>` — dokładnie tak, jak w AWX.

## Sprawdzenie
- Dlaczego w inventory dla AWX hasła są zaszyfrowane pojedynczo, a nie całym plikiem?
- Kto zna hasło vault prod, gdy projekt działa w AWX?
- Czym różni się uprawnienie Execute od Admin na szablonie?
- Co zyskujesz, trzymając konfigurację AWX w gicie (`awx.awx`)?

Rozwiązanie: `odpowiedz/awx_jako_kod.yml`.
