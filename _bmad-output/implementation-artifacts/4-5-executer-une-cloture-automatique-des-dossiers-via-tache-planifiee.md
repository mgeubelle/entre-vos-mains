# Story 4.5: Executer une cloture automatique des dossiers via tache planifiee

Status: ready-for-dev

## Story

As a administrateur de la plateforme,
I want une tache planifiee qui applique les regles d'auto-cloture,
so that la plateforme reste propre operationnellement sans intervention manuelle systematique.

## Acceptance Criteria

1. **Given** des dossiers eligibles a l'auto-cloture existent
   **When** la tache planifiee s'execute
   **Then** seuls les dossiers qui respectent les regles definies sont clotures
   **And** chaque cloture automatique laisse une trace exploitable

2. **Given** un dossier non eligible
   **When** la tache planifiee l'evalue
   **Then** il n'est pas cloture par erreur
   **And** aucune regression n'est introduite sur les dossiers encore actifs

## Tasks / Subtasks

- [ ] Ajouter la methode cron d'auto-cloture sur `evm.case`
- [ ] Declarer la tache planifiee dans les donnees du module
- [ ] Reutiliser la meme logique d'eligibilite que la cloture manuelle
- [ ] Tracer les clotures automatiques et tester les faux positifs

## Dev Notes

- Dependances: Story 4.4.
- Le cron doit rester idempotent et sans effet sur les dossiers non eligibles.
- Pas de logique dupliquee entre action manuelle et automatique.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/case.py`, `addons/evm/data/scheduled_actions.xml`.
- La planification doit rester compatible avec une exploitation Odoo standard.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 4.5"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Automation Boundary (Cron)", "Project Organization"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR7"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

