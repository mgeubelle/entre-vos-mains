# Story 2.1: Permettre au patient de consulter son dossier accepte dans le portail

Status: done

## Story

As a patient,
I want consulter mon dossier accepte depuis le portail,
so that je comprenne l'etat de ma prise en charge et les actions disponibles.

## Acceptance Criteria

1. **Given** un patient avec un acces portail actif
   **When** il ouvre son dossier
   **Then** il voit les informations utiles du dossier et son statut
   **And** il peut consulter la liste de ses demandes avec leur date d'introduction, leur statut et les informations de seances pertinentes

2. **Given** un patient qui consulte son dossier
   **When** des seances ont ete autorisees ou deja consommees
   **Then** il voit le nombre de seances autorisees et le suivi utile pour comprendre sa prise en charge
   **And** l'interface reste simple, lisible et en francais

3. **Given** un utilisateur non autorise
   **When** il tente d'acceder au dossier d'un autre patient
   **Then** l'acces est refuse
   **And** aucune information sensible n'est exposee

## Tasks / Subtasks

- [x] Construire la vue portail du dossier patient
- [x] Afficher statuts, compteurs de seances et liste des demandes liees
- [x] Renforcer les controles d'acces portail et verifier l'appui sur les record rules existantes pour l'acces strict au seul dossier du patient
- [x] Verifier lisibilite, libelles francais et absence de fuite d'information

## Dev Notes

- Dependances: Stories 1.7 et 2.3.
- Les compteurs a montrer: `authorized_session_count`, `sessions_consumed` et le reste utile au patient.
- L'UX doit rester sobre, sans scroll horizontal sur parcours critique.
- Cette story suppose que le socle minimal de `evm.payment_request` existe deja pour afficher une liste exploitable des demandes.

### Project Structure Notes

- Fichiers cibles: `addons/evm/controllers/portal.py`, `addons/evm/templates/portal_templates.xml`, eventuellement `models/case.py`.
- Reutiliser les patterns portail Odoo plutot qu'une UI custom.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Story 2.1"]
- [Source: _bmad-output/planning-artifacts/architecture.md - "Project Organization", "UI Language Rule"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR5", "FR6", "FR8"]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log

- Rouge confirme le 2026-03-10 avec `make quality-smoke`: absence des champs `sessions_consumed` / `remaining_session_count` et du rendu portail patient attendu.
- Vert confirme le 2026-03-10 avec `make quality-lint` puis `make quality-smoke`.

### Completion Notes List

- Le detail portail patient affiche maintenant le statut du dossier, la date d'introduction, les compteurs de seances demandes/autorisees/consommees/restantes et une action explicite vers la creation de demande de paiement.
- `evm.case` expose des compteurs calcules `sessions_consumed` et `remaining_session_count`, alimentes uniquement par les demandes `validated` et `paid`.
- Le controle de route patient est renforce avec une verification defensive du couple `patient_user_id` / `state=accepted` avant rendu du detail.
- La couverture de tests est etendue sur le modele de dossier et le portail patient pour les compteurs, les libelles visibles et les redirections sur acces non autorise.

## File List

- addons/evm/controllers/portal.py
- addons/evm/models/evm_case.py
- addons/evm/tests/test_case_consultation.py
- addons/evm/tests/test_patient_payment_request_portal.py
- addons/evm/views/portal_templates.xml
- _bmad-output/implementation-artifacts/2-1-permettre-au-patient-de-consulter-son-dossier-accepte-dans-le-portail.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-03-10: implementation de la story 2.1 avec solde de seances calcule, detail portail patient enrichi et durcissement des controles d'acces.
- 2026-03-10: correctifs de review sur le suivi de solde, la pagination des demandes patient et la clarification des controles d'acces.

## Senior Developer Review (AI)

### Outcome

Approved.

### Findings

- Corrige: le solde de seances restait borne a zero et masquait les depassements. Le detail patient affiche maintenant la valeur reelle et un avertissement lorsqu'un dossier depasse son quota autorise.
- Corrige: la liste des demandes de paiement etait chargee sans pagination depuis le detail patient. Le controleur applique maintenant un pager sur la collection portail.
- Corrige: le detail patient reutilisait un tableau portail responsive susceptible d'introduire un scroll horizontal sur mobile. Le rendu passe sur une liste de cartes empilees sans debordement horizontal.
- Corrige: la task de story sur les controles d'acces a ete clarifiee pour refleter le changement reel du lot, a savoir un durcissement du controleur en complement des record rules deja en place.

### Verification

- `make quality-smoke`
