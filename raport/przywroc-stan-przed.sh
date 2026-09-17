#!/usr/bin/env bash
# Cofnięcie WSZYSTKICH zmian odtłuszczenia (2026-08-20) jednym poleceniem.
#
#   bash raport/przywroc-stan-przed.sh
#
# Przywraca całe repozytorium do stanu z commita 40dc877 (przed odtłuszczeniem)
# i usuwa pliki dodane później. Gałąź main nie jest w ogóle dotykana.

set -euo pipefail

BAZA="40dc87708158765315d339ef33a2c7c07666a74c"
cd "$(dirname "$0")/.."

echo "Przywracam stan z commita ${BAZA:0:7} (przed odtłuszczeniem)."
read -r -p "To usunie wszystkie niezapisane zmiany. Kontynuować? [t/N] " odp
case "$odp" in
  t|T|y|Y) ;;
  *) echo "Przerwano — nic nie zmieniono."; exit 1 ;;
esac

git reset --hard "$BAZA"
git clean -fd -- . ':!docs'

echo "Gotowe. Stan witryny jest taki, jak przed 20 sierpnia 2026 r."
echo "Aby usunąć także gałąź roboczą:  git checkout main && git branch -D odtluszczenie-2026-08"
