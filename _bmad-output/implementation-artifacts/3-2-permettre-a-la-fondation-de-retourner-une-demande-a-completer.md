# Story 3.2: Permettre a la fondation de retourner une demande a completer

Status: ready-for-dev

## Story

As a membre de la fondation,
I want renvoyer une demande incomplete au patient avec un motif clair,
so that le patient puisse fournir les informations ou justificatifs manquants.

## Acceptance Criteria

1. **Given** une demande en cours d'instruction
   **When** la fondation estime qu'elle est incomplete
   **Then** elle peut la passer au statut `to_complete`
   **And** un motif exploitable est enregistre pour le patient

2. **Given** une demande retournee a completer
   **When** son historique est consulte
   **Then** la transition et son motif sont tracables
   **And** la demande peut etre reprise plus tard apres complementation

## Tasks / Subtasks

- [ ] Ajouter le champ ou mecanisme de motif de retour
- [ ] Implementer l'action metier vers `to_complete`
- [ ] Rendre le motif visible au patient sur le portail
- [ ] Tracer la transition dans l'historique et tester la reprise ulterieure

## Dev Notes

- Dependances: Story 3.1.
- Le motif doit etre exploitable par le patient; eviter les formulations internes opaques.
- La demande doit rester dans un workflow coherent, sans creation de doublon.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, vues fondation et portail patient.
- Les transitions se font via methode `action_*` avec controle de statut entrant.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.2"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR9", "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

