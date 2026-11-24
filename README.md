# Akademia Ansible — szkolenie 5 dni: laby

Materiały dla uczestników: instrukcje labów, pliki do ćwiczeń z rozwiązaniami, prezentacje dni
i środowisko z hostami do ćwiczeń.

```
lab-env/              hosty web01–web04 w Dockerze (Ubuntu 24.04, systemd, SSH) — tu robisz laby
inventory/szkolenie/  te same hosty na maszynach w chmurze: zapas, gdy Docker nie działa, i do rozwiązań
pokaz_vault/          ansible-vault w publicznym repo: plik zaszyfrowany w całości, git diff na sekretach
szkolenie5dni/dzienN/ lab/ (instrukcje L1–L22, pliki, rozwiązania) i prezentacja dnia (dni 1–5)
```

| Dzień | Temat | Laby |
|---|---|---|
| 1 | środowisko, polecenia ad-hoc, YAML i Jinja2, pierwszy playbook, zmienne | L1–L5 |
| 2 | pakiety i pliki, warunki i pętle, wdrożenie aplikacji `naszaaplikacja`, handlery, tagi | L6–L10 |
| 3 | role, Ansible Galaxy, baza MySQL, load balancer i skalowanie | L11–L14 |
| 4 | wiele środowisk, ansible-vault, diagnostyka, sterowanie wykonaniem, restart bez przerwy | L15–L18 |
| 5 | AWX, ansible-lint i Molecule, przyspieszanie, własny moduł, Windows | L19–L22 |

## Start

Na szkoleniu z prowadzącym masz maszynę z gotowym środowiskiem — zaloguj się i przeczytaj powitanie.
Samodzielnie (Linux, macOS albo Windows z WSL2; potrzebny Docker):

```bash
git clone https://github.com/jakubgitcode/akademia-ansible.git ~/akademia-ansible
cd ~/akademia-ansible/lab-env && ./setup.sh       # hosty web01–web04
cd ~/akademia-ansible/szkolenie5dni/dzien1/lab && cat README.md  # od tego zaczynasz
```

Rozwiązania leżą obok zadań: pliki `*_odpowiedz*`, katalogi `odpowiedz/` i `inventory_odpowiedz/`.
Zajrzyj do nich, gdy utkniesz — albo po to, żeby porównać ze swoim.

W trakcie szkolenia pobieraj zmiany: `cd ~/akademia-ansible && git pull`.
