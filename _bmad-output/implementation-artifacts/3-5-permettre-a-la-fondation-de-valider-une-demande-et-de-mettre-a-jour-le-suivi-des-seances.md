# Story 3.5: Permettre a la fondation de valider une demande et de mettre a jour le suivi des seances

Status: ready-for-dev

## Story

As a membre de la fondation,
I want valider une demande de paiement et confirmer les seances retenues,
so that le dossier reste a jour et pret pour le paiement.

## Acceptance Criteria

1. **Given** une demande complete en cours d'instruction
   **When** la fondation la valide
   **Then** elle peut confirmer ou ajuster les donnees utiles a la validation
   **And** le suivi des seances consommees du dossier est mis a jour de maniere coherente

2. **Given** une demande validee
   **When** la mise a jour du dossier est appliquee
   **Then** le systeme preserve la coherence entre `sessions_authorized`, `sessions_consumed` et le solde restant
   **And** le patient peut ensuite retrouver ces informations dans son dossier

3. **Given** une validation qui depasserait les regles du dossier
   **When** la fondation tente de confirmer la demande
   **Then** le systeme bloque ou signale clairement l'incoherence
   **And** evite une mise a jour incorrecte des compteurs

## Tasks / Subtasks

- [ ] Implementer l'action de validation metier de la demande
- [ ] Mettre a jour `sessions_consumed` et le solde restant du dossier
- [ ] Bloquer toute incoherence vis-a-vis de `sessions_authorized`
- [ ] Rendre les compteurs mis a jour visibles cote patient et fondation

## Dev Notes

- Dependances: Stories 3.1 a 3.4.
- La source de verite des seances consommees est la validation de la demande, pas la simple saisie patient.
- Aucun solde negatif ne doit etre possible.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/payment_request.py`, `addons/evm/models/case.py`, vues associees.
- La logique de calcul doit rester centralisee et testable, pas dispersee en plusieurs vues.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 3.5"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Sessions Tracking (V1)", "Core Business Models"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR5", "FR9"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

