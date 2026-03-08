# Story 4.4: Cloturer operationnellement un dossier selon les regles metier

Status: ready-for-dev

## Story

As a membre de la fondation,
I want qu'un dossier puisse etre cloture selon les regles prevues,
so that les dossiers termines n'encombrent plus le flux actif et restent historises proprement.

## Acceptance Criteria

1. **Given** un dossier qui remplit les conditions de cloture
   **When** une cloture manuelle ou automatique est declenchee
   **Then** le statut du dossier passe a `closed`
   **And** le dossier n'apparait plus dans les vues de traitement actif tout en restant consultable en lecture

2. **Given** un dossier dont le nombre maximal de seances ou la regle de delai est atteint
   **When** les conditions de cloture sont evaluees
   **Then** le systeme peut considerer le dossier comme eligible a la cloture
   **And** une nouvelle demande doit etre introduite si une nouvelle prise en charge est necessaire

3. **Given** un dossier qui ne remplit pas encore les conditions de cloture
   **When** une tentative de cloture est lancee
   **Then** le systeme refuse ou reporte l'action de maniere coherente
   **And** il preserve l'integrite du workflow

## Tasks / Subtasks

- [ ] Definir les conditions d'eligibilite a la cloture sur `evm.case`
- [ ] Implementer l'action metier de cloture manuelle
- [ ] Exclure les dossiers clos des vues actives tout en les gardant consultables
- [ ] Tracer la cloture et tester les cas non eligibles

## Dev Notes

- Dependances: suivi des seances et workflow dossier en place.
- La cloture ne doit pas casser l'historique ni les consultations legitimes.
- Les regles metier combinent au moins seuil de seances et regle de delai definie pour le projet.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/case.py`, vues dossier, filtres de listes.
- Garder une logique de cloture unique reutilisable par l'action manuelle et le cron.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 4.4"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Automation Boundary (Cron)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR7"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

