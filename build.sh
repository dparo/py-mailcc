#!/usr/bin/env bash
# -*- coding: utf-8 -*-

set -eou pipefail

pandoc -f markdown -s --embed-resources main.md -o main.html

