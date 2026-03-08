# Story 3.4: Permettre a la fondation de refuser une demande de paiement

Status: ready-for-dev

## Story

As a membre de la fondation,
I want refuser une demande de paiement lorsqu'elle n'est pas recevable,
so that le workflow de la demande reste coherent et trace jusqu'a sa sortie finale.

## Acceptance Criteria

1. **Given** une demande en cours d'instruction
   **When** la fondation decide qu'elle ne peut pas etre acceptee
   **Then** elle peut la passer au statut `refused`
   **And** le motif du refus est enregistre de maniere exploitable

2. **Given** une demande refusee
   **When** son historique est consulte
   **Then** le statut final et son motif sont visibles
   **And** la demande n'apparait plus comme element a traiter dans la file active

## Tasks / Subtasks

- [ ] Ajouter le motif de refus et l'action de transition vers `refused`
- [ ] Retirer la demande refusee de la file active tout en la gardant consultable
- [ ] Afficher l'historique et le motif de facon lisible
- [ ] Verifier les restrictions sur les transitions ulterieures

## Dev Notes

- Dependances: Story 3.1.
- Un refus est un etat final metier; ne pas laisser une reprise implicite sans nouvelle regle explicite.
- Le motif doit etre presentable au patient/fondation selon les droits definis.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, vues fondation, vues de consultation.
- Garder des filtres clairs entre file active et historiques.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.4"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR9", "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

