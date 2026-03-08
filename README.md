# Entre Vos Mains

Bootstrap local du module Odoo 19 `evm` sur le stack Docker partage.

## Prerequis

- Docker et `docker compose`
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

Commandes utiles:

```bash
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml ps
docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml logs -f odoo-19
curl -I http://127.0.0.1/web/login
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
- Le pipeline qualite complet n'est pas installe dans cette story; seul le bootstrap local et le smoke test sont couverts ici.
