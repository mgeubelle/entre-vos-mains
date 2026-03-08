# Story 2.2: Permettre au patient de consulter l'espace documentaire de son dossier

Status: ready-for-dev

## Story

As a patient,
I want acceder a l'espace documentaire de mon dossier,
so that je puisse retrouver les pieces deja partagees en toute securite.

## Acceptance Criteria

1. **Given** un patient connecte sur son dossier
   **When** il ouvre l'espace documentaire
   **Then** il voit les documents associes a ses demandes de paiement
   **And** l'historique documentaire reste consultable de maniere simple et securisee

2. **Given** un document rattache a une demande de paiement
   **When** le patient consulte le dossier
   **Then** le document apparait dans la vue agregee du dossier
   **And** un utilisateur non autorise ne peut ni le voir ni y acceder

## Tasks / Subtasks

- [ ] Ajouter la vue documentaire agregee depuis le dossier patient
- [ ] Lister les `ir.attachment` lies aux `evm.payment_request` du dossier
- [ ] Securiser la consultation et le telechargement des pieces
- [ ] Verifier l'historique documentaire et la non-exposition des pieces d'autres dossiers

## Dev Notes

- Dependances: Stories 2.1 et socle de securite des stories 1.x.
- L'architecture impose une attache des documents sur `evm.payment_request`, pas directement sur `evm.case`.
- Le dossier doit seulement agreger les pieces des demandes autorisees.

### Project Structure Notes

- Fichiers cibles: `addons/evm/controllers/portal.py`, `addons/evm/templates/portal_templates.xml`, logiques d'acces aux attachments.
- Les permissions sur `ir.attachment` doivent suivre les record rules metier.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 2.2"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Document Storage", "Attachment Access Model (V1)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR2", "FR8"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

