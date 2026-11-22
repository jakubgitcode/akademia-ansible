# L14 — Load balancer, skalowanie, diagnoza warstwami

Część A robisz w bloku 6 (35 min), część B w bloku 7 (15 min).

## Część A — load balancer i skalowanie (blok 6)

### Krok 1 — Rola loadbalancer

Rola `roles/loadbalancer` jest prawie gotowa: instaluje nginx, wgrywa konfigurację i przeładowuje nginx
handlerem. Przeczytaj `defaults/main.yml` (parametry) i `tasks/main.yml`.

### Krok 2 — Lista backendów z inventory

W `roles/loadbalancer/templates/naszaaplikacja.conf.j2` zamień `server TODO:TODO;` na pętlę po hostach z grupy
`loadbalancer_grupa_backendow` (wskazówki w komentarzu nad tą linią). Efekt na serwerze:

```nginx
upstream naszaaplikacja {
    server 172.18.0.3:80;
}
```

Nie wpisujesz adresów — szablon bierze je z faktów hostów z grupy.

### Krok 3 — Play warstwy load balancera

Na końcu `site.yml`, **po** playu aplikacji, dopisz:

```yaml
- name: Warstwa load balancera
  hosts: loadbalancers
  become: true
  roles:
    - loadbalancer
```

Load balancer jest ostatni: potrzebuje faktów serwerów aplikacji, a te zbiera play aplikacji.

### Krok 4 — Uruchom

```bash
ansible-playbook site.yml
curl http://localhost:8081/                 # przez load balancer: Serwer: web02
ansible loadbalancers -b -m command -a "cat /etc/nginx/sites-available/naszaaplikacja"
ansible-playbook site.yml                   # changed=0
```

### Krok 5 — Skalowanie: trzeci host

Ruch rośnie, potrzebny drugi serwer aplikacji. W `inventory/hosts.yml`, w grupie `appservers`, odkomentuj linię
z `web03`:

```bash
ansible-inventory --graph appservers        # web02 i web03
```

### Krok 6 — Jedno polecenie

```bash
time ansible-playbook site.yml
```

Obserwuj: web03 dostaje wszystko od zera (Apache, kod, virtualenv, konfigurację z adresem bazy), a load balancer —
nową linię `server` i przeładowanie nginx. Nikt nie edytował konfiguracji nginx ani aplikacji.

```bash
curl http://localhost:8083/                                              # web03 bezpośrednio
for i in 1 2 3 4 5 6; do curl -s http://localhost:8081/ | grep -o 'Serwer: web0.'; done   # na zmianę web02 i web03
```

Ile trwało dołożenie serwera? Ile trwałoby ręcznie według instrukcji dewelopera z dnia 2?

## Część B — diagnoza warstwami (blok 7, 15 min)

### Krok 7 — Awaria

`awaria.yml` psuje jedną losową warstwę. Uruchom go tak, żeby nie widzieć, co zrobił:

```bash
ansible-playbook awaria.yml > /dev/null
```

### Krok 8 — Znajdź przyczynę, warstwa po warstwie

Zacznij od tego, co widzi użytkownik, i schodź w dół:

```bash
curl -s http://localhost:8081/                                  # 1. load balancer: odpowiada? co pokazuje?
curl -s http://localhost:8082/ ; curl -s http://localhost:8083/ # 2. każdy serwer aplikacji osobno
ansible databases -b -m command -a "systemctl is-active mysql"  # 3. baza
ansible all -b -m command -a "ss -ltnp"                         # kto słucha na jakich portach
```

Przydatne też: `ansible appservers -b -m command -a "tail -5 /var/log/naszaaplikacja/error.log"`,
`ansible loadbalancers -b -m command -a "nginx -t"`.

> Gdy padnie jeden serwer aplikacji, strona przez load balancer działa dalej — nginx przekazuje ruch do drugiego.
> Awarię widać dopiero, gdy sprawdzisz każdy serwer osobno. Dlatego monitoring sprawdza każdy serwer, nie tylko adres
> load balancera.

### Krok 9 — Naprawa

```bash
ansible-playbook site.yml --check --diff     # co odbiega od opisu? (przy awarii bazy --check też nie przejdzie)
ansible-playbook site.yml                    # przywraca stan opisany w kodzie
```

Powtórz kroki 7–9 jeszcze raz albo dwa — warstwa jest losowana. Konkretną warstwę zepsujesz tak:
`ansible-playbook awaria.yml -e awaria=baza` (albo `aplikacja`, `balanser`).

## Dodatkowe (gdy skończysz wcześniej)

- Skalowanie w dół: zakomentuj web03 w `appservers` i uruchom `site.yml`. Load balancer przestaje kierować ruch na web03,
  ale aplikacja na web03 nadal działa — jak byś ją wyłączył?
- Z oryginalnego LAB 10: trzy instancje aplikacji na jednym hoście na różnych portach — `include_role` w pętli.
  Co trzeba sparametryzować w roli, żeby instancje się nie nadpisywały?

## Sprawdzenie
- Dlaczego kolejność playów to baza → aplikacja → load balancer?
- Jak lista backendów w nginx buduje się sama? Co się stanie, gdy grupa `appservers` będzie pusta?
- Co zmieniłeś, żeby dołożyć serwer? Gdzie w tym projekcie jest „stan docelowy” infrastruktury?
- Dlaczego awarię jednego serwera aplikacji trudno zauważyć przez load balancer?

Rozwiązanie: `odpowiedz/roles/loadbalancer/templates/naszaaplikacja.conf.j2`, `odpowiedz/site.yml`,
`odpowiedz/inventory/hosts.yml`.
