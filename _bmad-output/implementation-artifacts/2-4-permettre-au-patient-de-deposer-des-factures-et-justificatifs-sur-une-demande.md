# Story 2.4: Permettre au patient de deposer des factures et justificatifs sur une demande

Status: ready-for-dev

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

- [ ] Ajouter l'upload multi-fichiers sur une demande de paiement
- [ ] Attacher les fichiers en `ir.attachment` sur `evm.payment_request`
- [ ] Appliquer validations de type, taille et autorisation
- [ ] Verifier la visibilite des pieces dans le dossier et la preservation de l'historique

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

### Completion Notes List

- Story prete pour execution par `dev-story`

