from flask import Flask, request, jsonify, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import MySQLdb.cursors
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, supports_credentials=True)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user_feedback'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Load dataset high popularity
high_popularity_df = pd.read_csv('high_popularity_spotify_data.csv')

# Load dataset low popularity
low_popularity_df = pd.read_csv('low_popularity_spotify_data.csv')

# Menggabungkan kedua dataset
spotify_df = pd.concat([high_popularity_df, low_popularity_df], ignore_index=True)

# Pilih fitur numerik untuk cosine similarity
features = ['energy', 'tempo', 'danceability', 'loudness', 'valence', 'speechiness', 'instrumentalness', 'acousticness', 'key', 'duration_ms']
scaler = StandardScaler()
spotify_df[features] = scaler.fit_transform(spotify_df[features])

spotify_df.dropna(inplace=True)
spotify_df.drop_duplicates(inplace=True)

def find_similar_songs(song_names, top_n=30):
    song_vectors = []
    for song_name in song_names:
        if song_name not in spotify_df['track_name'].values:
            continue
        song_idx = spotify_df.index[spotify_df['track_name'] == song_name][0]
        song_vector = spotify_df.loc[song_idx, features].values
        song_vectors.append(song_vector)

    if not song_vectors:
        return None
    
    avg_vector = np.mean(song_vectors, axis=0).reshape(1, -1)
    similarity_scores = cosine_similarity(avg_vector, spotify_df[features])[0]
    sorted_indices = np.argsort(similarity_scores)[::-1]
    
    similar_songs = spotify_df.iloc[sorted_indices][['track_name', 'track_artist', 'uri']].copy()
    similar_songs['similarity'] = similarity_scores[sorted_indices]
    similar_songs = similar_songs[~similar_songs['track_name'].isin(song_names)]
    
    return similar_songs.head(top_n)

class EpsilonGreedyRecommender:
    def __init__(self, songs, epsilon=0.1):
        self.songs = songs
        self.epsilon = epsilon
        self.similarities = {song: songs[songs['track_name'] == song]['similarity'].values[0] for song in songs['track_name']}
    
    def select_top_songs(self, top_n=10):
        all_songs = list(self.songs['track_name'])
        if np.random.random() < self.epsilon:
            selected_songs = np.random.choice(all_songs, size=top_n, replace=False)
        else:
            sorted_songs = sorted(self.similarities, key=self.similarities.get, reverse=True)
            selected_songs = sorted_songs[:top_n]
        return [(song, self.similarities[song]) for song in selected_songs]

class ThompsonSamplingRecommender:
    def __init__(self, songs):
        self.songs = songs
        self.alpha = {song: songs[songs['track_name'] == song]['similarity'].values[0] + 1 for song in songs['track_name']}
        self.beta = {song: 1 for song in songs['track_name']}
    
    def select_top_songs(self, top_n=10):
        samples = {song: np.random.beta(self.alpha[song], self.beta[song]) for song in self.songs['track_name']}
        top_songs = sorted(samples, key=samples.get, reverse=True)[:top_n]
        return [(song, samples[song]) for song in top_songs]

def calculate_precision(recommendations, feedback):
    liked_songs = feedback[feedback['liked'] > 0].song_name.tolist()
    hits = [rec for rec in recommendations if rec in liked_songs]
    precision = len(hits) / len(recommendations) if recommendations else 0
    return precision

def calculate_average_precision(recommendations, feedback):
    liked_songs = feedback[feedback['liked'] > 0].song_name.tolist()
    hits = 0
    sum_precisions = 0
    for i, rec in enumerate(recommendations):
        if rec in liked_songs:
            hits += 1
            sum_precisions += hits / (i + 1)
    average_precision = sum_precisions / len(liked_songs) if liked_songs else 0
    return average_precision

def calculate_hitrate_at_k(recommendations, feedback, k=3):
    liked_songs = feedback[feedback['liked'] > 0].song_name.tolist()
    top_k_recommendations = recommendations[:k]
    hits = [rec for rec in top_k_recommendations if rec in liked_songs]
    hitrate = 1 if len(hits)>0 else 0
    return hitrate

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    account = cursor.fetchone()
    
    if account:
        return jsonify({'message': 'Account already exists!'}), 409
    else:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        mysql.connection.commit()
        return jsonify({'message': 'You have successfully registered!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    account = cursor.fetchone()
    
    if account and bcrypt.check_password_hash(account['password'], password):
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        return jsonify({'message': 'Login successful!'}), 200
    else:
        return jsonify({'message': 'Invalid username/password!'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return jsonify({'message': 'Logout successful!'}), 200

@app.route('/profile', methods=['GET'])
def profile():
    if 'loggedin' in session:
        return jsonify({'message': f'Welcome {session["username"]}!'}), 200
    else:
        return jsonify({'message': 'Please log in to view this page!'}), 401

@app.route('/recommend', methods=['POST'])
def recommend():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to get recommendations!'}), 401

    try:
        data = request.json
        song_names = data.get('song_names')
        
        similar_songs = find_similar_songs(song_names)
        if similar_songs is None or similar_songs.empty:
            return jsonify({'error': 'Lagu tidak ditemukan. Coba input lain.'}), 404
        
        ts_model = ThompsonSamplingRecommender(similar_songs)
        ts_recommendations = ts_model.select_top_songs()
        
        epsilon_greedy_model = EpsilonGreedyRecommender(similar_songs)
        epsilon_greedy_recommendations = epsilon_greedy_model.select_top_songs()
        
        cosine_recommendations = similar_songs[['track_name', 'track_artist', 'uri', 'similarity']].head(10).to_dict(orient='records')
        
        ts_recommendations = [{'song': song, 'artist': similar_songs.loc[similar_songs['track_name'] == song, 'track_artist'].values[0], 'uri': similar_songs.loc[similar_songs['track_name'] == song, 'uri'].values[0], 'score': score} for song, score in ts_recommendations]
        
        epsilon_greedy_recommendations = [{'song': song, 'artist': similar_songs.loc[similar_songs['track_name'] == song, 'track_artist'].values[0], 'uri': similar_songs.loc[similar_songs['track_name'] == song, 'uri'].values[0], 'score': score} for song, score in epsilon_greedy_recommendations]
        
        return jsonify({
            'cosine_recommendations': cosine_recommendations,
            'ts_recommendations': ts_recommendations,
            'epsilon_greedy_recommendations': epsilon_greedy_recommendations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to provide feedback!'}), 401

    try:
        data = request.json
        song_name = data.get('song_name')
        liked = data.get('liked')
        
        user_id = session.get('id')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM feedback WHERE user_id = %s AND song_name = %s', (user_id, song_name))
        existing_feedback = cursor.fetchone()
        
        if existing_feedback:
            cursor.execute('UPDATE feedback SET liked = %s WHERE user_id = %s AND song_name = %s', (liked, user_id, song_name))
        else:
            cursor.execute('INSERT INTO feedback (user_id, song_name, liked) VALUES (%s, %s, %s)', (user_id, song_name, liked))
        
        mysql.connection.commit()
        
        return jsonify({'message': 'Feedback berhasil disimpan'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/feedback', methods=['GET'])
def get_feedback():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to view feedback!'}), 401

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM feedback WHERE user_id = %s', (session.get('id'),))
    feedback = cursor.fetchall()
    return jsonify(feedback), 200

@app.route('/save_accuracy', methods=['POST'])
def save_accuracy():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to save accuracy!'}), 401

    try:
        data = request.json
        user_id = session.get('id')
        ts_accuracy = data.get('ts_accuracy')
        epsilon_greedy_accuracy = data.get('epsilon_greedy_accuracy')
        ts_hitrate_at_3 = data.get('ts_hitrate_at_3')
        epsilon_greedy_hitrate_at_3 = data.get('epsilon_greedy_hitrate_at_3')
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO accuracy (user_id, ts_accuracy, epsilon_greedy_accuracy, ts_hitrate_at_3, epsilon_greedy_hitrate_at_3) VALUES (%s, %s, %s, %s, %s)', (user_id, ts_accuracy, epsilon_greedy_accuracy, ts_hitrate_at_3, epsilon_greedy_hitrate_at_3))
        mysql.connection.commit()
        
        return jsonify({'message': 'Accuracy saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/evaluate', methods=['GET'])
def evaluate_users():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to view evaluations!'}), 401

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT 
            users.username, 
            MAX(accuracy.ts_accuracy) as ts_accuracy, 
            MAX(accuracy.epsilon_greedy_accuracy) as epsilon_greedy_accuracy, 
            MAX(accuracy.ts_hitrate_at_3) as ts_hitrate_at_3, 
            MAX(accuracy.epsilon_greedy_hitrate_at_3) as epsilon_greedy_hitrate_at_3
        FROM 
            accuracy 
        JOIN 
            users ON users.id = accuracy.user_id 
        GROUP BY 
            users.username
    ''')
    evaluation_data = cursor.fetchall()

    evaluations = {}
    for row in evaluation_data:
        username = row['username']
        evaluations[username] = {
            'ts_accuracy': row['ts_accuracy'],
            'epsilon_greedy_accuracy': row['epsilon_greedy_accuracy'],
            'ts_hitrate_at_3': row['ts_hitrate_at_3'],
            'epsilon_greedy_hitrate_at_3': row['epsilon_greedy_hitrate_at_3']
        }
    
    return jsonify(evaluations), 200

@app.route('/combined_accuracy', methods=['GET'])
def combined_accuracy():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to view combined accuracy!'}), 401

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT 
            MAX(accuracy.ts_accuracy) as ts_accuracy, 
            MAX(accuracy.epsilon_greedy_accuracy) as epsilon_greedy_accuracy, 
            MAX(accuracy.ts_hitrate_at_3) as ts_hitrate_at_3, 
            MAX(accuracy.epsilon_greedy_hitrate_at_3) as epsilon_greedy_hitrate_at_3
        FROM 
            accuracy 
        JOIN 
            users ON users.id = accuracy.user_id 
        GROUP BY 
            users.username
    ''')
    accuracy_data = cursor.fetchall()

    total_ts_accuracy = 0
    total_epsilon_greedy_accuracy = 0
    total_ts_hitrate_at_3 = 0
    total_epsilon_greedy_hitrate_at_3 = 0
    count = len(accuracy_data)

    for row in accuracy_data:
        total_ts_accuracy += row['ts_accuracy']
        total_epsilon_greedy_accuracy += row['epsilon_greedy_accuracy']
        total_ts_hitrate_at_3 += row['ts_hitrate_at_3']
        total_epsilon_greedy_hitrate_at_3 += row['epsilon_greedy_hitrate_at_3']
    
    combined_ts_accuracy = total_ts_accuracy / count if count > 0 else 0
    combined_epsilon_greedy_accuracy = total_epsilon_greedy_accuracy / count if count > 0 else 0
    combined_ts_hitrate_at_3 = total_ts_hitrate_at_3 / count if count > 0 else 0
    combined_epsilon_greedy_hitrate_at_3 = total_epsilon_greedy_hitrate_at_3 / count if count > 0 else 0

    return jsonify({
        'combined_ts_accuracy': combined_ts_accuracy,
        'combined_epsilon_greedy_accuracy': combined_epsilon_greedy_accuracy,
        'combined_ts_hitrate_at_3': combined_ts_hitrate_at_3,
        'combined_epsilon_greedy_hitrate_at_3': combined_epsilon_greedy_hitrate_at_3
    }), 200



@app.route('/search', methods=['GET'])
def search():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to search songs!'}), 401

    try:
        query = request.args.get('query', '').lower()
        
        if not query:
            return jsonify({'suggestions': []})
        
        matched_songs = spotify_df[(spotify_df['track_name'].str.lower().str.contains(query)) | (spotify_df['track_artist'].str.lower().str.contains(query))][['track_name', 'track_artist', 'uri']]
        suggestions = matched_songs.to_dict(orient='records')
        
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)