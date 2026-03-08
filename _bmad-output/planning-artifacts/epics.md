---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - docs/project-context.md
---

# dev - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for dev, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Gestion des dossiers de prise en charge de kinésithérapie avec création, revue, approbation, consultation selon le rôle, suivi et clôture selon les règles métier.
FR2: Gestion sécurisée des documents avec dépôt, accès et validation des factures et pièces justificatives.
FR3: Gestion des utilisateurs et des accès avec rôles distincts pour kinésithérapeutes, patients, membres de la fondation et administrateurs.
FR4: Suivi des paiements avec intégration au module de comptabilité Odoo pour créer et historiser les paiements liés aux demandes.
FR5: Suivi manuel des séances consommées par dossier, alimenté par les demandes de paiement.
FR6: Interface très simple et accessible pour tous les âges, y compris les personnes âgées et avec déficiences motrices, en minimisant les clics inutiles.
FR7: Sécurité et conformité avec protection des données, contrôle d’accès, traçabilité des actions, respect du GDPR et du contexte belge.
FR8: Portail patient avec accès sécurisé au dossier après acceptation, consultation du dossier, dépôt de factures/justificatifs et création de demandes de paiement.
FR9: Traitement par la fondation des dossiers et demandes avec validation, demandes d’informations complémentaires, commentaires et suivi opérationnel.
FR10: Communication asynchrone via notes, commentaires, historique d'activite et notifications sur les événements clés du dossier et des demandes.

### NonFunctional Requirements

NFR1: Les écrans liste, détail et actions métier usuelles doivent charger ou confirmer en moins de 2 secondes pour 95 % des actions en heures ouvrées, hors temps de transfert des fichiers.
NFR2: La plateforme doit viser une disponibilité d’au moins 99,5 % pendant les heures ouvrées, hors fenêtres de maintenance planifiées.
NFR3: Les données sensibles et les documents doivent être protégés par un contrôle d’accès strict, une journalisation appropriée et des échanges sécurisés.
NFR4: L’application doit respecter les exigences de confidentialité belges et GDPR, avec une minimisation des données sensibles stockées.
NFR5: L’interface doit être utilisable par des personnes âgées et des personnes avec déficiences motrices, respecter WCAG 2.2 AA sur les parcours MVP critiques, et conserver des parcours courts.
NFR6: La solution doit fonctionner sur Chrome, Firefox, Safari et les principaux navigateurs modernes.
NFR7: L’intégration avec Odoo Community 19 et le module Accounting doit être fiable, sécurisée et sans automatisation bancaire.
NFR8: La plateforme doit supporter au moins 50 utilisateurs simultanés et 10 000 dossiers ou demandes historisés sans dégradation perceptible sur les parcours MVP.
NFR9: L’architecture doit rester simple, idiomatique Odoo 19, maintenable et alignée avec le principe KISS.
NFR10: L’interface visible utilisateur doit être en français, tandis que le code et les identifiants techniques restent en anglais.

### Additional Requirements

- Le projet est un add-on Odoo 19 Community dans une application MPA, sans front séparé, sans besoin SEO ni temps réel.
- Un starter template est explicitement défini : scaffold officiel Odoo via `odoo-bin scaffold`, complété par un outillage qualité minimal. Cela doit orienter l’Epic 1 Story 1.
- Le module principal cible est `addons/evm` avec conventions de nommage `evm_` pour les `xml_id`.
- Les modèles métier principaux sont `evm.case` pour le dossier et `evm.payment_request` pour la demande de paiement.
- Les pièces jointes doivent utiliser `ir.attachment` avec filestore local Odoo, rattachées aux `evm.payment_request`, avec une vue agrégée des documents du dossier.
- Le suivi des séances V1 est piloté par les champs `sessions_requested`, `sessions_authorized`, `sessions_consumed` au niveau dossier et `sessions_count` au niveau demande, sans saisie séance-par-séance.
- `sessions_requested` est saisi par le kiné lors de la création du dossier; `sessions_authorized` est fixé par la fondation lors de l'acceptation, sans dépasser la demande initiale.
- Un plafond annuel global de séances couvertes par la fondation doit être configurable dans l'application et pris en compte dans le traitement métier.
- La création d’un `account.payment` en brouillon doit intervenir au statut demande validée, avec lien explicite `payment_id` et garde-fou d’idempotence pour éviter les doublons.
- Les paiements restent réalisés hors plateforme; le statut payé est confirmé dans l’application mais le posting comptable peut rester manuel en V1.
- Les kinésithérapeutes et les patients utilisent des comptes portail Odoo; seuls les membres de la fondation et les administrateurs utilisent des comptes internes Odoo.
- L’autorisation doit reposer sur des groupes Odoo, ACL et record rules strictes pour `evm.case`, `evm.payment_request` et les pièces jointes.
- Les règles d'upload V1 sont: types autorisés `pdf`, `jpg`, `jpeg`, `png`; taille maximale 10 Mo par fichier; multi-fichiers autorisé; pas d'écrasement en place, chaque nouveau fichier ajoute une nouvelle pièce jointe pour préserver l'historique.
- Les transitions métier doivent passer par des méthodes `action_*` et publier des traces dans l'historique d'activite sur les changements importants.
- Les notifications V1 doivent couvrir au minimum les événements dossier accepté/refusé, demande soumise, demande à compléter, demande validée et demande payée.
- Une auto-clôture des dossiers via cron est prévue après une durée définie par les règles métier.
- Les vues, menus, aides et messages utilisateur doivent être en français; les valeurs techniques, noms de méthodes et champs restent en anglais.
- Le site statique existant sera intégré dans une page `website` en fin de projet, hors cœur du MVP métier.
- Les exigences de conformité incluent l’évitement du stockage structuré de données médicales; les factures servent de preuve principale et le code INAMI peut n’apparaître que dans les documents.
- Les politiques automatisées de rétention, suppression et anonymisation sont explicitement hors scope V1.
- La cible d'accessibilite MVP est WCAG 2.2 AA sur les parcours critiques: creation de dossier cote kine, consultation du dossier et soumission de demande cote patient, revue dossier et revue demande cote fondation.

### FR Coverage Map

FR1: Epic 1 et Epic 3 et Epic 4 - cycle de vie du dossier, traitement métier et cloture
FR2: Epic 2 - depot, acces et validation documentaire cote patient/demande
FR3: Epic 1 - roles, groupes, acces securises et activation des acteurs
FR4: Epic 3 - integration comptable et historique de paiement
FR5: Epic 3 - suivi manuel des seances consommees
FR6: Epic 1 et Epic 2 - simplicite d'usage sur parcours de creation et portail patient
FR7: Epic 1 et Epic 4 - securite d'acces, conformite et auditabilite
FR8: Epic 2 - portail patient et soumission de demandes
FR9: Epic 3 - traitement operationnel par la fondation
FR10: Epic 4 - commentaires, historique d'activite et notifications

## Epic List

## Implementation Prerequisites

Les elements suivants sont des prerequis obligatoires a traiter avant le demarrage des stories fonctionnelles de l'Epic 1.

- Enabling Item 1.1: Initialiser le module EVM et l'environnement local Docker
- Enabling Item 1.2: Mettre en place le pipeline qualite minimal

### Blocking Rule

- Aucune story fonctionnelle de l'Epic 1, de l'Epic 2, de l'Epic 3 ou de l'Epic 4 ne doit commencer tant que les Enabling Items 1.1 et 1.2 ne sont pas termines.
- Lors de la planification de sprint, ces enabling items doivent etre estimes, suivis et marques comme prerequis de demarrage.
- Si l'un de ces enabling items n'est pas termine, les stories fonctionnelles dependantes doivent etre considerees comme bloquees.

### Epic 1: Soumettre et ouvrir un dossier de prise en charge
Le kinesitherapeute peut creer un dossier, la fondation peut le revoir et l'accepter ou le refuser, et la plateforme met en place les acces et le cadre securise minimal pour demarrer le parcours.
**FRs covered:** FR1, FR3, FR6, FR7

### Epic 2: Permettre au patient de gerer sa demande de remboursement
Le patient peut acceder a son dossier accepte, deposer ses factures et justificatifs, puis soumettre des demandes de paiement dans un parcours simple et accessible.
**FRs covered:** FR2, FR6, FR8

### Epic 3: Instruire les demandes et suivre les paiements
La fondation peut examiner les demandes de paiement, demander des complements, valider les montants, suivre les seances consommees et tracer le paiement dans Odoo.
**FRs covered:** FR1, FR4, FR5, FR9

### Epic 4: Assurer la tracabilite et la fluidite operationnelle
Tous les acteurs beneficient de commentaires, notifications, journalisation des actions et cloture operationnelle des dossiers pour securiser l'exploitation au quotidien.
**FRs covered:** FR1, FR7, FR10

## Epic 1: Soumettre et ouvrir un dossier de prise en charge

Le kinesitherapeute peut creer un dossier, la fondation peut le revoir et l'accepter ou le refuser, et la plateforme met en place les acces et le cadre securise minimal pour demarrer le parcours.

### Enabling Stories (prerequis obligatoires)

### Story 1.1: Initialiser le module EVM et l'environnement local Docker

- Type: enabling story technique a terminer avant toute story fonctionnelle.

- Objectif: fournir un socle technique executable pour permettre l'implementation des user stories de l'Epic 1.

**Given** un poste de developpement avec Docker
**When** je demarre l'environnement local
**Then** une instance Odoo 19 avec la base de developpement demarre correctement
**And** le module `evm` peut etre installe sans erreur

**Given** le depot du projet
**When** je consulte le module `evm`
**Then** sa structure suit les conventions Odoo retenues dans l'architecture
**And** le chargement local permet de verifier que le socle est pret pour les stories suivantes

### Story 1.2: Mettre en place le pipeline qualite minimal

- Type: enabling story technique a terminer avant toute story fonctionnelle.

- Objectif: garantir un socle de qualite greenfield avant l'implementation fonctionnelle.

**Given** le depot du projet
**When** le pipeline qualite minimal est configure
**Then** les commandes de verification retenues pour le projet peuvent s'executer automatiquement
**And** leur usage est documente pour l'equipe

**Given** une modification sur le module `evm`
**When** l'equipe lance les controles locaux prevus
**Then** elle peut verifier au minimum le linting ou les tests de base retenus
**And** un echec de controle est visible avant fusion

### Story 1.3: Definir les roles et le socle de securite metier

As a administrateur de la plateforme,
I want les groupes metier et le socle de securite du module configures,
So that chaque acteur puisse etre rattache a un role clair avant l'ajout progressif des fonctionnalites metier.

**Acceptance Criteria:**

**Given** le module `evm` installe
**When** les groupes sont charges
**Then** les roles `kine`, `patient`, `fondation` et `admin` existent
**And** les roles `kine` et `patient` sont concus comme roles portail tandis que `fondation` et `admin` sont des roles internes Odoo

**Given** un utilisateur affecte a un role
**When** la configuration de securite du module est verifiee
**Then** les permissions minimales de lecture, creation, modification et suppression sont definies pour chaque role sur les futurs objets `evm.case` et `evm.payment_request`
**And** il est explicite que `kine` et `patient` n'ont pas d'acces transverse aux dossiers ou demandes d'autres personnes

### Story 1.4: Permettre au kinesitherapeute d'acceder a son espace et consulter ses dossiers

As a kinesitherapeute,
I want acceder a mon espace et retrouver les dossiers que j'ai introduits,
So that je puisse soumettre de nouvelles demandes et suivre les prises en charge deja lancees.

**Acceptance Criteria:**

**Given** un kinesitherapeute avec un compte autorise
**When** il se connecte a l'application
**Then** il accede a une vue listant uniquement les dossiers qu'il a crees
**And** chaque ligne affiche au minimum le statut du dossier, la date de creation et l'identite du patient ou son libelle metier autorise

**Given** un kinesitherapeute connecte
**When** il ouvre un dossier qu'il a introduit
**Then** il peut consulter le statut du dossier, le nombre de seances demandees, le nombre de seances autorisees si renseigne, et l'historique d'activite autorise
**And** il ne peut pas acceder aux dossiers introduits par un autre kinesitherapeute

### Story 1.5: Permettre au kinesitherapeute de creer un dossier de prise en charge

As a kinesitherapeute,
I want creer un dossier de prise en charge pour un patient,
So that je puisse initier une demande d'aide sans friction administrative.

**Acceptance Criteria:**

**Given** un kinesitherapeute autorise
**When** il cree un nouveau dossier
**Then** il peut encoder les informations minimales requises
**And** il peut renseigner le nombre maximum de seances demandees pour le dossier

**Given** une demande de prise en charge complete
**When** le kinesitherapeute la soumet
**Then** un dossier patient est cree automatiquement avec le statut `pending`
**And** la demande initiale reste tracable dans l'historique du dossier

**Given** un dossier en creation
**When** des donnees obligatoires sont absentes ou invalides
**Then** le systeme bloque la soumission
**And** affiche des messages d'erreur clairs en francais

### Story 1.6: Permettre a la fondation de revoir et decider un dossier

As a membre de la fondation,
I want examiner un dossier soumis et l'accepter ou le refuser,
So that les demandes legitimes puissent entrer dans le parcours de remboursement.

**Acceptance Criteria:**

**Given** un dossier soumis par un kinesitherapeute
**When** un membre de la fondation le consulte
**Then** il voit les informations necessaires a la decision
**And** il peut accepter ou refuser le dossier via des actions metier explicites

**Given** un dossier que la fondation accepte
**When** la decision est confirmee
**Then** le dossier passe au statut `accepted`
**And** le nombre de seances autorisees pour le dossier est fixe de maniere explicite

**Given** un dossier que la fondation accepte
**When** la decision ferait depasser le plafond annuel configure de la fondation
**Then** le systeme bloque l'acceptation
**And** la fondation dispose de la visibilite necessaire sur le plafond annuel restant

**Given** un dossier que la fondation refuse
**When** la decision est confirmee
**Then** le dossier passe au statut `refused`
**And** la decision reste tracable dans le dossier

**Given** une decision d'acceptation ou de refus
**When** l'action est confirmee
**Then** le statut du dossier est mis a jour correctement
**And** une trace est enregistree dans l'historique d'activite

### Story 1.7: Ouvrir l'acces patient apres acceptation du dossier

As a patient,
I want recevoir un acces securise a mon dossier une fois accepte,
So that je puisse ensuite suivre mon dossier et preparer mes futures demandes.

**Acceptance Criteria:**

**Given** un dossier accepte par la fondation
**When** le processus d'activation patient est execute
**Then** un acces portail patient est cree ou active selon les regles definies
**And** cet acces n'est pas disponible avant acceptation

**Given** un patient dont l'acces vient d'etre active
**When** il recoit l'invitation ou les informations de connexion
**Then** il peut se connecter au portail de maniere securisee
**And** le dossier accepte devient accessible pour les stories du portail patient de l'Epic 2

## Epic 2: Permettre au patient de gerer sa demande de remboursement

Le patient peut acceder a son dossier accepte, deposer ses factures et justificatifs, puis soumettre des demandes de paiement dans un parcours simple et accessible.

### Story 2.1: Permettre au patient de consulter son dossier accepte dans le portail

As a patient,
I want consulter mon dossier accepte depuis le portail,
So that je comprenne facilement l'etat de ma prise en charge et les actions disponibles.

**Acceptance Criteria:**

**Given** un patient avec un acces portail actif
**When** il ouvre son dossier
**Then** il voit les informations utiles du dossier et son statut
**And** il peut consulter la liste de ses demandes avec leur date d'introduction, leur statut et les informations de seances pertinentes

**Given** un patient qui consulte son dossier
**When** des seances ont ete autorisees ou deja consommees
**Then** il voit le nombre de seances autorisees et le suivi utile pour comprendre sa prise en charge
**And** l'interface reste simple, lisible et en francais

**Given** un utilisateur non autorise
**When** il tente d'acceder au dossier d'un autre patient
**Then** l'acces est refuse
**And** aucune information sensible n'est exposee

### Story 2.2: Permettre au patient de consulter l'espace documentaire de son dossier

As a patient,
I want acceder a l'espace documentaire de mon dossier,
So that je puisse retrouver les pieces deja partagees et comprendre l'historique documentaire de ma prise en charge.

**Acceptance Criteria:**

**Given** un patient connecte sur son dossier
**When** il ouvre l'espace documentaire
**Then** il voit les documents associes a ses demandes de paiement
**And** l'historique documentaire reste consultable de maniere simple et securisee

**Given** un document rattache a une demande de paiement
**When** le patient consulte le dossier
**Then** le document apparait dans la vue agregée du dossier
**And** un utilisateur non autorise ne peut ni le voir ni y acceder

### Story 2.3: Permettre au patient de creer une demande de paiement

As a patient,
I want creer une demande de paiement associee a mon dossier,
So that je puisse solliciter un remboursement sur base de mes justificatifs.

**Acceptance Criteria:**

**Given** un dossier accepte et accessible par le patient
**When** il cree une nouvelle demande de paiement
**Then** il peut encoder les informations minimales requises, y compris le nombre de seances concernees
**And** il peut renseigner un montant total a payer lorsque cette information est disponible sans le rendre obligatoire en V1
**And** la demande est enregistree avec un statut initial explicite

**Given** une demande incomplete
**When** le patient tente de la soumettre
**Then** le systeme bloque la soumission
**And** indique clairement les informations manquantes

### Story 2.4: Permettre au patient de deposer des factures et justificatifs sur une demande

As a patient,
I want deposer des factures et justificatifs lies a une demande de paiement,
So that la fondation puisse verifier les pieces necessaires au remboursement.

**Acceptance Criteria:**

**Given** un patient sur une demande de paiement autorisee
**When** il ajoute des documents
**Then** les fichiers sont enregistres de maniere securisee via les mecanismes Odoo prevus
**And** ils sont relies a la bonne demande

**Given** un patient qui charge des pieces justificatives
**When** les fichiers sont verifies
**Then** seuls les formats `pdf`, `jpg`, `jpeg` et `png` sont acceptes
**And** chaque fichier ne depasse pas 10 Mo

**Given** un patient qui depose plusieurs documents pour une meme demande
**When** l'upload est valide
**Then** plusieurs fichiers peuvent etre attaches a la meme demande
**And** un nouveau fichier n'ecrase pas un document existant mais s'ajoute a l'historique

**Given** un document ajoute a une demande
**When** le patient revient sur son dossier
**Then** le document est visible dans l'espace documentaire du dossier
**And** son historique de presence est conserve

**Given** un fichier invalide ou une tentative non autorisee
**When** le depot est effectue
**Then** le systeme refuse l'operation
**And** affiche un message clair en francais

### Story 2.5: Permettre au patient de soumettre une demande complete a la fondation

As a patient,
I want soumettre ma demande de paiement complete,
So that la fondation puisse commencer son instruction.

**Acceptance Criteria:**

**Given** une demande de paiement complete avec ses pieces
**When** le patient la soumet
**Then** son statut passe a un etat de demande soumise
**And** la fondation peut la retrouver dans son flux de traitement

**Given** une demande sans les elements requis
**When** le patient tente de la soumettre
**Then** la soumission est refusee
**And** les erreurs sont presentees de facon simple et exploitable

## Epic 3: Instruire les demandes et suivre les paiements

La fondation peut examiner les demandes de paiement, demander des complements, valider les montants, suivre les seances consommees et tracer le paiement dans Odoo.

### Story 3.1: Permettre a la fondation de consulter la file des demandes de paiement soumises

As a membre de la fondation,
I want voir les demandes de paiement a instruire et leurs informations essentielles,
So that je puisse traiter les dossiers en attente de maniere efficace.

**Acceptance Criteria:**

**Given** des demandes de paiement soumises existent
**When** un membre de la fondation ouvre la vue de traitement
**Then** il voit la liste des demandes pertinentes avec au minimum le dossier lie, le patient, la date de soumission, le statut, le montant demande s'il existe, et le nombre de seances declarees
**And** il peut acceder au detail d'une demande autorisee

**Given** un utilisateur non autorise
**When** il tente d'acceder a cette file de traitement
**Then** l'acces est refuse
**And** aucune donnee sensible n'est exposee

### Story 3.2: Permettre a la fondation de retourner une demande a completer

As a membre de la fondation,
I want renvoyer une demande incomplete au patient avec un motif clair,
So that le patient puisse fournir les informations ou justificatifs manquants.

**Acceptance Criteria:**

**Given** une demande en cours d'instruction
**When** la fondation estime qu'elle est incomplete
**Then** elle peut la passer au statut `to_complete`
**And** un motif exploitable est enregistre pour le patient

**Given** une demande retournee a completer
**When** son historique est consulte
**Then** la transition et son motif sont tracables
**And** la demande peut etre reprise plus tard apres complementation

### Story 3.3: Permettre au patient de suivre et completer une demande retournee par la fondation

As a patient,
I want voir si ma demande doit etre completee,
So that je puisse fournir rapidement les informations ou documents manquants.

**Acceptance Criteria:**

**Given** une demande renvoyee a completer par la fondation
**When** le patient consulte le portail
**Then** il voit clairement que la demande requiert une action
**And** il peut identifier les informations ou documents attendus

**Given** une demande a completer
**When** le patient ajoute les elements manquants et la renvoie
**Then** la demande repasse dans un etat permettant une nouvelle revue
**And** l'historique de l'echange reste tracable

### Story 3.4: Permettre a la fondation de refuser une demande de paiement

As a membre de la fondation,
I want refuser une demande de paiement lorsqu'elle n'est pas recevable,
So that le workflow de la demande reste coherent et trace jusqu'a sa sortie finale.

**Acceptance Criteria:**

**Given** une demande en cours d'instruction
**When** la fondation decide qu'elle ne peut pas etre acceptee
**Then** elle peut la passer au statut `refused`
**And** le motif du refus est enregistre de maniere exploitable

**Given** une demande refusee
**When** son historique est consulte
**Then** le statut final et son motif sont visibles
**And** la demande n'apparait plus comme element a traiter dans la file active

### Story 3.5: Permettre a la fondation de valider une demande et de mettre a jour le suivi des seances

As a membre de la fondation,
I want valider une demande de paiement et confirmer les seances retenues,
So that le dossier reste a jour et pret pour le paiement.

**Acceptance Criteria:**

**Given** une demande complete en cours d'instruction
**When** la fondation la valide
**Then** elle peut confirmer ou ajuster les donnees utiles a la validation
**And** le suivi des seances consommees du dossier est mis a jour de maniere coherente

**Given** une demande validee
**When** la mise a jour du dossier est appliquee
**Then** le systeme preserve la coherence entre `sessions_authorized`, `sessions_consumed` et le solde restant
**And** le patient peut ensuite retrouver ces informations dans son dossier

**Given** une validation qui depasserait les regles du dossier
**When** la fondation tente de confirmer la demande
**Then** le systeme bloque ou signale clairement l'incoherence
**And** evite une mise a jour incorrecte des compteurs

### Story 3.6: Creer et lier un paiement Odoo brouillon a une demande validee

As a membre de la fondation,
I want qu'un `account.payment` brouillon soit cree pour une demande validee,
So that le suivi comptable du paiement soit assure dans Odoo.

**Acceptance Criteria:**

**Given** une demande validee sans paiement lie
**When** la transition metier prevue est executee
**Then** un `account.payment` brouillon est cree et lie a la demande
**And** les informations necessaires a la tracabilite sont conservees

**Given** une demande possedant deja un `payment_id`
**When** une nouvelle creation de paiement est tentee
**Then** aucun doublon n'est cree
**And** le garde-fou d'idempotence est respecte

### Story 3.7: Permettre a la fondation de confirmer un paiement effectue hors plateforme

As a membre de la fondation,
I want marquer une demande comme payee apres confirmation du paiement externe,
So that le dossier reflete correctement l'etat reel du remboursement.

**Acceptance Criteria:**

**Given** une demande avec un paiement Odoo lie
**When** la fondation confirme que le paiement a ete effectue hors plateforme
**Then** la demande passe au statut `paid`
**And** la trace de confirmation est conservee dans le dossier

**Given** une demande non validee ou sans paiement lie
**When** un utilisateur tente de la marquer comme payee
**Then** l'action est refusee
**And** un message clair explique pourquoi

## Epic 4: Assurer la tracabilite et la fluidite operationnelle

Tous les acteurs beneficient de commentaires, notifications, journalisation des actions via un historique d'activite et cloture operationnelle des dossiers pour securiser l'exploitation au quotidien.

### Story 4.1: Permettre les commentaires et echanges asynchrones sur les dossiers et demandes

As a patient ou membre de la fondation,
I want ajouter des commentaires et notes sur un dossier ou une demande,
So that les echanges restent centralises et exploitables sans recourir a des emails disperses.

**Acceptance Criteria:**

**Given** un dossier ou une demande accessible a un utilisateur autorise
**When** il ajoute un commentaire via les mecanismes prevus
**Then** le commentaire est enregistre sur le bon objet
**And** il reste visible aux acteurs autorises selon les regles metier

**Given** un patient ou un membre de la fondation autorise
**When** il consulte une demande
**Then** il peut y retrouver l'espace de notes pertinent au suivi
**And** les echanges restent historises dans le dossier ou la demande

**Given** un utilisateur non autorise
**When** il tente de consulter ou poster un commentaire
**Then** l'acces ou l'action est refuse
**And** aucune information sensible n'est exposee

### Story 4.2: Journaliser automatiquement les transitions metier importantes

As a membre de la fondation,
I want que les changements importants soient traces automatiquement,
So that je puisse auditer les decisions et suivre l'historique d'un dossier sans ambiguite.

**Acceptance Criteria:**

**Given** une transition importante de dossier ou de demande
**When** l'action metier est executee
**Then** un message systeme est enregistre dans l'historique d'activite
**And** les champs suivis pertinents conservent leur historique

**Given** une consultation ulterieure du dossier ou de la demande
**When** un utilisateur autorise ouvre l'historique
**Then** il peut comprendre les principales decisions et changements d'etat
**And** les traces sont presentees de maniere lisible

### Story 4.3: Notifier les acteurs sur les evenements cles du workflow

As a patient ou membre de la fondation,
I want recevoir une notification lors des evenements importants,
So that je puisse agir rapidement sans surveiller en permanence la plateforme.

**Acceptance Criteria:**

**Given** un evenement metier notifiable survient
**When** le workflow correspondant se termine
**Then** une notification email ou interne est emise au bon destinataire selon la configuration V1
**And** son contenu indique au minimum l'objet concerne, le nouveau statut ou l'action attendue, et le lien vers le dossier ou la demande si disponible

**Given** un utilisateur qui consulte l'objet apres notification
**When** il ouvre le dossier ou la demande
**Then** l'etat visible est coherent avec la notification envoyee
**And** aucune notification n'est emise a un destinataire non autorise

**Given** les evenements minimums definis pour la V1 surviennent
**When** les workflows correspondants se terminent
**Then** les notifications couvrent au minimum dossier accepte, dossier refuse, demande soumise, demande a completer, demande validee et demande payee
**And** aucun autre evenement n'est requis pour declarer la V1 complete

### Story 4.4: Cloturer operationnellement un dossier selon les regles metier

As a membre de la fondation,
I want qu'un dossier puisse etre cloture selon les regles prevues,
So that les dossiers termines n'encombrent plus le flux actif et restent historises proprement.

**Acceptance Criteria:**

**Given** un dossier qui remplit les conditions de cloture
**When** une cloture manuelle ou automatique est declenchee
**Then** le statut du dossier passe a `closed`
**And** le dossier n'apparait plus dans les vues de traitement actif tout en restant consultable en lecture

**Given** un dossier dont le nombre maximal de seances ou la regle de delai est atteint
**When** les conditions de cloture sont evaluees
**Then** le systeme peut considerer le dossier comme eligible a la cloture
**And** une nouvelle demande doit etre introduite si une nouvelle prise en charge est necessaire

**Given** un dossier qui ne remplit pas encore les conditions de cloture
**When** une tentative de cloture est lancee
**Then** le systeme refuse ou reporte l'action de maniere coherente
**And** il preserve l'integrite du workflow

### Story 4.5: Executer une cloture automatique des dossiers via tache planifiee

As a administrateur de la plateforme,
I want une tache planifiee qui applique les regles d'auto-cloture,
So that la plateforme reste propre operationnellement sans intervention manuelle systematique.

**Acceptance Criteria:**

**Given** des dossiers eligibles a l'auto-cloture existent
**When** la tache planifiee s'execute
**Then** seuls les dossiers qui respectent les regles definies sont clotures
**And** chaque cloture automatique laisse une trace exploitable

**Given** un dossier non eligible
**When** la tache planifiee l'evalue
**Then** il n'est pas cloture par erreur
**And** aucune regression n'est introduite sur les dossiers encore actifs
