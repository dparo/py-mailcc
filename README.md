# README

## Setup

```sh
docker compose up
./setup.sh email add pepe@mail.example.com password
./setup.sh email add fabrette@mail.example.com password
./setup.sh email add penelope@mail.example.com password
```

###  Setup Mutt Wizard

```sh
mw -a fabrette@example.com -i localhost -I 143 -s localhost -S 587  -x "password" -f
```
