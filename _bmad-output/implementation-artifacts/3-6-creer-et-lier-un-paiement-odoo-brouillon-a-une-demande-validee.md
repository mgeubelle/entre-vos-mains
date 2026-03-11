# Story 3.6: Creer et lier un paiement Odoo brouillon a une demande validee

Status: done

## Story

As a membre de la fondation,
I want qu'un `account.payment` brouillon soit cree pour une demande validee,
so that le suivi comptable du paiement soit assure dans Odoo.

## Acceptance Criteria

1. **Given** une demande validee sans paiement lie
   **When** la transition metier prevue est executee
   **Then** un `account.payment` brouillon est cree et lie a la demande
   **And** les informations necessaires a la tracabilite sont conservees

2. **Given** une demande possedant deja un `payment_id`
   **When** une nouvelle creation de paiement est tentee
   **Then** aucun doublon n'est cree
   **And** le garde-fou d'idempotence est respecte

## Tasks / Subtasks

- [x] Ajouter le champ `payment_id` sur `evm.payment_request`
- [x] Implementer la creation d'un `account.payment` brouillon lors de la validation prevue
- [x] Assurer l'idempotence stricte si un paiement est deja lie
- [x] Tracer la creation et rendre le lien visible pour la fondation

## Dev Notes

- Dependances: Story 3.5.
- Le paiement est cree en brouillon; le posting peut rester manuel en V1.
- L'integration doit soit creer exactement un paiement lie, soit echouer clairement sans doublon.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, dependances manifest vers `account` si necessaire, vues fondation.
- Ne pas introduire d'automatisation bancaire ni de flux comptable hors scope.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.6"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Accounting Integration (Odoo Accounting)", "Idempotence (KISS)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR4", "Non-Functional Requirements - Integration"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log

- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8074 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_payment_request.py'"` -> OK
- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8075 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_patient_payment_request_portal.py,/evm/tests/test_case_consultation.py'"` -> OK
- `./scripts/quality-check.sh lint` -> OK
- `./scripts/quality-check.sh smoke` -> OK

### Completion Notes List

- Ajout du champ `payment_id` sur `evm.payment_request` avec ecriture controlee dans le workflow.
- La validation fondation cree automatiquement un `account.payment` brouillon et le lie a la demande validee.
- La creation est strictement idempotente: si un paiement est deja lie, aucun doublon n'est cree.
- La revue a durci le workflow: blocage de l'injection de champs systeme au `create`, verrou SQL sur la creation du paiement, controle de coherence d'un paiement deja lie et restriction serveur de l'ouverture du paiement a la fondation.
- Un journal de paiement sortant compatible est selectionne automatiquement en suivant les idiomes Odoo 19 `account`: journal `bank/cash/credit` avec methode sortante, preference pour `manual`, aucun posting automatique ni flux bancaire belge additionnel.
- La demande trace la creation du paiement dans le chatter et expose un lien direct vers le paiement cote fondation.
- La couverture de tests modele, vue et integration a ete etendue, avec un ajustement d'un test smoke adjacent pour supprimer une hypothese fragile sur les donnees existantes.

## File List

- `addons/evm/__manifest__.py`
- `addons/evm/models/evm_payment_request.py`
- `addons/evm/security/ir.model.access.csv`
- `addons/evm/views/evm_payment_request_views.xml`
- `addons/evm/tests/test_case_consultation.py`
- `addons/evm/tests/test_patient_payment_request_portal.py`
- `addons/evm/tests/test_payment_request.py`
- `addons/evm/tests/test_case_review.py`

## Change Log

- 2026-03-11: implementation de la creation et liaison automatique d'un paiement Odoo brouillon a la validation d'une demande.
- 2026-03-11: ajout des droits de lecture comptables minimaux, du lien fondation vers le paiement et de la couverture de tests associee.
- 2026-03-11: correction des points de revue high/medium sur le workflow, l'idempotence et le controle d'acces; verification lint, tests cibles et smoke completees; story passee en `done`.
