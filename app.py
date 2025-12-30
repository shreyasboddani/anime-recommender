from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import difflib
import random  # <--- Added random library

app = Flask(__name__)

# --- LOAD DATA ---
print("Initializing Neural Link...")
with open('model/cosine_sim_nn.pkl', 'rb') as f:
    cosine_sim = pickle.load(f)
with open('model/indices_nn.pkl', 'rb') as f:
    indices = pickle.load(f)
with open('model/df_clean.pkl', 'rb') as f:
    df = pickle.load(f)

# Convert keys to list for random selection and search
all_titles = list(indices.keys())

print("System Ready.")


@app.route('/')
def home():
    return render_template('index.html')

# --- HELPER FUNCTION ---


def get_recommendations_for_title(title):
    """Reusable logic to get recs for a specific title"""
    idx = indices[title]
    if isinstance(idx, (pd.Series, pd.Index)):
        idx = idx.iloc[0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    seen = {title}

    for i, score in sim_scores[1:100]:
        if i >= len(df):
            continue
        row = df.iloc[i]
        t = row['title_english'] if row.get('title_english') else row['title']

        if t not in seen:
            recommendations.append(t)
            seen.add(t)
        if len(recommendations) >= 10:
            break

    return recommendations


@app.route('/recommend', methods=['POST'])
def recommend():
    request_data = request.json
    user_input = request_data.get('anime_name', '')

    # Smart Search (Fuzzy Match)
    if user_input in indices:
        found_title = user_input
    else:
        closest_matches = difflib.get_close_matches(
            user_input, all_titles, n=1, cutoff=0.4)
        if closest_matches:
            found_title = closest_matches[0]
        else:
            return jsonify({'error': f"Could not find anime similar to '{user_input}'."})

    recs = get_recommendations_for_title(found_title)

    return jsonify({
        'recommendations': recs,
        'matched_name': found_title
    })


@app.route('/random', methods=['GET'])
def surprise_me():
    # 1. Pick a random seed anime
    random_seed = random.choice(all_titles)

    # 2. Get recommendations for it
    recs = get_recommendations_for_title(random_seed)

    # 3. Return results (We tell the frontend which anime we picked)
    return jsonify({
        'recommendations': recs,
        'matched_name': random_seed
    })


if __name__ == '__main__':
    app.run(debug=True)
