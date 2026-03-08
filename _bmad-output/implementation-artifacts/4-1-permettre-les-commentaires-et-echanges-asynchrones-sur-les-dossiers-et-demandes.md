# Story 4.1: Permettre les commentaires et echanges asynchrones sur les dossiers et demandes

Status: ready-for-dev

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

- [ ] Activer ou finaliser le mecanisme de commentaires sur `evm.case` et `evm.payment_request`
- [ ] Rendre les echanges visibles selon les droits metier
- [ ] Ajouter les points d'entree UI cote fondation et patient
- [ ] Verifier l'absence de fuite d'information et la bonne historisation

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

- Story prete pour execution par `dev-story`

