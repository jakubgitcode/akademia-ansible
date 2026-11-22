#!/usr/bin/python
# -*- coding: utf-8 -*-
"""L22 (opcja) — własny moduł: odczytuje config.cfg aplikacji naszaaplikacja i zwraca jego treść jako fakty.

Moduł leży w katalogu library/ obok playbooka — Ansible znajduje go sam. Dokumentacja:
  ansible-doc -M library naszaaplikacja_info
"""

DOCUMENTATION = r"""
module: naszaaplikacja_info
short_description: Odczytuje konfigurację aplikacji naszaaplikacja
description:
  - Czyta plik C(config.cfg) aplikacji i zwraca jego sekcje jako fakt C(naszaaplikacja).
  - Hasła z sekcji C([baza]) nie trafiają do wyniku.
  - Niczego nie zmienia, więc działa także w trybie C(--check).
options:
  katalog:
    description: Katalog aplikacji.
    type: path
    default: /var/www/naszaaplikacja
author: uczestnik szkolenia
"""

EXAMPLES = r"""
- name: Konfiguracja aplikacji
  naszaaplikacja_info:
  register: info

- name: Wersja
  ansible.builtin.debug:
    msg: "{{ ansible_facts.naszaaplikacja.config.wersja }}"
"""

RETURN = r"""
ansible_facts:
  description: Fakt naszaaplikacja z sekcjami config.cfg (bez haseł).
  returned: success
  type: dict
"""

import configparser
import os

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(katalog=dict(type="path", default="/var/www/naszaaplikacja")),
        supports_check_mode=True,
    )
    plik = os.path.join(module.params["katalog"], "config.cfg")
    if not os.path.isfile(plik):
        module.fail_json(msg=f"Nie ma pliku {plik} — czy aplikacja jest wdrożona?")

    config = configparser.ConfigParser()
    try:
        config.read(plik, encoding="utf-8")
    except (OSError, configparser.Error) as blad:
        module.fail_json(msg=f"Nie mogę odczytać {plik}: {blad}")

    sekcje = {nazwa: dict(config[nazwa]) for nazwa in config.sections()}
    if "baza" in sekcje and "haslo" in sekcje["baza"]:
        sekcje["baza"]["haslo"] = "********"

    module.exit_json(changed=False, ansible_facts={"naszaaplikacja": sekcje})


if __name__ == "__main__":
    main()
