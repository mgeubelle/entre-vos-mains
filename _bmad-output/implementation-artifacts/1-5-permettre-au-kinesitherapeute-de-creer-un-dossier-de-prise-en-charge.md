# Story 1.5: Permettre au kinesitherapeute de creer un dossier de prise-en-charge

Status: done

## Story

As a kinesitherapeute,
I want creer un dossier de prise en charge pour un patient,
so that je puisse initier une demande d'aide sans friction administrative.

## Acceptance Criteria

1. **Given** un kinesitherapeute autorise
   **When** il cree un nouveau dossier
   **Then** il peut encoder les informations minimales requises
   **And** il peut renseigner le nombre maximum de seances demandees pour le dossier

2. **Given** une demande de prise en charge complete
   **When** le kinesitherapeute la soumet
   **Then** un dossier patient est cree automatiquement avec le statut `pending`
   **And** la demande initiale reste tracable dans l'historique du dossier

3. **Given** un dossier en creation
   **When** des donnees obligatoires sont absentes ou invalides
   **Then** le systeme bloque la soumission
   **And** affiche des messages d'erreur clairs en francais

## Tasks / Subtasks

- [x] Completer `evm.case` avec les champs de creation et les validations minimales
- [x] Construire le formulaire de creation cote kine avec feedback clair en francais
- [x] Implementer l'action metier de soumission vers `pending`
- [x] Tracer la soumission dans l'historique d'activite et tester les cas invalides

## Dev Notes

- Dependances: Stories 1.1 a 1.4.
- `requested_session_count` est saisi ici et doit servir de borne pour la suite du workflow.
- Garder le parcours court et accessible: erreurs proches des champs + resume global si pertinent.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/case.py`, `addons/evm/views/evm_case_views.xml`, composants portail eventuels.
- La transition doit passer par une methode `action_*`, pas par logique inline en vue.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 1.5"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Data Architecture", "Workflow & Traceability Patterns"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR5", "Minimal UX Guardrails For MVP"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Implementation Plan

- Ajouter `patient_name` et `patient_email` sur `evm.case`, centraliser la validation de soumission et normaliser la creation des brouillons.
- Exposer un formulaire portail kine dedie avec erreurs proches des champs, resume global et redirection vers le detail du dossier soumis.
- Etendre les tests modele/portail pour couvrir creation valide, blocage des cas invalides et robustesse des assertions de securite liees au fixture.

### Completion Notes List

- Champs de creation `patient_name` et `patient_email` ajoutes sur `evm.case`, avec validation metier centralisee pour la soumission et nom de dossier aligne sur le patient.
- Parcours portail kine ajoute: CTA "Nouveau dossier", ecran `/my/evm/cases/new`, POST `/my/evm/cases/create`, erreurs FR conservees dans le formulaire.
- Transition `action_submit_to_pending` implementeee avec journalisation chatter de la demande initiale.
- Tests Odoo completes ajoutes ou mis a jour pour le modele, le portail et une assertion de securite rendue independante des donnees globales.
- Correction de revue appliquee: le workflow de soumission est maintenant enforce cote modele pour empecher tout passage direct a `pending` ou `accepted` par ecriture ORM, et les dossiers soumis deviennent non modifiables par le kinesitherapeute.

## File List

- addons/evm/controllers/portal.py
- addons/evm/models/evm_case.py
- addons/evm/tests/test_case_consultation.py
- addons/evm/tests/test_kine_portal.py
- addons/evm/tests/test_security.py
- addons/evm/views/evm_case_views.xml
- addons/evm/views/portal_templates.xml
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-03-08: ajout du parcours de creation de dossier cote kine, de la soumission vers `pending`, des validations FR et des tests associes.
- 2026-03-08: corrections de revue appliquees sur l'integrite du workflow `draft -> pending`, les gardes serveur contre les bypass ORM et les tests de regression; story passee au statut `done`.

## Senior Developer Review (AI)

### Outcome

done

### Notes

- Le workflow de soumission n'est plus contournable par `write({'state': ...})`: les kines sont limites aux brouillons, la transition reste centralisee dans `action_submit_to_pending` et la methode refuse desormais les dossiers non `draft`.
- Les dossiers deja soumis sont figes pour le kinesitherapeute, ce qui preserve les invariants de la story 1.5 et evite de casser la future story 1.6 avec des retours arbitraires vers `pending`.
- Regression couverte par tests sur les bypasss identifies pendant la revue, et validation complete repassee avec succes via `make quality-lint` et `make quality-smoke`.
