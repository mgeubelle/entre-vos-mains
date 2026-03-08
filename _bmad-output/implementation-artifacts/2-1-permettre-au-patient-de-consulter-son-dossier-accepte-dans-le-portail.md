# Story 2.1: Permettre au patient de consulter son dossier accepte dans le portail

Status: ready-for-dev

## Story

As a patient,
I want consulter mon dossier accepte depuis le portail,
so that je comprenne l'etat de ma prise en charge et les actions disponibles.

## Acceptance Criteria

1. **Given** un patient avec un acces portail actif
   **When** il ouvre son dossier
   **Then** il voit les informations utiles du dossier et son statut
   **And** il peut consulter la liste de ses demandes avec leur date d'introduction, leur statut et les informations de seances pertinentes

2. **Given** un patient qui consulte son dossier
   **When** des seances ont ete autorisees ou deja consommees
   **Then** il voit le nombre de seances autorisees et le suivi utile pour comprendre sa prise en charge
   **And** l'interface reste simple, lisible et en francais

3. **Given** un utilisateur non autorise
   **When** il tente d'acceder au dossier d'un autre patient
   **Then** l'acces est refuse
   **And** aucune information sensible n'est exposee

## Tasks / Subtasks

- [ ] Construire la vue portail du dossier patient
- [ ] Afficher statuts, compteurs de seances et liste des demandes liees
- [ ] Renforcer les record rules et controles de route pour l'acces strict au seul dossier du patient
- [ ] Verifier lisibilite, libelles francais et absence de fuite d'information

## Dev Notes

- Dependances: Epic 1 completee au moins jusqu'a la Story 1.7.
- Les compteurs a montrer: `sessions_authorized`, `sessions_consumed` et le reste utile au patient.
- L'UX doit rester sobre, sans scroll horizontal sur parcours critique.

### Project Structure Notes

- Fichiers cibles: `addons/evm/controllers/portal.py`, `addons/evm/templates/portal_templates.xml`, eventuellement `models/case.py`.
- Reutiliser les patterns portail Odoo plutot qu'une UI custom.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 2.1"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Project Organization", "UI Language Rule"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR5", "FR6", "FR8"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

