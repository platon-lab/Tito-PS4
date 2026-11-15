#!/bin/sh
# Пробует варианты вызова create-eboot, пока не получится fake SELF (eboot.bin).
# Успех = файл начинается с SELF-магии 4F 15 3D 1D.
TOOL="$1"
PAID=0x3800000000000011

is_self() {
  [ -s "$1" ] && [ "$(head -c 4 "$1" | od -An -tx1 | tr -d ' \n')" = "4f153d1d" ]
}

try() {
  echo ">>> $*"
  rm -f eboot.bin tito.oelf
  "$@" || echo "    (код выхода $?)"
  for f in eboot.bin tito.oelf; do
    if is_self "$f"; then
      cp "$f" eboot.bin
      echo "OK: $f — это SELF, кладу как eboot.bin"
      exit 0
    fi
  done
  echo "    SELF не получился"
}

try "$TOOL" -in tito.elf -out tito.oelf -ptype fake -paid $PAID
try "$TOOL" -in tito.elf -out tito.oelf -paid $PAID
try "$TOOL" -in tito.elf -out eboot.bin -ptype fake -paid $PAID
try "$TOOL" -in tito.elf -out eboot.bin -paid $PAID

echo "create-eboot не собрал SELF ни одним вариантом. Вывод выше."
exit 1
