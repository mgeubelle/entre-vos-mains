# Story 1.7: Ouvrir l'acces patient apres acceptation du dossier

Status: ready-for-dev

## Story

As a patient,
I want recevoir un acces securise a mon dossier une fois accepte,
so that je puisse ensuite suivre mon dossier et preparer mes futures demandes.

## Acceptance Criteria

1. **Given** un dossier accepte par la fondation
   **When** le processus d'activation patient est execute
   **Then** un acces portail patient est cree ou active selon les regles definies
   **And** cet acces n'est pas disponible avant acceptation

2. **Given** un patient dont l'acces vient d'etre active
   **When** il recoit l'invitation ou les informations de connexion
   **Then** il peut se connecter au portail de maniere securisee
   **And** le dossier accepte devient accessible pour les stories du portail patient de l'Epic 2

## Tasks / Subtasks

- [ ] Definir le lien patient sur `evm.case` et la regle d'activation portail
- [ ] Implementer la creation/activation du compte portail lors de l'acceptation
- [ ] Assurer que l'acces patient est impossible tant que le dossier n'est pas `accepted`
- [ ] Envoyer ou preparer l'invitation/notifier le patient selon les mecanismes retenus en V1

## Dev Notes

- Dependances: Stories 1.1 a 1.6.
- Les patients sont des comptes portail Odoo standard; ne pas creer un systeme d'authentification custom.
- L'epic 2 depend directement de cet onboarding.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/case.py`, `addons/evm/controllers/portal.py`, templates portail et eventuels mails.
- L'acces doit etre pilote par groupes/record rules, pas par simple filtrage visuel.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 1.7"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Authentication (Portal Users)", "Notifications (V1)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR3", "FR8"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

