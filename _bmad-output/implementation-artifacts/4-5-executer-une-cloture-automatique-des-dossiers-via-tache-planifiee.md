# Story 4.5: Executer une cloture automatique des dossiers via tache planifiee

Status: done

## Story

As a administrateur de la plateforme,
I want une tache planifiee qui applique les regles d'auto-cloture,
so that la plateforme reste propre operationnellement sans intervention manuelle systematique.

## Acceptance Criteria

1. **Given** des dossiers eligibles a l'auto-cloture existent
   **When** la tache planifiee s'execute
   **Then** seuls les dossiers qui respectent les regles definies sont clotures
   **And** chaque cloture automatique laisse une trace exploitable

2. **Given** un dossier non eligible
   **When** la tache planifiee l'evalue
   **Then** il n'est pas cloture par erreur
   **And** aucune regression n'est introduite sur les dossiers encore actifs

## Tasks / Subtasks

- [x] Ajouter la methode cron d'auto-cloture sur `evm.case`
- [x] Declarer la tache planifiee dans les donnees du module
- [x] Reutiliser la meme logique d'eligibilite que la cloture manuelle
- [x] Tracer les clotures automatiques et tester les faux positifs

## Dev Notes

- Dependances: Story 4.4.
- Le cron doit rester idempotent et sans effet sur les dossiers non eligibles.
- Pas de logique dupliquee entre action manuelle et automatique.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/evm_case.py`, `addons/evm/data/scheduled_actions.xml`.
- La planification doit rester compatible avec une exploitation Odoo standard.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 4.5"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Automation Boundary (Cron)", "Project Organization"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR7"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Implementation Plan

- Verifier l'implementation existante de la cloture automatique sur `addons/evm/models/evm_case.py` et la declaration cron sur `addons/evm/data/scheduled_actions.xml`.
- Valider que le cron reutilise strictement `_get_closure_eligibility()` et `_close_case()` pour eviter toute duplication entre cloture manuelle et automatique.
- Executer les tests cibles puis la suite qualite du module pour confirmer l'absence de faux positifs et la trace de l'origine automatique dans le chatter.

### Completion Notes List

- L'implementation story 4.5 etait deja presente dans le code: `_cron_auto_close_cases()` sur `evm.case`, cron `evm_ir_cron_auto_close_cases` et reutilisation de `_get_closure_eligibility()` / `_close_case()` sans duplication de logique.
- La declaration cron existante dans `addons/evm/data/scheduled_actions.xml` a ete revalidee pendant la revue et n'a pas necessite de correction applicative.
- La cloture automatique laisse une trace exploitable via `_build_closure_message(..., close_origin="automatic")`, avec mention explicite `automatiquement par la plateforme`.
- Correctifs de revue appliques sur `evm.case`: isolation des erreurs par dossier via `savepoint`/journalisation et restriction du cron aux candidats plausibles pour eviter un balayage complet des dossiers `accepted`.
- La couverture de test cron a ete etendue pour couvrir la cloture par quota de seances, le blocage par demande active et la poursuite du traitement apres echec isole d'un dossier.
- Validations executees: `make reload-evm`, `make quality-lint`, `./scripts/quality-check.sh smoke` (133 post-tests, 0 echec; 1 web tour ignore faute de Chrome).

## File List

- _bmad-output/implementation-artifacts/4-5-executer-une-cloture-automatique-des-dossiers-via-tache-planifiee.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- addons/evm/models/evm_case.py
- addons/evm/tests/test_case_review.py

## Senior Developer Review (AI)

- Revue du `2026-03-19`: le cron ne tolerait pas une erreur isolee et balayait tous les dossiers acceptes sans ciblage minimal, ce qui exposait la tache planifiee a des echecs globaux et a une degradation previsible.
- Correctifs appliques: isolation des erreurs dossier par dossier avec journalisation, reduction du perimetre du cron aux candidats plausibles, et ajout de tests sur les faux positifs et la resilience d'execution.
- Validation finale: `make reload-evm`, `make quality-lint`, `./scripts/quality-check.sh smoke` verts; le web tour reste ignore localement faute de Chrome.

## Change Log

- 2026-03-19: verification complete de l'implementation existante de la story 4.5, validation par tests Odoo et suite qualite, puis passage du story artifact en `review`.
- 2026-03-19: correctifs de revue sur la resilience du cron d'auto-cloture, son ciblage des candidats et l'extension de la couverture de tests associee.
- 2026-03-19: revue finalisee apres validations locales vertes et synchronisation du statut story vers `done`.
