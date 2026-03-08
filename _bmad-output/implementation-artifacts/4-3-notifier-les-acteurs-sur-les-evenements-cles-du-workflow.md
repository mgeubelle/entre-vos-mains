# Story 4.3: Notifier les acteurs sur les evenements cles du workflow

Status: ready-for-dev

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

- [ ] Definir les declencheurs et destinataires pour les evenements V1
- [ ] Ajouter les templates email/in-app necessaires
- [ ] Brancher l'emission des notifications sur les actions metier existantes
- [ ] Verifier la coherence entre notification, statut visible et autorisations

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

- Story prete pour execution par `dev-story`

