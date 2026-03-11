# Entre Vos Mains

Bootstrap local du module Odoo 19 `evm` sur le stack Docker partage.

## Prerequis

- Docker et `docker compose`
- `uv` disponible en local pour executer `uvx`
- Checkout Odoo local disponible dans `/home/mgeubelle/dev/odoo` pour consulter le code source Odoo et ses exemples si necessaire
- Stack local disponible dans `/home/mgeubelle/dev/odoo-scripts/local-setup-docker`
- Services existants: `db`, `odoo-19`, `nginx`

## Structure locale

- Module custom: `addons/evm`
- Stack Docker partage: `/home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml`
- Configuration Odoo du stack partage: `/home/mgeubelle/dev/odoo-scripts/local-setup-docker/odoo/odoo.conf`

## Bootstrap

1. Demarrer ou recharger le stack partage:

```bash
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml up -d
```

2. Initialiser la base de developpement `evm_dev` et installer `evm`:

```bash
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml \
  exec -T odoo-19 sh -lc \
  'odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo \
  -d evm_dev --http-port=8070 --stop-after-init -i base,web,evm --test-enable --test-tags /evm'
```

Cette commande:

- utilise le conteneur `db` du stack partage
- cree la base `evm_dev` si necessaire
- installe `base`, `web` et `evm`
- execute le test Odoo du module `evm`

## Demarrage quotidien

Mettre a jour le module sur la base `evm_dev`:

```bash
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml \
  exec -T odoo-19 sh -lc \
  'odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo \
  -d evm_dev --http-port=8070 --stop-after-init -u evm'
```

Important pour les tests manuels:

- apres chaque implementation de story, relancer au minimum cette commande d'upgrade avant de tester dans l'UI
- si la story ajoute ou modifie des modeles Python, des champs ou des vues techniques, redemarrer aussi le service `odoo-19` pour s'assurer que le serveur web actif utilise la version fraiche du code
- sans cette mise a jour, les tests manuels peuvent se faire sur une registry ou un processus web non rafraichi, avec des erreurs trompeuses du type `field is undefined`

Commande recommandee apres une story:

```bash
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml restart odoo-19
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml \
  exec -T odoo-19 sh -lc \
  'odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo \
  -d evm_dev --http-port=8070 --stop-after-init -u evm'
```

Commandes utiles:

```bash
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml ps
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml logs -f odoo-19
curl -I http://127.0.0.1/web/login
```

## Comptes de demo locaux

Le stack local partage charge les demo data Odoo pour `evm` car `without_demo = False` dans la configuration locale.
Sur une installation locale fraiche de `evm`, cela cree les comptes de demo suivants :

| Role | Login | Mot de passe |
|---|---|---|
| Kine | `kine@evm.com` | `odoo` |
| Patient | `patient@evm.com` | `odoo` |
| Fondation | `fondation@evm.com` | `odoo` |
| Admin | `admin@evm.com` | `odoo` |

Si la base locale a ete initialisee avant ce changement avec `without_demo = True`, Odoo garde la trace qu'`evm` a ete installe sans demo data. Le chemin le plus simple est alors de recreer la base locale puis de reinstalller `evm`.

## Pipeline qualite minimal

Commande unique:

```bash
make quality
```

Cette commande enchaine:

- `uvx --from 'ruff==0.11.0' ruff check addons/evm`
- un smoke test Odoo via le stack partage pour installer `evm` si `evm_dev` n'existe pas encore, sinon upgrader `evm` sur cette base

Commandes ciblees:

```bash
make quality-lint
make quality-smoke
```

Notes d'usage:

- `uvx` telecharge `ruff` a la premiere execution puis reutilise le cache local
- le smoke test reutilise `/home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml`
- tout echec de lint ou de smoke test fait echouer la commande avec un code de sortie non nul
- pour verifier un echec de lint, utiliser un fichier contenant volontairement un probleme simple, par exemple:

```bash
tmp="$(mktemp --suffix .py)"
printf 'import os\n' > "$tmp"
QUALITY_LINT_TARGET="$tmp" make quality-lint
rm -f "$tmp"
```

## Reset local

Supprimer seulement la base applicative de dev:

```bash
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml \
  exec -T db dropdb -U odoo evm_dev
```

Puis recreer:

```bash
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml \
  exec -T odoo-19 sh -lc \
  'odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo \
  -d evm_dev --http-port=8070 --stop-after-init -i base,web,evm --test-enable --test-tags /evm'
```

## Notes

- Le stack partage monte ce depot dans `odoo-19` via `/mnt/extra-addons/entre-vos-mains`.
- Le checkout local Odoo situe dans `/home/mgeubelle/dev/odoo` sert uniquement de reference source et d'exemples Odoo; il n'est pas utilise comme runtime ni comme cible d'implementation pour ce projet.
- L'`addons_path` du stack partage inclut `/mnt/extra-addons/entre-vos-mains`, ce qui rend `evm` installable sans runtime Odoo local dans ce repo.
- Le pipeline qualite du depot reste volontairement minimal: lint `ruff` cible sur `addons/evm` et smoke test Odoo sur le stack partage.
