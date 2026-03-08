# Story 2.3: Permettre au patient de creer une demande de paiement

Status: ready-for-dev

## Story

As a patient,
I want creer une demande de paiement associee a mon dossier,
so that je puisse solliciter un remboursement sur base de mes justificatifs.

## Acceptance Criteria

1. **Given** un dossier accepte et accessible par le patient
   **When** il cree une nouvelle demande de paiement
   **Then** il peut encoder les informations minimales requises, y compris le nombre de seances concernees
   **And** il peut renseigner un montant total a payer lorsque cette information est disponible sans le rendre obligatoire en V1
   **And** la demande est enregistree avec un statut initial explicite

2. **Given** une demande incomplete
   **When** le patient tente de la soumettre
   **Then** le systeme bloque la soumission
   **And** indique clairement les informations manquantes

## Tasks / Subtasks

- [ ] Creer le modele et workflow initial de `evm.payment_request`
- [ ] Ajouter le formulaire portail de creation lie au dossier accepte
- [ ] Valider les champs obligatoires, notamment `sessions_count`
- [ ] Definir un statut initial clair et preparer la soumission ulterieure

## Dev Notes

- Dependances: Stories 1.7, 2.1 et 2.2.
- `sessions_count` est saisi par le patient puis pourra etre ajuste par la fondation en Epic 3.
- Le montant total reste facultatif en V1; ne pas imposer une regle metier absente du PRD.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, vues/portail associees, menus si necessaires.
- Le lien technique attendu est `case_id` sur la demande.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 2.3"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Core Business Models", "Sessions Tracking (V1)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR4", "FR5", "FR8"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

