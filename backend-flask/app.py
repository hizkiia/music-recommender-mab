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

CORS(app, supports_credentials=True, origins=["http://localhost:5173"])


# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'music_recommendation'

mysql = MySQL(app)
bcrypt = Bcrypt(app)
def load_songs_from_db():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM songs')
    result = cursor.fetchall()
    df = pd.DataFrame(result)

    # Pilih fitur numerik
    features = ['energy', 'tempo', 'danceability', 'loudness', 'valence',
                'speechiness', 'instrumentalness', 'acousticness']
    
    # Paksa fitur jadi numerik (jika ada yang string)
    df[features] = df[features].apply(pd.to_numeric, errors='coerce')

    # Hilangkan yang tidak bisa dikonversi (NaN hasil coercion)
    df.dropna(subset=features, inplace=True)

    # Hapus duplikat
    df.drop_duplicates(inplace=True)
    
    return df, features
# Load data saat app dijalankan
with app.app_context():
    spotify_df, features = load_songs_from_db()


# # Load dataset high popularity
# high_popularity_df = pd.read_csv('high_popularity_spotify_data.csv')

# # Load dataset low popularity
# low_popularity_df = pd.read_csv('low_popularity_spotify_data.csv')

# # Menggabungkan kedua dataset
# spotify_df = pd.concat([high_popularity_df, low_popularity_df], ignore_index=True)

# # Pilih fitur numerik untuk cosine similarity
# features = ['energy', 'tempo', 'danceability', 'loudness', 'valence', 'speechiness', 'instrumentalness', 'acousticness', 'key', 'duration_ms']
# scaler = StandardScaler()
# spotify_df[features] = scaler.fit_transform(spotify_df[features])

# spotify_df.dropna(inplace=True)
# spotify_df.drop_duplicates(inplace=True)

def find_similar_songs(song_ids, top_n=50):
    song_vectors = []
    
    for song_id in song_ids:
        matches = spotify_df[spotify_df['song_id'] == song_id]  
        if matches.empty:
            continue
        song_vector = matches.iloc[0][features].values
        song_vectors.append(song_vector)

    if not song_vectors:
        return None

    avg_vector = np.mean(song_vectors, axis=0).reshape(1, -1)
    similarity_scores = cosine_similarity(avg_vector, spotify_df[features])[0]
    spotify_df['similarity'] = similarity_scores

    # Sort by similarity and exclude the songs already in the song_ids list
    similar_songs = spotify_df.copy()
    similar_songs = similar_songs[~similar_songs['song_id'].isin(song_ids)]  # Exclude selected songs
    similar_songs = similar_songs.sort_values(by='similarity', ascending=False)

    # Return the top_n similar songs based on the highest similarity
    return similar_songs[['song_id', 'track_name', 'track_artist', 'uri', 'similarity']].head(top_n)

class EpsilonGreedyRecommender:
    def __init__(self, songs, epsilon=0.2):
        self.songs = songs
        self.epsilon = epsilon
        # Inisialisasi rewards berdasarkan song_id
        self.rewards = {song['song_id']: song['similarity'] for _, song in self.songs.iterrows()}
        self.likes = {song['song_id']: 0 for _, song in self.songs.iterrows()}  # Total like (dari feedback)

    def select_top_songs(self, top_n=10):
        # Pilih top 10 berdasarkan reward tertinggi
        sorted_songs = sorted(self.rewards, key=self.rewards.get, reverse=True)[:top_n]
        
        # Mengembalikan daftar lagu dengan song_id dan reward-nya
        return [(song_id, self.rewards[song_id]) for song_id in sorted_songs]

    def update_feedback(self, song_id, liked):
        # Update reward dan like berdasarkan feedback song_id
        if liked:
            self.rewards[song_id] += 1
        self.likes[song_id] += 1

class ThompsonSamplingRecommender:
    def __init__(self, songs):
        self.songs = songs
        # Inisialisasi alpha dan beta untuk song_id
        self.alpha = {song['song_id']: song['similarity'] + 1 for _, song in self.songs.iterrows()}
        self.beta = {song['song_id']: 1 for _, song in self.songs.iterrows()}

    def select_top_songs(self, top_n=10):
        # Ambil sampel dari distribusi Beta untuk setiap song_id
        samples = {song_id: np.random.beta(self.alpha[song_id], self.beta[song_id]) for song_id in self.songs['song_id']}
        
        # Ambil top 10 song_id dengan nilai sampel tertinggi
        top_songs = sorted(samples, key=samples.get, reverse=True)[:top_n]
        
        # Mengembalikan daftar song_id dan nilai sampelnya
        return [(song_id, samples[song_id]) for song_id in top_songs]

    def update_feedback(self, song_id, liked):
        # Update alpha dan beta berdasarkan feedback song_id
        if liked:
            self.alpha[song_id] += 1
        else:
            self.beta[song_id] += 1


# def calculate_precision_at_k(recommendations, feedback, k):
#     liked_songs = feedback[feedback['liked'] > 0].song_name.tolist()
#     top_k_recommendations = recommendations[:k]
#     hits = [rec for rec in top_k_recommendations if rec in liked_songs]
#     precision = len(hits) / k if k > 0 else 0
#     return precision

# def calculate_average_precision_at_k(recommendations, feedback, k):
#     liked_songs = feedback[feedback['liked'] > 0].song_name.tolist()
#     hits = 0
#     sum_precisions = 0
#     for i, rec in enumerate(recommendations[:k]):
#         if rec in liked_songs:
#             hits += 1
#             sum_precisions += hits / (i + 1)
#     average_precision = sum_precisions / len(liked_songs) if liked_songs else 0
#     return average_precision

# def calculate_hitrate_at_k(recommendations, feedback, k):
#     liked_songs = feedback[feedback['liked'] > 0].song_name.tolist()
#     top_k_recommendations = recommendations[:k]
#     hits = [rec for rec in top_k_recommendations if rec in liked_songs]
#     hitrate = 1 if len(hits) > 0 else 0
#     return hitrate

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
        session['id'] = account['user_id']
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
        song_ids = data.get('song_ids', [])

        print("🎵 Song IDs received:", song_ids)  # Debugging
        
        if not song_ids:
            return jsonify({'error': 'song_ids is required and cannot be empty'}), 400

        # Proses rekomendasi dengan song_ids
        similar_songs = find_similar_songs(song_ids)
        if similar_songs is None or similar_songs.empty:
            return jsonify({'error': 'No similar songs found. Try another input.'}), 404

        ts_model = ThompsonSamplingRecommender(similar_songs)
        ts_recommendations = ts_model.select_top_songs()

        eg_model = EpsilonGreedyRecommender(similar_songs)
        eg_recommendations = eg_model.select_top_songs()

        # Format output
        ts_recommendations = [{
            'song_id': song_id,
            'track_name': similar_songs.loc[similar_songs['song_id'] == song_id, 'track_name'].values[0],
            'track_artist': similar_songs.loc[similar_songs['song_id'] == song_id, 'track_artist'].values[0],
            'uri': similar_songs.loc[similar_songs['song_id'] == song_id, 'uri'].values[0],
            'score': score,
             'relevance_ts': 0
        } for song_id, score in ts_recommendations]

        eg_recommendations = [{
            'song_id': song_id,
            'track_name': similar_songs.loc[similar_songs['song_id'] == song_id, 'track_name'].values[0],
            'track_artist': similar_songs.loc[similar_songs['song_id'] == song_id, 'track_artist'].values[0],
            'uri': similar_songs.loc[similar_songs['song_id'] == song_id, 'uri'].values[0],
            'score': score,
             'relevance_eg': 0
        } for song_id, score in eg_recommendations]

        return jsonify({
            'ts_recommendations': ts_recommendations,
            'epsilon_greedy_recommendations': eg_recommendations
        }), 200

    except Exception as e:
        print("🔥 Error in /recommend:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    if 'loggedin' not in session:
        return jsonify({'message': 'Login untuk memberikan feedback!'}), 401

    try:
        data = request.json
        song_id = data.get('song_id')
        liked = data.get('liked')
        relevance_ts = data.get('relevance_ts')  # New field for Thompson Sampling
        relevance_eg = data.get('relevance_eg')  # New field for Epsilon-Greedy

        user_id = session.get('id')
        cursor = mysql.connection.cursor()
        
        # Check if feedback exists
        cursor.execute('SELECT * FROM feedback WHERE user_id = %s AND song_id = %s', 
                      (user_id, song_id))
        existing_feedback = cursor.fetchone()
        
        if existing_feedback:
            # Update existing feedback with new relevance values
            cursor.execute('''
                UPDATE feedback 
                SET liked = %s, 
                    relevance_ts = COALESCE(%s, relevance_ts),
                    relevance_eg = COALESCE(%s, relevance_eg)
                WHERE user_id = %s AND song_id = %s
            ''', (liked, relevance_ts, relevance_eg, user_id, song_id))
        else:
            # Insert new feedback with relevance values
            cursor.execute('''
                INSERT INTO feedback 
                (user_id, song_id, liked, relevance_ts, relevance_eg) 
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, song_id, liked, relevance_ts, relevance_eg))
        
        mysql.connection.commit()
        return jsonify({'message': 'Feedback berhasil disimpan'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/feedback', methods=['GET'])
def get_feedback():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in!'}), 401

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Ambil feedback + data lagu
    cursor.execute('''
        SELECT 
            f.song_id,
            f.liked,
            f.relevance_ts,
            f.relevance_eg,
                   f.updated_at,  
            s.track_name,
            s.track_artist,
            s.playlist_genre,
            s.uri
        FROM feedback f
        JOIN songs s ON f.song_id = s.song_id
        WHERE f.user_id = %s
    ''', (session['id'],))
    
    feedback = cursor.fetchall()
    return jsonify(feedback), 200

@app.route('/save_accuracy', methods=['POST'])
def save_accuracy():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to save accuracy!'}), 401

    try:
        data = request.json
        user_id = session.get('id')
        evaluations = data.get('evaluations') 

        cursor = mysql.connection.cursor()

        for item in evaluations:
            algorithm = item['algorithm']  
            metric_type = item['metric_type']  
            k_value = item['k']
            score = item['score']

            cursor.execute('''
                INSERT INTO evaluation_metrics (user_id, algorithm, metric_type, k_value, metric_score)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, algorithm, metric_type, k_value, score))

        mysql.connection.commit()
        return jsonify({'message': 'All evaluation metrics saved successfully!'}), 200
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
            em.algorithm,
            em.metric_type,
            em.k_value,
            em.metric_score
        FROM evaluation_metrics em
        JOIN users ON users.user_id = em.user_id
        WHERE em.evaluated_at IN (
            SELECT MAX(evaluated_at)
            FROM evaluation_metrics
            GROUP BY user_id, algorithm, metric_type, k_value
        )
        ORDER BY users.username, em.algorithm, em.metric_type, em.k_value
    ''')
    evaluation_data = cursor.fetchall()

    evaluations = {}
    for row in evaluation_data:
        username = row['username']
        if username not in evaluations:
            evaluations[username] = {}
        key = f"{row['algorithm']}_{row['metric_type']}_@{row['k_value']}"
        evaluations[username][key] = row['metric_score']

    # Tambahkan logging untuk memeriksa data sebelum mengirim respons
    print("Evaluation Data:", evaluations)
    
    return jsonify(evaluations), 200

@app.route('/all_songs', methods=['GET'])
def get_all_songs():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to view songs!'}), 401
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM songs')
        songs = cursor.fetchall()

        return jsonify({'songs': songs})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/all-songs-by-genre', methods=['GET'])
def get_all_songs_by_genre():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM songs')
        all_songs = cursor.fetchall()
        
        # Kelompokkan lagu berdasarkan genre
        songs_by_genre = {}
        for song in all_songs:
            genre = song['playlist_genre']
            if genre not in songs_by_genre:
                songs_by_genre[genre] = []
            songs_by_genre[genre].append({
                'song_id': song['song_id'],
                'track_name': song['track_name'],
                'track_artist': song['track_artist'],
                'playlist_genre': song['playlist_genre'],
                'playlist_subgenre': song['playlist_subgenre'],
                'uri': song['uri']
            })
        
        return jsonify(songs_by_genre), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['GET'])
def search():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in to search songs!'}), 401

    try:
        query = request.args.get('query', '').lower()
        
        if not query:
            return jsonify({'suggestions': []})
        
        matched_songs = spotify_df[(spotify_df['track_name'].str.lower().str.contains(query)) | (spotify_df['track_artist'].str.lower().str.contains(query))][['song_id','track_name', 'track_artist', 'uri']]
        suggestions = matched_songs.to_dict(orient='records')
        
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True)