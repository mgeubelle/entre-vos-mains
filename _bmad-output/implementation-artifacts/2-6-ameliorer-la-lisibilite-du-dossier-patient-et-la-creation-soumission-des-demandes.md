# Story 2.6: Ameliorer la lisibilite du dossier patient et la creation-soumission des demandes

Status: done

## Story

As a patient,
I want un detail de dossier plus lisible et un parcours de creation de demande plus direct,
so that je puisse comprendre rapidement mes demandes, retrouver les justificatifs associes a chacune et soumettre une nouvelle demande sans friction.

## Acceptance Criteria

1. **Given** un dossier patient avec plusieurs demandes de paiement
   **When** le patient ouvre le detail du dossier
   **Then** les demandes sont presentees sous forme de cartes repliables avec un resume compact
   **And** le detail de chaque demande reste lisible sans surcharger l'ecran

2. **Given** une demande de paiement avec des justificatifs
   **When** le patient consulte le detail du dossier
   **Then** il voit les justificatifs associes directement dans la carte de cette demande
   **And** le bloc agrege "Documents du dossier" est conserve pour la vue transverse
   **And** les demandes non modifiables restent consultables en lecture seule

3. **Given** un patient qui cree une nouvelle demande depuis le portail
   **When** il choisit de l'enregistrer en brouillon
   **Then** il peut joindre des justificatifs des la creation
   **And** la demande est creee en `draft`

4. **Given** un patient qui cree une nouvelle demande depuis le portail
   **When** il choisit "Creer et soumettre"
   **Then** la demande est creee, les justificatifs sont attaches a la bonne demande et la soumission est executee dans le meme parcours
   **And** la demande arrive directement au statut `submitted`

5. **Given** une erreur de validation sur le parcours de creation et soumission directe
   **When** le formulaire est renvoye au patient
   **Then** les messages restent clairs et en francais
   **And** aucun brouillon partiel ni piece jointe orpheline n'est conserve
   **And** la re-selection des fichiers peut etre necessaire

## Tasks / Subtasks

- [x] Repenser la section des demandes de paiement du detail dossier patient en cartes repliables
- [x] Afficher les justificatifs dans chaque demande tout en conservant l'espace documentaire agrege du dossier
- [x] Etendre le formulaire de creation pour accepter des justificatifs et proposer les actions "Enregistrer en brouillon" et "Creer et soumettre"
- [x] Rendre transactionnel le parcours de creation + upload + soumission pour eviter les enregistrements partiels
- [x] Completer la couverture de tests portail sur la nouvelle UI documentaire et le flux de creation-soumission directe

## Dev Notes

- Cette story complete et affine les stories 2.1 a 2.5 sans modifier le modele documentaire de base: les pieces restent rattachees a `evm.payment_request`.
- Le choix UX valide est une presentation en cartes repliables / accordéon, en gardant l'historique documentaire agrege au niveau dossier.
- Le choix technique valide pour les fichiers est l'Option 1: en cas d'erreur de validation, le navigateur peut imposer une re-selection des pieces.
- Le parcours direct "Creer et soumettre" doit rester atomique pour ne pas laisser de brouillon ni d'attachment si l'une des etapes echoue.

### Project Structure Notes

- Fichiers cibles principaux: `addons/evm/controllers/portal.py`, `addons/evm/views/portal_templates.xml`, `addons/evm/tests/test_patient_payment_request_portal.py`.
- Reutiliser les mecanismes portail Odoo et les validations d'upload deja centralisees dans `evm.payment_request`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md - "Epic 2"]
- [Source: _bmad-output/planning-artifacts/prd.md - "FR2", "FR6", "FR8"]
- [Source: discussion de cadrage fonctionnel du 2026-03-18 sur le portail patient]

## Dev Agent Record

### Agent Model Used

GPT-5.4

### Completion Notes List

- Le detail dossier patient affiche maintenant les demandes dans des cartes repliables avec resume, actions et historique regroupes par demande.
- Chaque carte expose ses propres justificatifs avec telechargement, y compris pour les demandes en lecture seule, tandis que le bloc agrege "Documents du dossier" reste disponible.
- Le formulaire de creation permet desormais soit d'enregistrer un brouillon, soit de creer + joindre + soumettre dans le meme POST multipart.
- Le flux direct de creation-soumission est execute dans un `savepoint` pour garantir l'atomicite et eviter les demandes partielles en cas d'erreur de validation.
- Les tests HTTP couvrent la presence de l'espace documentaire par demande, la nouvelle UI de creation et le scenario de creation + justificatif + soumission directe.

## File List

- addons/evm/controllers/portal.py
- addons/evm/views/portal_templates.xml
- addons/evm/tests/test_patient_payment_request_portal.py
- _bmad-output/implementation-artifacts/2-6-ameliorer-la-lisibilite-du-dossier-patient-et-la-creation-soumission-des-demandes.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- _bmad-output/planning-artifacts/epics.md

## Change Log

- 2026-03-18: story ajoutee et implementee pour ameliorer la lisibilite du detail dossier patient, afficher les justificatifs par demande et permettre la creation + upload + soumission directe.
