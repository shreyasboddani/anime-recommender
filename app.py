from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import difflib  # <--- This is the library that does the fuzzy matching

app = Flask(__name__)

# --- LOAD DATA ---
print("Initializing Neural Link...")
with open('model/cosine_sim_nn.pkl', 'rb') as f:
    cosine_sim = pickle.load(f)
with open('model/indices_nn.pkl', 'rb') as f:
    indices = pickle.load(f)
with open('model/df_clean.pkl', 'rb') as f:
    df = pickle.load(f)

# Create a list of all valid titles for the search engine to look through
# We convert keys to a list so the matcher can scan them
all_titles = list(indices.keys())

print("System Ready.")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    request_data = request.json
    user_input = request_data.get('anime_name', '')

    # --- SMART SEARCH LOGIC ---
    # 1. Try an exact match first (Fastest)
    if user_input in indices:
        found_title = user_input
    else:
        # 2. If not found, try to find the closest match
        # n=1 means "give me the top 1 best match"
        # cutoff=0.4 means "it doesn't have to be perfect, just 40% similar"
        closest_matches = difflib.get_close_matches(
            user_input, all_titles, n=1, cutoff=0.4)

        if closest_matches:
            found_title = closest_matches[0]
        else:
            return jsonify({'error': f"Could not find anime similar to '{user_input}'. Try being more specific!"})

    # --- RECOMMENDATION LOGIC ---
    idx = indices[found_title]

    # Handle case where index might be a Series (duplicate titles in DB)
    if isinstance(idx, (pd.Series, pd.Index)):
        idx = idx.iloc[0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    seen = {found_title}  # Don't recommend the anime itself

    # Get Top 10
    for i, score in sim_scores[1:100]:
        if i >= len(df):
            continue

        row = df.iloc[i]
        title = row['title_english'] if row.get(
            'title_english') else row['title']

        if title not in seen:
            recommendations.append(title)
            seen.add(title)

        if len(recommendations) >= 10:
            break

    # We send back the 'matched_name' so the frontend can tell the user
    # "We found recommendations for [Corrected Name]"
    return jsonify({
        'recommendations': recommendations,
        'matched_name': found_title
    })


if __name__ == '__main__':
    app.run(debug=True)
