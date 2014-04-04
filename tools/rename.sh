#!/bin/bash

for f in $1/*; do
    movie=$(basename "$f")
    nfile=$(python tools/gylfie -t "$movie" -P --language=en -a1 -p tmdbmovie);
    mv -v "$f" "$1/$nfile";
done
