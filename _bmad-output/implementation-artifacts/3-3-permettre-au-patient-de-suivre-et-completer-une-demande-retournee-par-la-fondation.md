# Story 3.3: Permettre au patient de suivre et completer une demande retournee par la fondation

Status: ready-for-dev

## Story

As a patient,
I want voir si ma demande doit etre completee,
so that je puisse fournir rapidement les informations ou documents manquants.

## Acceptance Criteria

1. **Given** une demande renvoyee a completer par la fondation
   **When** le patient consulte le portail
   **Then** il voit clairement que la demande requiert une action
   **And** il peut identifier les informations ou documents attendus

2. **Given** une demande a completer
   **When** le patient ajoute les elements manquants et la renvoie
   **Then** la demande repasse dans un etat permettant une nouvelle revue
   **And** l'historique de l'echange reste tracable

## Tasks / Subtasks

- [ ] Mettre en avant l'etat `to_complete` et son motif cote patient
- [ ] Autoriser l'ajout des elements manquants sur la demande existante
- [ ] Implementer la re-soumission vers un etat de revue
- [ ] Verifier la conservation de l'historique et des pieces deja presentes

## Dev Notes

- Dependances: Story 3.2.
- Le patient ne doit pas recreer une nouvelle demande si une completion suffit.
- Conserver le maximum de contexte visible pour eviter les allers-retours inutiles.

### Project Structure Notes

- Fichiers cibles: portail patient, `payment_request.py`, templates associes.
- Les pieces jointes existantes restent historisees; ne pas supprimer l'ancien contexte.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.3"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Document Upload Rules (V1)", "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR2", "FR8", "FR9"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

