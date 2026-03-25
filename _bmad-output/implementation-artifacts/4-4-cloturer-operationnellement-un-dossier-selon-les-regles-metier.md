# Story 4.4: Cloturer operationnellement un dossier selon les regles metier

Status: done

## Story

As a membre de la fondation,
I want qu'un dossier puisse etre cloture selon les regles prevues,
so that les dossiers termines n'encombrent plus le flux actif et restent historises proprement.

## Acceptance Criteria

1. **Given** un dossier qui remplit les conditions de cloture
   **When** une cloture manuelle ou automatique est declenchee
   **Then** le statut du dossier passe a `closed`
   **And** le dossier n'apparait plus dans les vues de traitement actif tout en restant consultable en lecture

2. **Given** un dossier dont le nombre maximal de seances ou la regle de delai est atteint
   **When** les conditions de cloture sont evaluees
   **Then** le systeme peut considerer le dossier comme eligible a la cloture
   **And** une nouvelle demande doit etre introduite si une nouvelle prise en charge est necessaire

3. **Given** un dossier qui ne remplit pas encore les conditions de cloture
   **When** une tentative de cloture est lancee
   **Then** le systeme refuse ou reporte l'action de maniere coherente
   **And** il preserve l'integrite du workflow

## Tasks / Subtasks

- [x] Definir les conditions d'eligibilite a la cloture sur `evm.case`
- [x] Implementer l'action metier de cloture manuelle
- [x] Exclure les dossiers clos des vues actives tout en les gardant consultables
- [x] Tracer la cloture et tester les cas non eligibles

## Dev Notes

- Dependances: suivi des seances et workflow dossier en place.
- La cloture ne doit pas casser l'historique ni les consultations legitimes.
- Les regles metier combinent au moins seuil de seances et regle de delai definie pour le projet.

### Project Structure Notes

- Fichiers cibles: `addons/evm/models/case.py`, vues dossier, filtres de listes.
- Garder une logique de cloture unique reutilisable par l'action manuelle et le cron.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 4.4"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Automation Boundary (Cron)"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR1", "FR7"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Implementation Notes

- Ajout d'une logique unique de cloture dans `evm.case` avec evaluation reutilisable pour action manuelle et futur cron: quota de seances atteint ou delai projet atteint, avec blocage si une demande de paiement reste active.
- Ajout de `action_close()` et d'une trace chatter rappelant qu'une nouvelle prise en charge exige un nouveau dossier.
- Mise en lecture seule des dossiers clos cote portail tout en conservant l'acces detail patient/kine et l'historique associe.
- Mise a jour des record rules patient pour permettre la consultation des dossiers clos et des demandes associees sans rouvrir les mutations.
- Correctif de revue: delai de cloture sorti du code en dur vers les parametres `res.config.settings`, ajout d'une entree d'auto-cloture via cron Odoo et verrouillage explicite de la route de creation patient sur dossier clos.

### Completion Notes List

- Conditions d'eligibilite a la cloture implementees sur `evm.case` avec seuil de seances, delai projet configurable et blocage des demandes de paiement actives.
- Action metier `action_close()` ajoutee au back-office avec historique chatter et logique mutualisable pour la cloture automatique.
- Vues actives nettoyees des dossiers clos cote back-office, tandis que le portail conserve la consultation via l'onglet `Archives / clotures`; les actions patient restent masquees sur dossier clos.
- Tests ajoutes et verifies pour cloture eligible/non eligible, lecture seule portail, securite patient sur dossiers clos et vues back-office.
- Validations executees: `make reload-evm`, suite Odoo ciblee 9 tests, suite Odoo elargie 124 tests, `make quality-lint`, `make quality-smoke`.
- Correctifs de revue appliques: delai projet configurable via `evm.case_closure_delay_days` (90 jours par defaut, `0` pour desactiver), cron `evm_ir_cron_auto_close_cases` ajoute et route `/my/evm/cases/<id>/payment-requests/new` redirigee vers le detail pour un dossier clos.
- Validations de revue executees: `make reload-evm`, `python3 -m compileall addons/evm/models addons/evm/controllers addons/evm/tests`, suite Odoo ciblee `test_case_review.py` + `test_patient_payment_request_portal.py` (56 tests, 0 echec), `make quality-lint`.

## File List

- addons/evm/__manifest__.py
- addons/evm/controllers/portal.py
- addons/evm/data/scheduled_actions.xml
- addons/evm/models/evm_case.py
- addons/evm/models/evm_payment_request.py
- addons/evm/models/res_config_settings.py
- addons/evm/security/rules.xml
- addons/evm/tests/test_case_review.py
- addons/evm/tests/test_kine_portal.py
- addons/evm/tests/test_patient_payment_request_portal.py
- addons/evm/tests/test_payment_request.py
- addons/evm/tests/test_security.py
- addons/evm/views/evm_case_views.xml
- addons/evm/views/portal_templates.xml
- addons/evm/views/res_config_settings_views.xml

## Senior Developer Review (AI)

- Revue du `2026-03-19`: les ecarts releves sur la cloture automatique, la configurabilite du delai projet et la route patient encore editable sur dossier clos ont ete corriges avant validation.
- Validation finale: `make reload-evm`, `python3 -m compileall addons/evm/models addons/evm/controllers addons/evm/tests`, suite Odoo ciblee `test_case_review.py` + `test_patient_payment_request_portal.py` verte (56 tests), `make quality-lint`.
- Risque residuel accepte: le cron d'auto-cloture est introduit ici pour satisfaire l'AC de cloture automatique, ce qui anticipe partiellement la story 4.5 sans changer la logique metier de fermeture.

## Change Log

- 2026-03-18: implementation de la cloture operationnelle des dossiers, mise en lecture seule des dossiers clos et extension des tests workflow/portail/securite.
- 2026-03-19: correctifs de revue sur la configurabilite du delai de cloture, l'entree cron d'auto-cloture et le verrouillage effectif de la creation patient sur dossier clos.
