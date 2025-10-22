"""
Exemples de requêtes SQL sur BigQuery
Analyse des données BF6 Top Weapons
"""

import os
from dotenv import load_dotenv
from google.cloud import bigquery

# Charger les variables d'environnement
load_dotenv()

def run_query(client, query, description):
    """Exécute une requête et affiche les résultats"""
    
    print("=" * 80)
    print(f"📊 {description}")
    print("=" * 80)
    print()
    print("Requête SQL:")
    print("-" * 80)
    print(query)
    print()
    print("Résultats:")
    print("-" * 80)
    
    try:
        query_job = client.query(query)
        results = query_job.result()
        
        # Afficher les résultats
        row_count = 0
        for row in results:
            row_count += 1
            print(f"{row_count}. {dict(row)}")
        
        if row_count == 0:
            print("(Aucun résultat)")
        
        print()
        print(f"✅ {row_count} ligne(s) retournée(s)")
        print()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print()

def main():
    """Fonction principale"""
    
    project_id = os.getenv('GCP_PROJECT_ID')
    
    print("=" * 80)
    print("🔍 REQUÊTES SQL - BATTLEFIELD 6 META ANALYSIS")
    print("=" * 80)
    print()
    print(f"Projet: {project_id}")
    print(f"Dataset: bf6_meta")
    print(f"Table: top_weapons")
    print()
    
    # Créer le client BigQuery
    client = bigquery.Client(project=project_id)
    
    # Requête 1: Top 10 joueurs
    query1 = f"""
    SELECT 
        player_id,
        handle,
        status
    FROM `{project_id}.bf6_meta.top_weapons`
    LIMIT 10
    """
    run_query(client, query1, "REQUÊTE 1: Top 10 joueurs du leaderboard")
    
    # Requête 2: Top 5 armes les plus utilisées
    query2 = f"""
    SELECT 
        weapon.name as arme,
        COUNT(*) as nb_joueurs_utilisant,
        ROUND(AVG(weapon.kills), 2) as kills_moyens,
        MAX(weapon.kills) as kills_max
    FROM `{project_id}.bf6_meta.top_weapons`,
        UNNEST(top_weapons) as weapon
    GROUP BY weapon.name
    ORDER BY nb_joueurs_utilisant DESC
    LIMIT 5
    """
    run_query(client, query2, "REQUÊTE 2: Top 5 armes les plus populaires")
    
    # Requête 3: Armes avec le plus de kills
    query3 = f"""
    SELECT 
        weapon.name as arme,
        MAX(weapon.kills) as kills_max,
        COUNT(*) as nb_joueurs
    FROM `{project_id}.bf6_meta.top_weapons`,
        UNNEST(top_weapons) as weapon
    GROUP BY weapon.name
    ORDER BY kills_max DESC
    LIMIT 5
    """
    run_query(client, query3, "REQUÊTE 3: Armes avec le plus de kills (record)")
    
    # Requête 4: Statistiques globales
    query4 = f"""
    SELECT 
        COUNT(DISTINCT player_id) as total_joueurs,
        COUNT(DISTINCT weapon.name) as total_armes_differentes,
        ROUND(AVG(ARRAY_LENGTH(top_weapons)), 2) as nb_armes_moyen_par_joueur
    FROM `{project_id}.bf6_meta.top_weapons`,
        UNNEST(top_weapons) as weapon
    """
    run_query(client, query4, "REQUÊTE 4: Statistiques globales")
    
    # Requête 5: Joueur avec le plus de kills sur une arme
    query5 = f"""
    SELECT 
        handle as joueur,
        weapon.name as arme,
        weapon.kills as kills
    FROM `{project_id}.bf6_meta.top_weapons`,
        UNNEST(top_weapons) as weapon
    ORDER BY weapon.kills DESC
    LIMIT 5
    """
    run_query(client, query5, "REQUÊTE 5: Top 5 records joueur/arme")
    
    # Requête 6: Liste de toutes les armes uniques
    query6 = f"""
    SELECT 
        weapon.name as arme,
        COUNT(*) as occurrences
    FROM `{project_id}.bf6_meta.top_weapons`,
        UNNEST(top_weapons) as weapon
    GROUP BY weapon.name
    ORDER BY arme
    """
    run_query(client, query6, "REQUÊTE 6: Liste complète des armes")
    
    print("=" * 80)
    print("✅ ANALYSE TERMINÉE")
    print("=" * 80)
    print()
    print("💡 Tu peux aussi utiliser la console web BigQuery:")
    print(f"   https://console.cloud.google.com/bigquery?project={project_id}")
    print()

if __name__ == "__main__":
    main()
