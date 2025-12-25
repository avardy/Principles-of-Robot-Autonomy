#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  cat <<'USAGE'
Usage: ./compile_slides.sh <deck> [additional decks]
       ./compile_slides.sh clean [deck ...]
       ./compile_slides.sh clean-all [deck ...]

Without a mode, the script builds presentation PDFs and then reruns the
Makefile with HANDOUT=1 (which also creates quad-print variants). With
`clean` or `clean-all`, the corresponding Make targets are invoked, optionally
scoped to the provided deck list.

Examples:
  ./compile_slides.sh ch02
  ./compile_slides.sh ch01 ch05 ap01
  ./compile_slides.sh clean ch02
  ./compile_slides.sh clean-all
USAGE
  exit 1
fi

command="$1"
shift || true

if [[ "$command" == "clean" || "$command" == "clean-all" ]]; then
  slides="$*"
  if [[ -n "$slides" ]]; then
    echo "Running make $command for: $slides"
    make -C slides "$command" SLIDES="$slides"
  else
    echo "Running make $command for all decks"
    make -C slides "$command"
  fi
  exit 0
fi

SLIDES="$command"
if [[ $# -gt 0 ]]; then
  SLIDES="$SLIDES $*"
fi

echo "Building presentation deck(s): $SLIDES"
make -C slides SLIDES="$SLIDES"

echo

echo "Building handout deck(s): $SLIDES"
make -C slides HANDOUT=1 SLIDES="$SLIDES"
