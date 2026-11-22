#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    RECHERCHEUR DE TEXTE DANS LES FICHIERS
═══════════════════════════════════════════════════════════════════════════════

DESCRIPTION :
  Ce script permet de rechercher une chaîne de caractères (ou une expression
  régulière) dans l'ensemble des fichiers textes d'un projet, en excluant
  automatiquement :
    • Les fichiers/dossiers cachés (commençant par ".")
    • Les dossiers __pycache__, .git, .venv, venv
    • Les fichiers binaires (images, exécutables, etc.)
    • Les fichiers compilés (.pyc, .pyo, .pyd)

UTILISATION :
  python recherche_texte.py "CHAINE_A_RECHERCHER" [OPTIONS]

EXEMPLES :
  # Recherche simple de texte
  python recherche_texte.py "ALLOWED_HOSTS"

  # Recherche insensible à la casse
  python recherche_texte.py -i "mydjangoapp"

  # Recherche avec expression régulière (IP locale)
  python recherche_texte.py -r "192\.168\.\d+\.\d+"

  # Afficher le contexte des lignes trouvées (2 lignes avant/après)
  python recherche_texte.py "runserver" --contexte

  # Rechercher dans un dossier spécifique
  python recherche_texte.py "petrodashboard" -d /chemin/vers/projet

OPTIONS :
  -h, --help            Afficher ce message d'aide
  -i, --insensible      Ignorer la casse lors de la recherche
  -r, --regex           Interpréter la chaîne comme une expression régulière
  -c, --contexte        Afficher le contexte des lignes (lignes adjacentes)
  -d CHEMIN, --dossier CHEMIN
                        Dossier racine pour la recherche (défaut: dossier courant)

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import argparse
import re
from pathlib import Path

def est_fichier_binaire(chemin_fichier, taille_echantillon=1024):
    """Détecte si un fichier est binaire pour éviter les erreurs de lecture."""
    try:
        with open(chemin_fichier, 'rb') as f:
            echantillon = f.read(taille_echantillon)
            return b'\0' in echantillon
    except Exception:
        return True

def rechercher_dans_fichier(chemin_fichier, motif, sensible=True, contexte=False):
    """Recherche le motif dans un fichier texte avec gestion des encodages."""
    if est_fichier_binaire(chemin_fichier):
        return []
    
    encodage_trouve = None
    for enc in ['utf-8', 'latin-1', 'cp1252', 'ascii']:
        try:
            with open(chemin_fichier, 'r', encoding=enc) as f:
                lignes = f.readlines()
            encodage_trouve = enc
            break
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    
    if encodage_trouve is None:
        return []
    
    flags = 0 if sensible else re.IGNORECASE
    resultats = []
    
    for idx, ligne in enumerate(lignes, 1):
        if re.search(motif, ligne, flags):
            lignes_contexte = []
            if contexte:
                debut = max(0, idx - 3)
                fin = min(len(lignes), idx + 2)
                for i in range(debut, fin):
                    marqueur = " ➤ " if i + 1 == idx else "   "
                    lignes_contexte.append(f"{marqueur}{i+1:4d}: {lignes[i].rstrip()}")
            resultats.append((idx, ligne.rstrip(), lignes_contexte))
    
    return resultats

def recherche_recursive(racine, motif, sensible=True, contexte=False):
    """Parcourt récursivement l'arborescence en excluant les éléments indésirables."""
    nb_correspondances = 0
    racine = Path(racine).resolve()
    
    for dossier_actuel, sous_dossiers, fichiers in os.walk(racine):
        # Exclure les dossiers indésirables
        sous_dossiers[:] = [d for d in sous_dossiers 
                          if d not in ('__pycache__', '.git', '.venv', 'venv') 
                          and not d.startswith('.')]
        
        chemin_relatif = Path(dossier_actuel).relative_to(racine)
        if str(chemin_relatif) == '.':
            chemin_relatif = ''
        
        for nom_fichier in fichiers:
            # Ignorer les fichiers cachés et compilés
            if (nom_fichier.startswith('.') or 
                nom_fichier.endswith(('.pyc', '.pyo', '.pyd', '.sqlite', '.db'))):
                continue
            
            chemin_complet = Path(dossier_actuel) / nom_fichier
            try:
                resultats = rechercher_dans_fichier(chemin_complet, motif, sensible, contexte)
                if resultats:
                    print(f"\n📁 {chemin_relatif / nom_fichier if chemin_relatif else nom_fichier}")
                    print("─" * 70)
                    for num_ligne, contenu, lignes_ctx in resultats:
                        if contexte:
                            for ligne in lignes_ctx:
                                print(f"   {ligne}")
                        else:
                            extrait = contenu[:120] + "..." if len(contenu) > 120 else contenu
                            print(f"   🔍 Ligne {num_ligne:4d}: {extrait}")
                        nb_correspondances += 1
            except Exception as e:
                print(f"⚠️  Erreur de lecture {chemin_complet}: {e}", file=sys.stderr)
    
    return nb_correspondances

def main():
    parser = argparse.ArgumentParser(
        description="Recherche avancée de texte dans les fichiers d'un projet",
        epilog="Exemple: python recherche_texte.py 'petrodashboard' -i --contexte",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('motif', nargs='?', help="Chaîne ou expression régulière à rechercher")
    parser.add_argument('-d', '--dossier', default='.', help="Dossier racine pour la recherche (défaut: .)")
    parser.add_argument('-i', '--insensible', action='store_true', help="Ignorer la casse")
    parser.add_argument('-r', '--regex', action='store_true', help="Utiliser une expression régulière")
    parser.add_argument('-c', '--contexte', action='store_true', help="Afficher le contexte des lignes")
    parser.add_argument('-h', '--help', action='help', help="Afficher ce message d'aide")
    
    args = parser.parse_args()
    
    if not args.motif:
        print(__doc__)
        print("\n❌ ERREUR : Vous devez spécifier une chaîne à rechercher.")
        print("   Exemple: python recherche_texte.py \"ALLOWED_HOSTS\"\n")
        sys.exit(1)
    
    print("=" * 70)
    print(f"🔍 RECHERCHE EN COURS : '{args.motif}'")
    print(f"   Dossier : {os.path.abspath(args.dossier)}")
    print(f"   Type    : {'Expression régulière' if args.regex else 'Texte littéral'}")
    print(f"   Casse   : {'Sensible' if not args.insensible else 'Insensible'}")
    print("=" * 70 + "\n")
    
    motif_final = args.motif if args.regex else re.escape(args.motif)
    total = recherche_recursive(args.dossier, motif_final, not args.insensible, args.contexte)
    
    print("\n" + "=" * 70)
    if total == 0:
        print("❌ AUCUNE CORRESPONDANCE TROUVÉE")
    elif total == 1:
        print("✅ 1 CORRESPONDANCE TROUVÉE")
    else:
        print(f"✅ {total} CORRESPONDANCES TROUVÉES")
    print("=" * 70)

if __name__ == "__main__":
    main()