# Story 4.2: Journaliser automatiquement les transitions metier importantes

Status: ready-for-dev

## Story

As a membre de la fondation,
I want que les changements importants soient traces automatiquement,
so that je puisse auditer les decisions et suivre l'historique d'un dossier sans ambiguite.

## Acceptance Criteria

1. **Given** une transition importante de dossier ou de demande
   **When** l'action metier est executee
   **Then** un message systeme est enregistre dans l'historique d'activite
   **And** les champs suivis pertinents conservent leur historique

2. **Given** une consultation ulterieure du dossier ou de la demande
   **When** un utilisateur autorise ouvre l'historique
   **Then** il peut comprendre les principales decisions et changements d'etat
   **And** les traces sont presentees de maniere lisible

## Tasks / Subtasks

- [ ] Identifier toutes les transitions metier a tracer sur `evm.case` et `evm.payment_request`
- [ ] Ajouter les messages systeme et le tracking des champs cles
- [ ] Uniformiser le format des traces pour les rendre lisibles
- [ ] Verifier la presence des traces sur les parcours critiques

## Dev Notes

- Dependances: stories metier qui introduisent les transitions.
- Les transitions majeures incluent au minimum: soumission, acceptation, refus, retour a completer, validation, paiement, cloture.
- Ne pas creer de table d'audit dediee tant que `mail.thread` couvre le besoin V1.

### Project Structure Notes

- Fichiers cibles: modeles `case.py` et `payment_request.py`.
- Centraliser l'ecriture des logs autour des methodes `action_*`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 4.2"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Audit Trail (V1)", "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR7", "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

