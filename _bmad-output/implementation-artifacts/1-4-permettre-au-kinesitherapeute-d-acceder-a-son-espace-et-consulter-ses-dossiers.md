# Story 1.4: Permettre au kinesitherapeute d'acceder a son espace et consulter ses dossiers

Status: ready-for-dev

## Story

As a kinesitherapeute,
I want acceder a mon espace et retrouver les dossiers que j'ai introduits,
so that je puisse suivre mes prises en charge sans voir celles des autres.

## Acceptance Criteria

1. **Given** un kinesitherapeute avec un compte autorise
   **When** il se connecte a l'application
   **Then** il accede a une vue listant uniquement les dossiers qu'il a crees
   **And** chaque ligne affiche au minimum le statut du dossier, la date de creation et l'identite du patient ou son libelle metier autorise

2. **Given** un kinesitherapeute connecte
   **When** il ouvre un dossier qu'il a introduit
   **Then** il peut consulter le statut du dossier, le nombre de seances demandees, le nombre de seances autorisees si renseigne, et l'historique d'activite autorise
   **And** il ne peut pas acceder aux dossiers introduits par un autre kinesitherapeute

## Tasks / Subtasks

- [ ] Finaliser le modele `evm.case` avec les champs minimaux necessaires a la consultation
- [ ] Ajouter les vues liste/detail et, si necessaire, le portail ou menu d'entree pour le role kine
- [ ] Restreindre l'acces via record rules pour n'afficher que les dossiers du kinesitherapeute connecte
- [ ] Verifier les informations visibles et l'absence d'acces transverse

## Dev Notes

- Dependances: Stories 1.1 a 1.3.
- L'interface doit rester simple, en francais, avec statuts et compteurs visibles sans navigation inutile.
- Le tracking/historique peut s'appuyer sur `mail.thread` ou equivalent Odoo retenu dans l'architecture.

### Project Structure Notes

- Fichiers cibles probables: `addons/evm/models/case.py`, `addons/evm/views/evm_case_views.xml`, `addons/evm/controllers/portal.py`, `addons/evm/templates/portal_templates.xml`.
- La logique d'autorisation doit rester cote ORM/record rules, pas seulement dans la vue.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 1.4"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Project Organization", "Authentication & Security", "UI Language Rule"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR6", "FR7"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Completion Notes List

- Story prete pour execution par `dev-story`

