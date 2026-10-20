# 🎫 Système de Gestion et Routage de Tickets Internes

Une application de bureau Python simple, efficace et intuitive permettant de gérer et de router les demandes d'assistance (tickets) entre les différents départements d'une entreprise.

---

## 📌 Présentation du Projet

Cette application repose sur une architecture claire séparant l'interface graphique du stockage des données :
* **Base de données (SQLite3) :** Structuration propre des départements, employés et tickets avec gestion des clés étrangères et contraintes d'intégrité sur les statuts.
* **Interface graphique (Tkinter) :** Interface fluide comprenant un écran d'authentification, des tableaux de bord personnalisés et des contrôles d'action adaptés aux rôles des utilisateurs.

---

## ✨ Fonctionnalités Principales

1. **🔐 Authentification**
   * Écran de connexion sécurisé pour les employés.

2. **📊 Tableaux de bord personnalisés**
   * **Mes Tickets :** Suivi en temps réel des tickets créés par l'utilisateur connecté.
   * **Tickets de mon Département :** Vue d'ensemble des tickets assignés au département de l'utilisateur.

3. **📝 Gestion des Tickets**
   * **Création :** Formulaire de création avec sélection du département destinataire via une liste déroulante (statut initial par défaut : `Open`).
   * **Annulation :** Le créateur du ticket peut annuler sa demande à tout moment (passage au statut `Canceled`).

4. **🔄 Workflow de Traitement Strict**
   Les employés traitent les tickets de leur département selon la séquence suivante :
   $$\text{Open} \longrightarrow \text{In treatment} \longrightarrow \text{Done}$$
   * **Prise en charge :** Passage du statut `Open` à `In treatment`.
   * **Résolution :** Passage du statut `In treatment` à `Done`.

---

## 🗄️ Schéma de la Base de Données

L'application s'appuie sur trois entités relationnelles :

| Entité | Attributs | Description |
| :--- | :--- | :--- |
| **Department** | `ID` (PK), `Name`, `Description` | Départements de l'entreprise. |
| **Employee** | `ID` (PK), `Name`, `Department_ID` (FK) | Informations sur les utilisateurs. |
| **Ticket** | `ID` (PK), `Description`, `Creator_ID` (FK), `Target_Department_ID` (FK), `Status` | Suivi et état de la demande. |

> **Remarque :** Le champ `Status` de la table **Ticket** est strictement limité aux valeurs : `Open`, `In treatment`, `Done`, ou `Canceled`.

---

## 🛠️ Stack Technique

* **Langage :** Python 3.x
* **Interface Graphique (GUI) :** Tkinter
* **Base de données :** SQLite3

---





