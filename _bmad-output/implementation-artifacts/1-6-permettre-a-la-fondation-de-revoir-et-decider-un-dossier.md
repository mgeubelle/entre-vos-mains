# Story 1.6: Permettre a la fondation de revoir et decider un dossier

Status: ready-for-dev

## Story

As a membre de la fondation,
I want examiner un dossier soumis et l'accepter ou le refuser,
so that les demandes legitimes puissent entrer dans le parcours de remboursement.

## Acceptance Criteria

1. **Given** un dossier soumis par un kinesitherapeute
   **When** un membre de la fondation le consulte
   **Then** il voit les informations necessaires a la decision
   **And** il peut accepter ou refuser le dossier via des actions metier explicites

2. **Given** un dossier que la fondation accepte
   **When** la decision est confirmee
   **Then** le dossier passe au statut `accepted`
   **And** le nombre de seances autorisees pour le dossier est fixe de maniere explicite

3. **Given** un dossier que la fondation accepte
   **When** la decision ferait depasser le plafond annuel configure de la fondation
   **Then** le systeme bloque l'acceptation
   **And** la fondation dispose de la visibilite necessaire sur le plafond annuel restant

4. **Given** un dossier que la fondation refuse
   **When** la decision est confirmee
   **Then** le dossier passe au statut `refused`
   **And** la decision reste tracable dans le dossier

5. **Given** une decision d'acceptation ou de refus
   **When** l'action est confirmee
   **Then** le statut du dossier est mis a jour correctement
   **And** une trace est enregistree dans l'historique d'activite

## Tasks / Subtasks

- [ ] Ajouter la vue fondation de revue des dossiers soumis
- [ ] Implementer les actions `action_accept` et `action_refuse` sur `evm.case`
- [ ] Introduire la configuration et le controle du plafond annuel de seances
- [ ] Tracer chaque decision dans l'historique et verifier les garde-fous de statut

## Dev Notes

- Dependances: Stories 1.1 a 1.5.
- `authorized_session_count` ne peut jamais depasser `requested_session_count`.
- La logique de plafond annuel est bloquante a l'acceptation; ne pas la reporter a une story ulterieure.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/case.py`, `addons/evm/views/evm_case_views.xml`, `addons/evm/data/` pour la configuration si necessaire.
- Garder les transitions centralisees dans le modele avec messages d'erreur explicites en francais.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 1.6"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Sessions Tracking", "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR5", "FR9"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`
