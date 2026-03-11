# Story 3.4: Permettre a la fondation de refuser une demande de paiement

Status: done

## Story

As a membre de la fondation,
I want refuser une demande de paiement lorsqu'elle n'est pas recevable,
so that le workflow de la demande reste coherent et trace jusqu'a sa sortie finale.

## Acceptance Criteria

1. **Given** une demande en cours d'instruction
   **When** la fondation decide qu'elle ne peut pas etre acceptee
   **Then** elle peut la passer au statut `refused`
   **And** le motif du refus est enregistre de maniere exploitable

2. **Given** une demande refusee
   **When** son historique est consulte
   **Then** le statut final et son motif sont visibles
   **And** la demande n'apparait plus comme element a traiter dans la file active

## Tasks / Subtasks

- [x] Ajouter le motif de refus et l'action de transition vers `refused`
- [x] Retirer la demande refusee de la file active tout en la gardant consultable
- [x] Afficher l'historique et le motif de facon lisible
- [x] Verifier les restrictions sur les transitions ulterieures

## Dev Notes

- Dependances: Story 3.1.
- Un refus est un etat final metier; ne pas laisser une reprise implicite sans nouvelle regle explicite.
- Le motif doit etre presentable au patient/fondation selon les droits definis.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, vues fondation, vues de consultation.
- Garder des filtres clairs entre file active et historiques.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.4"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR9", "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log

- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8074 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_foundation_can_refuse_submitted_request_with_reason_history_and_active_queue_exit,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_foundation_can_prepare_refusal_reason_inline_and_refuse_from_form,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_refusal_requires_foundation_user_submitted_state_reason_and_blocks_later_transitions,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_payment_request_model_exposes_creation_fields_and_initial_workflow_state,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_foundation_processing_action_defaults_to_submitted_queue'"` -> OK
- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8075 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_patient_payment_request_portal.py:TestEvmPatientPaymentRequestPortal.test_patient_portal_case_detail_shows_refusal_reason_for_refused_request'"` -> OK
- `./scripts/quality-check.sh lint` -> OK
- `./scripts/quality-check.sh smoke` -> OK

### Completion Notes List

- Ajout du champ `refusal_reason` avec sanitization dediee et preparation inline reservee a la fondation sur demande `submitted`.
- Ajout de l'action metier `action_refuse` pour cloturer une demande en `refused`, tracer le motif dans le chatter et nettoyer les motifs incompatibles.
- Conservation de la file active sur les demandes soumises, avec consultation explicite des demandes refusees via l'etat et les filtres existants.
- Affichage cote fondation et portail du refus et de son motif, sans laisser de reprise ni de resoumission implicite cote patient.
- Ajout de tests modele et portail couvrant la transition de refus, la visibilite du motif, la sortie de la file active et le blocage des transitions ulterieures.

## File List

- `addons/evm/models/evm_payment_request.py`
- `addons/evm/views/evm_payment_request_views.xml`
- `addons/evm/views/portal_templates.xml`
- `addons/evm/tests/test_payment_request.py`
- `addons/evm/tests/test_patient_payment_request_portal.py`

## Change Log

- 2026-03-10: implementation completee du refus des demandes de paiement avec motif dedie, traçabilite chatter, visibilite portail/fondation et couverture de tests associee.
- 2026-03-11: revue finale AI validee, story passee a `done`.

## Senior Developer Review (AI)

### Outcome

Approved

### Findings

- Aucun finding bloquant releve sur le scope de refus. Les criteres d'acceptation sont couverts par `action_refuse`, les vues fondation/portail et les tests modele + portail.
