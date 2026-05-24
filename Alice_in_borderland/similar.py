import sys
import os
import requests
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def download_if_needed(resource):
    try:
        nltk.data.find(resource)
    except LookupError:
        nltk.download(resource.split("/")[-1], quiet=True)

download_if_needed("corpora/stopwords")

BOOKS = {
    11: "Alice's Adventures in Wonderland",
    12: "Through the Looking-Glass",
    16: "Peter Pan",
    55: "The Wonderful Wizard of Oz",
    113: "The Secret Garden",
    120: "Treasure Island",
    236: "The Jungle Book",
    108: "The Return of Sherlock Holmes",
    834: "The Memoirs of Sherlock Holmes",
    863: "The Mysterious Affair at Styles",
    1661: "The Adventures of Sherlock Holmes",
    61262: "Poirot Investigates",
    69087: "The murder of Roger Ackroyd",
    70114: "The Big Four",
    35: "The Time Machine",
    36: "The War of the Worlds",
    84: "Frankenstein; Or, The Modern Prometheus",
    159: "The island of Doctor Moreau",
    164: "Twenty Thousand Leagues under the Sea",
    345: "Dracula",
    68283: "The call of Cthulhu"
}

def download_book(book_id : int):
    # Vérifie le cache ou télécharge depuis Project Gutenberg
    cache_file = f"cache/{book_id}.txt"
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()
    # url = "https://www.gutenberg.org/files/" + book_id + "/" + book_id + ".txt"
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            os.makedirs("cache", exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(response.text)
            return response.text
    except:
        pass
    return ""

def get_similar(target_id : int):
    # Téléchargement des livres servant de comparaison
    texts = {}
    for bid in BOOKS:
        t = download_book(bid)
        if t:
            texts[bid] = t
    
    # Téléchargement du livre de référence
    if target_id not in texts:
        ref_book = download_book(target_id)
        if ref_book:
            texts[target_id] = ref_book

    # Similarité cosinus
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
    book_ids = list(texts.keys())
    matrix = vectorizer.fit_transform(texts.values())
    
    # Compare le livre
    target_index = book_ids.index(target_id)
    scores = cosine_similarity(matrix[target_index], matrix).flatten()
    
    # Trie décroissante et donne les 5 premières valeurs 
    sorted_indices = scores.argsort()[::-1]
    result = []
    for idx in sorted_indices:
        if idx != target_index:
            result.append(BOOKS[book_ids[idx]])
        if len(result) == 5:
            break
    return result

if __name__ == "__main__":
    if "--similar" not in sys.argv:
        print("Usage: python bookworm.py --similar <ID>")
        sys.exit(1)
    
    try:
        book_id = int(sys.argv[sys.argv.index("--similar") + 1])
    except:
        print("ID manquant")
        sys.exit(1)
    
    #if book_id not in BOOKS:
        #print("Livre non trouvé")
        #sys.exit(1)
    
    similar = get_similar(book_id)
    print(similar)
