# Środowisko labowe (Docker)

Cztery hosty zarządzane (`web01`–`web04`: Ubuntu 24.04, systemd, sshd, użytkownik `ubuntu` z sudo bez hasła).
Dni 1–2 używają `web01` i `web02`; `web03` dochodzi w dniu 3 (skalowanie aplikacji na kolejny serwer),
`web04` w dniu 4 (osobny host środowiska dev).

Wymagania: Docker (Linux/macOS: Docker Engine lub Docker Desktop; Windows: WSL2 + Docker Desktop) i Ansible
zainstalowany u siebie (lab L1). Na Windows wszystko uruchamiasz **wewnątrz WSL2 (Ubuntu)**, a repozytorium
trzymasz w katalogu domowym Linuksa, nie pod `/mnt/c`.

```bash
./setup.sh                                  # klucz ~/.ssh/akademia_lab_key + kontenery + test SSH
ansible -i inventory.yml all -m ping        # web01 i web02
docker compose down                         # sprzątanie
```

| Host | SSH | Strona WWW |
|---|---|---|
| web01 | `127.0.0.1:2221` | http://localhost:8081 |
| web02 | `127.0.0.1:2222` | http://localhost:8082 |
| web03 | `127.0.0.1:2223` | http://localhost:8083 |
| web04 | `127.0.0.1:2224` | http://localhost:8084 |

Użytkownik `ubuntu`, klucz `~/.ssh/akademia_lab_key`. Porty z wnętrza kontenera inne niż 80 nie są wystawione
na Twój komputer; sprawdzisz je tak: `docker exec web04 curl -s http://localhost:8080/` (dzień 4: aplikacja dev na porcie 8080).

Hosty nie działają? `./setup.sh` jeszcze raz (bezpieczne — działające hosty zostają). Zamiast kontenerów możesz
użyć maszyn w chmurze od prowadzącego: `../inventory/szkolenie/README.md`.

Kontenery to nie pełne serwery: pakiety nie uruchamiają ani nie zatrzymują same swoich usług (np. po
`apt purge apache2` Apache dalej działa), a `systemctl` wymaga `sudo` (`-b` w Ansible).
