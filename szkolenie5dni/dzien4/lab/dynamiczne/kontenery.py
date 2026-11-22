#!/usr/bin/env python3
"""Dynamiczne inventory (skrypt): hosty labowe, które naprawdę działają w Dockerze.

Kontrakt skryptu inventory:
  --list          → całe inventory jako JSON: grupy, hosty i ich zmienne w _meta.hostvars
  --host <nazwa>  → zmienne jednego hosta (tu puste — wszystko jest już w _meta)

Źródłem prawdy jest `docker ps`: host trafia do inventory tylko wtedy, gdy kontener działa.
W firmie w tym miejscu jest zapytanie do API chmury, CMDB albo systemu wirtualizacji.
"""
import json
import re
import subprocess
import sys


def kontenery():
    wynik = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}"],
        capture_output=True, text=True, check=True,
    )
    for linia in wynik.stdout.splitlines():
        nazwa, _, porty = linia.partition("\t")
        port_ssh = re.search(r":(\d+)->22/tcp", porty)
        if re.fullmatch(r"web\d+", nazwa) and port_ssh:
            yield nazwa, int(port_ssh.group(1))


def inventory():
    hosty = dict(sorted(kontenery()))
    return {
        "all": {
            "vars": {
                "ansible_user": "ubuntu",
                "ansible_ssh_private_key_file": "~/.ssh/akademia_lab_key",
                "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
                "ansible_python_interpreter": "/usr/bin/python3",
            },
        },
        "kontenery": {"hosts": list(hosty)},
        "_meta": {
            "hostvars": {nazwa: {"ansible_host": "127.0.0.1", "ansible_port": port} for nazwa, port in hosty.items()},
        },
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--list"]:
        print(json.dumps(inventory(), indent=2))
    elif len(sys.argv) == 3 and sys.argv[1] == "--host":
        print(json.dumps({}))
    else:
        sys.exit(f"Użycie: {sys.argv[0]} --list | --host <nazwa>")
