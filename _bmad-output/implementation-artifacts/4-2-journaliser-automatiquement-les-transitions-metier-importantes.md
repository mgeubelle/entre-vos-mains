# Story 4.2: Journaliser automatiquement les transitions metier importantes

Status: done

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

- [x] Identifier les transitions metier actuellement implementees a tracer sur `evm.case` et `evm.payment_request`
- [x] Ajouter les messages systeme et le tracking des champs cles
- [x] Uniformiser le format des traces pour les rendre lisibles
- [x] Verifier la presence des traces sur les parcours critiques

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

### Implementation Plan

- `evm.case`: tracer les transitions `create`, `action_submit_to_pending`, `action_accept`, `action_refuse`, l'activation d'acces patient, et la trace dossier emise lors du paiement confirme sur une demande.
- `evm.payment_request`: tracer `create`, `action_submit`, `action_return_to_complete`, `action_refuse`, `action_validate`, `action_confirm_external_payment`.
- Uniformiser les messages systeme via un prefixe lisible `Systeme:` en conservant `mail.thread` et le tracking natif Odoo pour l'audit V1.
- Completer le tracking sur les champs workflow manquants: `evm.case.name`, `evm.case.patient_user_id`, `evm.payment_request.payment_id`.

### Completion Notes List

- Transitions actuellement implementees couvertes et inventoriees sur `evm.case` et `evm.payment_request`; la cloture reste deferree aux stories 4.4 et 4.5 qui introduiront l'action metier correspondante.
- Ajout d'un helper `_post_system_message` sur les deux modeles pour imposer un format homogene `Systeme: ...` sur toutes les transitions metier deja implementees.
- Ajout du tracking sur `evm.case.name`, `evm.case.patient_user_id` et `evm.payment_request.payment_id`.
- Tests mis a jour pour verifier le prefixe systeme sur les parcours critiques dossier/demande et la declaration `tracking=True` sur les champs workflow ajoutes.
- Validation executee avec `make reload-evm`, `make quality-smoke` et `make quality-lint`.

## File List

- `_bmad-output/implementation-artifacts/4-2-journaliser-automatiquement-les-transitions-metier-importantes.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `addons/evm/models/evm_case.py`
- `addons/evm/models/evm_payment_request.py`
- `addons/evm/tests/test_case_consultation.py`
- `addons/evm/tests/test_case_review.py`
- `addons/evm/tests/test_patient_payment_request_portal.py`
- `addons/evm/tests/test_payment_request.py`

## Senior Developer Review (AI)

- Revue du `2026-03-18`: l'exposition des references internes `account.payment` dans l'historique public a ete corrigee avant validation.
- Risque residuel accepte: la couverture comportementale des champs tracked ajoutes (`evm.case.patient_user_id`, `evm.payment_request.payment_id`) reste plus faible que le reste du workflow, mais elle est jugee acceptable pour cette iteration.
- Risque residuel accepte: la cloture n'est pas couverte par cette story et reste explicitement reportee aux stories 4.4 et 4.5.
- Revue de cloture du `2026-03-19`: aucun finding supplementaire sur les traces systeme, la segregation public/interne ou le tracking workflow. Validation repo confirmee par `make quality-lint` et `make quality-smoke` ; le web tour E2E reste saute faute de Chrome, conformement au test summary existant.

## Change Log

- `2026-03-18`: uniformisation des traces systeme des transitions metier dossier/demande, ajout du tracking workflow manquant et couverture de test sur les parcours critiques.
- `2026-03-18`: revue finalisee avec correction de l'exposition des references de paiement cote portail et acceptation explicite des risques residuels restants.
- `2026-03-19`: cloture de la story apres revue finale sans finding supplementaire et validation lint/smoke verte.
