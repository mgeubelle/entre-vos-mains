# Story 1.2: Mettre en place le pipeline qualite minimal

Status: ready-for-dev

## Story

As a developpeur du module EVM,
I want disposer d'un pipeline qualite local minimal,
so that je puisse verifier rapidement la sante du module avant toute implementation fonctionnelle.

## Acceptance Criteria

1. **Given** le depot du projet
   **When** le pipeline qualite minimal est configure
   **Then** les commandes de verification retenues pour le projet peuvent s'executer automatiquement
   **And** leur usage est documente pour l'equipe

2. **Given** une modification sur le module `evm`
   **When** l'equipe lance les controles locaux prevus
   **Then** elle peut verifier au minimum le linting ou les tests de base retenus
   **And** un echec de controle est visible avant fusion

## Tasks / Subtasks

- [ ] Definir le jeu minimal de controles pour le depot: lint Python cible sur `addons/evm` et smoke test d'installation ou d'upgrade du module `evm` (AC: 1, 2)
- [ ] Ajouter au repo les fichiers/outils strictement necessaires pour executer ces controles de facon reproductible, sans introduire une stack QA lourde (AC: 1, 2)
- [ ] Exposer une commande unique ou une sequence tres courte documentee dans `README.md` pour lancer le pipeline local (AC: 1)
- [ ] Verifier qu'un controle en echec remonte bien un code de sortie non nul et est observable avant fusion (AC: 2)

## Dev Notes

- Cette story est un enabling item technique bloquant avant le demarrage des stories fonctionnelles de l'Epic 1 puis des epics 2 a 4.
- Dependance directe: Story 1.1 terminee ou au moins executable localement.
- Recommandation KISS: partir de `ruff check` sur `addons/evm` et d'un smoke test d'installation Odoo plutot que d'une stack QA lourde.
- Ne pas introduire de CI distante obligatoire si le besoin n'est pas explicite; l'objectif minimum est d'avoir une verification locale claire.

### Technical Requirements

- Le pipeline doit s'executer uniquement depuis ce depot d'add-ons et cibler `addons/evm`.
- Le smoke test Odoo doit reutiliser le runtime local du stack partage `odoo-scripts/local-setup-docker` etabli par la Story 1.1.
- Le checkout `/home/mgeubelle/dev/odoo` reste une reference source Odoo et, si utile, une source d'exemples; il ne doit recevoir ni code projet ni installation specifique au pipeline qualite `evm`.
- Privilegier un outillage sobre et lisible, par exemple une configuration repo-locale (`pyproject.toml` ou equivalent) plus un point d'entree simple (`Makefile` ou script shell dedie).

### Architecture Compliance

- Respecter l'approche d'architecture hybride: module Odoo standard dans `addons/evm` et outillage qualite minimal ajoute progressivement.
- Ne pas etendre le scope vers les modeles metier, ACL, portail, accounting ou notifications. Cette story ne doit poser que le garde-fou qualite pour les stories suivantes.
- Les commandes de verification doivent etre compatibles avec l'organisation actuelle du projet: add-ons dans ce depot, runtime Odoo porte par le stack partage externe.

### File Structure Requirements

- Fichiers cibles probables: `README.md`, `pyproject.toml` ou configuration equivalente, `Makefile` et/ou `scripts/quality-check.sh`.
- Les scripts eventuels doivent rester explicites, deterministes et sans dependance cachee a un environnement non documente.
- La documentation `README.md` doit completer le bootstrap de la Story 1.1, pas le contredire.

### Testing Requirements

- Verifier au minimum:
  - qu'un controle de lint sur `addons/evm` peut etre lance localement
  - qu'un smoke test d'installation ou d'upgrade du module `evm` peut etre rejoue via le stack partage
  - qu'un echec de controle retourne un code de sortie non nul
  - qu'un developpeur peut lancer le pipeline avec une commande unique ou une sequence tres courte documentee

### Git Intelligence Summary

- Le depot applicatif reste tres minimal: module `addons/evm` bootstrappe, test d'installation Odoo present, aucun outillage qualite repo-local installe a ce stade.
- Consequence: cette story doit introduire le plus petit ensemble d'artefacts permettant un garde-fou local credible sans sur-ingenierie.

### Project Structure Notes

- Fichiers cibles probables: `README.md`, `pyproject.toml` ou config equivalente, scripts helper eventuels sous `scripts/`.
- Le pipeline doit pointer vers le module `addons/evm` et reutiliser l'environnement defini en Story 1.1.
- Le checkout `/home/mgeubelle/dev/odoo` peut servir de reference pour comprendre des patterns Odoo, mais il n'est ni une cible d'implementation ni un emplacement ou installer le pipeline qualite du projet.
- Le `README.md` documente aujourd'hui le bootstrap et le smoke test local; cette story doit etendre cette base avec la couche qualite minimale sans changer le runtime de reference.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 1.2"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Selected Starter", "Project Organization"]
- [Source: docs/project-context.md]
- [Source: README.md]
- [Source: _bmad-output/implementation-artifacts/1-1-initialiser-le-module-evm-et-l-environnement-local-docker.md]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`
- 2026-03-08: story revalidee apres clarification de contexte sur le checkout Odoo local et le runtime Docker partage.
