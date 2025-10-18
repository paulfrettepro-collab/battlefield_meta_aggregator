"""
Script de test de l'API Tracker.gg pour Battlefield 6

Ce script teste la connexion à l'API et affiche les données disponibles.
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class TrackerGGAPITester:
    """Testeur de l'API Tracker.gg"""
    
    def __init__(self):
        self.api_key = os.getenv('TRACKER_GG_API_KEY')
        if not self.api_key:
            raise ValueError("❌ TRACKER_GG_API_KEY non trouvée dans .env")
        
        self.base_url = "https://public-api.tracker.gg/v2/bf6"
        self.headers = {
            "TRN-Api-Key": self.api_key,
            "User-Agent": "Battlefield6MetaAggregator/1.0"
        }
    
    def test_connection(self):
        """Test 1 : Vérifier la connexion API"""
        print("━" * 60)
        print("🔍 TEST 1 : Connexion à l'API Tracker.gg")
        print("━" * 60)
        
        # Test avec un joueur du top leaderboard
        test_player = "BnanaMilk"  # #1 du leaderboard
        url = f"{self.base_url}/standard/profile/origin/{test_player}"
        
        print(f"📡 URL : {url}")
        print(f"🔑 Clé API : {self.api_key[:20]}...")
        print(f"⏳ Envoi de la requête...\n")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            print(f"📊 Status Code : {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCÈS ! L'API fonctionne parfaitement !\n")
                data = response.json()
                
                # Afficher un aperçu des données
                print("📦 Données reçues (aperçu) :")
                print(json.dumps(data, indent=2)[:500] + "...")
                
                return True, data
            
            elif response.status_code == 401:
                print("❌ ERREUR : Clé API invalide")
                print("💡 Vérifiez que la clé est correcte dans .env")
                return False, None
            
            elif response.status_code == 404:
                print("⚠️  Joueur non trouvé (normal si le pseudo a changé)")
                print("💡 On va tester avec le leaderboard direct")
                return self.test_leaderboard()
            
            else:
                print(f"⚠️  Code inattendu : {response.status_code}")
                print(f"📄 Réponse : {response.text[:200]}")
                return False, None
                
        except requests.exceptions.Timeout:
            print("❌ ERREUR : Timeout (serveur lent)")
            return False, None
        except requests.exceptions.ConnectionError:
            print("❌ ERREUR : Impossible de se connecter")
            return False, None
        except Exception as e:
            print(f"❌ ERREUR : {str(e)}")
            return False, None
    
    def test_leaderboard(self):
        """Test 2 : Récupérer le leaderboard"""
        print("\n" + "━" * 60)
        print("🏆 TEST 2 : Récupération du Leaderboard")
        print("━" * 60)
        
        # Note: L'API Tracker.gg n'a peut-être pas d'endpoint leaderboard direct
        # On va tester différentes URLs possibles
        
        possible_urls = [
            f"{self.base_url}/leaderboards/stats/all/kills",
            f"{self.base_url}/leaderboards",
            "https://public-api.tracker.gg/v2/leaderboards/bf6",
        ]
        
        for url in possible_urls:
            print(f"\n📡 Test URL : {url}")
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                print(f"   Status : {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Endpoint trouvé !")
                    data = response.json()
                    print(f"   📦 Données : {json.dumps(data, indent=2)[:200]}...")
                    return True, data
                    
            except Exception as e:
                print(f"   ❌ Erreur : {str(e)}")
        
        print("\n⚠️  Aucun endpoint leaderboard trouvé via API")
        print("💡 Solution : On utilisera le scraping HTML du site")
        return False, None
    
    def analyze_api_capabilities(self, profile_data):
        """Analyser les capacités de l'API"""
        print("\n" + "━" * 60)
        print("🔍 ANALYSE : Données disponibles via l'API")
        print("━" * 60)
        
        if not profile_data:
            print("❌ Pas de données à analyser")
            return
        
        print("\n📊 Structure des données :")
        
        # Explorer la structure
        if isinstance(profile_data, dict):
            for key in profile_data.keys():
                print(f"   • {key}")
        
        # Chercher les données importantes
        print("\n🎯 Recherche de données clés :")
        
        # Statistiques
        if 'data' in profile_data:
            print("   ✅ Section 'data' trouvée")
            if 'segments' in profile_data['data']:
                print(f"      • Segments : {len(profile_data['data']['segments'])} trouvés")
        
        # Metadata
        if 'metadata' in profile_data:
            print("   ✅ Metadata disponibles")
        
        print("\n" + "━" * 60)
    
    def generate_report(self, success, data):
        """Générer un rapport de test"""
        print("\n" + "=" * 60)
        print("📋 RAPPORT FINAL")
        print("=" * 60)
        
        print(f"\n📅 Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔑 Clé API : Configurée ✅")
        print(f"🌐 Base URL : {self.base_url}")
        
        if success:
            print(f"\n✅ STATUS : API FONCTIONNELLE !")
            print("\n🎯 Prochaines étapes :")
            print("   1. ✅ API testée et validée")
            print("   2. 🔄 Implémenter extraction complète")
            print("   3. 📊 Extraire Top 100 joueurs")
            print("   4. 💾 Sauvegarder en NDJSON")
            print("   5. 📤 Upload vers MinIO")
        else:
            print(f"\n⚠️  STATUS : API LIMITÉE")
            print("\n💡 Solutions alternatives :")
            print("   1. Scraping HTML du leaderboard (Scrapy)")
            print("   2. Extraction profil par profil (API)")
            print("   3. Combinaison scraping + API")
        
        print("\n" + "=" * 60)
    
    def run(self):
        """Exécuter tous les tests"""
        print("\n" + "🎮" * 30)
        print("  BATTLEFIELD 6 META AGGREGATOR - API TEST")
        print("🎮" * 30 + "\n")
        
        # Test 1 : Connexion
        success1, profile_data = self.test_connection()
        
        # Test 2 : Leaderboard (si Test 1 échoue)
        if not success1:
            success2, leaderboard_data = self.test_leaderboard()
        else:
            success2 = False
            leaderboard_data = None
        
        # Analyse
        if profile_data:
            self.analyze_api_capabilities(profile_data)
        
        # Rapport final
        self.generate_report(success1 or success2, profile_data or leaderboard_data)


if __name__ == "__main__":
    try:
        tester = TrackerGGAPITester()
        tester.run()
    except ValueError as e:
        print(f"\n❌ {str(e)}")
        print("\n💡 Solution :")
        print("   1. Vérifiez que le fichier .env existe")
        print("   2. Vérifiez que TRACKER_GG_API_KEY est renseignée")
        print("   3. Relancez le script")
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {str(e)}")
        import traceback
        traceback.print_exc()
