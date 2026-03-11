# Story 3.5: Permettre a la fondation de valider une demande et de mettre a jour le suivi des seances

Status: done

## Story

As a membre de la fondation,
I want valider une demande de paiement et confirmer les seances retenues,
so that le dossier reste a jour et pret pour le paiement.

## Acceptance Criteria

1. **Given** une demande complete en cours d'instruction
   **When** la fondation la valide
   **Then** elle peut confirmer ou ajuster les donnees utiles a la validation
   **And** le suivi des seances consommees du dossier est mis a jour de maniere coherente

2. **Given** une demande validee
   **When** la mise a jour du dossier est appliquee
   **Then** le systeme preserve la coherence entre `authorized_session_count`, `sessions_consumed` et le solde restant
   **And** le patient peut ensuite retrouver ces informations dans son dossier

3. **Given** une validation qui depasserait les regles du dossier
   **When** la fondation tente de confirmer la demande
   **Then** le systeme bloque ou signale clairement l'incoherence
   **And** evite une mise a jour incorrecte des compteurs

## Tasks / Subtasks

- [x] Implementer l'action de validation metier de la demande
- [x] Mettre a jour `sessions_consumed` et le solde restant du dossier
- [x] Bloquer toute incoherence vis-a-vis de `authorized_session_count`
- [x] Rendre les compteurs mis a jour visibles cote patient et fondation

## Dev Notes

- Dependances: Stories 3.1 a 3.4.
- La source de verite des seances consommees est la validation de la demande, pas la simple saisie patient.
- Aucun solde negatif ne doit etre possible.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, `addons/evm/models/case.py`, vues associees.
- La logique de calcul doit rester centralisee et testable, pas dispersee en plusieurs vues.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.5"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Sessions Tracking (V1)", "Core Business Models"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR5", "FR9"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log

- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8074 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_foundation_can_validate_submitted_request_with_inline_adjustments_and_update_case_balance,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_validation_requires_foundation_user_submitted_state_and_available_authorized_sessions,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_validated_or_paid_requests_cannot_exceed_authorized_case_sessions,/evm/tests/test_case_consultation.py:TestEvmCaseConsultation.test_case_remaining_sessions_cannot_be_driven_negative_by_validated_requests,/evm/tests/test_patient_payment_request_portal.py:TestEvmPatientPaymentRequestPortal.test_patient_portal_case_detail_shows_validated_request_adjustments_and_updated_balance'"` -> OK
- `./scripts/quality-check.sh lint` -> OK
- `./scripts/quality-check.sh smoke` -> OK
- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8074 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_foundation_can_validate_submitted_request_with_inline_adjustments_and_update_case_balance,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_validation_requires_foundation_user_submitted_state_and_available_authorized_sessions,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_validation_rejects_requests_on_non_accepted_cases,/evm/tests/test_payment_request.py:TestEvmPaymentRequest.test_validated_paid_or_closed_requests_cannot_exceed_authorized_case_sessions,/evm/tests/test_case_consultation.py:TestEvmCaseConsultation.test_case_consumed_and_remaining_sessions_only_follow_finalized_requests,/evm/tests/test_case_consultation.py:TestEvmCaseConsultation.test_case_remaining_sessions_cannot_be_driven_negative_by_validated_requests,/evm/tests/test_patient_payment_request_portal.py:TestEvmPatientPaymentRequestPortal.test_patient_portal_case_detail_shows_validated_request_adjustments_and_updated_balance'"` -> OK

### Completion Notes List

- Ajout de `action_validate` sur `evm.payment_request` avec trace chatter explicite et nettoyage des motifs incompatibles a la validation.
- La validation devient la seule source de verite pour la consommation: les demandes `validated/paid` sont maintenant bloquees si elles depassent `authorized_session_count`.
- Les ajustements fondation utiles a la validation sont limites a `sessions_count` et `amount_total` tant que la demande est `submitted`, puis verrouilles ensuite.
- Les compteurs dossier sont exposes dans la vue fondation de la demande et restent visibles cote patient via le detail dossier avec les donnees validees mises a jour.
- La couverture de tests a ete etendue sur le modele, le portail patient et la consultation dossier pour verrouiller le workflow et l'absence de solde negatif.
- Corrections post-review: refus des validations hors dossier `accepted`, prise en compte des demandes `closed` dans les compteurs et suppression du rendu portail lie a un solde negatif impossible.
- Risque accepte: le verrou SQL explicite sur le controle de quota a ete retire par simplification, en assumant le tres faible niveau de concurrence cote fondation a ce stade.

## File List

- `addons/evm/models/evm_case.py`
- `addons/evm/models/evm_payment_request.py`
- `addons/evm/views/portal_templates.xml`
- `addons/evm/views/evm_payment_request_views.xml`
- `addons/evm/tests/test_payment_request.py`
- `addons/evm/tests/test_patient_payment_request_portal.py`
- `addons/evm/tests/test_case_consultation.py`

## Change Log

- 2026-03-10: implementation completee de la validation des demandes de paiement avec override fondation controle, blocage des depassements de quota, mise a jour visible des compteurs et couverture de tests associee.
- 2026-03-10: revue senior AI effectuee, statut repasse a `in-progress` avec demandes de corrections avant approbation.
- 2026-03-10: corrections de review appliquees, tests cibles relances et story remise en `review`.
- 2026-03-10: simplification post-correctif avec retrait du verrou SQL de quota et acceptation explicite du risque de concurrence residuel.
- 2026-03-11: risque de concurrence residuel explicitement accepte, revue finalisee et story passee a `done`.

## Senior Developer Review (AI)

### Outcome

Approved with Accepted Risk

### Findings

- [HIGH] `action_validate()` ne prend aucun verrou metier avant de recalculer le quota restant. `_check_authorized_session_quota()` lit les demandes deja `validated/paid` sans `SELECT ... FOR UPDATE` ni verrou applicatif, puis `action_validate()` valide dans un simple `savepoint`. Deux validations concurrentes sur un meme dossier peuvent donc lire le meme reste et depasser `authorized_session_count` au commit. Preuve: `addons/evm/models/evm_payment_request.py:160-176` et `addons/evm/models/evm_payment_request.py:448-470`.
- [HIGH] La validation fondation ne verifie jamais que le dossier parent est encore `accepted`. Les chemins patient bloquent bien creation, upload et soumission hors dossier accepte, mais `action_validate()` peut encore valider une demande `submitted` rattachee a un dossier `pending`, `refused` ou `closed` si un tel enregistrement existe deja ou apparait via une evolution future. Preuve: controles `accepted` presents en `addons/evm/models/evm_payment_request.py:277-291` et `addons/evm/models/evm_payment_request.py:488-499`, absents de `addons/evm/models/evm_payment_request.py:448-470`.
- [MEDIUM] Le modele declare deja l'etat `closed` pour `evm.payment_request`, mais les calculs de consommation et de quota n'incluent que `validated` et `paid`. Le jour ou une demande historisee passe a `closed`, `sessions_consumed` et `remaining_session_count` reculeront artificiellement et rouvriront du quota. Preuve: `addons/evm/models/evm_payment_request.py:46-55`, `addons/evm/models/evm_payment_request.py:152-176` et `addons/evm/models/evm_case.py:142-152`.
- [MEDIUM] L'invariant annonce dans la story "Aucun solde negatif ne doit etre possible" n'est pas centralise au niveau dossier. `remaining_session_count` reste une simple soustraction qui peut devenir negative si des donnees invalides existent deja ou reapparaissent par migration/evolution, et le portail conserve encore une branche explicite pour afficher ce depassement au patient. Preuve: `addons/evm/models/evm_case.py:142-152` et `addons/evm/views/portal_templates.xml:260-273`.

### Review Decision

- Les findings sur le controle `accepted`, la prise en compte de `closed` et le bornage du solde negatif sont corriges dans l'implementation actuelle.
- Le risque de concurrence residuel sur la validation sans verrou explicite est connu et explicitement accepte pour cette V1 compte tenu du tres faible volume d'utilisateurs et du faible niveau de concurrence cote fondation.
- Aucun correctif supplementaire n'est requis avant cloture de la story.
