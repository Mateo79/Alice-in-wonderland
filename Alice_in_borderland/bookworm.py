import argparse
import sys
from lexdiv import lexdiv
from topics import get_topics
from entities import entities
from card import card
from summarize import get_summary
from similar import get_similar, BOOKS

VALID_IDS = set(BOOKS.keys())

# Vérifie que l'ID du livre est dans le catalogue, appelle la fonction donnée et affiche le résultat.
# Quitte avec un message d'erreur si l'ID est invalide ou si la fonction lève une exception.
def run(fn, id: int):
    if id not in VALID_IDS:
        print(f"Error: book ID {id} is not in the catalog. Valid IDs: {sorted(VALID_IDS)}")
        sys.exit(1)
    try:
        print(fn(id))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


parser = argparse.ArgumentParser(description="Bookworm — NLP Book Card Engine")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--lexdiv",    nargs=1, type=int, help="Returns a dictionary detailing the book's rich vocabulary.")
group.add_argument("--topics",    nargs=1, type=int, help="Extract the 10 most frequently used words from each section of the book.")
group.add_argument("--entities",  nargs=1, type=int, help="Returns a dictionary containing the list of characters and the list of locations.")
group.add_argument("--summarize", nargs=1, type=int, help="Returns a short summary of the book.")
group.add_argument("--similar",   nargs=1, type=int, help="Returns the 5 books most similar to the book with the specified ID.")
group.add_argument("--card",      nargs=1, type=int, help="Returns a metadata dictionary based on the provided book ID.")

args = parser.parse_args()

if args.lexdiv    is not None: run(lexdiv,       args.lexdiv[0])
if args.topics    is not None: run(get_topics,   args.topics[0])
if args.entities  is not None: run(entities,     args.entities[0])
if args.summarize is not None: run(get_summary,  args.summarize[0])
if args.similar   is not None: run(get_similar,  args.similar[0])
if args.card      is not None: run(card,         args.card[0])
