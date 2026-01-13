# Projet COBOL sur IBM Z/OS — Revenu Québec

Ce dossier rassemble des ressources et un mini‑projet pour apprendre
et pratiquer le COBOL dans un environnement IBM Z/OS, avec un focus
sur le traitement fiscal (cas Revenu Québec).

Contenu principal
- **Guide historique et didactique COBOL** : explications sur le
	langage, exemples, structure d'un programme, gestion des fichiers,
	et exercices. Voir [cobol_ibmZos.md](projet_cobol_zos_RQ/cobol_ibmZos.md#L1).
- **Plan d'installation et ateliers pratiques** : installation du
	terminal 3270, prise en main ISPF/TSO/JCL, et exercices axés fiscalité
	au Québec. Voir [projet_cobol_revenu_quebec.md](projet_cobol_zos_RQ/projet_cobol_revenu_quebec.md#L1).

Objectifs
- Fournir un rappel des concepts COBOL modernes (z/OS).
- Proposer un mini‑projet : traitement de déclarations fiscales,
	calcul des cotisations (RRQ, RQAP) et de l'impôt provincial, génération
	de fichiers de sortie et rapports.

Prérequis rapides
- Accès réseau au mainframe (VPN si nécessaire).
- Émulateur 3270 (`x3270` / `c3270`) pour se connecter au terminal.
- Accès ISPF/TSO et droits pour soumettre des jobs JCL.

Quickstart (résumé)
1. Installer et lancer `x3270` ou `c3270` (voir `projet_cobol_revenu_quebec.md`).
2. Se connecter via TSO et ouvrir ISPF.
3. Éditer / compiler un programme COBOL et soumettre via JCL (exemples
	 dans les deux documents).
4. Pour le mini‑projet : préparer un fichier d'entrée de contribuables,
	 exécuter le programme de calcul fiscal et vérifier le fichier de sortie.

Fichiers clés
- [cobol_ibmZos.md](projet_cobol_zos_RQ/cobol_ibmZos.md#L1) — Guide
	détaillé, exemples et mini‑projet fiscal.
- [projet_cobol_revenu_quebec.md](projet_cobol_zos_RQ/projet_cobol_revenu_quebec.md#L1) —
	Installation 3270, prise en main ISPF/JCL et procédures pratiques.

Prochaines étapes (suggestions)
- mise en place du vpn pour acces a vm IBM Z/os ou cobol est installe.
- Tester les exemples fournis dans un environnement z/OS ou simulateur.
- Adapter les tableaux de taux et fichiers d'entrée aux jeux de données
	réels pour valider la logique fiscale.

Auteur
- Synthèse générée à partir des documents existants du dossier.

