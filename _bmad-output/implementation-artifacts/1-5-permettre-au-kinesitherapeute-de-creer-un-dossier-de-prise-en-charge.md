# Story 1.5: Permettre au kinesitherapeute de creer un dossier de prise-en-charge

Status: ready-for-dev

## Story

As a kinesitherapeute,
I want creer un dossier de prise en charge pour un patient,
so that je puisse initier une demande d'aide sans friction administrative.

## Acceptance Criteria

1. **Given** un kinesitherapeute autorise
   **When** il cree un nouveau dossier
   **Then** il peut encoder les informations minimales requises
   **And** il peut renseigner le nombre maximum de seances demandees pour le dossier

2. **Given** une demande de prise en charge complete
   **When** le kinesitherapeute la soumet
   **Then** un dossier patient est cree automatiquement avec le statut `pending`
   **And** la demande initiale reste tracable dans l'historique du dossier

3. **Given** un dossier en creation
   **When** des donnees obligatoires sont absentes ou invalides
   **Then** le systeme bloque la soumission
   **And** affiche des messages d'erreur clairs en francais

## Tasks / Subtasks

- [ ] Completer `evm.case` avec les champs de creation et les validations minimales
- [ ] Construire le formulaire de creation cote kine avec feedback clair en francais
- [ ] Implementer l'action metier de soumission vers `pending`
- [ ] Tracer la soumission dans l'historique d'activite et tester les cas invalides

## Dev Notes

- Dependances: Stories 1.1 a 1.4.
- `sessions_requested` est saisi ici et doit servir de borne pour la suite du workflow.
- Garder le parcours court et accessible: erreurs proches des champs + resume global si pertinent.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/case.py`, `addons/evm/views/evm_case_views.xml`, composants portail eventuels.
- La transition doit passer par une methode `action_*`, pas par logique inline en vue.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 1.5"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Data Architecture", "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR5", "Minimal UX Guardrails For MVP"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

