**02/11/2024** : 
- Visiter le site de tracker GG et plutôt que d'extraire les joueurs le top 100 extraire aller directement dans la fiche de chaque joueurs filtré par nb kills desc en plus de récupérer leurs armes récupérer le nb de kills et faire un classement soit même avec une window function rank. over(partition by player_id order by kills desc)
- Prévoir un endroit ou l'on retrouve tous les liens du projets -> Bigquery -> Streamlit -> GitHub repo -> Documentation

**Notes techniques :**
Orchestration : Clarification sur l'approche GitHub Actions/Cron en priorité, Airflow pour V2
- Question sur la jointure silver_player_weapons à vérifier
- Réflexion sur l'utilité de MinIO dans le pipeline actuel
- Idée d'amélioration extraction :
Approche directe par joueur avec filtre kills DESC
Implémentation de rank() OVER(PARTITION BY player_id ORDER BY kills DESC)

TODO : Créer section centralisée des liens projet (BigQuery, Streamlit, GitHub, docs)

05.11.2025 : 
Comment vérifier que mon tableau streamlit est bien à jour par rapport à bigquery ? car par rapport au site tracker GG les résultats sont différents.