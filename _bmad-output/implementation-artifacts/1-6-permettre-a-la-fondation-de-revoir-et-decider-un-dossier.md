# Story 1.6: Permettre a la fondation de revoir et decider un dossier

Status: done

## Story

As a membre de la fondation,
I want examiner un dossier soumis et l'accepter ou le refuser,
so that les demandes legitimes puissent entrer dans le parcours de remboursement.

## Acceptance Criteria

1. **Given** un dossier soumis par un kinesitherapeute
   **When** un membre de la fondation le consulte
   **Then** il voit les informations necessaires a la decision
   **And** il peut accepter ou refuser le dossier via des actions metier explicites

2. **Given** un dossier que la fondation accepte
   **When** la decision est confirmee
   **Then** le dossier passe au statut `accepted`
   **And** le nombre de seances autorisees pour le dossier est fixe de maniere explicite

3. **Given** un dossier que la fondation accepte
   **When** la decision ferait depasser le plafond annuel configure de la fondation
   **Then** le systeme bloque l'acceptation
   **And** la fondation dispose de la visibilite necessaire sur le plafond annuel restant

4. **Given** un dossier que la fondation refuse
   **When** la decision est confirmee
   **Then** le dossier passe au statut `refused`
   **And** la decision reste tracable dans le dossier

5. **Given** une decision d'acceptation ou de refus
   **When** l'action est confirmee
   **Then** le statut du dossier est mis a jour correctement
   **And** une trace est enregistree dans l'historique d'activite

## Tasks / Subtasks

- [x] Ajouter la vue fondation de revue des dossiers soumis
- [x] Implementer les actions `action_accept` et `action_refuse` sur `evm.case`
- [x] Introduire la configuration et le controle du plafond annuel de seances
- [x] Tracer chaque decision dans l'historique et verifier les garde-fous de statut

## Dev Notes

- Dependances: Stories 1.1 a 1.5.
- `authorized_session_count` ne peut jamais depasser `requested_session_count`.
- La logique de plafond annuel est bloquante a l'acceptation; ne pas la reporter a une story ulterieure.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/case.py`, `addons/evm/views/evm_case_views.xml`, `addons/evm/data/` pour la configuration si necessaire.
- Garder les transitions centralisees dans le modele avec messages d'erreur explicites en francais.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 1.6"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Sessions Tracking", "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR5", "FR9"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Implementation Plan

- Centraliser les decisions fondation et les garde-fous de transition dans `evm.case`.
- Exposer une file de revue Odoo avec actions explicites, visibilite du plafond annuel et statut par dossier.
- Introduire un parametre `res.config.settings` pour le plafond annuel et couvrir le flux par tests Odoo.

### Debug Log

- 2026-03-08: suite rouge confirmee avec `make quality-smoke` apres ajout de `test_case_review.py`.
- 2026-03-08: correction du schema XML search view Odoo 19 et adaptation des assertions de vue a `arch_db`.
- 2026-03-08: validation finale via `uvx --from 'ruff==0.11.0' ruff check addons/evm`, `make quality-smoke`, puis `make quality`.

### Completion Notes List

- Vue fondation enrichie avec file de revue, filtres, boutons `Accepter` / `Refuser`, et visibilite du plafond annuel restant.
- `evm.case` couvre maintenant les transitions `pending -> accepted/refused`, la trace chatter, l'auteur/date de decision et le blocage des changements de statut hors actions metier.
- Le plafond annuel global de seances est configurable via `res.config.settings` avec controle bloquant a l'acceptation.
- Tests ajoutes pour les decisions fondation, le quota annuel, les garde-fous de statut, les vues de revue et la configuration.

## File List

- addons/evm/__manifest__.py
- addons/evm/models/__init__.py
- addons/evm/models/evm_case.py
- addons/evm/models/res_config_settings.py
- addons/evm/tests/__init__.py
- addons/evm/tests/test_case_review.py
- addons/evm/views/evm_case_views.xml
- addons/evm/views/res_config_settings_views.xml

## Change Log

- 2026-03-08: implementation complete de la revue fondation des dossiers, du plafond annuel configurable et des tests associes.
- 2026-03-08: code review adverse realisee; verrouillage des editions inutiles apres soumission/decision et simplification du message de decision.

## Senior Developer Review (AI)

### Outcome

Approved after fixes.

### Findings

- High: le formulaire de revue laissait encore modifier les informations soumises (`nom`, `kinesitherapeute`, `email`, `seances demandees`) apres envoi du dossier, ce qui ajoutait une capacite d'edition non demandee et affaiblissait la tracabilite. Corrige dans le modele et la vue.
- High: les champs de decision restaient modifiables apres acceptation/refus via `write()`, ce qui permettait d'alterer la decision sans repasser par une action metier ni produire une trace coherente. Corrige par des garde-fous ORM et des tests.
- Medium: la construction du message de decision dependait d'une comparaison sur un libelle traduit, ce qui etait inutilement fragile. Simplifiee avec un branchement sur la decision technique.

### Verification

- `uvx --from 'ruff==0.11.0' ruff check addons/evm`
- `make quality-smoke`
