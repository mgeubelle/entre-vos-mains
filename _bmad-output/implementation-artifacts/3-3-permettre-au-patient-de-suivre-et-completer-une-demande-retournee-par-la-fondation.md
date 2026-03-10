# Story 3.3: Permettre au patient de suivre et completer une demande retournee par la fondation

Status: done

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

- [x] Mettre en avant l'etat `to_complete` et son motif cote patient
- [x] Autoriser l'ajout des elements manquants sur la demande existante
- [x] Implementer la re-soumission vers un etat de revue
- [x] Verifier la conservation de l'historique et des pieces deja presentes

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

### Debug Log

- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8074 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_patient_payment_request_portal.py:TestEvmPatientPaymentRequestPortal.test_patient_portal_case_detail_can_update_request_to_complete_before_resubmission,/evm/tests/test_patient_payment_request_portal.py:TestEvmPatientPaymentRequestPortal.test_patient_portal_case_detail_shows_update_errors_for_request_to_complete'"` -> OK
- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8075 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_patient_can_update_request_to_complete_without_losing_history,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_patient_can_complete_request_to_complete_and_resubmit_it'"` -> OK
- `./scripts/quality-check.sh lint` -> OK
- `./scripts/quality-check.sh smoke` -> OK

### Completion Notes List

- Ajout d'un flux portail patient pour modifier une demande `draft` ou `to_complete` existante sans recreer de doublon.
- Mise en avant cote patient des demandes `to_complete` avec message d'action explicite, motif de retour et conservation du contexte visible avant resoumission.
- Ajout d'un feedback utilisateur dedie apres mise a jour et conservation des pieces jointes existantes pendant la completion et la resoumission.
- Extension des tests modele et portail pour couvrir la mise a jour inline, les erreurs de validation, la resoumission et la preservation de l'historique documentaire.
- Correctifs post-review sur la tracabilite visible cote patient, la validation stricte du libelle en edition et le rejet des montants non finis.

## File List

- `addons/evm/controllers/portal.py`
- `addons/evm/models/evm_payment_request.py`
- `addons/evm/tests/test_patient_payment_request_portal.py`
- `addons/evm/tests/test_payment_request.py`
- `addons/evm/views/portal_templates.xml`

## Change Log

- 2026-03-10: implementation de la completion patient d'une demande retournee, avec edition inline sur le portail, feedback de mise a jour et couverture de tests associee.
- 2026-03-10: correctifs post-review sur l'historique visible cote patient, la validation du nom en edition et la validation des montants non finis.
- 2026-03-10: review finale approuvee apres correction des points bloques et verification des tests.

## Senior Developer Review (AI)

### Reviewer

Martin

### Outcome

Approve

### Summary

- La tracabilite de l'echange est maintenant visible dans le portail patient via un historique par demande de paiement.
- L'edition inline refuse desormais explicitement un libelle vide au lieu de regenerer un nom par defaut.
- La validation du montant rejette des entrees non finies (`NaN`, `Infinity`, debordements) avant toute ecriture.

### Validation

- `./scripts/quality-check.sh lint` -> OK
- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8074 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_patient_payment_request_portal.py:TestEvmPatientPaymentRequestPortal.test_patient_portal_case_detail_can_resubmit_request_to_complete,/evm/tests/test_patient_payment_request_portal.py:TestEvmPatientPaymentRequestPortal.test_patient_portal_case_detail_shows_update_errors_for_request_to_complete,/evm/tests/test_patient_payment_request_portal.py:TestEvmPatientPaymentRequestPortal.test_patient_portal_case_detail_rejects_empty_name_on_update,/evm/tests/test_patient_payment_request_portal.py:TestEvmPatientPaymentRequestPortal.test_patient_portal_case_detail_can_update_request_to_complete_before_resubmission'"` -> OK
- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8075 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_patient_can_complete_request_to_complete_and_resubmit_it,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_patient_can_update_request_to_complete_without_losing_history,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_validate_portal_creation_data_rejects_non_finite_amounts'"` -> OK
- `./scripts/quality-check.sh smoke` -> OK
