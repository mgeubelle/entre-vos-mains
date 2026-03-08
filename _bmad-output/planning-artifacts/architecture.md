---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/product-brief-dev-2026-03-07.md
  - analyse-projet.md
  - docs/project-context.md
workflowType: 'architecture'
project_name: 'dev'
user_name: 'Martin'
date: '2026-03-07T18:12:25+01:00'
lastStep: 8
status: 'complete'
completedAt: '2026-03-07T18:24:56+01:00'
---

# Architecture Decision Document

_Ce document se construit de façon collaborative, étape par étape. Les sections seront ajoutées au fur et à mesure que nous prendrons des décisions d’architecture._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
- Gestion de dossiers (cases) : création par kiné, statuts simples, consultation selon rôle, clôture automatique selon règles (délai / plafond).
- Portail patient : accès sécurisé après acceptation, consultation du dossier, dépôt de factures/justificatifs, création de demandes de paiement.
- Traitement fondation : validation de dossiers et demandes, commentaires/demandes d’infos, suivi manuel des séances consommées.
- Suivi paiements : paiement effectué hors plateforme, mais suivi et historique dans Odoo via le module Accounting (création d’`account.payment`).
- Gestion des accès : rôles (kiné, patient, membres fondation, admin) et permissions strictes.
- Communication asynchrone : notes/commentaires attachés au dossier (pas de chat temps réel).
- Notifications : évènements clés notifiés au patient et à la fondation (canal à préciser).

**Non-Functional Requirements:**
- Sécurité & conformité : GDPR + contexte belge, contrôle d’accès, traçabilité/audit trail.
- Accessibilité/UX : interface très simple, minimiser les clics, adaptée aux personnes âgées et déficiences motrices (niveau WCAG à fixer).
- Fiabilité & performance : réponses rapides sur actions usuelles, disponibilité élevée pendant heures ouvrées.
- Intégration : Odoo Community v19 + Accounting, échanges fiables et sécurisés, pas d’automatisation bancaire.
- Scalabilité : croissance du nombre d’utilisateurs sans dégradation perceptible.

**Scale & Complexity:**
- Primary domain: Odoo / web workflow + documents + comptabilité
- Complexity level: medium (fonctionnel) / high (transverse: sécurité, audit, fichiers, conformité)
- Estimated architectural components: ~7–9

### Technical Constraints & Dependencies

- Odoo 19 Community, application MPA, navigateurs majeurs, pas de SEO.
- Pas de temps réel requis.
- Paiement réalisé hors plateforme; enregistrement et historique dans Odoo (Accounting, `account.payment`).
- Données sensibles minimisées : factures comme principale preuve; pas de stockage structuré de données médicales; code INAMI possible uniquement dans le document.
- Rétention/suppression/anonymisation : non définies et hors scope V1.

### Cross-Cutting Concerns Identified

- RBAC fin + séparation stricte des vues/données par rôle.
- Stockage/accès documents (sécurité, droits, audit, intégrité, anti-fuite).
- Traçabilité/audit (actions, décisions, changements de statuts, validations, paiements).
- Conformité GDPR (minimisation, journalisation, base légale/consentements à clarifier plus tard).
- Accessibilité et UX “faible friction” (parcours courts, ergonomie, erreurs tolérantes).
- Gouvernance des plafonds (plafond annuel global, affichage d’aide à la décision, règles de clôture).
- Notifications (déclencheurs, destinataires, fiabilité).

## Starter Template Evaluation

### Primary Technology Domain

Add-ons Odoo 19 Community (Python) dans ce dépôt, avec UI via Website/Portal Odoo (QWeb/OWL si nécessaire). Pas de front séparé. Un site statique existant sera intégré dans une page `website` en fin de projet.

### Technical Preferences (Project Context)

- Codebase Odoo (serveur) disponible localement dans `~/dev/odoo` pour consultation du code source et exemples idiomatiques Odoo.
- Ce checkout local n'est pas une cible de deploiement du projet; le runtime local reste porte par le stack partage Docker.
- Architecture idiomatique Odoo 19, best practices, principe KISS.

### Starter Options Considered

1) **Vanilla Odoo (officiel) — `odoo-bin scaffold`**
- Génère un squelette minimal de module Odoo.
- Avantages : simple, officiel, peu intrusif, bon point de départ pour un module pragmatique.
- Implications : ne tranche pas pour vous l’outillage qualité (lint/tests/CI) ni la structuration “multi-addons” du repo.

2) **Conventions/outillage inspirés OCA (sans adopter un template complet)**
- Ajouter progressivement des outils (lint/format/tests/CI) et des conventions de repo pour la cohérence.
- Avantages : valeur élevée (qualité, homogénéité) avec un coût d’adoption maîtrisé.
- Implications : nécessite de décider explicitement les règles/outils retenus.

### Selected Starter: Vanilla Odoo scaffold + outillage qualité minimal (approche hybride)

**Rationale for Selection:**
- Démarrer vite sur une base officielle Odoo 19.
- Garder la solution lean (KISS), et n’ajouter de la structure/outillage que si ça apporte une valeur immédiate.

**Initialization Command (squelette du module):**
```bash
mkdir -p addons
/home/mgeubelle/dev/odoo/odoo-bin scaffold <nom_du_module> ./addons
```

Ce checkout Odoo local est utilise ici comme source d'outillage et de reference pour initialiser ou comparer du code Odoo standard, pas comme environnement d'execution du projet.

**Architectural Decisions Provided by Starter:**
- Squelette standard module Odoo (manifest, modèles, vues, sécurité de base, etc.).
- Aucune décision CI/qualité imposée (sera définie et ajoutée ensuite).

**Note:** L’initialisation du projet via ce scaffold devrait être la première story d’implémentation.

## Core Architectural Decisions (Draft)

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Stockage documents: `ir.attachment` + filestore local (Odoo standard).
- Modèle dossier: nouveau modèle dédié (ex: `evm.case`).
- Demandes de paiement: modèle métier dédié (ex: `evm.payment_request`) + création/liaison à `account.payment`.
- Séances: approche “facture-driven” via `sessions_count` par demande; pas de saisie séance-par-séance en V1.
- RBAC/Portail: séparation stricte des accès par rôle + record rules (à détailler section sécurité).

**Important Decisions (Shape Architecture):**
- Déclencheurs de notifications (à préciser) + canaux (email/Odoo).
- Audit trail: journaliser actions clés (statuts, validations, paiements, accès documents).
- Idempotence intégration compta: éviter les doublons de `account.payment` par demande.

**Deferred Decisions (Post-MVP):**
- Stockage externe pièces jointes (S3/MinIO) si besoin.
- Détail séance-par-séance (journal détaillé), OCR/parsing de facture.
- Politique de rétention/suppression/anonymisation automatisée (hors scope V1).

### Data Architecture

**Document Storage:**
- Standard Odoo `ir.attachment` + filestore local (par défaut).
- Les pièces jointes (factures/justificatifs) sont reliées aux demandes de paiement (`evm.payment_request`) en V1; une vue “Documents du dossier” agrège les pièces de toutes les demandes du dossier.

**Core Business Models (indicatif):**
- `evm.case` (dossier): statuts, liens patient/kiné/fondation, quotas séances, chatter pour échanges.
- `evm.payment_request` (demande): workflow (soumis / à compléter / validé / payé / refusé), montant, pièces jointes, `sessions_count`.

**Sessions Tracking (V1):**
- Champs au niveau dossier: `sessions_authorized`, `sessions_consumed`, reste calculé.
- `sessions_requested` est défini par le kiné lors de la création du dossier et représente le nombre maximum demandé pour ce dossier.
- `sessions_authorized` est fixé par la fondation lors de l'acceptation du dossier et ne peut pas dépasser `sessions_requested`.
- Chaque `evm.payment_request` porte `sessions_count`.
- Encodage: le patient propose `sessions_count`, la fondation valide avec possibilité d’override.
- La fondation dispose d'un plafond annuel global de séances couvertes, configurable dans l'application. Ce plafond s'applique à l'ensemble des dossiers et constitue une contrainte métier bloquante lors de l'acceptation des dossiers et du suivi de consommation.
- Pas de saisie séance-par-séance en V1 (pas de liste d’occurrences, pas de planning, pas d’automatisation).

**Document Upload Rules (V1):**
- Types autorisés: `pdf`, `jpg`, `jpeg`, `png`.
- Taille maximale: 10 Mo par fichier.
- Multi-fichiers: autorisé.
- Remplacement: pas d'écrasement en place en V1. Un nouveau fichier ajoute une nouvelle pièce jointe, afin de préserver l'historique documentaire et l'auditabilité.

**Accounting Integration (Odoo Accounting):**
- Création d’un `account.payment` (brouillon) lors du passage d’une demande au statut “validé (prêt à payer)”.
- Passage au statut “payé” après confirmation de paiement hors plateforme; le `account.payment` reste en brouillon et le posting est fait manuellement si nécessaire (V1).
- Lien explicite `evm.payment_request.payment_id -> account.payment` pour traçabilité.
- Stratégie d’idempotence: une demande validée ne doit créer qu’un seul paiement (contrainte applicative + vérifs).

### Authentication & Security

**Authentication (Portal Users):**
- Les kinésithérapeutes utilisent des comptes portail Odoo standard (login/mot de passe).
- Les patients utilisent des comptes portail Odoo standard (login/mot de passe).
- Le compte patient est créé uniquement après acceptation du dossier.
- Les membres de la fondation et les administrateurs utilisent des comptes internes Odoo.

**Authorization (RBAC):**
- Groupes Odoo + record rules strictes par modèle (`evm.case`, `evm.payment_request`, `ir.attachment`).
- Matrice d’accès:
  - Patient: uniquement ses dossiers + demandes associées + pièces jointes associées.
  - Kiné (portail): uniquement les dossiers qu’il a créés et leur suivi autorisé.
  - Fondation (interne): accès complet fonctionnel de validation.
  - Admin (interne): accès complet.

**Attachment Access Model (V1):**
- Pièces (factures/justificatifs) attachées aux `evm.payment_request` (KISS).
- Vue “Documents du dossier” agrège les pièces de toutes les demandes du dossier.

**Audit Trail (V1):**
- `mail.thread` + tracking sur champs clés + messages système sur transitions (soumis, à compléter, validé, payé, refusé).
- Pas de journal technique dédié en V1; ajouter `evm.audit_log` uniquement si une exigence d’audit non couverte apparaît (ex: téléchargements).

### API & Communication Patterns

**Notifications (V1):**
- Canaux: email + in-app (chatter/activités).
- Événements minimum: dossier accepté/refusé; demande soumise; demande à compléter; demande validée; demande payée.

**Accounting Integration (V1, Community-friendly):**
- Utiliser `account.payment` (modules `account` / `account_payment`, + `l10n_be`).
- Création du `account.payment` en brouillon à “validé (prêt à payer)”.
- Statut “payé” après confirmation de paiement hors plateforme; posting laissé manuel en V1.

**Idempotence (KISS):**
- Garde-fou applicatif uniquement: si `payment_id` existe sur la demande, ne jamais recréer.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
- Nommage (module, modèles, champs, `xml_id`) et stabilité des valeurs techniques (sélections).
- Structure de module (où placer modèles, vues, sécurité, données, contrôleurs, assets).
- Conventions XML (IDs, organisation des vues, actions, menus).
- Sécurité (groupes, ACL, record rules) et accès aux pièces jointes.
- Workflows (transitions, effets de bord, traçabilité chatter).
- Langue UI (FR) vs code (EN).

### Naming Patterns

**Module & XML IDs:**
- Préfixe unique `evm_` pour le module et tous les `xml_id`.
- Convention `xml_id`: `evm_<objet>_<type>_<nom>` (ex: `evm_case_view_form`, `evm_payment_request_action_submit`).

**Models & Fields:**
- Modèles en anglais, idiomatiques Odoo: ex `evm.case`, `evm.payment_request`.
- Champs en `snake_case` (ex: `sessions_count`, `payment_id`, `case_id`).
- Méthodes métier en anglais, préfixées `action_` pour transitions (ex: `action_submit`, `action_validate`, `action_mark_paid`).

**State/Selection Values:**
- Valeurs techniques stables en anglais (ex: `draft`, `submitted`, `to_complete`, `validated`, `paid`, `refused`, `closed`).
- Libellés affichés en français.

### Structure Patterns

**Project Organization (module Odoo):**
- Répertoires standard: `models/`, `views/`, `security/`, `data/`, `controllers/` (si portail), `static/src/` (si assets OWL).
- 1 fichier par modèle principal (ex: `models/case.py`, `models/payment_request.py`) pour éviter les “god files”.

**Security Files:**
- ACLs dans `security/ir.model.access.csv`.
- Record rules dans `security/*.xml`, groupées par modèle et rôle.

### UI Language Rule

- Tout ce qui est visible par l’utilisateur (labels de champs, titres, menus, aides, libellés de statuts, messages utilisateurs) doit être en **français**.
- Le code (identifiants techniques, noms de champs, noms de méthodes, valeurs de sélections) reste en **anglais**.

### XML & View Patterns

- `xml_id` uniques, préfixés `evm_`.
- Pas de logique métier dans les vues; privilégier méthodes Python et actions.
- Les messages et intitulés UI en français; éviter l’anglais dans `string=`, `help=`, labels.

### Workflow & Traceability Patterns

- Les transitions se font via méthodes `action_*` (une responsabilité par action).
- Chaque transition importante poste un message dans le chatter (traçabilité) + tracking sur champs clés.

### Attachment Access Pattern (V1)

- Pièces (factures/justificatifs) attachées aux `evm.payment_request`.
- La vue “Documents du dossier” agrège les pièces de toutes les demandes du dossier (liste/filtre).

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
entre-vos-mains/
├── README.md
├── analyse-projet.md
├── docs/
│   └── project-context.md
├── _bmad-output/
│   └── planning-artifacts/
│       ├── architecture.md
│       ├── prd.md
│       └── product-brief-dev-2026-03-07.md
└── addons/
    └── evm/                                  # module principal (MVP)
        ├── __init__.py
        ├── __manifest__.py
        ├── models/
        │   ├── __init__.py
        │   ├── case.py                        # evm.case
        │   └── payment_request.py             # evm.payment_request
        ├── security/
        │   ├── ir.model.access.csv
        │   ├── groups.xml
        │   └── rules.xml
        ├── views/
        │   ├── evm_case_views.xml
        │   ├── evm_payment_request_views.xml
        │   └── menus.xml
        ├── data/
        │   ├── mail_templates.xml             # emails FR
        │   └── scheduled_actions.xml          # cron auto-clôture (3 mois)
        ├── controllers/
        │   └── portal.py                      # si nécessaire (portail)
        └── templates/
            └── portal_templates.xml           # QWeb portail
```

### Requirements → Structure Mapping

- FR-001 Case management → `addons/evm/models/case.py`, `addons/evm/views/evm_case_views.xml`
- FR-002 Documents → `ir.attachment` liés à `evm.payment_request` + vues/portail (listing)
- FR-003 RBAC → `addons/evm/security/groups.xml`, `addons/evm/security/ir.model.access.csv`, `addons/evm/security/rules.xml`
- FR-004 Payment tracking → `addons/evm/models/payment_request.py` + intégration `account.payment`
- FR-005 Sessions tracking → champs dossier dans `case.py` + `sessions_count` dans `payment_request.py`
- FR-006 Accessibilité/UX → `templates/portal_templates.xml` + vues back-office simples
- FR-007 Sécurité/Compliance → record rules + chatter tracking + templates FR

### Architectural Boundaries

**Domain Boundaries (Odoo ORM):**
- `evm.case` = agrégat “dossier” (statuts, quotas séances, liens acteurs).
- `evm.payment_request` = agrégat “demande” (workflow, pièces jointes, `sessions_count`, lien `payment_id`).

**Integration Boundary (Accounting):**
- Création/liaison `account.payment` depuis `evm.payment_request` (draft) ; posting manuel si besoin.

**Automation Boundary (Cron):**
- Auto-clôture via cron (défini dans `data/scheduled_actions.xml`) appelant une méthode dédiée (ex: `evm.case._cron_auto_close_cases()`), sans logique dans les vues.

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
- Stack Odoo 19 Community + add-on `evm` + portail Odoo standard est cohérent avec les besoins MVP.
- Stockage documents via `ir.attachment` + filestore local est compatible avec une approche KISS.
- Intégration compta via `account.payment` en brouillon + posting manuel est cohérente avec “paiement hors plateforme”.

**Pattern Consistency:**
- Conventions `evm_` (module + `xml_id`) + valeurs techniques EN / UI FR évitent les conflits et restent idiomatiques Odoo.
- Workflows via `action_*` + chatter tracking = traçabilité homogène.

**Structure Alignment:**
- La structure `addons/evm/{models,views,security,data,controllers,templates}` supporte les décisions et frontières (ORM, portail, cron, compta).

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**
- FR-001..FR-005 couverts via `evm.case` et `evm.payment_request` + vues + cron + lien `account.payment`.
- FR-002 couvert via pièces jointes sur `evm.payment_request` + agrégation “Documents du dossier”.
- FR-006 couvert par choix portail simple + KISS, mais métriques d’accessibilité à préciser.
- FR-007 couvert via RBAC/record rules + minimisation données + chatter tracking.

**Non-Functional Requirements Coverage:**
- Sécurité/RBAC: adressé (groupes + ACL + record rules).
- Audit: adressé (chatter + tracking; audit technique dédié seulement si exigé).
- Accessibilité: intention adressée, mais niveau WCAG non défini (gap).
- Performance/fiabilité: aligné Odoo standard (pas de temps réel), à compléter par limites upload et volumétrie.

### Gap Analysis Results

**Important Gaps (à décider avant implémentation “portail”):**
- Accessibilité: fixer une cible mesurable (ex: WCAG 2.1 AA) ou critères concrets.

**Deferred / Out of Scope (V1):**
- Rétention/suppression/anonymisation automatisée (confirmé hors scope V1).
- OCR/parsing factures, séance-par-séance détaillée.
- Stockage externe (S3/MinIO).

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION (MVP)
