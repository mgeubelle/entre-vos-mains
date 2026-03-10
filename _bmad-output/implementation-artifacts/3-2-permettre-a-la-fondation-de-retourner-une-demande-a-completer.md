# Story 3.2: Permettre a la fondation de retourner une demande a completer

Status: done

## Story

As a membre de la fondation,
I want renvoyer une demande incomplete au patient avec un motif clair,
so that le patient puisse fournir les informations ou justificatifs manquants.

## Acceptance Criteria

1. **Given** une demande en cours d'instruction
   **When** la fondation estime qu'elle est incomplete
   **Then** elle peut la passer au statut `to_complete`
   **And** un motif exploitable est enregistre pour le patient

2. **Given** une demande retournee a completer
   **When** son historique est consulte
   **Then** la transition et son motif sont tracables
   **And** la demande peut etre reprise plus tard apres complementation

## Tasks / Subtasks

- [x] Ajouter le champ ou mecanisme de motif de retour
- [x] Implementer l'action metier vers `to_complete`
- [x] Rendre le motif visible au patient sur le portail
- [x] Tracer la transition dans l'historique et tester la reprise ulterieure

## Dev Notes

- Dependances: Story 3.1.
- Le motif doit etre exploitable par le patient; eviter les formulations internes opaques.
- La demande doit rester dans un workflow coherent, sans creation de doublon.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, vues fondation et portail patient.
- Les transitions se font via methode `action_*` avec controle de statut entrant.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.2"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR9", "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log

- `./scripts/quality-check.sh smoke` -> OK
- `./scripts/quality-check.sh lint` -> OK

### Completion Notes List

- Ajout du champ `completion_request_reason` protege par workflow et trace dans le chatter.
- Ajout de l'action metier `action_return_to_complete` avec controles de role, statut entrant et motif obligatoire.
- Simplification UX: suppression du wizard au profit d'une saisie inline du motif sur la vue formulaire, avec bouton metier dedie.
- Affichage du motif de retour sur le portail patient pour les demandes `to_complete`.
- Correction du cycle de reprise patient: une demande `to_complete` peut a nouveau etre completee, enrichie en justificatifs puis resoumise a la fondation.
- La file fondation conserve un filtre par defaut sur les demandes soumises sans masquer le statut `to_complete`.
- Ajout de tests modele, securite, vues et portail couvrant la transition, la saisie inline, la reprise ulterieure et la visibilite patient.

## File List

- `addons/evm/controllers/portal.py`
- `addons/evm/models/evm_payment_request.py`
- `addons/evm/tests/test_patient_payment_request_portal.py`
- `addons/evm/tests/test_payment_request.py`
- `addons/evm/tests/test_security.py`
- `addons/evm/views/evm_payment_request_views.xml`
- `addons/evm/views/portal_templates.xml`

## Change Log

- 2026-03-10: implementation completee pour le retour a completer des demandes de paiement cote fondation, avec saisie inline du motif, visibilite portail et couverture de tests associee.
- 2026-03-10: correctifs post-review sur la reprise patient d'une demande `to_complete`, la visibilite du statut cote fondation et la mise a jour de la couverture de tests.
- 2026-03-10: review finale approuvee apres correction des regressions de workflow et verification complete du module.

## Senior Developer Review (AI)

### Reviewer

Martin

### Outcome

Approve

### Summary

- Les regressions de review ont ete corrigees: le patient peut reprendre une demande `to_complete`, la file fondation n'occulte plus ce statut et la traçabilite reste intacte.
- La story et son `File List` reflettent maintenant les fichiers reellement touches.

### Validation

- `./scripts/quality-check.sh lint` -> OK
- `./scripts/quality-check.sh smoke` -> OK
