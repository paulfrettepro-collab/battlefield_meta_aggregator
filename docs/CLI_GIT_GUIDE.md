# 🧭 RÉCAPITULATIF GLOBAL – COMMANDES CLI & GIT

## 🧩 1. Commandes Git en CLI

| Commande | Signification | Description | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| `git init` | Initialize | Crée un dépôt Git local dans le dossier courant. | **INIT**ier un projet = Démarrer | `git init` |
| `git status` | Status | Affiche l'état actuel des fichiers (modifiés, ajoutés, supprimés). | **STATUS** = Bilan de santé du projet | `git status` |
| `git add` | Add | Ajoute des fichiers à l'index (staging area). | **ADD** = Ajouter dans le panier avant de payer | `git add script.py` |
| `git commit` | Commit | Valide les changements ajoutés avec un message. | **COMMIT** = S'engager/Valider (comme un contrat) | `git commit -m "Ajout du script"` |
| `git log` | Log | Affiche l'historique des commits. | **LOG** = Journal de bord (capitaine de navire) | `git log --oneline` |
| `git diff` | Difference | Montre les différences entre la version actuelle et la dernière commitée. | **DIFF**érence = Jeu des 7 différences | `git diff` |
| `git restore` | Restore | Annule les changements sur un fichier non commité. | **RESTORE** = Ctrl+Z (restaurer version d'avant) | `git restore script.py` |
| `git reset` | Reset | Retire les fichiers de l'index ou revient à un commit précédent. | **RESET** = Bouton reset d'une console de jeu | `git reset HEAD script.py` |
| `git push` | Push | Envoie les commits vers le dépôt distant (GitHub, GitLab...). | **PUSH** = Pousser un colis vers le cloud ☁️ | `git push origin main` |
| `git pull` | Pull | Récupère et fusionne les dernières modifications du dépôt distant. | **PULL** = Tirer/Ramener les nouveautés vers toi | `git pull origin main` |
| `git branch` | Branch | Liste ou crée des branches. | **BRANCH** = Branche d'arbre 🌳 (versions parallèles) | `git branch feature-x` |
| `git checkout` | Checkout | Change de branche ou de commit. | **CHECKOUT** = Changer de caisse (supermarché) | `git checkout main` |
| `git merge` | Merge | Fusionne une branche dans la branche courante. | **MERGE** = Fusionner 2 routes en 1 🛣️ | `git merge feature-x` |
| `git clone` | Clone | Copie un dépôt distant en local. | **CLONE** = Photocopie complète du projet | `git clone https://github.com/paul/project.git` |

---

## 💻 2. Commandes CLI Système Essentielles

| Commande | Signification | À quoi ça sert | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| `pwd` | Print Working Directory | Affiche le chemin du dossier courant. | **P**aul, **W**here (are you) **D**ude? = Où es-tu? | `pwd` |
| `ls` | List | Liste les fichiers et dossiers. | **L**i**S**te (comme liste de courses) | `ls -la` |
| `cd` | Change Directory | Change de répertoire. | **C**hange **D**e pièce (dans une maison) | `cd data/` |
| `mkdir` | Make Directory | Crée un dossier. | **M**a**K**e **DIR**ectory = Construire une pièce 🏠 | `mkdir new_folder` |
| `rmdir` | Remove Directory | Supprime un dossier vide. | **R**e**M**ove **DIR** = Démolir une pièce vide | `rmdir old_folder` |
| `rm` | Remove | Supprime fichiers ou dossiers (`-r` pour récursif). | **R**e**M**ove = Supprimer (mettre à la poubelle 🗑️) | `rm -rf data/` |
| `cp` | Copy | Copie un fichier. | **C**o**P**y = Photocopier 📄 | `cp source.txt backup.txt` |
| `mv` | Move | Déplace ou renomme un fichier. | **M**o**V**e = Déménager 🚚 ou changer de nom | `mv old.txt new.txt` |
| `touch` | — | Crée un fichier vide. | **TOUCH** = Toucher pour créer (comme un écran tactile) | `touch notes.txt` |
| `cat` | Concatenate | Affiche le contenu d'un fichier. | **CAT** = Le chat lit le fichier 🐱📖 | `cat fichier.txt` |
| `less` | — | Permet de lire un fichier page par page. | **LESS** = Moins pressé, on lit tranquillement | `less log.txt` |
| `head` | — | Affiche le début d'un fichier. | **HEAD** = La tête (haut) du fichier | `head -n 5 fichier.txt` |
| `tail` | — | Affiche la fin d'un fichier (ou suit en direct avec `-f`). | **TAIL** = La queue (bas) du fichier 🦎 | `tail -f log.txt` |
| `grep` | Global Regular Expression Print | Recherche du texte dans un fichier. | **GREP** = Chercher avec une loupe 🔍 | `grep "error" log.txt` |
| `chmod` | Change Mode | Modifie les permissions d'un fichier. | **CH**ange **MOD**e = Changer les droits d'accès 🔐 | `chmod +x script.sh` |
| `chown` | Change Owner | Change le propriétaire d'un fichier. | **CH**ange **OWN**er = Changer de propriétaire 👤 | `chown paul fichier.txt` |
| `echo` | — | Affiche du texte ou des variables. | **ECHO** = Écho dans une grotte 🗣️ (répète) | `echo "Hello Paul"` |
| `clear` | — | Efface l'écran du terminal. | **CLEAR** = Nettoyer l'écran (comme un tableau noir) | `clear` |
| `history` | — | Montre l'historique des commandes tapées. | **HISTORY** = Livre d'histoire 📚 de tes commandes | `history` |
| `man` | Manual | Affiche la documentation d'une commande. | **MAN**uel d'instructions (comme IKEA 📖) | `man ls` |
| `which` | — | Indique le chemin de l'exécutable d'une commande. | **WHICH** = "Lequel?" Où est cette commande? | `which python` |
| `sleep` | — | Fait une pause pendant un certain nombre de secondes. | **SLEEP** = Dormir/Faire une sieste 😴 | `sleep 5` |

---

## 🔵 3. Signification des icônes Git dans VS Code

| Symbole / Lettre | Signification | Explication |
|:--:|:--:|:--|
| ● | Fichier modifié | Le fichier a été modifié depuis le dernier commit. |
| U | Untracked | Fichier nouveau, non encore ajouté à Git. |
| M | Modified | Fichier suivi par Git, modifié depuis le dernier commit. |
| A | Added | Fichier ajouté à l’index (staging area). |
| D | Deleted | Fichier supprimé depuis le dernier commit. |
| R | Renamed | Fichier renommé ou déplacé. |
| C | Copied | Fichier copié depuis un autre fichier versionné. |
| ? | Ignoré / Non suivi | Fichier non suivi et ignoré via `.gitignore`. |
| 1 U / 2 U | Conflit de merge | Fichier en conflit entre deux branches. |
| + / - | Ligne ajoutée / supprimée (dans un diff) | Visible dans la vue de comparaison de VS Code. |

---

## 🚀 4. En résumé
- **CLI système** : sert à naviguer, créer, copier, supprimer, lire et gérer les fichiers.  
- **Git CLI** : sert à suivre, sauvegarder et versionner les modifications dans un projet.  
- **Icônes VS Code** : reflètent l'état Git de chaque fichier.  

---

## 🧠 5. Moyens Mnémotechniques pour le Workflow Git

### Le Workflow Git = Un Restaurant 🍽️

1. **`git status`** = 👀 Regarder la cuisine (voir ce qui a changé)
2. **`git add`** = 🛒 Mettre les plats dans le chariot du serveur
3. **`git commit`** = � Emballer le plateau avec une étiquette (message)
4. **`git push`** = 🚚 Livrer au client (GitHub)

### Mémoriser PUSH vs PULL 📤📥

- **PUSH** = **P**ousser vers le **H**aut (cloud) ☁️ → Envoyer
- **PULL** = **P**rendre **L**e truc qui **L** à-bas → Ramener

### Mémoriser ADD vs COMMIT 

- **ADD** = Préparer ton sac 🎒 (staging)
- **COMMIT** = Fermer ton sac avec un cadenas 🔒 (permanent)

### HEAD, BRANCH, MERGE 🌳

- **HEAD** = Ta tête 👤 (où tu es actuellement)
- **BRANCH** = Branche d'arbre (chemins parallèles)
- **MERGE** = Fusionner 2 rivières 🌊 qui se rejoignent

---

## 👉 6. Bonne pratique Git (Le mantra à retenir)

**S.A.C.P.** = **S**tatus → **A**dd → **C**ommit → **P**ush

1. `git status` → 👀 Voir ce qui a changé  
2. `git add .` → 🛒 Ajouter tous les fichiers modifiés  
3. `git commit -m "message clair"` → 📦 Enregistrer la version  
4. `git push` → 🚚 Envoyer sur ton dépôt distant  

**Phrase mnémotechnique** : _"**S**alut **A**lice, **C**'est **P**aul"_ 🎯

---

🧠 *Astuce - Alias Terminal :*  
Tu peux combiner ces commandes avec des alias dans ton terminal, par exemple :  
```bash
alias gs="git status"
alias ga="git add ."
alias gc="git commit -m"
alias gp="git push"
alias glog="git log --oneline --graph"
```

---

## 💡 7. Scénarios Pratiques avec Mnémotechniques

### Scénario 1 : J'ai fait une erreur avant de commit 🤦

**Problème** : Tu as modifié `script.py` mais tu veux annuler
```bash
git restore script.py
```
🧠 **Mémo** : **RESTORE** = Ctrl+Z (comme dans Word)

---

### Scénario 2 : J'ai fait `git add` par erreur 😱

**Problème** : Tu as ajouté un fichier avec `git add` mais tu ne veux plus le commiter
```bash
git reset HEAD script.py
```
🧠 **Mémo** : **RESET** = Retirer du panier avant de payer 🛒

---

### Scénario 3 : Je veux voir les différences ⚖️

**Problème** : Tu veux voir ce qui a changé dans un fichier
```bash
git diff script.py
```
🧠 **Mémo** : **DIFF** = Jeu des 7 différences 🔍

---

### Scénario 4 : Je veux créer une branche de test 🌳

**Problème** : Tu veux tester une nouvelle feature sans toucher au code principal
```bash
git branch feature-test    # Créer la branche
git checkout feature-test  # Se déplacer sur la branche
```
🧠 **Mémo** : 
- **BRANCH** = Faire pousser une nouvelle branche d'arbre
- **CHECKOUT** = Changer de rayon au supermarché

---

### Scénario 5 : Mon dossier est en désordre 🗂️

**Problème** : Tu ne sais plus où tu es
```bash
pwd          # Où suis-je?
ls -la       # Qu'est-ce qu'il y a ici?
cd ..        # Remonter d'un niveau
```
🧠 **Mémo** : 
- **PWD** = "Paul, Where Dude?" 
- **LS** = Liste de courses
- **CD..** = Sortir de la pièce

---

## 🎯 8. La Checklist du Pro

Avant chaque `git push`, fais cette checklist mentale :

- ✅ `git status` → Y a-t-il des fichiers modifiés?
- ✅ `.env` n'est PAS dans la liste? (sécurité)
- ✅ `git add` → J'ai ajouté ce que je veux?
- ✅ `git commit -m "message clair"` → Message descriptif?
- ✅ `git push` → Envoyer vers GitHub

**Phrase mnémotechnique** : _"**S**écurité **A**vant **C**haque **P**ush"_ 🔐

---

## 🐍 9. Fondamentaux Python – Le Strict Nécessaire

### 9.1 Types de Données de Base

| Concept | Syntaxe | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| **String** | `str` | Texte entre guillemets | **STR**ing = Une ficelle de mots 🧵 | `nom = "Paul"` |
| **Integer** | `int` | Nombre entier | **INT**eger = Nombre **INT**act (pas cassé) | `age = 25` |
| **Float** | `float` | Nombre décimal | **FLOAT** = Flotte sur l'eau 🌊 (virgule flottante) | `prix = 19.99` |
| **Boolean** | `bool` | Vrai ou Faux | **BOOL**ean = Interrupteur ⚡ (on/off) | `actif = True` |
| **List** | `[]` | Liste modifiable | **LIST** = Liste de courses 📝 (on peut modifier) | `fruits = ["pomme", "banane"]` |
| **Tuple** | `()` | Liste non modifiable | **TUPLE** = Cadenas 🔒 (immuable) | `coords = (48.8, 2.3)` |
| **Dictionary** | `{}` | Clé-Valeur | **DICT** = Dictionnaire 📖 (mot → définition) | `user = {"nom": "Paul", "age": 25}` |
| **Set** | `set()` | Collection unique | **SET** = Ensemble mathématique (pas de doublons) | `tags = {1, 2, 3}` |

---

### 9.2 Structures de Contrôle

| Concept | Syntaxe | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| **if/elif/else** | `if condition:` | Condition si/sinon | **IF** = Fourche dans la route 🛣️ | `if age >= 18: print("Majeur")` |
| **for** | `for item in list:` | Boucle sur collection | **FOR** = Pour chaque élément dans le panier 🛒 | `for fruit in fruits: print(fruit)` |
| **while** | `while condition:` | Boucle tant que vrai | **WHILE** = Pendant que la lampe est allumée 💡 | `while i < 10: i += 1` |
| **break** | `break` | Sortir de la boucle | **BREAK** = Casser la boucle (sortie d'urgence) 🚪 | `if x == 5: break` |
| **continue** | `continue` | Passer à l'itération suivante | **CONTINUE** = Sauter cette étape, continuer ⏭️ | `if x % 2 == 0: continue` |
| **pass** | `pass` | Ne rien faire (placeholder) | **PASS** = Passe ton tour (comme au Uno) 🎴 | `if condition: pass` |

---

### 9.3 Fonctions Essentielles

| Fonction | Usage | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| `def` | Définir fonction | Créer une fonction réutilisable | **DEF**inir = Créer une recette de cuisine 👨‍🍳 | `def saluer(nom): return f"Bonjour {nom}"` |
| `return` | Retourner valeur | Renvoie le résultat | **RETURN** = Rendre la monnaie 💰 | `return resultat` |
| `len()` | Longueur | Compte les éléments | **LEN**gth = Longueur avec une règle 📏 | `len([1, 2, 3])  # 3` |
| `print()` | Afficher | Affiche dans le terminal | **PRINT** = Imprimante 🖨️ (affiche) | `print("Hello")` |
| `input()` | Saisie utilisateur | Demande une entrée | **INPUT** = Boîte aux lettres 📬 (reçoit) | `nom = input("Ton nom?")` |
| `range()` | Séquence nombres | Génère une suite | **RANGE** = Portée de tir 🎯 (0 à N) | `for i in range(5): print(i)` |
| `enumerate()` | Index + Valeur | Compte et donne valeur | **ENUMERATE** = Numéroter une liste 🔢 | `for i, fruit in enumerate(fruits)` |
| `zip()` | Assembler listes | Combine 2 listes | **ZIP** = Fermeture éclair 🤐 (assemble) | `zip([1,2], ["a","b"])` |

---

### 9.4 Manipulation de Données

| Opération | Syntaxe | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| **Slice** | `[start:end]` | Découper liste/string | **SLICE** = Couper une baguette 🥖 | `fruits[0:2]  # 2 premiers` |
| **Append** | `.append()` | Ajouter à la fin | **APPEND** = Coller un post-it à la fin 📌 | `liste.append("nouveau")` |
| **Extend** | `.extend()` | Fusionner listes | **EXTEND** = Rallonger une table 🪑 | `liste1.extend(liste2)` |
| **Pop** | `.pop()` | Retirer dernier élément | **POP** = Faire sauter un ballon 🎈 | `liste.pop()` |
| **Remove** | `.remove()` | Supprimer par valeur | **REMOVE** = Retirer une carte du jeu 🃏 | `liste.remove("pomme")` |
| **Split** | `.split()` | Découper string | **SPLIT** = Couper une phrase en mots ✂️ | `"a b c".split()  # ["a","b","c"]` |
| **Join** | `.join()` | Assembler en string | **JOIN** = Coller des mots avec de la glue 📎 | `" ".join(["a","b"])  # "a b"` |
| **Replace** | `.replace()` | Remplacer texte | **REPLACE** = Chercher/Remplacer (Word) 🔄 | `"hello".replace("l", "x")` |

---

### 9.5 Concepts Avancés Essentiels

| Concept | Syntaxe | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| **List Comprehension** | `[x for x in liste]` | Créer liste en 1 ligne | **LC** = Machine à transformer 🏭 | `[x*2 for x in range(5)]` |
| **Lambda** | `lambda x: x*2` | Fonction anonyme courte | **LAMBDA** = Post-it de fonction 📝 | `double = lambda x: x*2` |
| **Try/Except** | `try: ... except:` | Gérer les erreurs | **TRY** = Essayer de sauter, filet en dessous 🤸 | `try: 1/0 except: print("Erreur")` |
| **With** | `with open() as f:` | Ouvrir fichier proprement | **WITH** = Fermer le robinet après usage 🚰 | `with open("f.txt") as f: data = f.read()` |
| **Import** | `import module` | Importer bibliothèque | **IMPORT** = Acheter un outil au magasin 🛠️ | `import pandas as pd` |
| **Class** | `class NomClasse:` | Créer un objet | **CLASS** = Moule à gâteau 🍰 (créer objets) | `class Voiture: pass` |
| **f-string** | `f"texte {var}"` | Format string moderne | **F-STRING** = Remplir les blancs _____ ✏️ | `f"J'ai {age} ans"` |

---

### 🧠 Mnémotechnique Python : **L.I.F.T**

**L**istes → **I**tération (for) → **F**onctions (def) → **T**ry/Except

_"Pour **L**ever un projet, il faut **I**térer, créer des **F**onctions, et gérer les erreurs avec **T**ry"_ 🚀

---

## 🗄️ 10. Fondamentaux SQL – Le Strict Nécessaire

### 10.1 Commandes CRUD (Create, Read, Update, Delete)

| Commande | Usage | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| **SELECT** | Lire données | Récupère des données | **SELECT** = Sélectionner des produits 🛒 | `SELECT * FROM users` |
| **INSERT** | Créer données | Ajoute de nouvelles lignes | **INSERT** = Insérer une pièce dans un puzzle 🧩 | `INSERT INTO users (nom) VALUES ('Paul')` |
| **UPDATE** | Modifier données | Change des valeurs existantes | **UPDATE** = Mise à jour (Windows Update) 🔄 | `UPDATE users SET age=26 WHERE nom='Paul'` |
| **DELETE** | Supprimer données | Efface des lignes | **DELETE** = Gomme 🧹 (attention, permanent!) | `DELETE FROM users WHERE id=1` |

**Phrase mnémotechnique** : _"**S**électionner **I**nsérer **U**pdater **D**életer"_ → **SIUD** (comme CRUD)

---

### 10.2 Filtrage et Tri

| Commande | Usage | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| **WHERE** | Filtrer | Condition de sélection | **WHERE** = Où? (chercher dans un tiroir 🗄️) | `SELECT * FROM users WHERE age > 18` |
| **AND/OR** | Combiner conditions | ET/OU logique | **AND** = Les 2 en même temps / **OR** = L'un ou l'autre 🔀 | `WHERE age > 18 AND pays='France'` |
| **LIKE** | Recherche pattern | Recherche avec % (joker) | **LIKE** = Chercher avec une loupe 🔍 | `WHERE nom LIKE 'P%'  -- commence par P` |
| **IN** | Liste de valeurs | Vérifier si dans liste | **IN** = Dans la liste de courses 📝 | `WHERE pays IN ('France', 'Belgique')` |
| **BETWEEN** | Entre 2 valeurs | Intervalle | **BETWEEN** = Entre 2 bornes 🚧 | `WHERE age BETWEEN 18 AND 30` |
| **ORDER BY** | Trier | Ordre croissant/décroissant | **ORDER** = Ranger par ordre alphabétique 📚 | `ORDER BY age DESC  -- plus âgé d'abord` |
| **LIMIT** | Limiter résultats | Prendre N premiers | **LIMIT** = Couper après N 🔪 | `SELECT * FROM users LIMIT 10` |

---

### 10.3 Agrégations (Calculs sur Données)

| Fonction | Usage | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| **COUNT()** | Compter lignes | Nombre d'éléments | **COUNT** = Compter sur ses doigts 🤚 | `SELECT COUNT(*) FROM users` |
| **SUM()** | Somme | Addition de valeurs | **SUM** = Addition (calculatrice ➕) | `SELECT SUM(prix) FROM achats` |
| **AVG()** | Moyenne | Moyenne arithmétique | **AVG** = **AV**era**G**e = Note moyenne 📊 | `SELECT AVG(age) FROM users` |
| **MIN()** | Minimum | Plus petite valeur | **MIN** = **MIN**uscule (plus petit) 🔽 | `SELECT MIN(prix) FROM produits` |
| **MAX()** | Maximum | Plus grande valeur | **MAX** = **MAX**imum (plus grand) 🔼 | `SELECT MAX(prix) FROM produits` |
| **GROUP BY** | Regrouper | Grouper par colonne | **GROUP** = Ranger par catégorie 📦 | `SELECT pays, COUNT(*) FROM users GROUP BY pays` |
| **HAVING** | Filtrer groupes | WHERE pour GROUP BY | **HAVING** = Filtre après regroupement 🔬 | `HAVING COUNT(*) > 5` |

**Phrase mnémotechnique** : _"**C**ompter **S**ommer **A**veragé **M**in **M**ax"_ → **CSAMM** (comme "Je calcule")

---

### 10.4 Jointures (Relier des Tables)

| Type | Usage | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| **INNER JOIN** | Intersection | Seulement correspondances | **INNER** = Centre du diagramme de Venn ⭕ | `SELECT * FROM users u INNER JOIN orders o ON u.id = o.user_id` |
| **LEFT JOIN** | Tout à gauche + matches | Garde tout de la table de gauche | **LEFT** = Priorité à gauche ⬅️ | `SELECT * FROM users u LEFT JOIN orders o ON u.id = o.user_id` |
| **RIGHT JOIN** | Tout à droite + matches | Garde tout de la table de droite | **RIGHT** = Priorité à droite ➡️ | `SELECT * FROM users u RIGHT JOIN orders o ON u.id = o.user_id` |
| **FULL JOIN** | Tout + tout | Toutes les lignes des 2 tables | **FULL** = Tout prendre 🎁 | `SELECT * FROM users u FULL JOIN orders o ON u.id = o.user_id` |

**Phrase mnémotechnique** : _"**I**ntérieur **L**eft **R**ight **F**ull"_ → **ILRF** (comme "Je Lie Relais Fusionne")

---

### 10.5 Commandes de Structure (DDL)

| Commande | Usage | Explication | Moyen mnémotechnique 🧠 | Exemple |
|:--:|:--:|:--|:--|:--|
| **CREATE TABLE** | Créer table | Nouvelle table vide | **CREATE** = Construire une maison 🏠 | `CREATE TABLE users (id INT, nom VARCHAR(50))` |
| **DROP TABLE** | Supprimer table | Efface complètement | **DROP** = Faire tomber/Détruire 💥 | `DROP TABLE users` |
| **ALTER TABLE** | Modifier structure | Ajouter/supprimer colonnes | **ALTER** = Rénover une maison 🔨 | `ALTER TABLE users ADD email VARCHAR(100)` |
| **PRIMARY KEY** | Clé primaire | Identifiant unique | **PRIMARY** = Numéro de sécurité sociale 🆔 | `id INT PRIMARY KEY` |
| **FOREIGN KEY** | Clé étrangère | Lien vers autre table | **FOREIGN** = Passeport 🛂 (référence externe) | `FOREIGN KEY (user_id) REFERENCES users(id)` |

---

### 🧠 Mnémotechnique SQL : **S.W.O.G.L** (SELECT WHERE ORDER GROUP LIMIT)

_"Pour interroger une base : **S**électionne **W**here tu cherches, **O**rdonne, **G**roupe, **L**imite"_ 🎯

**Ordre d'exécution SQL** (à retenir) :
1. **FROM** → Quelle table?
2. **WHERE** → Quelles lignes?
3. **GROUP BY** → Regrouper comment?
4. **HAVING** → Filtrer les groupes?
5. **SELECT** → Quelles colonnes?
6. **ORDER BY** → Dans quel ordre?
7. **LIMIT** → Combien de résultats?

---

## 🎯 11. Checklist du Développeur Pro

### Python ✅
- Maîtrise des **types de base** (str, int, list, dict)
- Savoir faire des **boucles** (for, while)
- Créer des **fonctions** (def, return)
- Gérer les **erreurs** (try/except)
- Manipuler des **fichiers** (with open)
- Utiliser **pandas** pour les données (bonus)

### SQL ✅
- Savoir faire un **SELECT** simple
- Utiliser **WHERE** pour filtrer
- Faire des **JOIN** entre tables
- Utiliser **GROUP BY** et **COUNT**
- Connaître **INNER vs LEFT JOIN**
- Comprendre les **clés primaires/étrangères**

### Git ✅
- **S.A.C.P** = Status → Add → Commit → Push
- Toujours vérifier `.env` n'est **pas** dans `git status`
- Faire des **commits fréquents** avec messages clairs
- Utiliser des **branches** pour tester

---

## 💡 12. Les 10 Commandements du Dev

1. **Tu commenteras ton code** 💬 (pour toi dans 6 mois)
2. **Tu versioneras avec Git** 📦 (toujours sauvegarder)
3. **Tu ne pusheras pas .env** 🔒 (secrets = locaux)
4. **Tu testeras avant de commiter** ✅ (éviter les bugs)
5. **Tu utiliseras des noms clairs** 📝 (`age` > `a`)
6. **Tu feras des fonctions réutilisables** ♻️ (DRY = Don't Repeat Yourself)
7. **Tu gèreras les erreurs** 🛡️ (try/except)
8. **Tu liras la documentation** 📖 (Google est ton ami)
9. **Tu feras des commits atomiques** ⚛️ (1 commit = 1 feature)
10. **Tu prendras des pauses** ☕ (cerveau = muscle)

---

