#!/usr/bin/env bash
# -*- coding: utf-8 -*-

set -eou pipefail


# Render Latex equations to SVG / PNG
# pandoc -f markdown -s --embed-resources main.md -o main.html --webtex='https://latex.codecogs.com/svg.image?'
pandoc -f markdown -s --embed-resources main.md -o main.html --webtex='https://latex.codecogs.com/png.image?'

# Render Latex equations with mathml
# pandoc -f markdown -s --embed-resources main.md -o main.html --mathml

