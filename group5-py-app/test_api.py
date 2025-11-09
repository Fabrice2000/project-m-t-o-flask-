#!/usr/bin/env python3
"""
Script de test simple pour l'API Météo Activités
"""

import requests
import json
import sys

def test_api():
    """Test des endpoints principaux de l'API"""
    base_url = "http://localhost:8001"
    
    print("Test de l'API Météo Activités")
    print("=" * 50)
    
    # Test 1: Endpoint racine
    try:
        print("\n1. Test de l'endpoint racine (/)")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("Succès!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erreur: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Impossible de se connecter au serveur. Vérifiez qu'il fonctionne sur le port 8001")
        return False
    
    # Test 2: Santé de l'application
    try:
        print("\n2. Test de l'endpoint de santé (/health)")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("Succès!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erreur: {response.status_code}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Test 3: Démo météo
    try:
        print("\n3. Test de la démonstration météo (/demo/weather)")
        response = requests.get(f"{base_url}/demo/weather?ville=Paris")
        if response.status_code == 200:
            print("Succès!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erreur: {response.status_code}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Test 4: Démo activités
    try:
        print("\n4. Test de la démonstration activités (/demo/activities)")
        response = requests.get(f"{base_url}/demo/activities")
        if response.status_code == 200:
            print("Succès!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erreur: {response.status_code}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    # Test 5: Documentation
    try:
        print("\n5. Test de la documentation Swagger (/docs)")
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("Documentation accessible!")
            print(f"Ouvrez votre navigateur sur: {base_url}/docs")
        else:
            print(f"Erreur: {response.status_code}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    print("\nTests terminés!")
    print(f"Documentation complète: {base_url}/docs")
    print(f"Documentation alternative: {base_url}/redoc")
    
    return True

if __name__ == "__main__":
    test_api()