import pandas as pd
import pickle
import json

# 1. Load your dataframe
print("Loading data...")
with open('model/df_clean.pkl', 'rb') as f:
    df = pickle.load(f)

# 2. Define a function to create a story from the data


def create_story(row):
    title = row['title_english']
    # Handle genres/themes if they are lists or strings
    genres = ", ".join(row['genres']) if isinstance(
        row['genres'], list) else str(row['genres'])
    themes = ", ".join(row['themes']) if isinstance(
        row['themes'], list) else str(row['themes'])
    # Adjust score format if needed
    score = round(row['score'] * 10, 2) if row['score'] < 1 else row['score']

    # Construct the narrative
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


# 3. Apply it to every anime
print("Writing the scrolls...")
descriptions = {}
for index, row in df.iterrows():
    # Use English title as key, fallback to original title
    key = row['title_english'] if row['title_english'] else row['title']
    descriptions[key] = create_story(row)

# 4. Save to JSON
with open('model/descriptions.json', 'w') as f:
    json.dump(descriptions, f)

print("Success! 'descriptions.json' created in the model folder.")
