# L3 — YAML i Jinja2 (blok 3, 30 min)

## Cel
Przećwiczyć czytanie struktur danych YAML (listy, słowniki, zagnieżdżenia) oraz podstawy Jinja2:
dostęp do danych i filtry.

## Środowisko
Ten lab wykonujesz **lokalnie** (`hosts: localhost`) — nie potrzebujesz hostów web01 i web02.
Ćwiczymy sam język: YAML + Jinja2.

> Bez inventory Ansible wypisze ostrzeżenie `provided hosts list is empty, only localhost is available` — to oczekiwane.

---

## Przykłady ze slajdów (pokaz prowadzącego)

Dwa gotowe przykłady, które prowadzący uruchamia przed filtrami. Możesz je powtórzyć i zmieniać zmienne:

```bash
ansible-playbook jinja_w_playbooku.yml                 # {{ }} w argumentach modułów (slajd 41)
ansible-playbook konfiguracja.yml                      # szablon templates/aplikacja.conf.j2 → /tmp/aplikacja.conf
cat /tmp/aplikacja.conf
ansible-playbook konfiguracja.yml                      # 2. raz: changed=0
ansible-playbook konfiguracja.yml -e aplikacja_port=9090 --check --diff
```

---

## Krok 1 — Analiza struktur danych (5 min)

Otwórz plik `dane.yml` i odpowiedz na pytania (na papierze / w głowie):

1. Co jest **listą**, a co **słownikiem**?
2. Czym jest `uzytkownicy` — lista? słownik? lista słowników?
3. Czym jest `srodowiska` — jak dostać się do `db_host` środowiska `prod`?
4. Dlaczego `wersja: "2.5.1"` jest w cudzysłowie, a `port: 8080` nie?
5. Ilu użytkowników jest aktywnych (`aktywny: true`)?

Sprawdź, że plik jest poprawnym YAML-em:
```bash
python3 -c "import yaml; print(yaml.safe_load(open('dane.yml')))"
```

## Krok 2 — Dostęp do struktur danych (10 min)

Otwórz `struktury_danych.yml` i zastąp teksty `"TODO"` właściwymi wyrażeniami Jinja2.

```bash
ansible-playbook struktury_danych.yml      # działa od razu (wyświetla TODO); uruchamiaj po każdej zmianie
```

Wskazówki:
```yaml
{{ slownik.klucz }}           # dostęp do klucza słownika
{{ slownik['klucz'] }}        # zapis równoważny
{{ lista[0] }}                # pierwszy element listy (liczymy od 0!)
{{ lista_slownikow[1].pole }} # pole drugiego elementu
```

## Krok 3 — Filtry Jinja2 (15 min)

Otwórz `jinja_filtry.yml` i uzupełnij miejsca oznaczone `# TODO`.

```bash
ansible-playbook jinja_filtry.yml
```

Filtry, których będziesz potrzebować:
```yaml
| default('wartość')          # gdy zmienna nie istnieje
| join(', ')                  # lista → tekst
| length                      # liczba elementów
| upper                       # wielkie litery
| map(attribute='pole')       # wyciągnij pole z listy słowników
| selectattr('pole')          # przefiltruj listę słowników
| list                        # zamknięcie wyniku map/selectattr w listę
```

## Krok 4 (bonus albo zadanie domowe) — pętla w szablonie

Otwórz `templates/raport.txt.j2` i uzupełnij miejsca `TODO`. Playbook `generuj_raport.yml` wygeneruje z szablonu plik.

```bash
ansible-playbook generuj_raport.yml
cat /tmp/akademia/raport.txt
```

Składnia pętli w szablonie:
```jinja2
{% for element in lista %}
 - {{ element.pole }}
{% endfor %}
```

Szablony do plików konfiguracyjnych usług to temat dnia 2 — tu poznajesz składnię.

---

## Sprawdzenie
- Jak dostać się do elementu listy, a jak do klucza słownika w Jinja2?
- Co zwraca `uzytkownicy | map(attribute='name')` i po co na końcu `| list`?
- Czym różni się `{{ }}` od `{% %}`?
- Po co filtr `default()` i przed jakim błędem chroni?

## Odpowiedzi
- `struktury_danych_odpowiedz.yml`
- `jinja_filtry_odpowiedz.yml`
- `templates/raport_odpowiedz.txt.j2` — test: `ansible-playbook generuj_raport.yml -e szablon=raport_odpowiedz.txt.j2`
