#!/bin/sh
# textconv dla gita: odszyfrowana treść pliku vault przy git diff / git log -p (konfiguracja: README.md).
# Wersje zaszyfrowane innym hasłem (np. z poprzedniego szkolenia) nie przerywają git log — dostają opis zamiast treści.
ansible-vault view --vault-id "szkolenie@$HOME/.vault_szkolenie" "$1" 2>/dev/null \
  || echo "(zaszyfrowane innym hasłem vault — np. z poprzedniego szkolenia)"
