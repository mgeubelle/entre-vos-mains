# Story 1.1: Initialiser le module EVM et l'environnement local Docker

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developpeur du module EVM,
I want disposer d'un socle Odoo 19 local executable avec le module `evm` bootstrappe,
so that je puisse implementer les stories fonctionnelles suivantes sur une base reproductible et installable.

## Acceptance Criteria

1. **Given** un poste de developpement avec Docker  
   **When** je demarre l'environnement local  
   **Then** une instance Odoo 19 avec la base de developpement demarre correctement  
   **And** le module `evm` peut etre installe sans erreur

2. **Given** le depot du projet  
   **When** je consulte le module `evm`  
   **Then** sa structure suit les conventions Odoo retenues dans l'architecture  
   **And** le chargement local permet de verifier que le socle est pret pour les stories suivantes

## Tasks / Subtasks

- [x] Scaffold du module `evm` dans le depot (AC: 1, 2)
  - [x] Creer le repertoire `addons/` s'il n'existe pas et generer le squelette via `/home/mgeubelle/dev/odoo/odoo-bin scaffold evm ./addons`
  - [x] Conserver un module minimal, installable et idiomatique Odoo 19, sans introduire de logique metier anticipee sur les stories suivantes
  - [x] Verifier que les fichiers de base du module sont coherents avec les conventions du projet: identifiants techniques en anglais, futur prefixe `evm_` pour les `xml_id`, structure standard Odoo

- [x] Mettre en place l'environnement local Docker minimal (AC: 1)
  - [x] S'appuyer sur le stack Docker partage `local-setup-docker` pour fournir PostgreSQL et les services locaux necessaires au bootstrap
  - [x] Utiliser la syntaxe `docker compose` v2 avec la configuration du stack partage existant
  - [x] Verifier que la configuration Odoo du stack partage charge bien `./addons` du depot en plus des addons core Odoo

- [x] Fournir une commande de demarrage locale reproductible (AC: 1)
  - [x] Standardiser la commande de lancement Odoo via le service `odoo-19` du stack partage
  - [x] Fixer un nom de base de developpement explicite, par exemple `evm_dev`
  - [x] Verifier qu'un developpeur disposant du stack partage peut lancer la base, demarrer Odoo, puis installer `evm` sans adaptation manuelle supplementaire dans ce depot

- [x] Realiser le smoke test de bootstrap (AC: 1, 2)
  - [x] Demarrer PostgreSQL et Odoo via le stack partage `local-setup-docker`
  - [x] Lancer Odoo 19 avec la configuration du stack partage et installer le module `evm`
  - [x] Capturer les signaux de succes minimums: service PostgreSQL sain, serveur Odoo demarre, installation du module sans traceback bloquant

- [x] Documenter le demarrage pour les stories suivantes (AC: 2)
  - [x] Mettre a jour `README.md` avec les prerequis, commandes de bootstrap, demarrage, arret et reset local
  - [x] Documenter explicitement que le checkout local Odoo `/home/mgeubelle/dev/odoo` est une reference source seulement, pas le runtime du projet
  - [x] Ne pas embarquer dans cette story le pipeline qualite complet, reserve a la Story 1.2

## Dev Notes

- Cette story est un enabling item bloquant pour tout l'Epic 1 et, par extension, pour les epics fonctionnels 2 a 4.
- Le depot applicatif est actuellement quasi vide cote code. Il faut donc produire un bootstrap greenfield pragmatique, sans sur-ingenierie.
- L'architecture impose un module principal `addons/evm` dans une application Odoo MPA, sans front separe.
- L'objectif de cette story est l'executabilite et la reproductibilite locale, pas la mise en place complete du pipeline qualite ni des modeles metier.

### Technical Requirements

- Utiliser le scaffold officiel Odoo depuis le checkout local existant: `/home/mgeubelle/dev/odoo/odoo-bin scaffold evm ./addons`.
- Garder la structure du module simple et proche du scaffold officiel; supprimer ou ajuster uniquement ce qui empeche l'installation ou contredit l'architecture cible.
- Utiliser le checkout local Odoo comme reference source et, si utile, comme outillage ponctuel pour le scaffold; ne rien implementer dans ce checkout et ne pas l'utiliser comme runtime du projet.
- La configuration locale retenue via le stack partage doit permettre de charger les addons core Odoo plus le repertoire du depot `./addons` sans manipulation manuelle opaque.
- Les commandes de demarrage doivent etre deterministes et reutilisables par la Story 1.2 pour brancher ensuite le pipeline qualite.

### Architecture Compliance

- Respecter la structure cible definie dans l'architecture: `addons/evm/` comme module principal du MVP. Ne pas creer de multi-module premature.
- Respecter la regle "code en anglais / UI en francais". Pour cette story, privilegier les identifiants techniques anglais et des messages utilisateur francais seulement si necessaires au bootstrap.
- Respecter les conventions Odoo: fichiers standard (`__manifest__.py`, `__init__.py`, sous-repertoires standards), pas de logique metier dans les vues, pas de surcouche technique non justifiee.
- Ne pas pre-creer les modeles `evm.case` et `evm.payment_request` ici sauf si le scaffold ajoute des placeholders minimaux; ces objets seront traites dans les stories metier ulterieures.

### Library / Framework Requirements

- Base applicative: Odoo Community 19.
- Reference source Odoo: checkout disponible sous `/home/mgeubelle/dev/odoo` pour lecture du code et exemples uniquement.
- Base de donnees locale: PostgreSQL sous Docker, version compatible Odoo 19 (les prerequis Odoo source indiquent PostgreSQL 13+).
- Orchestration locale: Docker Compose v2 via `docker compose`, en s'appuyant sur le stack partage `local-setup-docker`.
- Eviter d'introduire des dependances Python ou des outils de qualite supplementaires dans cette story tant qu'ils ne sont pas necessaires au bootstrap.

### File Structure Requirements

- Fichiers a creer ou mettre a jour attendus:
  - `addons/evm/**` issus du scaffold officiel et normalises si besoin
  - `README.md` pour le demarrage du projet
- Le runtime Odoo/PostgreSQL est fourni par le stack partage `local-setup-docker`; ce depot doit rester lisible et documenter clairement cette dependance.
- Si un script helper est ajoute, le placer dans un emplacement explicite et sobre, par exemple `scripts/`, avec une responsabilite claire.

### Testing Requirements

- Le minimum requis dans cette story est un smoke test d'installation local, pas une suite de tests automatisee complete.
- Verifier au minimum:
  - que PostgreSQL demarre et devient healthy
  - qu'Odoo peut se connecter a la base de dev cible
  - que `evm` s'installe sans erreur bloquante
  - que le module reste reinstallable ou upgradable sans bricolage manuel evident
- Reporter les commandes exactes de verification dans le `README.md` afin que la Story 1.2 puisse s'appuyer sur une base claire.

### Git Intelligence Summary

- Historique git disponible: seulement deux commits, orientes documentation et cadrage (`first commit`, puis ajout des artefacts de planification).
- Aucun pattern d'implementation applicative n'existe encore dans ce depot. Les documents de planification et le scaffold officiel Odoo sont donc les seules sources de verite pour cette story.
- Consequence: privilegier des choix simples, standards et faciles a revoir plutot qu'une structure speculative.

### Latest Tech Information

- La CLI Odoo 19 documente toujours la commande `scaffold`, ce qui confirme que le bootstrap du module doit partir du generateur officiel plutot que d'une structure recomposee a la main.
- La meme reference CLI documente `--addons-path`; la configuration locale doit donc rendre explicite le chargement des addons core Odoo et du repertoire `./addons` du projet.
- La documentation Odoo 19 d'installation depuis les sources indique Python 3.10+ et PostgreSQL 13+; eviter toute hypothese plus ancienne dans la configuration locale.
- L'image Docker officielle Odoo 19 existe et suppose un serveur PostgreSQL distinct. Meme si Odoo est lance ici depuis le checkout local pour rester simple, la topologie cible reste bien separee entre application et base.
- La documentation Docker Compose indique que le champ top-level `version` est obsolete et que l'ordre de demarrage robuste passe par un healthcheck plus `depends_on: condition: service_healthy` lorsque necessaire.

### Project Structure Notes

- Le contexte projet confirme que ce depot ne contient que des add-ons Odoo 19 Community. Toute UI doit rester dans Odoo, sans front separe.
- Le choix le plus coherent avec l'architecture est donc: scaffold officiel du module dans ce depot, base PostgreSQL conteneurisee via le stack partage, et usage du checkout `/home/mgeubelle/dev/odoo` comme reference source uniquement.
- Pour ce projet, l'execution locale passe concretement par le stack partage `local-setup-docker`, qui embarque deja le runtime Odoo necessaire au bootstrap.
- Pour ce projet, l'execution locale passe concretement par le stack partage `local-setup-docker`; aucun code ne doit etre implemente dans `/home/mgeubelle/dev/odoo`.
- Cette story ne doit pas deriver vers les roles, ACL, modeles metier, portail patient, accounting ou notifications. Ces sujets sont couverts par les stories suivantes.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Implementation Prerequisites", "Story 1.1"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Selected Starter", "Project Organization", "Naming Patterns", "Architecture Readiness Assessment"]
- [Source: _bmad-output/planning-artifacts/prd.md - "Project-Type Requirements", "Minimal UX Guardrails For MVP", "Non-Functional Requirements"]
- [Source: docs/project-context.md]
- [Source externe: Odoo 19 CLI reference](https://www.odoo.com/documentation/19.0/developer/reference/cli.html)
- [Source externe: Odoo 19 source installation](https://www.odoo.com/documentation/19.0/administration/on_premise/source.html)
- [Source externe: Docker Compose version and name reference](https://docs.docker.com/reference/compose-file/version-and-name/)
- [Source externe: Docker Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/)
- [Source externe: Official Odoo Docker image](https://hub.docker.com/_/odoo)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Story creee a partir des artefacts BMAD de planification et du statut de sprint.
- Aucun precedent fichier de story implemente pour l'Epic 1 n'etait disponible.
- Scaffold execute via `/home/mgeubelle/dev/odoo/odoo18-venv/bin/python /home/mgeubelle/dev/odoo/odoo-bin scaffold evm ./addons`, uniquement pour initialiser le squelette du module.
- Stack externe configure via `/home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml` et `/home/mgeubelle/dev/odoo-scripts/local-setup-docker/odoo/odoo.conf`.
- Smoke test execute dans `odoo-19` via `odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8070 --stop-after-init -i base,web,evm --test-enable --test-tags /evm`.

### Implementation Plan

- Conserver un module `addons/evm` minimal et installable, sans modeles metier anticipes.
- Monter `addons/` du depot dans le conteneur `odoo-19` du stack partage.
- Porter la verification locale sur le stack `db` + `odoo-19` + `nginx` deja present, sans runtime Odoo local dans ce repo.

### Completion Notes List

- Module `addons/evm` scaffolded puis reduit a un socle Odoo 19 minimal avec manifest normalise et test d'installation Odoo.
- Stack partage `local-setup-docker` reconfigure pour monter `addons/` du depot dans `/mnt/extra-addons/entre-vos-mains` et exposer ce chemin dans `addons_path`.
- Validation reussie sur le stack externe: creation de `evm_dev`, installation initiale `base,web,evm`, upgrade `evm` rejouable, verification HTTP via `http://127.0.0.1/web/login`.
- Cleanup effectue: suppression du `compose.yaml`, du `odoo.conf`, des scripts de runtime local et du volume PostgreSQL local provisoire crees dans ce depot.
- README mis a jour pour documenter uniquement le bootstrap sur le stack partage, sans embarquer le pipeline qualite de la Story 1.2.

### File List

- `.gitignore`
- `README.md`
- `addons/evm/__manifest__.py`
- `addons/evm/__init__.py`
- `addons/evm/controllers/__init__.py`
- `addons/evm/controllers/controllers.py` (deleted)
- `addons/evm/demo/demo.xml` (deleted)
- `addons/evm/models/__init__.py`
- `addons/evm/models/models.py` (deleted)
- `addons/evm/security/ir.model.access.csv` (deleted)
- `addons/evm/tests/__init__.py`
- `addons/evm/tests/test_install.py`
- `addons/evm/views/templates.xml` (deleted)
- `addons/evm/views/views.xml` (deleted)

### Change Log

- 2026-03-08: bootstrap initial du module `evm`, puis bascule vers le stack Docker partage `local-setup-docker` avec cleanup complet du runtime local provisoire.
- 2026-03-08: alignement de la story de review avec le choix du stack partage et exclusion des artefacts Python locaux via `.gitignore`.
- 2026-03-08: clarification documentaire: le checkout `/home/mgeubelle/dev/odoo` sert de reference source Odoo uniquement et n'est pas une cible de deploiement ou d'implementation.
