# L12 — Ansible Galaxy i kolekcje (blok 3, 30 min)

**Po co:** bazy danych nie piszemy od zera — weźmiemy gotową rolę z Ansible Galaxy. Zanim jej użyjemy (L13),
instalujemy ją z przypiętą wersją i czytamy jej kod.

## Krok 1 — requirements.yml i miejsce instalacji

Przeczytaj `requirements.yml`: rola `geerlingguy.mysql` w wersji 6.5.0 i kolekcja `community.mysql`
w wersji co najmniej 5.0.0, ale poniżej 6.0.0. Komentarz w pliku wyjaśnia górną granicę.

W `ansible.cfg` są dwie linie, które kierują instalację do katalogu projektu:

```ini
roles_path = galaxy/roles
collections_path = galaxy/collections
```

Każdy projekt ma wtedy własne wersje zależności, a `galaxy/` jest w `.gitignore` — do repozytorium trafia tylko
`requirements.yml`.

## Krok 2 — Instalacja

```bash
ansible-galaxy install -r requirements.yml
ansible-galaxy role list
```

Rola trafia do `galaxy/roles/geerlingguy.mysql`. Przy kolekcji zobaczysz `Nothing to do. All requested
collections are already installed`: pakiet `ansible` zainstalowany przez pip ma już `community.mysql`
w wersji spełniającej wymaganie.

```bash
ansible-galaxy collection list community.mysql      # skąd: katalog site-packages pakietu ansible
pip show ansible | head -2                          # ansible = ansible-core + zestaw kolekcji
```

> Z samym `ansible-core` (bez pakietu `ansible`) — np. w kontenerach AWX — to samo polecenie pobierze kolekcję
> do `galaxy/collections`. Dlatego `requirements.yml` wymienia ją mimo to.

## Krok 3 — Skąd pełne nazwy modułów

```bash
ansible-doc community.mysql.mysql_db | head -5
```

`community.mysql.mysql_db` to: przestrzeń nazw `community`, kolekcja `mysql`, moduł `mysql_db`.
Ansible ostrzega, że moduł przeniesiono do `ansible.mysql.mysql_db` i w `community.mysql` 6.0.0 stara nazwa zniknie.
Rola `geerlingguy.mysql` 6.5.0 wciąż używa starych nazw — stąd górna granica wersji w `requirements.yml`.
Te same ostrzeżenia zobaczysz w L13 przy instalacji bazy.

## Krok 4 — Przeczytaj rolę, zanim jej użyjesz

```bash
tree galaxy/roles/geerlingguy.mysql
less galaxy/roles/geerlingguy.mysql/README.md               # sekcja „Role Variables”
less galaxy/roles/geerlingguy.mysql/defaults/main.yml
less galaxy/roles/geerlingguy.mysql/tasks/main.yml
```

Znajdź i zapisz:
1. Którymi zmiennymi tworzy się bazę i użytkownika? Jak wygląda jeden element każdej listy?
2. Jak ustawia się hasło roota MySQL i adres, na którym MySQL przyjmuje połączenia?
3. Jak rola obsługuje różne dystrybucje? (podpowiedź: `include_tasks` z `when` w `tasks/main.yml`)
4. Czym ta rola różni się od Twojej roli `aplikacja`? (pliki zadań, obsługiwane systemy, `meta/main.yml`)

## Krok 5 (jeśli zdążysz) — Galaxy w przeglądarce

Na <https://galaxy.ansible.com> wyszukaj `geerlingguy mysql`: wersje, data ostatniego wydania, liczba pobrań,
link do repozytorium z kodem i zgłoszeniami błędów. Tak oceniasz, czy rolę ktoś utrzymuje.

## Sprawdzenie
- Co oznaczają trzy części nazwy `community.mysql.mysql_db`?
- Dlaczego wersje w `requirements.yml` są przypięte? Co się stanie bez górnej granicy przy wydaniu `community.mysql` 6.0.0?
- Co jest w pakiecie `ansible`, a czego nie ma w `ansible-core`?
- Jakie trzy rzeczy sprawdzasz w roli z Galaxy, zanim jej użyjesz?
