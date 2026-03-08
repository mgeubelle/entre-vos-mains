# Story 3.7: Permettre a la fondation de confirmer un paiement effectue hors-plateforme

Status: ready-for-dev

## Story

As a membre de la fondation,
I want marquer une demande comme payee apres confirmation du paiement externe,
so that le dossier reflete correctement l'etat reel du remboursement.

## Acceptance Criteria

1. **Given** une demande avec un paiement Odoo lie
   **When** la fondation confirme que le paiement a ete effectue hors plateforme
   **Then** la demande passe au statut `paid`
   **And** la trace de confirmation est conservee dans le dossier

2. **Given** une demande non validee ou sans paiement lie
   **When** un utilisateur tente de la marquer comme payee
   **Then** l'action est refusee
   **And** un message clair explique pourquoi

## Tasks / Subtasks

- [ ] Implementer l'action de confirmation de paiement externe
- [ ] Verifier les preconditions: demande validee et `payment_id` present
- [ ] Passer la demande a `paid` et journaliser la confirmation
- [ ] Tester les refus de transition sur demandes non eligibles

## Dev Notes

- Dependances: Story 3.6.
- Le statut `paid` represente une confirmation metier, pas une automatisation bancaire.
- Preserver une trace lisible pour audit et suivi patient/fondation.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, vues de traitement fondation.
- Garder la logique simple: pas de webhook, pas d'integration bancaire supplementaire.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.7"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Accounting Integration (V1, Community-friendly)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR4", "FR9", "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

