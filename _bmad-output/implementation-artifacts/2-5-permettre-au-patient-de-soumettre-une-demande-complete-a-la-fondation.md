# Story 2.5: Permettre au patient de soumettre une demande complete a la fondation

Status: ready-for-dev

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

- [ ] Definir la condition de completude d'une demande en V1
- [ ] Implementer l'action de soumission et le changement de statut
- [ ] Rendre la demande visible dans le flux fondation de l'Epic 3
- [ ] Tracer l'evenement et afficher des erreurs simples si la demande est incomplete

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

- Story prete pour execution par `dev-story`

