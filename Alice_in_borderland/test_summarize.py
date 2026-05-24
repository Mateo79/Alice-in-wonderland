#!/usr/bin/env python3
# Exemple: python test_summarize.py 11
import sys
from summarize import get_summary


def test_summarize(id):    
    print("Génération du résumé...")
    try:
        summary = get_summary(id)
    except Exception as e:
        print(f"Erreur pendant le résumé : {e}")
        return False
    
    if not summary:
        print("Résumé vide")
        return False
    
    print("\nRésumé\n")
    print(summary)
    print(f"\nSuccès - {len(summary)} caractères, {len(summary.split())} mots")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_summarize.py <BOOK_ID>")
        sys.exit(1)

    success = test_summarize(int(sys.argv[1]))
    sys.exit(0 if success else 1)
