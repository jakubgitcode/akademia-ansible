# L18 — Sterowanie wykonaniem

Część A robisz w bloku 5 (35 min), część B w bloku 6 (35 min), część C w bloku 7 (15 min).

## Część A — changed_when, until, assert, failed_when, block/rescue (blok 5)

`sterowanie.yml` (dev, web04) sprawdza aplikację i zmienia jej wersję z możliwością wycofania. Uzupełnij `TODO 1–5`:

| TODO | Słowo kluczowe | Po co |
|---|---|---|
| 1 | `changed_when: false` | odczyt nie jest zmianą — `command` zawsze zgłasza `changed` |
| 2 | `until`, `retries`, `delay` | ponawiaj sprawdzenie, aż aplikacja wstanie po restarcie |
| 3 | `ansible.builtin.assert` | warunek z czytelnym komunikatem zamiast „coś nie działa” |
| 4 | `failed_when` | sam decydujesz, co jest błędem (`grep -c` bez trafień zwraca 1) |
| 5 | `rescue` | co zrobić, gdy coś w `block` się nie uda: przywróć kopię, zrestartuj, zgłoś |

```bash
ansible-playbook sterowanie.yml
curl -s http://localhost:8084/ | grep -o 'Wersja: [^<]*'       # 1.1-test
```

Teraz zmiana, która się nie uda (`-e zepsuj=true` psuje konfigurację w środku bloku):

```bash
ansible-playbook sterowanie.yml -e zepsuj=true                 # błąd: zmiana wycofana
curl -s http://localhost:8084/ | grep -o 'Wersja: [^<]*'       # strona działa na poprzedniej konfiguracji
ansible web04 -b -m command -a "cat /var/log/naszaaplikacja/zmiany.log"     # always: wpis także przy błędzie
```

> Pułapka, na którą trafiliśmy przy pisaniu tego labu: przywrócony plik bez `owner`/`group` dostaje właściciela kopii
> (`root:root`). Apache działa jako `www-data`, nie czyta konfiguracji i aplikacja wraca do ustawień przykładowych —
> strona działa, ale pokazuje złe dane. Dlatego w `rescue` uprawnienia są podane jawnie.

Na koniec przywróć stan opisany w kodzie: `ansible-playbook site.yml` (wersja wraca do 1.0).

| Sekcja | Kiedy się wykonuje |
|---|---|
| `block` | zawsze, zadanie po zadaniu |
| `rescue` | tylko gdy zadanie w `block` zakończy się błędem |
| `always` | zawsze, także po błędzie i po `rescue` |

## Część B — restart bez przerwy w działaniu (blok 6)

Prod: dwa serwery aplikacji za load balancerem. `restart_aplikacji.yml` symuluje aktualizację: zatrzymuje Apache,
czeka 5 sekund, uruchamia, sprawdza.

### Krok 1 — Drugi terminal: co widzi użytkownik

Otwórz drugi terminal (na maszynie kursanta: drugie połączenie SSH albo `tmux`) i uruchom:

```bash
while true; do curl -s -o /dev/null -w '%{http_code} ' http://localhost:8081/; sleep 0.3; done
```

Same `200` — strona działa.

### Krok 2 — Restart wszystkich naraz

```bash
ansible-playbook -i inventories/prod restart_aplikacji.yml
```

W drugim terminalu przez kilka sekund `502`: oba serwery stoją jednocześnie.

### Krok 3 — Po jednym: serial

W `restart_aplikacji.yml` odkomentuj `serial: 1` i uruchom ponownie. Same `200`: play przechodzi cały na web02,
a dopiero potem na web03. Ostatnie zadanie czeka, aż load balancer znów kieruje ruch na właśnie zrestartowany serwer
— dopiero wtedy wolno zatrzymać następny.

### Krok 4 — Awaria w trakcie

```bash
ansible-playbook -i inventories/prod restart_aplikacji.yml -e awaria_na=web02
```

Aktualizacja na web02 się nie udała. Play się zatrzymał, web03 nie został ruszony, użytkownicy dalej dostają `200`
(obsługuje ich web03). Przy `serial: 1` błąd jedynego hosta w partii zatrzymuje cały play; przy większych partiach
(np. `serial: 2` z dziesięciu hostów) próg ustawia `max_fail_percentage`.

Napraw: `ansible-playbook -i inventories/prod site.yml`.

## Część C — throttle i restart w handlerze (blok 7)

`serial` dotyczy całego playa. Co, gdy po jednym ma iść tylko restart, a reszta zadań równolegle?

### Krok 5 — throttle

```bash
ansible-playbook -i inventories/prod restart_throttle.yml       # obserwuj drugi terminal
```

Mimo `throttle: 1` są `502`. `throttle` ogranicza **jedno zadanie** do jednego hosta naraz — w bloku dotyczy każdego
zadania osobno: najpierw oba hosty po kolei się zatrzymują, potem po kolei czekają, potem startują.

Po zakończeniu playbooka `502` trwają jeszcze ok. 10 sekund: nginx po błędzie omija serwer przez `fail_timeout`
(domyślnie 10 s), a tu zawiodły oba. Odczekaj, aż w drugim terminalu są same `200`, zanim uruchomisz krok 6.

### Krok 6 — Handler z pętlą po węzłach

`restart_klastra.yml`: zmiana konfiguracji (na wszystkich hostach naraz) powiadamia handler z `run_once`.
Handler dołącza `zadania/restart_klastra_petla.yml` — pętlę po węzłach w `block` z `any_errors_fatal`;
każdy węzeł przechodzi `zadania/restart_wezla.yml` (zatrzymaj, aktualizuj, uruchom, sprawdź) przez `delegate_to`.

```bash
ansible-playbook -i inventories/prod restart_klastra.yml                          # same 200
ansible-playbook -i inventories/prod restart_klastra.yml -e awaria_na=web02       # przerwane przed web03; same 200
ansible-playbook -i inventories/prod site.yml                                     # naprawa
```

To wzorzec do restartu klastrów (Kafka, Elasticsearch, bazy z replikacją): po jednym węźle, ze sprawdzeniem,
że węzeł wrócił do klastra, i z przerwaniem przy pierwszym błędzie — bez spowalniania reszty playa.

## Sprawdzenie
- Czym różnią się `ignore_errors: true`, `failed_when: false` i `rescue`?
- Co się stanie z `until`, gdy skończą się próby?
- `serial`, `throttle`, pętla z `delegate_to` — kiedy które?
- Dlaczego przed restartem kolejnego węzła sprawdzamy load balancer, a nie tylko sam węzeł?

Rozwiązanie: `odpowiedz/sterowanie.yml`, `odpowiedz/restart_aplikacji.yml`.
