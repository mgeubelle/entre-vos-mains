# Story 4.3: Notifier les acteurs sur les evenements cles du workflow

Status: done

## Story

As a patient ou membre de la fondation,
I want recevoir une notification lors des evenements importants,
so that je puisse agir rapidement sans surveiller en permanence la plateforme.

## Acceptance Criteria

1. **Given** un evenement metier notifiable survient
   **When** le workflow correspondant se termine
   **Then** une notification email ou interne est emise au bon destinataire selon la configuration V1
   **And** son contenu indique au minimum l'objet concerne, le nouveau statut ou l'action attendue, et le lien vers le dossier ou la demande si disponible

2. **Given** un utilisateur qui consulte l'objet apres notification
   **When** il ouvre le dossier ou la demande
   **Then** l'etat visible est coherent avec la notification envoyee
   **And** aucune notification n'est emise a un destinataire non autorise

3. **Given** les evenements minimums definis pour la V1 surviennent
   **When** les workflows correspondants se terminent
   **Then** les notifications couvrent au minimum dossier accepte, dossier refuse, demande soumise, demande a completer, demande validee et demande payee
   **And** aucun autre evenement n'est requis pour declarer la V1 complete

## Tasks / Subtasks

- [x] Definir les declencheurs et destinataires pour les evenements V1
- [x] Ajouter les templates email/in-app necessaires
- [x] Brancher l'emission des notifications sur les actions metier existantes
- [x] Verifier la coherence entre notification, statut visible et autorisations

## Dev Notes

- Dependances: transitions metier des epics 1 a 3 disponibles.
- Les canaux V1 retenus dans l'architecture sont email + in-app/chatter.
- Ne pas notifier des utilisateurs non autorises ni multiplier les evenements hors scope.

### Project Structure Notes

- Fichiers cibles: `addons/evm/data/mail_templates.xml`, modeles metier, vues si necessaire.
- Les contenus visibles utilisateur doivent rester en francais.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 4.3"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Notifications (V1)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR10"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Ajout d'un mixin de notification EVM et d'un mapping V1 des declencheurs/destinataires pour `evm.case` et `evm.payment_request`.
- Ajout de templates email generiques pour les notifications dossier/demande avec sujet, statut, action attendue et lien vers le dossier ou la demande.
- Branchement des notifications sur les evenements V1: dossier accepte/refuse, demande soumise, demande a completer, demande validee et demande payee.
- Verification de la coherence portail/ACL via tests metier et portail, avec emission sous `sudo()` pour eviter les regressions de droits sur les effets de bord mail.
- Correctifs de revue appliques: routage des notifications selon le canal configure pour le destinataire et suppression du fallback dangereux vers `patient_email` sans partenaire resolu.
- Verification executee: `python3 -m compileall addons/evm/models/evm_case.py addons/evm/models/evm_payment_request.py addons/evm/models/evm_notification_mixin.py addons/evm/tests/test_case_review.py addons/evm/tests/test_payment_request.py`, `uvx --from 'ruff==0.11.0' ruff check addons/evm/models addons/evm/tests addons/evm/__manifest__.py`, `make reload-evm`, plus une suite Odoo ciblee sur les notifications et le scenario portail de resoumission.

## File List

- addons/evm/__manifest__.py
- addons/evm/data/mail_templates.xml
- addons/evm/models/__init__.py
- addons/evm/models/evm_case.py
- addons/evm/models/evm_notification_mixin.py
- addons/evm/models/evm_payment_request.py
- addons/evm/tests/test_case_review.py
- addons/evm/tests/test_payment_request.py

## Change Log

- 2026-03-18: Added V1 workflow notifications for cases and payment requests, plus regression coverage for portal and mail side effects.
- 2026-03-18: Applied review fixes for recipient channel routing and unauthorized refusal-notification prevention, then marked story done.
