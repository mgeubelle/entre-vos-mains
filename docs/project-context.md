# Project Context — Entre Vos Mains (Odoo 19)

## Contexte

- Ce dépôt contient des **add-ons Odoo 19 Community** (modules custom).
- L’UI reste **dans Odoo** (Website/Portal, QWeb/OWL si nécessaire). Un **site statique existant** sera intégré dans une page `website` en fin de projet.

## Dépendances & environnement local

- La codebase Odoo (serveur) est disponible localement dans `~/dev/odoo` (chemin attendu : `/home/mgeubelle/dev/odoo`) pour consultation du code source Odoo, lecture d'exemples et verification de patterns idiomatiques.
- Ce checkout Odoo local n'est pas une cible de deploiement pour ce projet et ne doit pas recevoir d'implementation specifique au module `evm`.
- Le runtime local du projet repose sur le stack partage `odoo-scripts/local-setup-docker`; les changements applicatifs se font uniquement dans ce depot d'add-ons.

## Principes d’architecture

- **Best practices Odoo 19**: architecture et patterns idiomatiques Odoo (modèles, vues, contrôleurs, sécurité, assets, etc.).
- **KISS**: préférer des solutions simples, lisibles et maintenables; éviter la sur-ingénierie.
- **Pragmatique**: minimiser les dépendances et la complexité tant que le besoin ne le justifie pas.
