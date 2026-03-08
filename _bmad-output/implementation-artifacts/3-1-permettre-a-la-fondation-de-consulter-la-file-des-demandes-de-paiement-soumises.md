# Story 3.1: Permettre a la fondation de consulter la file des demandes de paiement soumises

Status: ready-for-dev

## Story

As a membre de la fondation,
I want voir les demandes de paiement a instruire et leurs informations essentielles,
so that je puisse traiter les dossiers en attente de maniere efficace.

## Acceptance Criteria

1. **Given** des demandes de paiement soumises existent
   **When** un membre de la fondation ouvre la vue de traitement
   **Then** il voit la liste des demandes pertinentes avec au minimum le dossier lie, le patient, la date de soumission, le statut, le montant demande s'il existe, et le nombre de seances declarees
   **And** il peut acceder au detail d'une demande autorisee

2. **Given** un utilisateur non autorise
   **When** il tente d'acceder a cette file de traitement
   **Then** l'acces est refuse
   **And** aucune donnee sensible n'est exposee

## Tasks / Subtasks

- [ ] Creer la vue liste/detail fondation sur `evm.payment_request`
- [ ] Afficher les colonnes metier minimums attendues
- [ ] Restreindre l'acces au role fondation/admin
- [ ] Verifier que seules les demandes soumises pertinentes apparaissent dans la file active

## Dev Notes

- Dependances: Epic 2 fonctionnel.
- Cette vue est la porte d'entree de l'instruction fondation; privilegier le tri et la lisibilite.
- Ne pas exposer d'informations non necessaires aux autres roles.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, `addons/evm/views/evm_payment_request_views.xml`, menus.
- Garder le filtrage principal par statut soumis et par role.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.1"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Core Business Models", "Authorization (RBAC)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR9"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

