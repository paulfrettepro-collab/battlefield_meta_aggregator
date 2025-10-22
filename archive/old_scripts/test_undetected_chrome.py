"""
TEST UNDETECTED-CHROMEDRIVER - Bypass Cloudflare

Ce script teste si undetected-chromedriver peut bypasser la protection Cloudflare
sur les pages profil Tracker.gg.
"""

import undetected_chromedriver as uc
import time
from pathlib import Path


def test_cloudflare_bypass():
    """Teste le bypass Cloudflare avec undetected-chromedriver"""
    
    print("=" * 80)
    print("🔓 TEST BYPASS CLOUDFLARE - undetected-chromedriver")
    print("=" * 80)
    
    # Configure undetected-chromedriver
    options = uc.ChromeOptions()
    # options.add_argument('--headless=new')  # Désactivé pour voir ce qui se passe
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    print("\n🚀 Lancement de Chrome (undetected)...")
    driver = uc.Chrome(options=options, version_main=None)
    
    try:
        # Test 1 : Page profil Happy_3201
        player_id = "3208849653"
        url = f"https://tracker.gg/bf6/profile/{player_id}/overview"
        
        print(f"\n📡 Chargement de : {url}")
        driver.get(url)
        
        print("⏳ Attente 10 secondes pour Cloudflare...")
        time.sleep(10)
        
        # Sauvegarde le HTML
        html = driver.page_source
        output_file = Path("data/exploration/undetected_test.html")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"💾 HTML sauvegardé : {output_file}")
        print(f"📏 Taille : {len(html):,} caractères")
        
        # Vérifie si Cloudflare est présent
        if "Cloudflare" in html and "challenge" in html.lower():
            print("\n❌ Cloudflare toujours présent (challenge détecté)")
            print("💡 Undetected-chromedriver n'a pas réussi à bypasser")
            return False
        
        # Vérifie si on a des données de jeu
        if "Kills" in html or "Weapons" in html or "Stats" in html:
            print("\n✅ SUCCESS ! Page profil chargée correctement !")
            print("🎯 Cloudflare bypassé avec succès !")
            
            # Cherche des stats dans le HTML
            if "Kills" in html:
                print("   ✓ Section 'Kills' trouvée")
            if "Weapons" in html:
                print("   ✓ Section 'Weapons' trouvée")
            if "Accuracy" in html:
                print("   ✓ Statistique 'Accuracy' trouvée")
            
            return True
        else:
            print("\n⚠️  Page chargée mais contenu incomplet")
            print("💡 Peut-être besoin d'attendre plus longtemps")
            return False
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        return False
    
    finally:
        # Attente courte pour voir le résultat
        print("\n⏳ Fermeture automatique dans 3 secondes...")
        time.sleep(3)
        driver.quit()
        print("🏁 Test terminé.")


if __name__ == "__main__":
    success = test_cloudflare_bypass()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ RÉSULTAT : BYPASS RÉUSSI !")
        print("💡 On peut utiliser undetected-chromedriver pour l'extraction")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ RÉSULTAT : BYPASS ÉCHOUÉ")
        print("💡 Il faudra trouver une autre solution")
        print("=" * 80)
