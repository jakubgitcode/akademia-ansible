# L22 (opcja) — Własny moduł (blok 7 albo w domu, 10 min)

Gdy żaden moduł nie robi tego, czego potrzebujesz, a `command` z parsowaniem wyniku robi się nieczytelny —
piszesz moduł w Pythonie. Najprościej: plik w katalogu `library/` obok playbooka.

## Krok 1 — Przeczytaj moduł

```bash
cd ~/dzien5/projekt
less library/naszaaplikacja_info.py
ansible-doc -M library naszaaplikacja_info
```

Moduł czyta `config.cfg` aplikacji i zwraca go jako fakt `naszaaplikacja`, z zamaskowanym hasłem bazy.
Zwróć uwagę na: `DOCUMENTATION` i `EXAMPLES` (z nich powstaje `ansible-doc`), `argument_spec` (parametry z typami
i wartościami domyślnymi), `supports_check_mode=True`, `fail_json` z czytelnym komunikatem, `exit_json(changed=False, …)`.

## Krok 2 — Użyj

```bash
ansible-playbook modul.yml
ansible-playbook modul.yml --check
```

## Krok 3 — Rozbuduj (jeśli chcesz)

Dodaj parametr `pokaz_haslo` (bool, domyślnie `false`) — gdy `true`, moduł nie maskuje hasła. Uruchom
`ansible-doc -M library naszaaplikacja_info` — czy dokumentacja pokazuje nowy parametr? (Trzeba go dopisać
w `DOCUMENTATION`.)

## Dalej

- Moduł do udostępniania innym zespołom: w kolekcji (`ansible-galaxy collection init firma.narzedzia`, katalog `plugins/modules/`).
- Ansible wywoływany z Pythona: **ansible-runner** (`pip install ansible-runner`;
  `ansible_runner.run(private_data_dir=…, playbook='site.yml')`) — z niego korzysta AWX. Wewnętrzne API Ansible
  (`ansible.executor…`) nie jest przeznaczone do użycia z zewnątrz i zmienia się między wersjami.
