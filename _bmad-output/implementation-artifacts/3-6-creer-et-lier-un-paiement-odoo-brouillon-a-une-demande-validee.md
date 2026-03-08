# Story 3.6: Creer et lier un paiement Odoo brouillon a une demande validee

Status: ready-for-dev

## Story

As a membre de la fondation,
I want qu'un `account.payment` brouillon soit cree pour une demande validee,
so that le suivi comptable du paiement soit assure dans Odoo.

## Acceptance Criteria

1. **Given** une demande validee sans paiement lie
   **When** la transition metier prevue est executee
   **Then** un `account.payment` brouillon est cree et lie a la demande
   **And** les informations necessaires a la tracabilite sont conservees

2. **Given** une demande possedant deja un `payment_id`
   **When** une nouvelle creation de paiement est tentee
   **Then** aucun doublon n'est cree
   **And** le garde-fou d'idempotence est respecte

## Tasks / Subtasks

- [ ] Ajouter le champ `payment_id` sur `evm.payment_request`
- [ ] Implementer la creation d'un `account.payment` brouillon lors de la validation prevue
- [ ] Assurer l'idempotence stricte si un paiement est deja lie
- [ ] Tracer la creation et rendre le lien visible pour la fondation

## Dev Notes

- Dependances: Story 3.5.
- Le paiement est cree en brouillon; le posting peut rester manuel en V1.
- L'integration doit soit creer exactement un paiement lie, soit echouer clairement sans doublon.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, dependances manifest vers `account` si necessaire, vues fondation.
- Ne pas introduire d'automatisation bancaire ni de flux comptable hors scope.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.6"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Accounting Integration (Odoo Accounting)", "Idempotence (KISS)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR4", "Non-Functional Requirements - Integration"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

