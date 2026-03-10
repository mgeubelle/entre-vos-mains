# Story 2.2: Permettre au patient de consulter l'espace documentaire de son dossier

Status: done

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

- [x] Ajouter la vue documentaire agregee depuis le dossier patient
- [x] Lister les `ir.attachment` lies aux `evm.payment_request` du dossier
- [x] Securiser la consultation et le telechargement des pieces
- [x] Verifier l'historique documentaire et la non-exposition des pieces d'autres dossiers

## Dev Notes

- Dependances: Stories 2.1, 2.3 et socle de securite des stories 1.x.
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

- Vue "Documents du dossier" ajoutee au detail dossier patient avec historique agrege sur toutes les `evm.payment_request` autorisees du dossier.
- Chargement serveur `sudo()` des `ir.attachment` binaires lies aux demandes du dossier, borne aux pieces explicitement visibles cote patient, avec pagination dediee et libelles de type lisibles.
- Controle d'acces `ir.attachment` remplace par une surcharge ciblee: un patient ne peut lire que les pieces `evm.payment_request` autorisees et marquees visibles pour le portail.
- Rendu portail durci pour masquer les pieces internes, exposer des libelles accessibles sur les liens de telechargement, et conserver un historique documentaire pagine.
- Tests portail HTTP ajoutes pour verifier le listing agrege, l'exclusion des pieces internes, la pagination documentaire et le refus `404` sur une piece d'un autre dossier.
- Tests securite ORM ajoutes pour verrouiller l'acces aux pieces via les droits du `evm.payment_request` rattache et la visibilite portail de l'attachement.

## File List

- addons/evm/controllers/portal.py
- addons/evm/models/__init__.py
- addons/evm/models/ir_attachment.py
- addons/evm/security/ir.model.access.csv
- addons/evm/tests/test_patient_payment_request_portal.py
- addons/evm/tests/test_security.py
- addons/evm/views/portal_templates.xml
- _bmad-output/implementation-artifacts/2-2-permettre-au-patient-de-consulter-l-espace-documentaire-de-son-dossier.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-03-10: ajout de l'espace documentaire agrege du dossier patient, securisation de l'acces `ir.attachment` et couverture de tests portail/securite.
- 2026-03-10: correction de review sur la portee de lecture `ir.attachment`, la pagination documentaire et l'accessibilite des actions de telechargement.
