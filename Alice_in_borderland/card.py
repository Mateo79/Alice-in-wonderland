import argparse
import os
import pickle
import pandas as pd
from lexdiv import lexdiv
from topics import get_topics
from entities import entities
from summarize import get_summary
from similar import get_similar

df = pd.read_csv("pg_catalog.csv")

def card(id : int):
    if not os.path.exists(f"./cache/card_{id}.pkl"):
        card = {}

        ######################
        #####    info    #####
        ######################

        df_selection = df[df["Text#"] == id]
        
        info = {}
        info["id"] = str(df_selection["Text#"].values[0])
        info["author"] = str(df_selection["Authors"].values[0])
        info["bookshelves"] = str(df_selection["Bookshelves"].values[0])

        card["info"] = info

        ######################
        ####    lexdiv    ####
        ######################

        card["lexdiv"] = lexdiv(id)

        ######################
        ####    topics    ####
        ######################

        card["topics"] = get_topics(id)

        ######################
        ###   entitities   ###
        ######################

        card["entities"] = entities(id)

        #######################
        #####   summary   #####
        #######################

        card["summary"] = get_summary(id)

        #######################
        #####   similar   #####
        #######################

        card["similar"] = get_similar(id)

        ######################
        #####    card    #####
        ######################

        with open(f"./cache/card_{id}.pkl", 'wb') as f:
            pickle.dump(card, f)
        return(card)
    else:
        with open(f"./cache/card_{id}.pkl", 'rb') as f:
            card = pickle.load(f)
        return(card)

########################
######    CLI     ######
########################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--card", nargs=1, type=int, help="Returns a metadata dictionary based on the provided book ID.")

    args = parser.parse_args()

    if args.card is not None:
        print(card(args.card[0]))
