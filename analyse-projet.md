# Scope MVP

# **Scope MVP “Entre Vos Mains”**

## **1\. Contexte du projet**

La fondation souhaite mettre en place une première plateforme numérique simple permettant de soutenir financièrement des patients nécessitant des soins de kinésithérapie, tout en garantissant un usage approprié des fonds.

Le projet s’inscrit dans un contexte de :

* surcharge des kinésithérapeutes  
* coûts élevés pour les patients  
* volonté de la fondation de subventionner les séances des patients

La solution envisagée repose sur Odoo (version Community), avec une approche volontairement pragmatique et progressive.

## **2\. Objectif du MVP**

L’objectif du MVP (Minimum Viable Product) est de permettre de :

* introduire des demandes de prise en charge par des kinésithérapeutes  
* valider ces demandes par la fondation  
* créer un dossier patient avec accès sécurisé  
* permettre au patient de fournir des preuves (factures / justificatifs)  
* permettre à la fondation de valider et de procéder au paiement (hors plateforme)  
* permettre à la fondation d'avoir un suivi des paiements (réalisés hors plateforme)

Le MVP doit être :

* simple d’utilisation (patients, kinés et fondation)  
* limité en données sensibles  
* opérationnel rapidement  
* sans automatisations financières

## **3\. Acteurs concernés**

* **Kiné :** introduit la demande de prise en charge d’un patient  
* **Fondation** : valide les dossiers, contrôle les preuves, effectue les paiements  
* **Patient** : consulte son dossier, fournit les justificatifs nécessaires

## 

## **4\. Fonctionnalités incluses dans le MVP**

Cette section décrit les capacités fonctionnelles couvertes par le MVP, indépendamment du détail des use cases déjà définis.

### ***4.1 Gestion des comptes et accès***

* Compte utilisateur pour :  
  * les kinésithérapeutes  
  * la fondation: 2  
  * les patients (créés uniquement après validation du dossier)  
* Gestion des rôles et droits d’accès

---

### ***4.2 Dossiers patients***

* Création automatique d’un dossier patient suite à une demande introduite par un kinésithérapeute  
* Statuts de dossier simples (ex. : En attente, Accepté, Refusé, Clôturé)  
* Consultation du dossier par les parties autorisées

---

### ***4.3 Espace de partage documentaire***

* Espace sécurisé lié au dossier patient  
* Dépôt et consultation de documents (factures, justificatifs, demandes de justificatifs ?)  
* Historique des documents conservé

---

### ***4.4 Demandes de paiement***

* Introduction de demandes de remboursement ou de paiement par le patient  
* Association des demandes aux documents justificatifs  
* Suivi simple de l’état des demandes (soumis, à compléter, validé, payé, refusé)

---

### ***4.5 Validation et suivi par la fondation***

* Validation manuelle des dossiers et des demandes de paiement  
* Ajout de commentaires/notes ou demandes d’informations complémentaires aux demandes de paiement  
* Suivi du nombre de séances autorisées et consommées (niveau de détail à confirmer)

---

### ***4.6 Communication asynchrone***

* Échanges via notes ou commentaires liés au dossier  
* Pas de messagerie instantanée  
* Historique conservé

## **5\. Fonctionnalités explicitement exclues du MVP**

Les éléments suivants ne font pas partie du MVP et ne seront pas implémentés dans cette première phase :

* Paiement en ligne ou automatisé  
* Signature électronique ou mécanisme de validation légale formelle (ex. signature de consentement, contrats ou accords numériques)  
* Suivi médical détaillé ou diagnostic  
* Messagerie temps réel (chat)  
* Validation multi-niveaux côté fondation  
* Reporting avancé

### **5.1 Idées futures (exclues du MVP)**

Les idées ci-dessous ont été évoquées mais sont considérées comme des pistes futures incertaines, sans engagement ni impact sur le MVP.

### ***A) Subvention de formations pour thérapeutes***

* Demandes de subvention pour suivre des formations  
* Dossiers distincts des dossiers patients  
* Processus et critères à définir ultérieurement

---

### ***B) Groupes de parole et événements***

* Groupes de parole sans thérapeute  
* Événements encadrés par des thérapeutes

---

### ***C) Devenir praticien***

* Bouton ou formulaire permettant à un thérapeute de se manifester  
* Validation par la fondation non réalisable avec les moyens actuels  
* Aucune implémentation prévue à ce stade

# Use cases

# **1\. Liste de use cases**

## **UC-01 – Création d’une demande de prise en charge (kiné)**

**Acteur principal** : Kiné  
**Objectif** : Introduire un patient auprès de la fondation

**Description**

1. Le kiné se connecte via le site/app de la fondation  
2. Il encode :  
   * Infos patient (minimales)  
   * Nombre de séances demandées (15 / 30 / 45\)  
3. Il soumet la demande  
4. Création automatique d’un dossier patient (statut : “En attente”)

**Notes**

* Le kiné agit comme garant du besoin médical  
* Pas de diagnostic stocké  
* Pas encore de compte patient à ce stade

## **UC-02 – Validation du dossier (fondation)**

**Acteur principal** : Fondation  
**Objectif** : Accepter ou refuser une prise en charge

**Description**

1. La fondation consulte la liste des demandes  
2. Elle :  
   * valide → statut “Accepté”  
   * ou refuse → statut “Refusé”  
3. En cas d’acceptation :  
   * création automatique du compte utilisateur pour le patient  
   * le patient obtient l’accès au dossier

**Notes**

* tout les membres de la fondation sont validateur  
* Pas de workflow complexe  
* Historique conservé

## **UC-03 – Accès et consultation du dossier (patient)**

**Acteur principal** : Patient  
**Objectif** : Consulter et gérer son dossier

**Fonctionnalités**

* Voir :  
  * Liste des demandes avec leurs statuts  
  * Pour chaque demande:  
    * date d’introduction  
    * nombre de séances autorisées  
    * statut de la demande  
    * espace de notes  
* Accéder à l’espace de partage (dossier du patient)  
* Ajouter des documents (factures, preuves)  
* Ajouter des notes aux demandes

**Notes**

- explications de comment utiliser la plateforme par mail et aussi via l’application  
- helper pour encoder  
- upload document par mail  
- upload  
  - direct  
  - via un membre de la fondation  
  - via le kiné  
- si dépassement de séances, réintroduire une demande

## **UC-04 – Introduction de séances / preuves (patient)**

**Acteur principal** : Patient  
**Objectif** : Démontrer l’utilisation des soins

**Description**

1. Le patient encode :  
   * une séance ou un groupe de séances (avec un champs “total à payer” qu’il n’est pas obligé de remplir)  
   * ou directement une facture  
2. Il joint les preuves nécessaires  
3. Il soumet une demande de remboursement / paiement

**Notes**

* Le suivi “séance par séance” reste à confirmer  
* Peut être simplifié en V1 : facture \= preuve  
* Ce use case est dépendant du flow de paiement **(à Valider)** et peut devoir être divisé en plusieurs use cases si le flow le nécessite

## **UC-05 – Validation & paiement (fondation)**

**Acteur principal** : Fondation  
**Objectif** : Contrôler et payer

**Description**

1. La fondation consulte les demandes de paiement  
2. Elle :  
   * valide  
   * demande des infos complémentaires  
3. Le paiement est effectué hors Odoo  
4. Le dossier est mis à jour (statut / solde de séances)  
5. La gestion des factures liées aux paiements se fait dans Odoo ? **(à Valider)**

## **UC-06 – Communication asynchrone (fondation ↔ patient)**

**Acteurs** : Patient, Fondation  
**Objectif** : Gérer les allers-retours

**Fonctionnalités**

* Notes/commentaires liés au dossier  
* Pas de chat temps réel  
* Historique conservé

# Flow simple

# **Flow simple**

Kiné  
  ↓ (création demande)  
Dossier patient \[EN ATTENTE\]  
  ↓  
Fondation  
  ↓ (validation)  
Dossier patient \[ACCEPTÉ\]  
  ↓  
Compte patient créé  
  ↓  
Patient  
  ↓ (ajout preuves / factures)  
Demande de paiement  
  ↓  
Fondation  
  ↓ (validation)  
Paiement manuel  
  ↓  
Dossier mis à jour

# Nos questions

# **Nos questions**

### **Fonctionnel**

* Qui introduit les séances : patient   
* Une facture est-elle suffisante comme preuve ? oui  
* Paiement par séance, par facture ou par tranche de séances ? soit 1 séance soit plusieurs  
* Que se passe-t-il si toutes les séances ne sont pas utilisées ? auto-cloture après 3 mois  
* Que se passe-t-il si on dépasse le nombre de séances initialement demandées ? si on a atteint le nombre de séances max, le dossier est clôturé et il faut introduire une nouvelle demande

### **Légal / financier**

* Paiement direct de la facture : oui, autorisé  
* Obligations comptables spécifiques ? : NA  
* Suivi des paiements via l’application ? oui, paiement manuel et enregistrement du record dans Odoo  
* Conservation des données : combien de temps ? pas encore défini

### **GDPR**

* Quelles sont les données dont la fondation a besoin ?  
* Y a-t-il des informations médicales échangées dans les justificatifs de soins ou les demandes de paiements/remboursement entre le patient et la fondation ? CODE INAMI sur facture (ou juste des informations bancaires ? ou autre ?)  
* Y a-t-il des documents médicaux qui doivent être partagés par le patient ? non (à part facture de séance(s))

### **Produit**

* Le patient peut-il modifier ses infos (introduites par le kiné) ? oui sauf le nombre de séances  
* Notifications nécessaires ? oui, au patient \+ membre de la fondation  
* Budget de subvention illimité ? La fondation a un nombre maximal de séances par an. Pouvoir l’introduire dans l’app et avoir le décompte par rapports aux demandes déjà gérées. Avoir une vue sur le budget dépensé (quitte à encoder à la main le total d’un remboursement) par patient ou par kine \+ total

# Clarifications et mises à jour validées

## **1\. Clarifications et mises à jour validées**

### **1.1 Règles de plafond de séances**

* **Plafond global fondation** :  
  * La fondation dispose d’un plafond annuel global exprimé en **nombre maximal de séances**.  
  * Ce plafond est **paramétrable dans l’application** et décrémenté automatiquement à chaque remboursement.  
* **Plafond par patient** :  
  * Il n’est **pas bloquant techniquement** dans l’application.  
  * La décision de rembourser au-delà ou non est prise **manuellement par le membre de la fondation**.  
* **Aide à la décision** :  
  * Avant chaque remboursement, l’application affiche au membre de la fondation :  
    * le nombre de séances déjà remboursées pour le patient sur l’année en cours  
    * un message de confirmation avant validation du remboursement

---

### **1.2 Intégration Odoo (finance)**

* Version cible : **Odoo 19 Community**  
* Module utilisé : **Accounting**  
* Objet Odoo : `account.payment`  
* Le remboursement validé dans l’application :  
  * déclenche la création d’un paiement dans Odoo  
  * sans synchronisation bancaire automatique  
* Le suivi comptable détaillé reste effectué dans Odoo

---

### **1.3 Conservation des données (légal / GDPR)**

* Les règles de rétention des données (factures, documents uploadés, dossiers) **ne sont pas définies à ce stade**.  
* La mise en place de :  
  * suppression automatique  
  * anonymisation  
  * politiques de conservation par type de document  
* est **explicitement hors scope de la V1**.  
* Ces éléments feront l’objet d’une **itération ultérieure dédiée**.

---

### **1.4 Données médicales et factures**

* Aucun document médical n’est requis en dehors des **factures de séances**.  
* Le **code INAMI** :  
  * n’est **pas obligatoire**  
  * n’est **pas stocké comme donnée structurée** dans l’application  
  * peut apparaître uniquement sur la facture uploadée par l’utilisateur

---

## **2\. Rappel des règles fonctionnelles inchangées**

* La demande est introduite par le patient  
* Une facture suffit comme justificatif  
* Une demande peut couvrir :  
  * une seule séance  
  * ou plusieurs séances  
* Auto-clôture d’un dossier :  
  * après 3 mois si les séances ne sont pas utilisées  
  * ou dès que le nombre maximal de séances est atteint  
* Si le plafond est atteint, une **nouvelle demande** est requise  
* Le patient peut modifier ses informations personnelles  
  * sauf le nombre de séances  
* Notifications envoyées :  
  * au patient  
  * au membre de la fondation

---

## **3\. Hors scope V1 (rappel)**

* Gestion automatique GDPR (rétention / suppression)  
* Analyse automatique des factures  
* Automatisation bancaire  
* Règles médicales ou justificatifs cliniques

