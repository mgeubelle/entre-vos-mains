# Story 3.1: Permettre a la fondation de consulter la file des demandes de paiement soumises

Status: done

## Story

As a membre de la fondation,
I want voir les demandes de paiement a instruire et leurs informations essentielles,
so that je puisse traiter les dossiers en attente de maniere efficace.

## Acceptance Criteria

1. **Given** des demandes de paiement soumises existent
   **When** un membre de la fondation ouvre la vue de traitement
   **Then** il voit la liste des demandes pertinentes avec au minimum le dossier lie, le patient, la date de soumission, le statut, le montant demande s'il existe, et le nombre de seances declarees
   **And** il peut acceder au detail d'une demande autorisee

2. **Given** un utilisateur non autorise
   **When** il tente d'acceder a cette file de traitement
   **Then** l'acces est refuse
   **And** aucune donnee sensible n'est exposee

## Tasks / Subtasks

- [x] Creer la vue liste/detail fondation sur `evm.payment_request`
- [x] Afficher les colonnes metier minimums attendues
- [x] Restreindre l'acces au role fondation/admin
- [x] Verifier que seules les demandes soumises pertinentes apparaissent dans la file active

## Dev Notes

- Dependances: Epic 2 fonctionnel.
- Cette vue est la porte d'entree de l'instruction fondation; privilegier le tri et la lisibilite.
- Ne pas exposer d'informations non necessaires aux autres roles.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, `addons/evm/views/evm_payment_request_views.xml`, menus.
- Garder le filtrage principal par statut soumis et par role.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.1"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Core Business Models", "Authorization (RBAC)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR9"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- La file fondation `evm_payment_request_action` est maintenant contrainte aux demandes `submitted` via un domaine d'action explicite.
- L'action backend est reservee aux groupes `evm.group_evm_fondation` et `evm.group_evm_admin` pour eviter l'exposition de la file de traitement aux roles non autorises.
- La couverture de tests verifie la restriction de la file active, les groupes autorises et la presence des colonnes metier minimales dans la vue liste.
- Correctif de review applique: les vues liste/recherche/formulaire de la file fondation portent maintenant des groupes explicites fondation/admin.
- Correctif de review applique: la couverture de tests verifie desormais le refus d'acces effectif pour un patient non autorise sur les vues fondation.
- Decision produit iteration 1: pas de surcharge globale de `ir.actions.act_window`; le chargement direct des metadonnees d'action reste un risque accepte tant qu'aucune donnee transverse n'est exposee.
- Validations executees: `./scripts/quality-check.sh lint` puis `./scripts/quality-check.sh smoke` -> `0 failed, 0 error(s)`.

## File List

- addons/evm/tests/test_payment_request.py
- addons/evm/models/__init__.py
- addons/evm/views/evm_payment_request_views.xml
- _bmad-output/implementation-artifacts/3-1-permettre-a-la-fondation-de-consulter-la-file-des-demandes-de-paiement-soumises.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-03-10: durcissement de la file fondation des demandes de paiement soumises avec domaine d'action `submitted`, restriction explicite par groupes et tests de couverture story 3.1.
- 2026-03-10: revue senior AI effectuee, story repassee en `in-progress` suite a des ecarts de securite et de couverture de tests sur l'acces a la file fondation.
- 2026-03-10: corrections post-review appliquees sur l'action et les vues fondation avec tests de non-regression, story remise en `review`.
- 2026-03-10: simplification post-correctif, retrait de la surcharge globale `ir.actions.act_window`; on conserve le durcissement des vues et on accepte le risque residuel sur les metadonnees d'action pour la V1.
- 2026-03-10: review finalisee et approuvee; story passee en `done` avec acceptation explicite du risque residuel V1 sur les metadonnees d'action.

## Senior Developer Review (AI)

- Reviewer: Martin
- Date: 2026-03-10
- Outcome: Approve
- Notes:
  - Les ecarts de review sur la protection des vues et sur la couverture de tests ont ete corriges avant cloture.
  - Les vues `evm_payment_request_view_list`, `evm_payment_request_view_search` et `evm_payment_request_view_form` sont maintenant reservees aux groupes fondation/admin, ce qui ferme l'exposition de la file de traitement dans l'UI Odoo.
  - Les tests verifient desormais le refus d'acces effectif pour un patient non autorise sur ces vues.
  - Le chargement direct des metadonnees d'action par XML ID reste un risque residuel accepte pour la V1, borne a de la metadata sans exposition de donnees transverse selon la decision produit documentee.
  - Validation finale executee: `./scripts/quality-check.sh lint` puis `./scripts/quality-check.sh smoke` -> `0 failed, 0 error(s)`.
