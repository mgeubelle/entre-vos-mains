# Story 1.3: Definir les roles et le socle de securite metier

Status: ready-for-dev

## Story

As a administrateur de la plateforme,
I want les groupes metier et le socle de securite du module configures,
so that chaque acteur dispose d'un role clair avant l'ajout progressif des fonctionnalites metier.

## Acceptance Criteria

1. **Given** le module `evm` installe
   **When** les groupes sont charges
   **Then** les roles `kine`, `patient`, `fondation` et `admin` existent
   **And** les roles `kine` et `patient` sont concus comme roles portail tandis que `fondation` et `admin` sont des roles internes Odoo

2. **Given** un utilisateur affecte a un role
   **When** la configuration de securite du module est verifiee
   **Then** les permissions minimales de lecture, creation, modification et suppression sont definies pour chaque role sur les futurs objets `evm.case` et `evm.payment_request`
   **And** il est explicite que `kine` et `patient` n'ont pas d'acces transverse aux dossiers ou demandes d'autres personnes

## Tasks / Subtasks

- [ ] Declarer les groupes Odoo dans `security/groups.xml`
- [ ] Introduire le socle des modeles `evm.case` et `evm.payment_request` si necessaire pour porter ACL et record rules
- [ ] Ajouter `security/ir.model.access.csv` et des record rules strictes pour preparer les acces par role
- [ ] Verifier la separation portail/interne et documenter la matrice d'acces retenue

## Dev Notes

- Dependances: Stories 1.1 et 1.2.
- L'architecture impose ACL + record rules strictes sur `evm.case`, `evm.payment_request` et plus tard `ir.attachment`.
- Conserver les noms techniques en anglais et les libelles UI en francais.

### Project Structure Notes

- Fichiers cibles: `addons/evm/security/groups.xml`, `addons/evm/security/ir.model.access.csv`, `addons/evm/security/rules.xml`, `addons/evm/models/`.
- Les transitions et details metier riches ne sont pas dans le scope; ici on pose le cadre de securite minimal.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 1.3"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Authentication & Security", "Naming Patterns", "Security Files"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR3", "FR7"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

