──────────────────────────────────────────────
🧭 MARKDOWN CHEATSHEET – SYNTHÈSE RAPIDE
──────────────────────────────────────────────

# Titre1   ## Titre2   ### Titre3
**Gras**   *Italique*   ~~Barré~~   `Code`
> Citation / note

- Puce        • Sous-puce  
1. Numérotée  2. Élément suivant  

[Texte](url)     → Lien  
![Alt](img.jpg)  → Image  

```python
# Bloc de code
def hello(): print("Hi")
```

**Nexts prompts**

✅ *18/10/2025 18h* 
<V2 Objectif
Tu dois extraire, pour les 100 joueurs du leaderboard Kills (platform=all), les 3 armes les plus jouées par joueur depuis leur page profil Tracker.gg, avec kills et accuracy.

⚠️ **BLOCAGE CLOUDFLARE DÉTECTÉ** (18 oct 2025)
- Tracker.gg utilise Cloudflare protection anti-bot sur les pages profil
- Message : "Confirmez que vous êtes un humain en effectuant l'action ci-dessous"
- Selenium échoue même avec anti-détection (headless, user-agent, etc.)
- **Solutions possibles** :
  1. 🔴 PRIORITÉ : Retester API officielle Tracker.gg (19-20 oct) - clé: 55b66bdc-3610-482e-b94c-aa0b2dbc93f9
  2. Utiliser `undetected-chromedriver` (Python package qui bypasse Cloudflare)
  3. Attendre plus longtemps (>30s) pour que Cloudflare laisse passer
  4. Utiliser un service proxy/CAPTCHA solver (payant)

Périmètre des pages
1) Leaderboard (top 100) : https://tracker.gg/bf6/leaderboards?platform=all&board=Kills&page=1
2) Profil joueur (overview) : https://tracker.gg/bf6/profile/{player_id}/overview [🔒 BLOQUÉ PAR CLOUDFLARE]

Règles d'extraction
- Depuis le leaderboard, récupère pour chaque entrée :
  • player_id (numérique présent dans l'URL de profil)  
  • handle (pseudo affiché)  
  • url_profil (lien complet)
- Ouvre chaque profil. Dans la section Weapons, clique sur "View All" si présent pour forcer le chargement complet.
- Trie les armes par "Kills" décroissant et prends les 3 premières.
- Normalise les champs numériques :  
  • kills = entier (supprime les séparateurs de milliers)  
  • accuracy_pct = nombre à une décimale, sans symbole %
- Si la page charge les données via XHR/JSON, privilégie l'endpoint JSON (plus stable) ; sinon, scrape le DOM (CSS selectors).
- Gestion d'erreurs : 3 retries par page (backoff exponentiel), loggue player_id en "status=failed" si échec.
- Respecte rate limiting (≤ 1 req/s vers le profil, ≤ 5 req/s sur le leaderboard) et intercale un délai aléatoire 200–600 ms.

Sélecteurs (indicatifs, à adapter si le DOM diffère)
- Carte arme (liste) : container sous la section "Weapons" après clic "View All".
- Nom arme : noeud texte principal de la carte.
- Kills : libellé "Kills" voisin + valeur.
- Accuracy : libellé "Accuracy" voisin + valeur.

Schéma de sortie (NDJSON : 1 ligne = 1 joueur)
{
  "source": "tracker.gg",
  "board": "Kills",
  "snapshot_utc": "<ISO8601>",
  "player_id": "3208849653",
  "handle": "Happy_3201",
  "top_weapons": [
    {"name": "L85A3", "kills": 11950, "accuracy_pct": 48.9},
    {"name": "M45A1", "kills": 9710, "accuracy_pct": 1208.5},
    {"name": "KORD 6P67", "kills": 8041, "accuracy_pct": 28.5}
  ]
}

Critères d'acceptation
- 100 lignes NDJSON (1 par joueur) ou mention explicite des player_id échoués.
- Pour chaque joueur, exactement 3 armes (ou moins si <3 présentes), triées par kills desc.
- Numériques propres (kills int, accuracy_pct float).
- Taux d'échec < 5%. Tous les échecs listés avec raison (timeout, 403, parsing).

Sortie supplémentaire (optionnel)
- Fichier CSV agrégé `data/bronze/tracker_gg/leaderboard_kills/YYYY-MM-DD/top_weapons.csv`
  colonnes: snapshot_utc, player_id, handle, rank_weapon(1..3), weapon_name, kills, accuracy_pct.

Notes
- Si un endpoint JSON interne est découvert via DevTools Network, documente l'URL et le payload minimal.
- Si un blocage anti-bot survient, ralentis le rythme et active un user-agent navigateur standard.
- ⚠️ **Cloudflare détecté** : Prioriser retest API officielle (clé dans .env)>

✅ **20/10/2025 ** 
-  Prochaines étapes possibles : proposées initialement
    Extraction complète 100 joueurs - Lance le script en mode production ✅
    Ajout accuracy - Améliorer le parsing pour extraire aussi les pourcentages d'accuracy
    Analyse des données - Créer un dashboard ou visualisation
    MinIO upload - Uploader les données vers MinIO (Phase 1)
- Peux-tu réaliser du ménage dans les fichiers dossiers du projet. Garder que le nécessaire au bon fonctionnement du pipeline d'extraction et d'upload. Archiver le reste dans un dossier /archive. Mettre à jour le readme.md pour refléter la nouvelle structure.
- peux-tu parcourir l'ensemble des fichiers et corriger les erreurs que tu vois dans le contenu. En effet par exemple dans .env, je vois encore des mentions concernant SQL Server, or nous faisons une toute autre approche avec MinIO et BigQuery. Merci de faire une passe complète sur tous les fichiers pour t'assurer que tout est cohérent avec l'état actuel du projet. indiquée dans le readme.md. Peux-tu me dire à quoi sert également le README.md si cela fait doublon avec reandme.md merci de le supprimer. Globalement faire une passe de nettoyage et d'optimisation sur tout le projet documentaire et code.
- Peux-tu m'expliquer comment tu vas faire pour lancer un jobs hebdomadairement pour que l'extraction puisse se passer chaque semaine afin de voir les évolution de dans le leaderboard et par extension l'évolution des loadouts 

- peux-tu me donner les commandes à faire pour commit ce que nous avons fait aujourd'hui. 