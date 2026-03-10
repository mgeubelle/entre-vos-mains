# Story 2.3: Permettre au patient de creer une demande de paiement

Status: done

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

- [x] Creer le modele et workflow initial de `evm.payment_request`
- [x] Ajouter le formulaire portail de creation lie au dossier accepte
- [x] Valider les champs obligatoires, notamment `sessions_count`
- [x] Definir un statut initial clair et preparer la soumission ulterieure

## Dev Notes

- Dependances: Story 1.7.
- `sessions_count` est saisi par le patient puis pourra etre ajuste par la fondation en Epic 3.
- Le montant total reste facultatif en V1; ne pas imposer une regle metier absente du PRD.
- Cette story fournit le socle modele/workflow attendu par la story 2.1 pour afficher les demandes existantes dans le portail patient.

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

### Debug Log

- Rouge confirme le 2026-03-09 avec `make quality-smoke`: absence des routes portail patient et du workflow minimal `evm.payment_request`.
- Vert confirme le 2026-03-09 avec `make quality-lint` puis `make quality-smoke`.

### Completion Notes List

- Modele `evm.payment_request` complete avec workflow initial `draft -> submitted/to_complete/validated/paid/refused/closed`, `sessions_count`, `amount_total`, chatter et garde-fou sur l'ecriture directe du statut.
- Formulaire portail patient ajoute sur `/my/evm/cases/<case_id>/payment-requests/new`, reserve au patient du dossier accepte, avec POST securise et redirection de confirmation.
- Validation metier ajoutee pour `sessions_count` strictement positif et `amount_total` facultatif mais non negatif, avec messages d'erreur francais et preservation des donnees saisies.
- Couverture de tests ajoutee sur le modele, le portail patient et la non-regression securite; `make quality-lint` et `make quality-smoke` passent.

## File List

- addons/evm/controllers/portal.py
- addons/evm/models/evm_case.py
- addons/evm/models/evm_payment_request.py
- addons/evm/tests/__init__.py
- addons/evm/tests/test_patient_payment_request_portal.py
- addons/evm/tests/test_payment_request.py
- addons/evm/tests/test_security.py
- addons/evm/views/portal_templates.xml
- _bmad-output/implementation-artifacts/2-3-permettre-au-patient-de-creer-une-demande-de-paiement.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-03-09: implementation de la story 2.3 avec modele `evm.payment_request`, creation portail patient et validations associees.
- 2026-03-10: review cloturee apres revalidation `make quality-lint` et `make quality-smoke` sans echec.
