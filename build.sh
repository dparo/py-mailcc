#!/usr/bin/env bash
# -*- coding: utf-8 -*-

set -eou pipefail


# Render Latex equations to SVG / PNG with webtex
pandoc --toc \
    -s \
    --embed-resources \
    --webtex='https://latex.codecogs.com/png.image?' \
    -V lang=it \
    --highlight-style=zenburn \
    --css styles.css \
    -f markdown+smart \
    --to=html5 \
    -o main.html \
    main.md

cat main.html | xclip -t text/html -selection clipboard -i

# Render Latex equations with mathml
# pandoc -f markdown -s --embed-resources main.md -o main.html --mathml

