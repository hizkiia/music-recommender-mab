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


def get_feedback_from_db(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT song_id, liked FROM feedback WHERE user_id = %s", (user_id,))
    feedback = cursor.fetchall()
    cursor.close()
    return feedback


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
    def __init__(self, songs, epsilon=0.1, n_iter=100):
        self.songs = songs
        self.epsilon = epsilon
        self.n_iter = n_iter
        self.rewards = {song['song_id']: song['similarity'] for _, song in self.songs.iterrows()}
        self.counts = {song['song_id']: 1 for _, song in self.songs.iterrows()}
        self.likes = {song['song_id']: 0 for _, song in self.songs.iterrows()}

    def update_feedback(self, song_id, liked):
        if liked:
            self.rewards[song_id] += 1
        self.counts[song_id] += 1
        self.likes[song_id] += liked

    def apply_historical_feedback(self, feedback_data):
        for record in feedback_data:
            song_id = record['song_id']
            liked = record['liked']
            if song_id in self.rewards:
                self.update_feedback(song_id, liked)

    def warmup(self):
        for _ in range(self.n_iter):
            if np.random.random() < self.epsilon:
                song_id = np.random.choice(self.songs['song_id'])
            else:
                song_id = max(self.rewards.items(), key=lambda x: x[1])[0]
            self.update_feedback(song_id, liked=np.random.random() > 0.5)

    def select_top_songs(self, top_n=10):
        self.warmup()
        sorted_songs = sorted(self.rewards, key=self.rewards.get, reverse=True)[:top_n]
        return [(song_id, self.rewards[song_id]) for song_id in sorted_songs]

class ThompsonSamplingRecommender:
    def __init__(self, songs, n_iter=100):
        self.songs = songs
        self.n_iter = n_iter  # Jumlah iterasi
        self.alpha = {song['song_id']: song['similarity'] + 1 for _, song in self.songs.iterrows()}
        self.beta = {song['song_id']: 1 for _, song in self.songs.iterrows()}
        self.successes = {song['song_id']: 0 for _, song in self.songs.iterrows()}
        self.trials = {song['song_id']: 0 for _, song in self.songs.iterrows()}

    def update_feedback(self, song_id, liked):
        if liked:
            self.alpha[song_id] += 1
            self.successes[song_id] += 1
        else:
            self.beta[song_id] += 1
        self.trials[song_id] += 1

    def apply_historical_feedback(self, feedback_data):
        for record in feedback_data:
            song_id = record['song_id']
            liked = record['liked']
            if song_id in self.alpha:
                self.update_feedback(song_id, liked)

    def warmup(self):
        for _ in range(self.n_iter):
            samples = {song_id: np.random.beta(self.alpha[song_id], self.beta[song_id]) 
                       for song_id in self.songs['song_id']}
            song_id = max(samples.items(), key=lambda x: x[1])[0]
            self.update_feedback(song_id, liked=np.random.random() > 0.5)

    def select_top_songs(self, top_n=10):
        self.warmup()
        samples = {song_id: np.random.beta(self.alpha[song_id], self.beta[song_id]) 
                   for song_id in self.songs['song_id']}
        top_songs = sorted(samples, key=samples.get, reverse=True)[:top_n]
        return [(song_id, samples[song_id]) for song_id in top_songs]
    
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
        user_id = session['id']  # ambil ID user dari session
        data = request.json
        song_ids = data.get('song_ids', [])
        
        if not song_ids:
            return jsonify({'error': 'song_ids is required and cannot be empty'}), 400

        similar_songs = find_similar_songs(song_ids)
        if similar_songs is None or similar_songs.empty:
            return jsonify({'error': 'No similar songs found. Try another input.'}), 404

        # Ambil data feedback user dari database
        feedback_data = get_feedback_from_db(user_id)

        # Inisialisasi model dengan lagu yang mirip
        ts_model = ThompsonSamplingRecommender(similar_songs, n_iter=100)
        eg_model = EpsilonGreedyRecommender(similar_songs, n_iter=100)

        # Terapkan feedback historis ke model
        ts_model.apply_historical_feedback(feedback_data)
        eg_model.apply_historical_feedback(feedback_data)

        # Dapatkan rekomendasi
        ts_recommendations = ts_model.select_top_songs()
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
        print("Error in /recommend:", str(e))
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