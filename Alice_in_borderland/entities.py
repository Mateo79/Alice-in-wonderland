# Import librairies
import argparse
import requests
import re
import regex
import os
import spacy
import pandas as pd

# Import fonction
from gutenberg_cleaner import simple_cleaner

# Lecture csv
df = pd.read_csv("pg_catalog.csv")


##########################
######   entities   ######
##########################

def entities(id : int):
    # Création du cache
    if not os.path.exists(f"./cache/entites_{id}"):
        try:
            response = requests.get(f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt")
            
            if response.status_code == 200:
                # Cette fois-ci j'enlève juste le header, footer et les espaces multiples pour fournir le texte brut à spacy
                book = re.sub(' +', ' ', simple_cleaner(response.text))
                
                if not os.path.exists(f"./cache/entities_{id}"):
                    os.makedirs(f"./cache/entities_{id}")

                # Je fais des groupes de 100 000 caractères ou moins car je coupe à la fin d'une phrase pour conserver un sens
                # Ceci permet de ne pas saturer le modèle et de procéder à une analyse par morceaux
                # Par exemple, je ne pouvais pas analyser d'un coup le livre 10 car il était trop long
                sentence_endings = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'
                split_book = re.split(sentence_endings, book)

                chunks = []
                current_chunk = ""
                
                for sent in split_book:
                    sent = sent.strip()
                    if len(current_chunk) + len(sent) > 100000:
                        chunks.append(current_chunk.strip())
                        current_chunk = ""
                    else:
                        current_chunk += sent + " "
                
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Je sauvegarde chaque chunk dans le cache
                i = 1
                for chunk in chunks:
                    with open(f"./cache/entities_{id}/chunk{i}.txt", 'w') as f:
                        f.write(chunk)
                    i += 1
        
        except requests.exceptions.RequestException as e:
            print('An error occurred during the request:', e)
    
    # Je charge le modèle et je l'applique à chaque partie du livre
    nlp = spacy.load("en_core_web_sm")
    
    characters = set()
    locations = set()
    author = df[df["Text#"] == id]["Authors"].iloc[0]
    words_in_author = regex.split(r"[^\p{L}]+" ,author)
    lowered_words_in_author = [word.lower() for word in words_in_author if word]
    
    for filename in os.listdir(f"./cache/entities_{id}"):
        file_path = os.path.join(f"./cache/entities_{id}", filename)
        with open(file_path, 'r') as f:
            doc = nlp(f.read())

        for ent in doc.ents:
            if ("chapter" not in ent.text.lower() 
                and len(ent.text) > 2 
                and "gutenberg" not in ent.text.lower() 
                and any(word in ent.text.lower() for word in lowered_words_in_author) == False
                and ent.text.isalpha() == True):
                if ent.label_ == "PERSON":
                    # Je garde que les noms propres
                    if all(token.pos_ in ["PROPN"] and token.tag_ in ["NNP", "NNPS"] for token in ent):
                        characters.add(ent.text)
                if ent.label_ == "GPE" or ent.label_ == "LOC":
                    # Je garde que les noms et noms propres
                    if all(token.pos_ in ["NOUN", "PROPN"] and token.tag_ in ["NN", "NNS", "NNP", "NNPS"] for token in ent):
                        locations.add(ent.text)

    entities = {}
    entities["characters"] = sorted(list(characters))
    entities["locations"] = sorted(list(locations))

    return(entities)


########################
######    CLI     ######
########################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--entities", nargs=1, type=int, help="Returns a dictionary containing the list of characters and the list of locations.")

    args = parser.parse_args()

    if args.entities:
        print(entities(args.entities[0]))
