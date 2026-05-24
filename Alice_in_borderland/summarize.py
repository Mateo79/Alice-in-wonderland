import argparse
import requests
import os
import re
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from transformers import pipeline

# télécharge nltk
# punkt / punkt_tab pour découper le texte en phrases et en mots
for resource in ['punkt', 'punkt_tab', 'stopwords']:
    try:
        path = 'corpora/' + resource if resource == 'stopwords' else 'tokenizers/' + resource
        nltk.data.find(path)
    except LookupError:
        nltk.download(resource, quiet=True)

STOP = set(stopwords.words('english'))


##########################
######  load_book   ######
##########################
def load_book(id : int):
    # Si le livre a déjà été téléchargé on le relit depuis le cache
    # Sa évite de retélécharger à chaque fois
    if os.path.exists(f"./cache/book_{id}.txt"):
        with open(f"./cache/book_{id}.txt", encoding='utf-8') as f:
            return f.read()

    # Sinon on le télécharge depuis Project Gutenberg
    try:
        response = requests.get(f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt", timeout=15)
        
        if response.status_code == 200:
            os.makedirs('./cache', exist_ok=True)
            with open(f"./cache/book_{id}.txt", 'w', encoding='utf-8') as f:
                f.write(response.text)
            return response.text

    except requests.exceptions.RequestException as e:
        print('An error occurred during the request:', e)

    return ""


##########################
###### basic_summary #####
##########################
def basic_summary(text, n=4):
    
    # Nathan, on utilise uniquement cette fonction si le modèle d'ia échoue
    # les phrases qui contiennent les mots les plus fréquents du livre
    # sont probablement les plus importantes donc on les sélectionne
    sentences = sent_tokenize(text)
    if not sentences:
        return ""

    # On garde uniquement les mots significatifs (pas les stopwords, pas les mots trop courts)
    words = [w.lower() for w in word_tokenize(text) if w.isalpha() and w.lower() not in STOP and len(w) > 2]
    if not words:
        return sentences[0]

    # On calcule la fréquence de chaque mot, normalisée entre 0 et 1
    # si alice apparaît 200 fois et c'est le max son score = 200/200 = 1.0
    # si rabbit apparaît 50 fois son score = 50/200 = 0.25
    freq = Counter(words)
    top_freq = max(freq.values())
    scores = {w: c / top_freq for w, c in freq.items()}

    # Pour chaque phrase on calcule un score = moyenne des scores de ses mots
    ranked = []
    for i, sent in enumerate(sentences):
        sent_words = [w.lower() for w in word_tokenize(sent) if w.isalpha() and w.lower() not in STOP and len(w) > 2]
        # Ignore les phrases trop courtes ou qui commencent par un dialogue
        if len(sent_words) < 6 or sent.strip().startswith('"'):
            continue
        score = sum(scores.get(w, 0) for w in sent_words) / len(sent_words)
        # Les phrases de début posent souvent un contexte alors on donne plus de poids
        score *= 1.3 if i < 5 else 1.0
        ranked.append((i, sent.strip(), score))

    # On prend les n meilleures phrases et on les remet dans l'ordre du livre
    best = sorted(ranked, key=lambda x: x[2], reverse=True)[:n]
    return " ".join(s[1] for s in sorted(best, key=lambda x: x[0]))


##########################
######  get_summary ######
##########################
def get_summary(id : int):
    text = load_book(id)
    if not text:
        return ""

    # On charge le modèle de résumé*
    # Nathan ce modèle génère de nouvelles phrases il ne copie pas le texte
    model = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')

    # Nettoyage du texte
    # Les fichiers Gutenberg contiennent un entête et un pied de page légaux
    # Garde que se qui est entre les balises START / END
    clean_lines = []
    in_content = False

    for line in text.split('\n'):
        s = line.strip()

        if 'START OF THE PROJECT GUTENBERG' in line or 'START OF THIS PROJECT GUTENBERG' in line:
            in_content = True
            continue
        if 'END OF THE PROJECT GUTENBERG' in line or 'END OF THIS PROJECT GUTENBERG' in line:
            break
        if not in_content:
            continue

        # On filtre les lignes trop courtes, tout en majuscules (titres/chapitres),
        # numéros de version (ex: "3.0"), ou lignes contenant des mots de métadonnées
        if len(s) < 30 or s.isupper():
            continue
        
        # Quand tu auras lu jusqu'ici je veux que tu me dise comment sa s'appelle çà :"\b\d+\.\d+\b"
        if re.search(r'\b\d+\.\d+\b', s) and len(s.split()) < 10:
            continue
        if any(kw in s.lower() for kw in ['edition', 'copyright', 'license', 'project gutenberg', 'ebook', 'produced by', 'release date']):
            continue
        if s.lower().startswith(('produced by', 'transcribed by', 'prepared by')):
            continue

        clean_lines.append(s)

    clean_text = '\n'.join(clean_lines) if clean_lines else text

    # Découpage en chunks
    # Nathan le modèle ne peut pas traiter un livre entier d'un coup il a une limite de 512 token
    # On découpe donc le texte en morceaux de 1500 caractères en coupant aux paragraphes
    # pour pas couper une phrase en plein milieu
    chunks = []
    current = ""
    for para in clean_text.split('\n\n'):
        para = para.strip()
        if len(para) < 100:
            continue
        if current and len(current) + len(para) > 1500:
            chunks.append(current.strip())
            current = para + " "
        else:
            current += para + " "
    if current:
        chunks.append(current.strip())

    # Résumé de chaque chunk
    # Il y a 5 chunk pour que le temps de calcul ne soit pas trop long
    partial = []
    for chunk in chunks[:5]:
        try:
            # On limite à 512 mots car c'est la limite du modèle (mots = token)
            trimmed = " ".join(chunk.split()[:512])
            out = model(trimmed, max_length=150, min_length=50, do_sample=False)
            if out:
                partial.append(out[0]['summary_text'])
        except Exception:
            continue

    # Fusion des résumés partiels
    # Nathan maintenant on fusionne les résumer en repassant le modèle
    # pour avoir 1 seul résumer
    if len(partial) > 1:
        merged = " ".join(partial)
        if len(merged.split()) > 100:
            try:
                out = model(" ".join(merged.split()[:512]), max_length=150, min_length=50, do_sample=False)
                if out:
                    return out[0]['summary_text']
            except Exception:
                pass
        # Si la fusion échoue alors on retourne juste les 3 premiers résumés collés
        return " ".join(partial[:3])

    return partial[0]


########################
######    CLI     ######
########################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--summarize", nargs=1, type=int, help="Returns a short summary of the book.")

    args = parser.parse_args()

    if args.summarize:
        print(get_summary(args.summarize[0]))
