# Story 1.4: Permettre au kinesitherapeute d'acceder a son espace et consulter ses dossiers

Status: done

## Story

As a kinesitherapeute,
I want acceder a mon espace et retrouver les dossiers que j'ai introduits,
so that je puisse suivre mes prises en charge sans voir celles des autres.

## Acceptance Criteria

1. **Given** un kinesitherapeute avec un compte autorise
   **When** il se connecte a l'application
   **Then** il accede a une vue listant uniquement les dossiers qu'il a crees
   **And** chaque ligne affiche au minimum le statut du dossier, la date de creation et l'identite du patient ou son libelle metier autorise

2. **Given** un kinesitherapeute connecte
   **When** il ouvre un dossier qu'il a introduit
   **Then** il peut consulter le statut du dossier, le nombre de seances demandees, le nombre de seances autorisees si renseigne, et l'historique d'activite autorise
   **And** il ne peut pas acceder aux dossiers introduits par un autre kinesitherapeute

## Tasks / Subtasks

- [x] Finaliser le modele `evm.case` avec les champs minimaux necessaires a la consultation
- [x] Ajouter les vues liste/detail et, si necessaire, le portail ou menu d'entree pour le role kine
- [x] Restreindre l'acces via record rules pour n'afficher que les dossiers du kinesitherapeute connecte
- [x] Verifier les informations visibles et l'absence d'acces transverse

## Dev Notes

- Dependances: Stories 1.1 a 1.3.
- L'interface doit rester simple, en francais, avec statuts et compteurs visibles sans navigation inutile.
- Le tracking/historique peut s'appuyer sur `mail.thread` ou equivalent Odoo retenu dans l'architecture.

### Project Structure Notes

- Fichiers cibles probables: `addons/evm/models/case.py`, `addons/evm/views/evm_case_views.xml`, `addons/evm/controllers/portal.py`, `addons/evm/templates/portal_templates.xml`.
- La logique d'autorisation doit rester cote ORM/record rules, pas seulement dans la vue.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 1.4"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Project Organization", "Authentication & Security", "UI Language Rule"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR6", "FR7"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`
- Modele `evm.case` enrichi avec statut, compteurs de seances, libelle patient calcule et historique `mail.thread`.
- Portail kine ajoute avec entree `Mes dossiers`, liste `/my/evm/cases` et detail `/my/evm/cases/<id>`.
- Les record rules existantes ont ete preservees et verrouillees par tests sur le domaine `kine_user_id = user.id` et sur le redirect portail en acces transverse.
- Validation finale: `make quality` OK.

### File List

- addons/evm/__init__.py
- addons/evm/__manifest__.py
- addons/evm/controllers/__init__.py
- addons/evm/controllers/portal.py
- addons/evm/models/evm_case.py
- addons/evm/tests/__init__.py
- addons/evm/tests/test_case_consultation.py
- addons/evm/tests/test_kine_portal.py
- addons/evm/tests/test_security.py
- addons/evm/views/evm_case_views.xml
- addons/evm/views/portal_templates.xml

### Change Log

- 2026-03-08: story passee en `in-progress` et socle de consultation `evm.case` implemente.
- 2026-03-08: portail kine, vues internes et verifications de cloisonnement completes; story promue en `review`.
- 2026-03-09: code review adverse terminee; story approuvee et promue en `done`.

## Senior Developer Review (AI)

### Outcome

Approved.

### Findings

- Aucun point bloquant ou correctif necessaire n'a ete identifie sur les AC de la story 1.4 dans l'etat courant du code.

### Residual Risks

- Low: la couverture `HttpCase` verifie bien l'acces transverse entre kines et le rendu principal, mais ne couvre pas encore explicitement les redirects des routes liste/creation pour un patient authentifie.
- Low: le controleur renseigne `request.session["my_evm_cases_history"]` sans reutiliser ensuite le mecanisme `_get_page_view_values`, ce qui laisse un reliquat de navigation non exploite.
- Low: la preuve de cloisonnement ORM depend de tests securite transverses (`test_security.py`) plus que d'une trace explicite dans la story, ce qui complique legerement l'audit de continute entre 1.3, 1.4 et 1.7.

### Verification

- `make quality`
