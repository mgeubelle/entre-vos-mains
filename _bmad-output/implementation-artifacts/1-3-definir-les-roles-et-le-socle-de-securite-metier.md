# Story 1.3: Definir les roles et le socle de securite metier

Status: done

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

- [x] Declarer les groupes Odoo dans `security/groups.xml`
- [x] Introduire le socle des modeles `evm.case` et `evm.payment_request` si necessaire pour porter ACL et record rules
- [x] Ajouter `security/ir.model.access.csv` et des record rules strictes pour preparer les acces par role
- [x] Verifier la separation portail/interne et documenter la matrice d'acces retenue

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

### Debug Log References

- `make quality-lint`
- `make quality-smoke`
- `make quality`

### Implementation Plan

- Introduire des tests Odoo pour verrouiller l'existence des groupes, la separation portail/interne, la matrice ACL et l'isolement des enregistrements par role.
- Ajouter les modeles squelette `evm.case` et `evm.payment_request` avec les champs minimaux requis pour porter ACL et record rules.
- Declarer les groupes metier, les ACL et les record rules strictes dans `addons/evm/security/`, puis charger ces donnees via le manifest.

### Completion Notes List

- Groupes metier Odoo 19 ajoutes dans `addons/evm/security/groups.xml` avec le schema `res.groups.privilege` d'Odoo 19, en separant bien les roles portail (`kine`, `patient`) des roles internes (`fondation`, `admin`).
- Modeles squelette `evm.case` et `evm.payment_request` ajoutes pour porter ACL et record rules, avec les champs minimaux `kine_user_id`, `patient_user_id` et `case_id`.
- Matrice d'acces documentee et implementee:
  - `kine`: `evm.case` = `R/W/C`, `evm.payment_request` = `R`
  - `patient`: `evm.case` = `R`, `evm.payment_request` = `R/W/C/D`
  - `fondation`: acces complet sur les deux modeles
  - `admin`: acces complet sur les deux modeles
- Record rules strictes ajoutees pour limiter `kine` et `patient` a leurs propres dossiers et demandes, avec validation automatisee par tests Odoo.
- Corrections de revue appliquees: alignement explicite des permissions `ir.rule` avec la matrice ACL documentee, extension des tests Odoo pour couvrir les refus `AccessError` sur `create/write/unlink` et mise a jour du manifest pour refleter le socle de securite reellement embarque.
- Validations executees avec succes: `make quality-lint`, `make quality-smoke`, `make quality`.

### File List

- addons/evm/__manifest__.py
- addons/evm/models/__init__.py
- addons/evm/models/evm_case.py
- addons/evm/models/evm_payment_request.py
- addons/evm/security/groups.xml
- addons/evm/security/ir.model.access.csv
- addons/evm/security/rules.xml
- addons/evm/tests/__init__.py
- addons/evm/tests/test_security.py
- _bmad-output/implementation-artifacts/1-3-definir-les-roles-et-le-socle-de-securite-metier.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- 2026-03-08: story prise en charge par l'agent dev et passee au statut `in-progress`.
- 2026-03-08: ajout des groupes metier EVM, des modeles squelette securises, de la matrice ACL et des record rules portail/interne pour `evm.case` et `evm.payment_request`.
- 2026-03-08: corrections de revue appliquees sur la granularite des `ir.rule`, le durcissement des tests de securite et la coherence du manifest; story passee au statut `done`.

## Senior Developer Review (AI)

### Outcome

done

### Notes

- Les permissions operationnelles des record rules portail sont maintenant alignees sur la matrice ACL documentee afin de garder un socle strict meme si les ACL evoluent plus tard.
- Les tests couvrent des cas comportementaux reels: acces limite aux propres enregistrements, refus `AccessError` sur les operations interdites et verification des operations autorisees pour les roles portail/interne.
- Les nouveaux fichiers source de la story ont ete ajoutes a l'index git pour supprimer l'ecart entre le scope revendique dans la story et le scope visible par Git.
