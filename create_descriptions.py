import pandas as pd
import pickle
import json


print("Loading data...")
with open('model/df_clean.pkl', 'rb') as f:
    df = pickle.load(f)


def create_story(row):
    title = row['title_english']

    genres = ", ".join(row['genres']) if isinstance(
        row['genres'], list) else str(row['genres'])
    themes = ", ".join(row['themes']) if isinstance(
        row['themes'], list) else str(row['themes'])

    score = round(row['score'] * 10, 2) if row['score'] < 1 else row['score']

    desc = f"Journey into the world of {title}. "
    if genres != "unknown":
        desc += f"This captivating {genres} saga "
    else:
        desc += "This series "

    if themes != "unknown" and themes != "nan":
        desc += f"explores profound themes of {themes}. "
    else:
        desc += "takes you on an unforgettable adventure. "

    desc += f"Critically acclaimed with a score of {score:.1f}, it remains a fan favorite."
    return desc


print("Writing the scrolls...")
descriptions = {}
for index, row in df.iterrows():

    key = row['title_english'] if row['title_english'] else row['title']
    descriptions[key] = create_story(row)


with open('model/descriptions.json', 'w') as f:
    json.dump(descriptions, f)

print("Success! 'descriptions.json' created in the model folder.")
