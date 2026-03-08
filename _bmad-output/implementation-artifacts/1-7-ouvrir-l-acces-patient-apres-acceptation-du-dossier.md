# Story 1.7: Ouvrir l'acces patient apres acceptation du dossier

Status: done

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

- [x] Definir le lien patient sur `evm.case` et la regle d'activation portail
- [x] Implementer la creation/activation du compte portail lors de l'acceptation
- [x] Assurer que l'acces patient est impossible tant que le dossier n'est pas `accepted`
- [x] Envoyer ou preparer l'invitation/notifier le patient selon les mecanismes retenus en V1

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

- Ajout de `patient_partner_id` sur `evm.case` et encapsulation de l'activation portail patient dans le workflow d'acceptation.
- Reutilisation du mecanisme standard Odoo `portal.wizard` pour creer ou reactiver le compte portail patient, ajouter le groupe `evm.group_evm_patient` et preparer l'invitation securisee.
- Durcissement des record rules patient pour limiter l'acces aux seuls dossiers et demandes lies a un dossier `accepted`.
- Validation executee avec `./scripts/quality-check.sh smoke` puis `./scripts/quality-check.sh lint`.

## File List

- addons/evm/models/evm_case.py
- addons/evm/security/rules.xml
- addons/evm/tests/test_case_review.py
- addons/evm/tests/test_security.py
- addons/evm/views/evm_case_views.xml

## Change Log

- 2026-03-08: activation automatique du portail patient a l'acceptation, invitation standard Odoo et verrouillage de l'acces avant `accepted`.
- 2026-03-08: code review adverse realisee; acceptation rendue atomique, blocage des reutilisations d'identite ambigues et ajout des tests de non-regression sur l'activation portail patient.

## Senior Developer Review (AI)

### Outcome

Approved after fixes.

### Findings

- High: `action_accept()` ecrivait le statut `accepted` avant de verifier que l'activation portail patient aboutissait. En cas d'echec sur le wizard portail, le dossier pouvait rester accepte sans acces patient valide dans la meme transaction. Corrige en rendant l'acceptation atomique via savepoint et en n'ecrivant l'etat qu'apres succes de l'activation.
- High: l'activation portail reutilisait n'importe quel compte portail non interne partageant le meme email, y compris un compte `kine`, puis lui ajoutait le role patient. Cela melangeait les roles et pouvait exposer un dossier patient au mauvais acteur. Corrige en bloquant explicitement la reutilisation d'un compte kinesitherapeute.
- High: quand un contact existant portait deja un utilisateur avec un login different de l'email du dossier, le workflow reutilisait quand meme ce contact puis rattachait le dossier a cet utilisateur. Cela ouvrait le dossier au mauvais compte portail. Corrige en refusant les contacts deja lies a un login different de l'email patient saisi.

### Verification

- `./scripts/quality-check.sh lint`
- `./scripts/quality-check.sh smoke`
