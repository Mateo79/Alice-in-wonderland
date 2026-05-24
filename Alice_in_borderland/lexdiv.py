# Import librairies
import argparse
import requests
import re
import os
import pickle

# Import fonction
from gutenberg_cleaner import simple_cleaner
from collections import Counter

# Imports NLTK
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag


############################
######    download    ######
############################

# Je download les ressources seulement si elles ne sont pas déjà installées, ce qui fait gagner du temps
def download_if_needed(resource):
    try:
        nltk.data.find(resource)
    except LookupError:
        nltk.download(resource.split("/")[-1], quiet=True)

download_if_needed("corpora/stopwords")
download_if_needed("tokenizers/punkt")
download_if_needed("taggers/averaged_perceptron_tagger_eng")


###########################
######     clean     ######
###########################

# Je crée une fonction permettant de nettoyer le livre pour rendre son contenu utilisable
def clean_book(book):
    # J'enlève le header et le footer du livre
    strip_book = simple_cleaner(book) 

    # Je remplace les espaces multiples et les tabulations par un espace unique
    clean_book = re.sub(' +', ' ', strip_book)

    # Je mets en minuscule tous les mots n'étant pas des noms propres
    # Méthode à revoir car certains mots sont considérés comme noms propres alors qu'ils ne le sont pas
    tokens = word_tokenize(clean_book)
    
    pos_tags = pos_tag(tokens)

    lowered_words = []
    for word, tag in pos_tags:
        if tag not in ["NNP", "NNPS"] and word != "I": # "I" reste en majuscule, par convention de la langue anglaise
            lowered_words.append(word.lower())
        else:
            lowered_words.append(word)

    clean_book = " ".join(lowered_words)

    # Retourne le contenu sous forme de chaîne de caractères
    return(clean_book)


##########################
####   tokenization   ####
##########################

def tokenization(book):
    # J'enlève la ponctuation
    without_punct_book = re.sub(r'[^\w\s]', '', book)
    
    # J'enlève tous les stopwords
    tokens = word_tokenize(without_punct_book)
    
    stop_words = set(stopwords.words('english'))
    without_stopwords_book = [word for word in tokens if word not in stop_words]
    
    # Retourne le contenu sous forme de liste
    return(without_stopwords_book) 


##########################
#####     lexdiv     #####
##########################

def lexdiv(id : int):
    # Création du cache
    if not os.path.exists(f"./cache/lexdiv_{id}.pkl"):
        try:
            response = requests.get(f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt")
            
            if response.status_code == 200:
                book = clean_book(response.text)
                book = tokenization(book)

                if not os.path.exists("./cache"):
                    os.makedirs("./cache")

                with open(f"./cache/lexdiv_{id}.pkl", 'wb') as f:
                    pickle.dump(book, f)
        
        except requests.exceptions.RequestException as e:
            print('An error occurred during the request:', e)

    with open(f"./cache/lexdiv_{id}.pkl", 'rb') as f:
        book = pickle.load(f)

    # Création du dictionnaire final
    lexdiv = {}

    lexdiv["tok"] = int(len(book))

    lexdiv["typ"] = int(len(set(book)))

    freq = Counter(book)
    words_that_appear_once = [num for num, count in freq.items() if count == 1]
    lexdiv["hap"] = int(len(words_that_appear_once))

    lexdiv["ttr"] = float(int(len(set(book))) / int(len(book)))

    lengths = [len(i) for i in book]
    mean = float(sum(lengths) / len(lengths))
    lexdiv["mwl"] = mean

    lexdiv["mwf"] = float(int(len(book)) / int(len(set(book))))

    return(lexdiv)


########################
######    CLI     ######
########################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--lexdiv", nargs=1, type=int, help="Returns a dictionary detailing the book's rich vocabulary.")

    args = parser.parse_args()

    if args.lexdiv is not None:
        print(lexdiv(args.lexdiv[0]))
