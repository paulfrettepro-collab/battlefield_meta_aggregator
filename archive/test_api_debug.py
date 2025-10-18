"""
Test avancé de l'API Tracker.gg avec différents formats
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('TRACKER_GG_API_KEY')
print(f"🔑 Clé API chargée : {api_key[:20]}...\n")

# Test 1 : Header TRN-Api-Key
print("━" * 60)
print("TEST 1 : Header 'TRN-Api-Key'")
print("━" * 60)
headers1 = {"TRN-Api-Key": api_key}
url = "https://public-api.tracker.gg/v2/bf6/standard/profile/origin/BnanaMilk"
response1 = requests.get(url, headers=headers1)
print(f"Status : {response1.status_code}")
print(f"Réponse : {response1.text[:200]}\n")

# Test 2 : Header Authorization Bearer
print("━" * 60)
print("TEST 2 : Header 'Authorization: Bearer'")
print("━" * 60)
headers2 = {"Authorization": f"Bearer {api_key}"}
response2 = requests.get(url, headers=headers2)
print(f"Status : {response2.status_code}")
print(f"Réponse : {response2.text[:200]}\n")

# Test 3 : Tester avec apex (jeu supporté confirmé)
print("━" * 60)
print("TEST 3 : Test avec Apex Legends (jeu supporté)")
print("━" * 60)
url_apex = "https://public-api.tracker.gg/v2/apex/standard/profile/origin/ImperialHal"
response3 = requests.get(url_apex, headers=headers1)
print(f"Status : {response3.status_code}")
print(f"Réponse : {response3.text[:200]}\n")

# Test 4 : Vérifier si bf6 est supporté
print("━" * 60)
print("TEST 4 : Vérification support BF6")
print("━" * 60)
print("Endpoint testé : bf6")
print("Jeux confirmés supportés : apex, csgo, division-2, splitgate")
print("\n💡 Il est possible que BF6 ne soit PAS supporté par l'API")
print("   → Solution : Scraping HTML du site tracker.gg/bf6")
