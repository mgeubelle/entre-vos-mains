# Story 3.7: Permettre a la fondation de confirmer un paiement effectue hors-plateforme

Status: done

## Story

As a membre de la fondation,
I want marquer une demande comme payee apres confirmation du paiement externe,
so that le dossier reflete correctement l'etat reel du remboursement.

## Acceptance Criteria

1. **Given** une demande avec un paiement Odoo lie
   **When** la fondation confirme que le paiement a ete effectue hors plateforme
   **Then** la demande passe au statut `paid`
   **And** la trace de confirmation est conservee dans le dossier

2. **Given** une demande non validee ou sans paiement lie
   **When** un utilisateur tente de la marquer comme payee
   **Then** l'action est refusee
   **And** un message clair explique pourquoi

## Tasks / Subtasks

- [x] Implementer l'action de confirmation de paiement externe
- [x] Verifier les preconditions: demande validee et `payment_id` present
- [x] Passer la demande a `paid` et journaliser la confirmation
- [x] Tester les refus de transition sur demandes non eligibles

## Dev Notes

- Dependances: Story 3.6.
- Le statut `paid` represente une confirmation metier, pas une automatisation bancaire.
- Preserver une trace lisible pour audit et suivi patient/fondation.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, vues de traitement fondation.
- Garder la logique simple: pas de webhook, pas d'integration bancaire supplementaire.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.7"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Accounting Integration (V1, Community-friendly)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR4", "FR9", "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log

- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8076 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_payment_request.py'"` -> FAIL (fragilite existante sur une recherche `state='submitted'` non filtree par `id`)
- `docker compose -f /home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml exec -T odoo-19 sh -lc "odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8076 --stop-after-init -u evm --test-enable --test-tags '/evm/tests/test_payment_request.py'"` -> OK
- `./scripts/quality-check.sh lint` -> OK
- `./scripts/quality-check.sh smoke` -> OK
- `./scripts/quality-check.sh smoke` -> OK (post-review, avec verification de la trace sur dossier et du rejet des paiements lies modifies)

### Completion Notes List

- Ajout de l'action metier `action_confirm_external_payment` pour permettre a la fondation de confirmer un paiement hors plateforme sur une demande validee avec `payment_id`.
- La confirmation fait passer la demande a `paid` et journalise une trace lisible dans le chatter pour audit.
- La confirmation journalise aussi une trace dediee sur le dossier `evm.case` afin de conserver l'evenement directement au niveau du dossier.
- La transition vers `paid` revalide desormais la coherence du `account.payment` lie avant confirmation pour refuser un paiement brouillon stale ou modifie hors workflow.
- La vue fondation expose un bouton dedie uniquement sur les demandes `validated` avec paiement Odoo lie.
- La couverture de tests modele/vue couvre le succes, les refus d'acces, les refus de transition sur demande non validee ou sans paiement lie, ainsi que le rejet d'un paiement lie devenu incoherent.
- Un test adjacent a ete durci pour ne plus supposer qu'une recherche globale sur `state='submitted'` retourne une seule demande dans une base deja chargee.

## File List

- `addons/evm/models/evm_payment_request.py`
- `addons/evm/views/evm_payment_request_views.xml`
- `addons/evm/tests/test_payment_request.py`
- `_bmad-output/implementation-artifacts/3-7-permettre-a-la-fondation-de-confirmer-un-paiement-effectue-hors-plateforme.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-03-12: implementation de la confirmation de paiement hors plateforme avec passage a `paid`, trace chatter, bouton fondation dedie et couverture de tests associee.
- 2026-03-12: durcissement d'un test adjacent de file de demandes pour supprimer une hypothese fragile sur l'unicite d'une recherche `submitted`.
- 2026-03-12: correction post-review pour conserver la confirmation dans le dossier et refuser la confirmation sur paiement Odoo lie incoherent.
