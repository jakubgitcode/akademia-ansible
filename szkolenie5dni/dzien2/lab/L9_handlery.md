# L9 — Handlery, wait_for, pre_tasks i post_tasks (blok 6, 30 min)

**Problem z L8:** Apache restartuje się przy każdym uruchomieniu playbooka, także wtedy, gdy nic się nie zmieniło.
Na produkcji to przerwa w działaniu aplikacji przy każdym wdrożeniu. Restart ma się wykonać tylko wtedy,
gdy zmieniła się konfiguracja albo kod.

Pracujesz dalej na swoim `wgraj_aplikacje.yml`. Nie skończyłeś L8? `cp wgraj_aplikacje_odpowiedz.yml wgraj_aplikacje.yml`
(w tej kopii szablony są w `templates/odpowiedz/`).

## Krok 1 — Restart jako handler

1. Usuń zadanie „Zrestartuj Apache”. W jego miejsce wpisz zadanie, które tylko pilnuje, żeby usługa działała:
   `ansible.builtin.service` z `name: apache2`, `state: started`, `enabled: true`.
2. Na końcu playa (na poziomie `tasks:`, nie wewnątrz) dodaj sekcję `handlers:` z handlerem:

   ```yaml
     handlers:
       - name: Restartuj Apache
         ansible.builtin.service:
           name: apache2
           state: restarted
   ```

3. Do zadań, po których Apache musi wczytać zmiany, dopisz `notify: Restartuj Apache`: kod, virtualenv,
   konfiguracja, WSGI, VirtualHost, port, `a2ensite`, `a2dissite`.

```bash
ansible-playbook wgraj_aplikacje.yml --syntax-check
ansible-playbook wgraj_aplikacje.yml        # changed=0, handler się nie wykonuje
```

## Krok 2 — Zmiana wersji: handler w akcji

W sekcji `vars` zmień `aplikacja_wersja` na `"1.1"` i uruchom:

```bash
ansible-playbook wgraj_aplikacje.yml
curl http://localhost:8081/                 # Wersja: 1.1
```

Obserwuj: zmienia się tylko konfiguracja, a na końcu `RUNNING HANDLER [Restartuj Apache]` na obu hostach.
Uruchom jeszcze raz: `changed=0`, handler się nie wykonuje.

## Krok 3 — Czekanie na aplikację: wait_for

Po restarcie Apache potrzebuje chwili, zanim zacznie przyjmować połączenia. Dodaj drugi handler i wywołaj go
z pierwszego (handler też może mieć `notify`):

```yaml
    - name: Restartuj Apache
      ansible.builtin.service:
        name: apache2
        state: restarted
      notify: Czekaj na aplikację

    - name: Czekaj na aplikację
      ansible.builtin.wait_for:
        port: "{{ aplikacja_port }}"
        timeout: 30
```

## Krok 4 — pre_tasks i post_tasks

Dodaj do playa dwie sekcje (na poziomie `tasks:`):

- `pre_tasks:` — zadanie `ansible.builtin.debug` z komunikatem, co i gdzie wdrażasz, np.
  `"{{ aplikacja_nazwa }} {{ aplikacja_wersja }} → {{ inventory_hostname }}"`;
- `post_tasks:` — test po wdrożeniu: `ansible.builtin.uri` z `url: "http://localhost:{{ aplikacja_port }}/health"`
  (moduł zgłasza błąd, gdy odpowiedź nie ma kodu 200).

Zmień wersję na `"1.2"` i uruchom. Przeczytaj wynik od góry i zapisz kolejność:
`pre_tasks` → `tasks` → handlery → `post_tasks`. Handlery wykonują się na końcu każdej sekcji, więc test
w `post_tasks` sprawdza aplikację już po restarcie.

## Krok 5 (jeśli zdążysz) — pułapka: błąd po zmianie

1. Zmień wersję na `"1.3"` i na końcu `tasks` dopisz zadanie, które zawsze kończy się błędem:
   `ansible.builtin.command: /bin/false` (nazwa: „Symulowany błąd”).
2. Uruchom: konfiguracja się zmienia, potem błąd. Handler **nie** wykonuje się na hostach z błędem.
3. Usuń zadanie z błędem i uruchom ponownie: `changed=0`, handler też się nie wykonuje — konfiguracja już jest
   na miejscu, więc nic go nie powiadamia.
4. `curl http://localhost:8081/` — strona nadal pokazuje `1.2`: Apache działa ze starą konfiguracją.

Jak temu zapobiec: `--force-handlers` (handlery wykonują się mimo błędu) albo `force_handlers: true` w playu.
Naprawa po fakcie: restart ręczny `ansible webservers -b -m ansible.builtin.service -a "name=apache2 state=restarted"`.

## Sprawdzenie
- Ile razy wykona się handler, gdy powiadomią go trzy zadania na tym samym hoście?
- Dlaczego test z `post_tasks` widzi aplikację po restarcie, choć handler jest zdefiniowany na końcu playa?
- Do czego służy `wait_for` i co by się stało bez niego, gdyby aplikacja startowała 10 sekund?
- Co robi `meta: flush_handlers`? (dokumentacja: „Handlers: running operations on change”)

Rozwiązanie: `wgraj_aplikacje_odpowiedz_handlers.yml` (bez kroku 5).
