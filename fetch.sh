#! /bin/bash

for yyyy in "$@"; do
  mkdir -p html/$yyyy
  for xxxxx in `seq -w 24000`; do
    detail="detail?id=${yyyy}P${xxxxx}"
    if [ ! -f "html/$yyyy/$detail" ]; then
      wget -P "html/$yyyy" "https://www.tweedekamer.nl/kamerstukken/stemmingsuitslagen/$detail"
      echo "sleeping half a second"
      sleep .5
    fi
  done
done
