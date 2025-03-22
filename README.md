# README

## Setup

```sh
docker compose up
./setup.sh email add pepe@example.com password
./setup.sh email add fabrette@example.com password
./setup.sh email add penelope@example.com password
```

###  Setup Mutt Wizard

```sh
mw -a pepe@example.com -i 127.0.0.1 -I 143 -s localhost -S 587  -x "password" -f
mw -a fabrette@example.com -i 127.0.0.1 -I 143 -s localhost -S 587  -x "password" -f
mw -a penelope@example.com -i 127.0.0.1 -I 143 -s localhost -S 587  -x "password" -f
```
