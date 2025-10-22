"""
SCRIPT DE DÉBOGAGE - Inspection de la page profil joueur

Ce script charge la page profil d'un joueur et sauvegarde le HTML
pour analyser la structure DOM et trouver les bons sélecteurs.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from pathlib import Path


def setup_browser():
    """Configure Chrome en mode headless"""
    chrome_options = Options()
    # chrome_options.add_argument('--headless=new')  # Désactivé pour voir la page
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    
    return driver


def main():
    """Charge la page profil et sauvegarde le HTML"""
    # Exemple : Happy_3201
    player_id = "3208849653"
    url = f"https://tracker.gg/bf6/profile/{player_id}/overview"
    
    print(f"🌐 Chargement de : {url}")
    
    driver = setup_browser()
    
    try:
        driver.get(url)
        print("⏳ Attente 5 secondes pour le chargement complet...")
        time.sleep(5)
        
        # Sauvegarde du HTML
        html_content = driver.page_source
        output_file = Path("data/exploration/profile_page_debug.html")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML sauvegardé : {output_file}")
        print(f"📏 Taille : {len(html_content):,} caractères")
        
        # Affiche les 50 premières lignes du body
        print("\n🔍 Aperçu du contenu (100 premières lignes du body) :")
        print("-" * 80)
        lines = html_content.split('\n')
        body_started = False
        line_count = 0
        for line in lines:
            if '<body' in line:
                body_started = True
            if body_started:
                print(line[:150])  # Limite à 150 caractères par ligne
                line_count += 1
                if line_count >= 100:
                    break
        
        print("\n⏸️  Appuyez sur Entrée pour fermer le navigateur...")
        input()
        
    finally:
        driver.quit()
        print("🏁 Terminé.")


if __name__ == "__main__":
    main()
