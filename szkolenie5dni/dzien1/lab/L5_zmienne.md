# L5 — Zmienne i ich priorytety (blok 5, 30 min)

## Cel
Zobaczyć, skąd host bierze wartość zmiennej, gdy jest ona zdefiniowana w kilku miejscach.

Zmienne w Ansible mogą być zdefiniowane w kontekście grupy, hosta, playbooka, roli itp.
Nieco upraszczając, o ich znaczeniu decyduje lokalizacja w pliku i katalogu z naszą konfiguracją.

W tym przykładzie wykorzystamy (od najniższego priorytetu):

```
group_vars/all           zmienne globalne — wszystkie hosty
  \ group_vars/webservers   grupa nadrzędna
      \ group_vars/prod        grupa podrzędna
          \ host_vars/web01        konkretny host
              \ vars w playbooku
                  \ -e (extra vars)   zawsze wygrywa
```

Pełna lista: https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#understanding-variable-precedence

**Zasada ćwiczenia:** przed każdym uruchomieniem zapisz, jaki wynik przewidujesz dla web01 i web02. Potem sprawdź.

---

## Krok 1 — Zmienna, której nie ma

Polecenie zawiera szablon Jinja2 — w czasie wykonania w miejsce zmiennej zostanie wstawiona jej wartość:

```bash
ansible webservers -i inventory/hosts.yml -m debug -a 'msg={{ ciekawa_zmienna }}'
```

Oczekiwany błąd: `'ciekawa_zmienna' is undefined`. Znajdź, gdzie zmienna jest (jeszcze zakomentowana):

```bash
grep -R ciekawa_zmienna inventory/
```

## Krok 2 — group_vars/all

Odkomentuj zmienną w `inventory/group_vars/all.yml` i uruchom polecenie z kroku 1.

## Krok 3 — group_vars/webservers

Odkomentuj zmienną w `inventory/group_vars/webservers.yml`. Przewidywanie? Uruchom.

## Krok 4 — group_vars/prod

Odkomentuj zmienną w `inventory/group_vars/prod.yml`. Co się zmieniło i dlaczego tylko na jednym hoście?

## Krok 5 — host_vars/web01

Odkomentuj zmienną w `inventory/host_vars/web01.yml` i uruchom.

Gdy do grupy należy wiele hostów, wszystkie domyślnie przyjmą wartość z `group_vars`, ALE jeśli któryś host
ma swój plik w `host_vars/nazwa_hosta`, definicja zmiennej w tym pliku ma wyższy priorytet i nadpisze wartość grupy.

Zobacz komplet zmiennych hosta tak, jak widzi je Ansible:
```bash
ansible-inventory -i inventory/hosts.yml --host web01
ansible-inventory -i inventory/hosts.yml --host web02
ansible-inventory -i inventory/hosts.yml --graph --vars
```

## Krok 6 — Zmienna najwyższego poziomu: -e

```bash
ansible webservers -i inventory/hosts.yml -m debug -a 'msg={{ ciekawa_zmienna }}' -e 'ciekawa_zmienna="w extra vars"'
```

Zmienna podana z linii poleceń ma zawsze najwyższy priorytet.

## Krok 7 — Zmienne w playbooku

```bash
ansible-playbook -i inventory/hosts.yml zmienne.yml
```

Odkomentuj sekcję `vars` w `zmienne.yml` i uruchom ponownie. Co wygrało: `host_vars/web01` czy `vars` w playbooku?
Na koniec:

```bash
ansible-playbook -i inventory/hosts.yml zmienne.yml -e 'ciekawa_zmienna="z linii poleceń"'
```

> Uwaga na cudzysłowy. Bez zewnętrznych `'...'` (`-e ciekawa_zmienna="z linii poleceń"`) powłoka zdejmie `"`
> i Ansible dostanie `ciekawa_zmienna=z linii poleceń` — wartością będzie samo `z`. Sprawdź!

## Krok 8 (bonus) — wszystko jest słownikiem

```bash
ansible web01 -i inventory/hosts.yml -m debug -a 'var=hostvars[inventory_hostname]'
ansible web01 -i inventory/hosts.yml -m debug -a 'var=group_names'
```

Wśród zmiennych hosta są też te z inventory (`ansible_host`, `ansible_port`) i zmienne specjalne
(`inventory_hostname`, `group_names`). Fakty z modułu `setup` dostępne są w playbooku jako `ansible_facts`.

---

## Sprawdzenie
- Uporządkuj od najsłabszej: `-e`, `group_vars/all`, `host_vars/web01`, `group_vars/prod`, `vars` w playbooku.
- Dlaczego `group_vars/prod.yml` nie zmienia wartości na web01?
- Gdzie umieścisz port aplikacji, który na produkcji jest inny niż na dev?
- Jak sprawdzisz, jaką wartość zmiennej dostanie host, zanim uruchomisz playbook?

W następnych dniach poznasz kolejne miejsca definiowania zmiennych (role, `register`, `set_fact`) i ich użycie
w szablonach konfiguracji.

## Odpowiedzi
- `inventory_odpowiedz/` — wszystkie zmienne odkomentowane:
  `ansible webservers -i inventory_odpowiedz/hosts.yml -m debug -a 'msg={{ ciekawa_zmienna }}'`
- `zmienne_odpowiedz.yml`
