import sys, nltk, requests, os, pickle
from collections import Counter
from nltk.corpus import stopwords
from nltk import word_tokenize

for r in ['punkt', 'stopwords']:
    try: nltk.data.find(r)
    except: nltk.download(r, quiet=True)

STOP = set(stopwords.words('english'))

def load_book(book_id):
    if not os.path.exists(f"./cache/topics_{book_id}.pkl"):
        # url = f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt"
        url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            # Nettoyage et préparation des mots
            mots_propres = []
            for mot in word_tokenize(response.text):
                if mot.isalpha():
                    mot_minuscule = mot.lower()
                    if mot_minuscule not in STOP and len(mot_minuscule) > 2:
                        mots_propres.append(mot_minuscule)
            with open(f"./cache/topics_{book_id}.pkl", 'wb') as f:
                pickle.dump(mots_propres, f)
            return mots_propres
        except Exception as e:
            print(f"Erreur de téléchargement: {e}")
            return ""
    else:
        with open(f"./cache/topics_{book_id}.pkl", 'rb') as f:
            mots_propres = pickle.load(f)
        return mots_propres

def get_topics(book_id):
    mots_propres = load_book(book_id)

    # Préparation des sections
    total_mots = len(mots_propres)
    taille_section = total_mots // 4
    if taille_section == 0:
        taille_section = 1 # Sécurité

    resultat_final = {}

    # traitement de chaques sections
    for i in range(4):
        debut = i * taille_section
        fin = (i + 1) * taille_section if i < 3 else total_mots  # La dernière prend tout le reste        
        mots_section = mots_propres[debut:fin]
        compteur = Counter(mots_section)
        top_10 = [mot for mot, score in compteur.most_common(10)]
        resultat_final[i + 1] = top_10

    return resultat_final

if __name__ == "__main__":
    if "--topics" not in sys.argv: 
        print("Usage: python bookworm.py --topics <ID>"); sys.exit(1)
    try: book_id = sys.argv[sys.argv.index("--topics") + 1]
    except: print("ID manquant"); sys.exit(1)
    
    print(get_topics(book_id))
