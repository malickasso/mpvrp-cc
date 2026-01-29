# MPVRP-CC Optimizer

## Description
Le projet MPVRP-CC (Multi-Product Vehicle Routing Problem with Changeover Cost) est une solution logicielle permettant d'optimiser la distribution de plusieurs types de produits incompatibles depuis des dépôts vers des stations-service. Le solveur prend en compte les coûts de transport ainsi que les coûts de nettoyage (changeover costs) nécessaires lors du changement de produit transporté par un véhicule.

## Structure du Projet
- solver/ : Contient le cœur de l'optimisation (OR-Tools) et le parseur d'instances.
- platform/ : Fichiers liés au backend FastAPI.
- static/ : Interface utilisateur (HTML, CSS, JavaScript).
- uploads/ : Répertoire temporaire pour les instances téléchargées via l'interface.
- report_generator.py : Script de génération du rapport technique PDF.
- main_api.py : Point d'entrée principal pour lancer l'application web.

## Prerequisites
Assurez-vous d'avoir Python installé (version 3.8 ou supérieure recommandee). Installez les dependances suivantes :

```bash
pip install fastapi uvicorn python-multipart ortools fpdf2
```

## Installation et Lancement

### Lancer la Plateforme Web
1. Ouvrez un terminal a la racine du projet.
2. Executez la commande suivante :
   ```bash
   python main_api.py
   ```
3. Une fois le serveur lance, ouvrez votre navigateur a l'adresse : http://localhost:8000

### Utilisation de l'Interface
1. Glissez-deposez un fichier d'instance (.dat) dans la zone prevue a cet effet.
2. Cliquez sur le bouton "Lancer l'Optimisation".
3. Visualisez les tournees des vehicules sur la carte interactive et consultez les statistiques de cout.

### Tester le Solveur en Ligne de Commande
Pour tester une instance sans l'interface graphique :
1. Deplacez-vous dans le dossier solver :
   ```bash
   cd solver
   ```
2. Lancez le script avec le chemin d'une instance :
   ```bash
   python mpvrp_solver.py ../small/MPVRP_S_001_s9_d1_p2.dat
   ```

### Generer le Rapport PDF
Pour generer ou mettre a jour le rapport technique final :
```bash
python report_generator.py
```

## Technologies Utilisees
- Backend : Python 3, FastAPI, Uvicorn.
- Optimisation : Google OR-Tools (Constraint Programming).
- Frontend : HTML5, CSS3 (Glassmorphism), JavaScript (Vanilla), SVG pour la visualisation.
- Rapport : Library fpdf2.
