# Dzień 2 — laby

Wszystkie laby dnia 2 robisz w tym katalogu. Inventory (`inventory/hosts.yml`) i `ansible.cfg` są gotowe,
więc polecenia piszesz bez `-i inventory/hosts.yml`.

| Lab | Kiedy | Temat | Czas |
|---|---|---|---|
| [L6, część 0](L6_0_konfiguracja.md) | blok 1 | skąd Ansible bierze ustawienia: `ansible.cfg`, `ANSIBLE_*`, opcje, zmienne, `-e` | 7 min |
| [L6, część A](L6_administracja.md) | blok 1 | pakiety, aktualizacja, usługa | 20 min |
| [L6, część B](L6_administracja.md#część-b--pliki-konfiguracyjne-blok-2) | blok 2 | `template`, `copy`, `lineinfile`, `blockinfile`, `fetch` | 30 min |
| [L7](L7_warunki_petle.md) | blok 3 | warunki, pętle, `register`, `set_fact`, zmienne per środowisko | 30 min |
| [L8](L8_wdrozenie.md) | bloki 4 i 5 | wdrożenie aplikacji jednym playbookiem | 35 + 35 min |
| [L9](L9_handlery.md) | blok 6 | handlery, `wait_for`, `pre_tasks` i `post_tasks` | 30 min |
| [L10](L10_tagi.md) | blok 7 | tagi; playbook z asystentem AI i jego sprawdzenie | 20 min |

## Środowisko

Te same hosty co w dniu 1: web01 (grupa `dev`) i web02 (grupa `prod`), obie w grupie `webservers`.

```bash
source ~/venv-ansible/bin/activate      # Ansible z dnia 1 (L1)
cd ~/dzien2                             # albo: cd szkolenie5dni/dzien2/lab
ansible all -m ping                     # 2 × SUCCESS
```

Strony WWW hostów (od L8) otwierasz z maszyny, na której pracujesz:

```bash
curl http://localhost:8081/     # web01
curl http://localhost:8082/     # web02
```

> Ansible nie widzi hostów (`provided hosts list is empty`)? Sprawdź, czy jesteś w katalogu labu.
> W katalogu zapisywalnym dla wszystkich (np. `/mnt/c` w WSL) Ansible pomija `ansible.cfg` —
> dopisz wtedy `-i inventory/hosts.yml` albo przenieś katalog do domowego.

Masz inne hosty niż `lab-env`? Skopiuj swoje inventory z dnia 1: `cp ../dzien1/inventory/hosts.yml inventory/`
(w repozytorium: `cp ../../dzien1/lab/inventory/hosts.yml inventory/`).

## Gdy coś nie wychodzi

- Rozwiązania są obok zadań: pliki `*_odpowiedz.yml`, szablony w `templates/odpowiedz/`.
- Laby L8–L10 rozbudowują jeden playbook (`wgraj_aplikacje.yml`). Jeśli nie skończysz L8, zacznij L9 od kopii
  rozwiązania: `cp wgraj_aplikacje_odpowiedz.yml wgraj_aplikacje.yml` (szablony z `templates/odpowiedz/`).
- Zatrzymaj się i zawołaj prowadzącego, zanim spędzisz nad jednym błędem więcej niż 5 minut.
