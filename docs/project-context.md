# Project Context — Entre Vos Mains (Odoo 19)

## Contexte

- Ce dépôt contient des **add-ons Odoo 19 Community** (modules custom).
- L’UI reste **dans Odoo** (Website/Portal, QWeb/OWL si nécessaire).
- Le module `evm` embarque aussi le **website public** du projet: page d'accueil, navigation publique minimale et lien clair vers les parcours portail.
- La reprise plus complete d'un site statique existant peut se faire ensuite, mais la presence d'un website public dans `evm` fait desormais partie du besoin immediat.

## Dépendances & environnement local

- La codebase Odoo (serveur) est disponible localement dans `~/dev/odoo` (chemin attendu : `/home/mgeubelle/dev/odoo`) pour consultation du code source Odoo, lecture d'exemples et verification de patterns idiomatiques.
- Ce checkout Odoo local n'est pas une cible de deploiement pour ce projet et ne doit pas recevoir d'implementation specifique au module `evm`.
- Le runtime local du projet repose sur le stack partage `odoo-scripts/local-setup-docker`; les changements applicatifs se font uniquement dans ce depot d'add-ons.

## Principes d’architecture

- **Best practices Odoo 19**: architecture et patterns idiomatiques Odoo (modèles, vues, contrôleurs, sécurité, assets, etc.).
- **KISS**: préférer des solutions simples, lisibles et maintenables; éviter la sur-ingénierie.
- **Pragmatique**: minimiser les dépendances et la complexité tant que le besoin ne le justifie pas.
- **Concurrence pragmatique**: vu le faible nombre d'utilisateurs internes attendus, ne pas sur-investir par défaut dans des mécanismes lourds de gestion des mises à jour concurrentes. Traiter les conflits évidents si le métier l'impose, mais éviter d'en faire un axe de conception prioritaire sans besoin concret.
- **Wizards en exception**: éviter les wizards custom quand une saisie inline sur le modèle et une action métier dédiée (`action_*`) couvrent le besoin.
- **Justification explicite**: n'introduire un wizard que si la donnée est transitoire, si l'action est réellement multi-étapes ou bulk, ou si une confirmation/prévisualisation avant effet irréversible améliore clairement l'UX.

## Convention de commits

- Utiliser le format obligatoire suivant pour chaque commit:

	`[ADD|IMP|FIX|REF|DOC] module_name: short description assertive`

- Ajouter ensuite un corps de commit court mais explicite pour préciser l'intention, l'impact métier ou technique, et les points notables de l'implémentation.
- Signification des préfixes:
	- `ADD`: ajout de fonctionnalité ou de comportement nouveau
	- `IMP`: amélioration d'un comportement existant sans corriger un bug avéré
	- `FIX`: correction de bug
	- `REF`: refactorisation sans changement fonctionnel attendu
	- `DOC`: documentation uniquement
- `module_name` doit correspondre au périmètre principal du changement, par exemple `evm`, `docs`, `bmad`, `scripts`.
- La description courte doit être lisible dans la liste des commits, formulée de manière assertive, spécifique et concise.
- Modèle recommandé:

	Sujet:
	`[FIX] evm: escape refusal reason in history messages`

	Corps:
	`Sanitize refusal reason rendering in internal and portal histories.`
	`Keep the displayed trace readable without changing the validation workflow.`

## Regles de workflow local

- Apres toute code review approuvee qui modifie des artefacts Odoo charges par le serveur (`models/`, `views/`, `security/`, `__manifest__.py`), rafraichir l'environnement manuel local avant de clore la review: redemarrer `odoo-19` puis upgrader `evm` sur `evm_dev`.
