#!/usr/bin/env bash
# Uruchom raz: tworzy klucz SSH do labów, startuje kontenery web01–web04 i wgrywa im klucz.
# Klucz trzymamy w ~/.ssh (nie w repozytorium), żeby miał poprawne uprawnienia także wtedy,
# gdy repo leży na dysku współdzielonym z Windows lub maszyną wirtualną.
set -euo pipefail
cd "$(dirname "$0")"
KEY="$HOME/.ssh/akademia_lab_key"
SSH_OPTS=(-i "$KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 -o LogLevel=ERROR)

mkdir -p "$HOME/.ssh" && chmod 700 "$HOME/.ssh"
[ -f "$KEY" ] || ssh-keygen -q -t ed25519 -N '' -C akademia-ansible-lab -f "$KEY"
chmod 600 "$KEY"

# Bez --build: obraz powstaje tylko, gdy go nie ma. Z --build Docker potrafi zbudować obraz o nowym ID
# i odtworzyć działające kontenery — a wtedy znika wszystko, co laby zainstalowały na hostach.
# Nowy obraz po zmianie Dockerfile.node: docker compose down && docker compose build && ./setup.sh
docker compose up -d

for node in web01 web02 web03 web04; do
  docker exec -i "$node" sh -c 'cat > /home/ubuntu/.ssh/authorized_keys \
    && chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys \
    && chmod 600 /home/ubuntu/.ssh/authorized_keys' < "$KEY.pub"
done

for port in 2221 2222 2223 2224; do
  ok=no
  for _ in $(seq 1 20); do
    if ssh "${SSH_OPTS[@]}" -p "$port" ubuntu@127.0.0.1 'echo "OK: $(hostname)"'; then ok=yes; break; fi
    sleep 1
  done
  [ "$ok" = yes ] || { echo "BŁĄD: brak połączenia SSH na porcie $port (docker compose logs)"; exit 1; }
done
echo "Gotowe. Sprawdź: ansible -i $(pwd)/inventory.yml all -m ping"
