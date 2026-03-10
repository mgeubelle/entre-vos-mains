# Story 2.5: Permettre au patient de soumettre une demande complete a la fondation

Status: done

## Story

As a patient,
I want soumettre ma demande de paiement complete,
so that la fondation puisse commencer son instruction.

## Acceptance Criteria

1. **Given** une demande de paiement complete avec ses pieces
   **When** le patient la soumet
   **Then** son statut passe a un etat de demande soumise
   **And** la fondation peut la retrouver dans son flux de traitement

2. **Given** une demande sans les elements requis
   **When** le patient tente de la soumettre
   **Then** la soumission est refusee
   **And** les erreurs sont presentees de facon simple et exploitable

## Tasks / Subtasks

- [x] Definir la condition de completude d'une demande en V1
- [x] Implementer l'action de soumission et le changement de statut
- [x] Rendre la demande visible dans le flux fondation de l'Epic 3
- [x] Tracer l'evenement et afficher des erreurs simples si la demande est incomplete

## Dev Notes

- Dependances: Stories 2.3 et 2.4.
- La condition de completude doit rester alignee sur les champs et pieces effectivement requis en V1; ne pas inventer des justificatifs supplementaires.
- Preparer l'integration avec les notifications de l'Epic 4 sans la rendre bloquante.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, vues/portail associees.
- La transition doit rester une methode `action_*` avec historique associe.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 2.5"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Workflow & Traceability Patterns", "Notifications (V1)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR8", "FR9", "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- V1 de completude definie sans sur-specification: `sessions_count > 0` et au moins un justificatif patient visible attache a la demande.
- Ajout de `action_submit`, du champ `submitted_on`, des messages d'historique et du blocage des soumissions incompletes avec erreurs simples en francais.
- Ajout du parcours portail patient de soumission et de la file fondation `submitted` via une vue liste/formulaire, action et menu dedies.
- Validations executees: `uvx --from 'ruff==0.11.0' ruff check addons/evm` puis `./scripts/quality-check.sh smoke` -> `0 failed, 0 error(s)`.

## File List

- addons/evm/__manifest__.py
- addons/evm/controllers/portal.py
- addons/evm/models/evm_payment_request.py
- addons/evm/tests/test_patient_payment_request_portal.py
- addons/evm/tests/test_payment_request.py
- addons/evm/views/evm_payment_request_views.xml
- addons/evm/views/portal_templates.xml

## Change Log

- 2026-03-10: implementation de la story 2.5 avec complétude V1, soumission patient, feedback portail et file fondation des demandes soumises.
- 2026-03-10: corrections post-review appliquees; workflow fondation durci, justificatifs exposes et rejeu de soumission portail couvert.
