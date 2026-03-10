# Story 2.4: Permettre au patient de deposer des factures et justificatifs sur une demande

Status: done

## Story

As a patient,
I want deposer des factures et justificatifs lies a une demande de paiement,
so that la fondation puisse verifier les pieces necessaires au remboursement.

## Acceptance Criteria

1. **Given** un patient sur une demande de paiement autorisee
   **When** il ajoute des documents
   **Then** les fichiers sont enregistres de maniere securisee via les mecanismes Odoo prevus
   **And** ils sont relies a la bonne demande

2. **Given** un patient qui charge des pieces justificatives
   **When** les fichiers sont verifies
   **Then** seuls les formats `pdf`, `jpg`, `jpeg` et `png` sont acceptes
   **And** chaque fichier ne depasse pas 10 Mo

3. **Given** un patient qui depose plusieurs documents pour une meme demande
   **When** l'upload est valide
   **Then** plusieurs fichiers peuvent etre attaches a la meme demande
   **And** un nouveau fichier n'ecrase pas un document existant mais s'ajoute a l'historique

4. **Given** un document ajoute a une demande
   **When** le patient revient sur son dossier
   **Then** le document est visible dans l'espace documentaire du dossier
   **And** son historique de presence est conserve

5. **Given** un fichier invalide ou une tentative non autorisee
   **When** le depot est effectue
   **Then** le systeme refuse l'operation
   **And** affiche un message clair en francais

## Tasks / Subtasks

- [x] Ajouter l'upload multi-fichiers sur une demande de paiement
- [x] Attacher les fichiers en `ir.attachment` sur `evm.payment_request`
- [x] Appliquer validations de type, taille et autorisation
- [x] Verifier la visibilite des pieces dans le dossier et la preservation de l'historique

## Dev Notes

- Dependances: Stories 2.2 et 2.3.
- Regles V1 fermes: `pdf`, `jpg`, `jpeg`, `png`, 10 Mo max, multi-upload autorise, pas d'ecrasement.
- Utiliser les mecanismes Odoo standard pour stockage et securite des attachments.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, portail, templates, eventuelles aides sur l'upload.
- Toute erreur doit etre affichee en francais et laisser les autres donnees saisies intactes si possible.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 2.4"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Document Upload Rules (V1)", "Document Storage"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR2", "Minimal UX Guardrails For MVP"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Implementation Plan

- Ajouter une route portail dediee a l'upload multi-fichiers sur une `evm.payment_request` accessible au patient.
- Centraliser les validations d'autorisation, de format et de taille dans `evm.payment_request.portal_upload_attachments`.
- Afficher le formulaire d'upload sur les demandes en brouillon et reutiliser la vue dossier patient pour les retours succes/erreur.
- Couvrir le flux par des tests modele et portail, puis relancer la suite `evm` et le lint.

### Completion Notes List

- Upload multi-fichiers ajoute sur les cartes de demandes en brouillon du dossier patient, avec feedback succes/erreur en francais.
- Les fichiers sont rattaches a `evm.payment_request` via `ir.attachment`, stockes en binaire, marques `evm_patient_visible`, sans ecrasement des pieces existantes.
- Les validations bloquent les formats hors `pdf/jpg/jpeg/png`, les fichiers > 10 Mo, l'absence de selection, l'acces hors portail patient et les demandes non brouillon.
- Le dossier patient continue d'agreger l'historique documentaire, et les nouveaux uploads apparaissent dans cet espace apres redirection.
- Revue senior corrigee: message explicite en francais sur tentative non autorisee, verification du contenu MIME reelle, preservation du contexte de pagination apres upload et tests supplementaires de non-regression.
- Tests executes et verts:
  - `./scripts/quality-check.sh smoke`
  - `./scripts/quality-check.sh lint`

## File List

- addons/evm/models/evm_payment_request.py
- addons/evm/controllers/portal.py
- addons/evm/views/portal_templates.xml
- addons/evm/tests/test_payment_request.py
- addons/evm/tests/test_patient_payment_request_portal.py
- _bmad-output/implementation-artifacts/2-4-permettre-au-patient-de-deposer-des-factures-et-justificatifs-sur-une-demande.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-03-10: implementation story 2.4 terminee, upload multi-fichiers portail patient ajoute avec validations FR, rattachement `ir.attachment`, affichage dossier, tests et lint verts.
- 2026-03-10: revue senior AI appliquee, corrections de securite/UX sur upload, validations MIME renforcees, feedback portail et pagination preserves, suite qualite relancee au vert.

## Senior Developer Review (AI)

- Reviewer: Martin
- Date: 2026-03-10
- Outcome: Approve
- Notes:
  - Les ecarts identifies en review ont ete corriges avant cloture de la story.
  - Le portail affiche des messages FR clairs lors des refus d'acces et des erreurs de validation.
  - Les fichiers uploades sont verifies sur leur contenu en plus de l'extension autorisee.
  - Les tests couvrent maintenant le contenu MIME incoherent, le message d'acces refuse et la preservation du contexte de pagination.
