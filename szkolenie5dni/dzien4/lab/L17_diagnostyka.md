# L17 — Diagnostyka (blok 4, 35 min)

## Część A — pięć błędów (25 min)

`debuguj.yml` tworzy raport o serwerze aplikacji dev (web04). Ma pięć błędów różnego rodzaju. Pracuj w pętli:
uruchom → przeczytaj komunikat → popraw **jeden** błąd → uruchom ponownie.

```bash
ansible-playbook debuguj.yml
```

Jak czytać komunikat w ansible-core 2.21:
- pierwsza linia `[ERROR]: …` — co się stało;
- `Origin: plik:linia:kolumna` i fragment pliku ze strzałką `^` — gdzie;
- `<<< caused by >>>` — przyczyna głębiej (np. w szablonie), też z `Origin`.

Narzędzia, gdy komunikat nie wystarcza:

```bash
ansible-playbook debuguj.yml -v                                       # wynik każdego zadania (stdout, rc)
ansible-playbook debuguj.yml -vvv                                     # także połączenie i przesyłane pliki
ansible web04 -m ansible.builtin.setup -a "filter=ansible_default_ipv4"   # jak naprawdę wygląda fakt
ansible-playbook debuguj.yml --start-at-task "Zapisz raport"          # od wybranego zadania
```

Typy błędów, na które trafisz (w kolejności): składnia YAML, kod wyjścia polecenia, nazwa zmiennej, struktura faktu
w szablonie, typ wartości w warunku. Podpowiedzi — dopiero gdy utkniesz:

<details><summary>Podpowiedzi</summary>

1. `missing quotes around a template block` — wartość zaczynająca się od `{{` musi być w cudzysłowie.
2. `non-zero return code` przy `grep -c` — bez trafień `grep` zwraca 1. To błąd? `failed_when` (dzień 2: register).
3. `is undefined` — porównaj nazwę zmiennej w zadaniu z tą w `vars`.
4. `has no attribute` w szablonie — wypisz fakt modułem `setup` i zobacz, czy to słownik, lista czy wartość.
5. `Conditionals must have a boolean result` — `"false"` w cudzysłowie to napis; `| bool` (od ansible-core 2.19
   to błąd; starsze wersje po cichu uznawały niepusty napis za prawdę).
</details>

Gdy przejdzie: `cat /tmp/raport_serwera.txt` na web04 (`ansible web04 -b -m command -a "cat /tmp/raport_serwera.txt"`).

## Część B — moduł od środka (10 min)

Gdy moduł zachowuje się dziwnie, a komunikat nic nie mówi, można go uruchomić ręcznie na hoście. Ansible pakuje moduł
w plik `AnsiballZ_*.py`, wysyła na host, uruchamia i usuwa. Zatrzymajmy ten plik:

```bash
ANSIBLE_KEEP_REMOTE_FILES=1 ANSIBLE_PIPELINING=0 ansible web04 -m ansible.builtin.ping -vvv | grep AnsiballZ_ping.py
```

`ANSIBLE_PIPELINING=0` jest potrzebne, bo przy włączonym `pipelining` (nasz `ansible.cfg`) moduł nie trafia na dysk.
Skopiuj ścieżkę `/home/ubuntu/.ansible/tmp/ansible-tmp-…/AnsiballZ_ping.py` i zaloguj się na web04:

```bash
ssh -i ~/.ssh/akademia_lab_key -p 2224 ubuntu@127.0.0.1
cd /home/ubuntu/.ansible/tmp/ansible-tmp-…/          # katalog ze ścieżki
python3 AnsiballZ_ping.py explode                     # rozpakowuje do debug_dir/
ls debug_dir; cat debug_dir/args                      # kod modułu i argumenty
vi debug_dir/ansible/modules/ping.py                  # zmień default='pong' na default='pong-szkolenie'
python3 AnsiballZ_ping.py execute                     # uruchamia rozpakowany, zmieniony moduł
```

Tak debuguje się moduł bez Ansible pomiędzy: można dopisać `print`, uruchomić pod debuggerem Pythona, zmienić `args`.

## Sprawdzenie
- Gdzie w komunikacie błędu jest numer linii, a gdzie przyczyna z szablonu?
- Jak sprawdzisz strukturę faktu, zanim użyjesz go w szablonie?
- Kiedy `-v`, a kiedy `-vvv`?
- Po co `ANSIBLE_KEEP_REMOTE_FILES` i dlaczego razem z `ANSIBLE_PIPELINING=0`?

Rozwiązanie: `odpowiedz/debuguj.yml` i `odpowiedz/templates/raport.txt.j2`.
