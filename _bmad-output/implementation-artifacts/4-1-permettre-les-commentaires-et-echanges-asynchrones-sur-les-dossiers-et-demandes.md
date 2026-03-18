# Story 4.1: Permettre les commentaires et echanges asynchrones sur les dossiers et demandes

Status: done

## Story

As a patient ou membre de la fondation,
I want ajouter des commentaires et notes sur un dossier ou une demande,
so that les echanges restent centralises et exploitables sans recourir a des emails disperses.

## Acceptance Criteria

1. **Given** un dossier ou une demande accessible a un utilisateur autorise
   **When** il ajoute un commentaire via les mecanismes prevus
   **Then** le commentaire est enregistre sur le bon objet
   **And** il reste visible aux acteurs autorises selon les regles metier

2. **Given** un patient ou un membre de la fondation autorise
   **When** il consulte une demande
   **Then** il peut y retrouver l'espace de notes pertinent au suivi
   **And** les echanges restent historises dans le dossier ou la demande

3. **Given** un utilisateur non autorise
   **When** il tente de consulter ou poster un commentaire
   **Then** l'acces ou l'action est refuse
   **And** aucune information sensible n'est exposee

## Tasks / Subtasks

- [x] Activer ou finaliser le mecanisme de commentaires sur `evm.case` et `evm.payment_request`
- [x] Rendre les echanges visibles selon les droits metier
- [x] Ajouter les points d'entree UI cote fondation et patient
- [x] Verifier l'absence de fuite d'information et la bonne historisation

### Review Follow-ups (AI)

- [x] [AI-Review][High] Filtrer l'historique dossier expose au patient pour exclure les messages de decision internes de la fondation (`Plafond annuel restant`, `Note`) avant affichage portail. [addons/evm/controllers/portal.py:131] [addons/evm/models/evm_case.py:228] [addons/evm/models/evm_case.py:506]
- [x] [AI-Review][High] Aligner les acteurs autorises au commentaire dossier: le kine proprietaire n'a ni droit de poster ni point d'entree UI alors que l'AC parle d'utilisateur autorise et que FR10 couvre aussi le physiotherapeute. [addons/evm/models/evm_case.py:207] [addons/evm/controllers/portal.py:488] [addons/evm/tests/test_payment_request.py:517]
- [x] [AI-Review][Medium] Afficher l'auteur des messages dans le portail patient pour rendre les echanges exploitables et auditables comme sur la vue kine/back-office. [addons/evm/views/portal_templates.xml:291] [addons/evm/views/portal_templates.xml:555] [addons/evm/views/portal_templates.xml:148]
- [x] [AI-Review][Low] Preserver le contexte de pagination lors de l'envoi d'un commentaire dossier afin d'eviter un retour force en page 1. [addons/evm/views/portal_templates.xml:300] [addons/evm/controllers/portal.py:505]

## Dev Notes

- Dependances: epics 1 a 3 suffisamment avances pour disposer des objets metier.
- L'architecture recommande `mail.thread` et tracking Odoo standard en V1.
- Garder une experience simple, pas de chat temps reel.

### Project Structure Notes

- Fichiers cibles: modeles metier, vues back-office, portail et templates associes.
- Les droits de lecture/ecriture des commentaires doivent suivre les droits de l'objet parent.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 4.1"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Audit Trail (V1)", "Notifications (V1)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Ajout de `action_post_comment` sur `evm.case` et `evm.payment_request`, avec controle d'acces metier (patient proprietaire, fondation, admin), sanitation du texte et persistance via `mail.thread`.
- Ajout des points d'entree portail patient pour commenter un dossier et une demande de paiement, avec feedback UX dedie, conservation de l'historique visible et rejet des cibles inaccessibles.
- L'UI fondation reposait deja sur le chatter back-office existant sur les formulaires `evm.case` et `evm.payment_request`; la story a ete finalisee cote patient sans ouvrir d'ACL supplementaires.
- Validation executee: `ruff check` cible, tests Odoo cibles sur commentaires, puis `make quality` -> OK (`0 failed, 0 error(s)` sur le smoke `/evm`; web tour ignore car Chrome absent).
- Correctifs post-review appliques en mode KISS: details sensibles de decision bascules en notes internes, commentaire dossier ouvert au kine proprietaire, auteur affiche cote patient et contexte de pagination conserve sur le formulaire dossier.
- Revalidation executee: `make quality-lint` puis smoke Odoo equivalent a `make quality-smoke` via port alternatif (`8074`) -> OK (`0 failed, 0 error(s)` sur `/evm`; web tour ignore car Chrome absent).

## File List

- addons/evm/controllers/portal.py
- addons/evm/models/evm_case.py
- addons/evm/models/evm_payment_request.py
- addons/evm/tests/test_case_review.py
- addons/evm/tests/test_kine_portal.py
- addons/evm/tests/test_patient_payment_request_portal.py
- addons/evm/tests/test_payment_request.py
- addons/evm/views/portal_templates.xml

## Change Log

- 2026-03-18: finalisation des commentaires asynchrones dossier/demande via `mail.thread`, formulaires portail patient, controles d'acces et couverture de tests associee.
- 2026-03-18: revue senior AI executee, story repassee a `in-progress` et follow-ups ouverts sur fuite d'information, couverture acteur kine, attribution des messages et pagination.
- 2026-03-18: corrections post-review appliquees et story repassee a `review` apres revalidation technique complete.
- 2026-03-18: story validee et cloturee en `done`; workflow local formalise avec reload systematique `odoo-19` + upgrade `evm`.

## Senior Developer Review (AI)

### Outcome

Approved After Fixes

### Findings

1. High - La nouvelle vue patient affiche tous les messages dossier non internes, mais les messages de decision existants incluent des donnees operationnelles fondation (`Plafond annuel restant`) et la `foundation_decision_note`. Cela contrevient a l'AC 3 sur l'absence de fuite d'information. [addons/evm/controllers/portal.py:131] [addons/evm/models/evm_case.py:228] [addons/evm/models/evm_case.py:506]
2. High - Le mecanisme dossier exclut explicitement le kinesitherapeute proprietaire: `action_post_comment` n'autorise que patient/fondation/admin et la vue portail kine ne fournit aucun formulaire. L'AC 1 parle pourtant d'utilisateur autorise sur un dossier accessible, et FR10 couvre aussi le physiotherapeute. [addons/evm/models/evm_case.py:207] [addons/evm/controllers/portal.py:488] [addons/evm/tests/test_payment_request.py:517]
3. Medium - Le portail patient n'affiche pas l'auteur des messages ni sur le fil dossier ni sur le fil demande, contrairement a la vue kine. Des echanges asynchrones sans auteur identifiable sont peu exploitables pour le suivi. [addons/evm/views/portal_templates.xml:291] [addons/evm/views/portal_templates.xml:555] [addons/evm/views/portal_templates.xml:148]
4. Low - Poster un commentaire dossier fait toujours rediriger vers `/my/evm/cases/<id>` sans conserver `payment_request_page` ni `document_page`, ce qui casse le contexte des dossiers pagines alors que les autres actions du meme ecran le preservent. [addons/evm/views/portal_templates.xml:300] [addons/evm/controllers/portal.py:505]

### Validation

- `make quality-lint` OK
- Smoke Odoo equivalent a `make quality-smoke` relance sur port alternatif (`8074`) OK (`0 failed, 0 error(s)`; web tour Chrome ignore)
