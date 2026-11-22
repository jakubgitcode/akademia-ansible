#!/usr/bin/env bash
# L1, część B — środowisko projektu w jednym poleceniu:  source source_me.sh
# Wersja z prezentacji (slajd 74), uproszczona: venv obok projektu, wersje z requirements.txt.
#   source source_me.sh      tworzy venv przy pierwszym użyciu i go aktywuje
#   source source_me.sh -i   dodatkowo instaluje ponownie pakiety z requirements.txt (np. po zmianie wersji)
#   deactivate               wyłącza venv i czyści zmienne ANSIBLE_* projektu (jak w oryginale)

ANS_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export ANS_ROOT_DIR
if [ ! -f "$ANS_ROOT_DIR/requirements.txt" ]; then
  echo "!!! Brak $ANS_ROOT_DIR/requirements.txt: najpierw L1 część B, krok 6 (w ~/venv-ansible):"
  echo "    pip freeze | grep -iE '^ansible(-core)?==' > requirements.txt"
  echo "    (albo gotowe wersje: cp requirements.txt.odpowiedz requirements.txt)"
  unset ANS_ROOT_DIR
  return 1
fi

# Ustawienia Ansible dla tego projektu — poziom "zmienna środowiska" z L6 część 0 (dzień 2): wygrywają z ansible.cfg,
# przegrywają z opcjami polecenia. Sprawdzenie (źródło "env: ..."):
#   ansible-config dump --only-changed              ustawienia ogólne, np. ANSIBLE_FORKS
#   ansible-config dump --only-changed -t callback  ustawienia wtyczek, np. ANSIBLE_CALLBACK_RESULT_FORMAT
__ans_zmienne="ANSIBLE_CONFIG ANSIBLE_CALLBACK_RESULT_FORMAT"
export ANSIBLE_CONFIG="$ANS_ROOT_DIR/ansible.cfg"       # ten plik, nawet gdy uruchamiasz z innego katalogu
export ANSIBLE_CALLBACK_RESULT_FORMAT=yaml              # wyniki zadań czytelniej (wieloliniowo) niż domyślny JSON
# Odkomentuj i dopisz nazwę do __ans_zmienne, żeby deactivate ją czyściło:
# export ANSIBLE_FORKS=20                                         # więcej hostów naraz (domyślnie 5)
# export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible/vault_pass.txt   # dzień 4: sekrety
# export ANSIBLE_KEEP_REMOTE_FILES=1                              # dzień 4: debugowanie modułów — nigdy na stałe

__install=false
[ "${1:-}" = "-i" ] && __install=true

if [ ! -d "$ANS_ROOT_DIR/venv" ]; then
  echo "-- Brak venv; tworzę $ANS_ROOT_DIR/venv"
  python3 -m venv "$ANS_ROOT_DIR/venv" || { echo "!!! nie udało się utworzyć venv (Ubuntu: sudo apt install python3-venv)"; return 1; }
  __install=true
fi
# venv bez ansible (np. poprzednia instalacja się przerwała): instaluj ponownie
[ -x "$ANS_ROOT_DIR/venv/bin/ansible" ] || __install=true

# shellcheck disable=SC1091
source "$ANS_ROOT_DIR/venv/bin/activate"

if [ "$__install" = true ]; then
  echo "-- Instaluję pakiety z requirements.txt"
  pip install -q --upgrade pip
  pip install -q -r "$ANS_ROOT_DIR/requirements.txt" || { echo "!!! pip install nie powiódł się"; return 1; }
fi
unset __install

# deactivate z venv dodatkowo czyści zmienne projektu (aktywacja venv podmienia deactivate, więc owijamy ją za każdym razem)
__venv_deactivate_src=$(declare -f deactivate)
if [[ $__venv_deactivate_src != *__venv_deactivate* ]]; then
  eval "__venv_deactivate${__venv_deactivate_src#deactivate}"
  deactivate() {
    __venv_deactivate "$@"
    if [ "${1:-}" != nondestructive ]; then
      # shellcheck disable=SC2086
      unset ANS_ROOT_DIR $__ans_zmienne __ans_zmienne
      unset -f __venv_deactivate deactivate
    fi
  }
fi
unset __venv_deactivate_src
ansible --version | head -1
