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

    features = ['energy', 'tempo', 'danceability', 'loudness', 'valence',
                'speechiness', 'instrumentalness', 'acousticness']
    
    
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

def find_similar_songs(song_ids, top_n=100):
    try:
        if not song_ids:
            return None

        song_vectors = []
        valid_ids = []
        
        for song_id in song_ids:
            matches = spotify_df[spotify_df['song_id'] == song_id]
            if not matches.empty:
                song_vector = matches.iloc[0][features].values
                song_vectors.append(song_vector)
                valid_ids.append(song_id)

        if not song_vectors:
            return None

        print(f"Memproses {len(valid_ids)} lagu valid dari {len(song_ids)} input")
        
        avg_vector = np.mean(song_vectors, axis=0).reshape(1, -1)
        similarity_scores = cosine_similarity(avg_vector, spotify_df[features])[0]
        
        result_df = spotify_df.copy()
        result_df['similarity'] = similarity_scores
        result_df = result_df[~result_df['song_id'].isin(valid_ids)]  # Exclude input songs
        result_df = result_df.sort_values(by='similarity', ascending=False)
        
        return result_df.head(top_n)
    
    except Exception as e:
        print(f"ERROR dalam find_similar_songs: {str(e)}")
        return None

class EpsilonGreedyRecommender:
    def __init__(self, songs, epsilon=0.1, n_iter=100):
        self.songs = songs
        self.epsilon = epsilon
        self.n_iter = n_iter
        self.rewards = {song['song_id']: song['similarity'] for _, song in self.songs.iterrows()}
        self.counts = {song['song_id']: 1 for _, song in self.songs.iterrows()}
        self.likes = {song['song_id']: 0 for _, song in self.songs.iterrows()}

    def update_feedback(self, song_id, liked):
        # --- PERBAIKAN UTAMA BAGIAN 1 ---
        # Mengonversi nilai `liked` menjadi integer 0 atau 1 untuk menghindari error
        # jika nilainya None dari database.
        liked_value = int(liked) if liked is not None else 0

        if liked_value == 1:
            self.rewards[song_id] += 1
        
        self.counts[song_id] += 1
        self.likes[song_id] += liked_value
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
        self.n_iter = n_iter  
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

        feedback_data = get_feedback_from_db(user_id)

        ts_model = ThompsonSamplingRecommender(similar_songs, n_iter=100)
        eg_model = EpsilonGreedyRecommender(similar_songs, n_iter=100)

        ts_model.apply_historical_feedback(feedback_data)
        eg_model.apply_historical_feedback(feedback_data)

        ts_recommendations = ts_model.select_top_songs()
        eg_recommendations = eg_model.select_top_songs()

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
    
@app.route('/recommend_from_liked', methods=['GET'])
def recommend_from_liked():
    try:
        print("\n=== Memulai recommend_from_liked ===")
        
        if 'loggedin' not in session:
            print("User not logged in")
            return jsonify({'message': 'Please log in!'}), 401

        user_id = session['id']
        print(f"User ID: {user_id}")

        # Dapatkan lagu yang disukai user
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT song_id FROM feedback WHERE user_id = %s AND liked = 1', (user_id,))
        liked_songs = cursor.fetchall()
        print(f"Jumlah liked songs: {len(liked_songs)}")

        if not liked_songs:
            print("Tidak ada liked songs")
            return jsonify({'epsilon_greedy_recommendations': []}), 200

        liked_song_ids = [song['song_id'] for song in liked_songs]
        print(f"Liked song IDs: {liked_song_ids}")

        # Dapatkan lagu serupa
        similar_songs = find_similar_songs(liked_song_ids)
        if similar_songs is None or similar_songs.empty:
            print("Tidak ada lagu serupa ditemukan")
            return jsonify({'epsilon_greedy_recommendations': []}), 200

        print(f"Jumlah lagu serupa ditemukan: {len(similar_songs)}")

        # Dapatkan feedback historis
        feedback_data = get_feedback_from_db(user_id)
        print(f"Jumlah feedback historis: {len(feedback_data)}")

        # Buat rekomendasi
        eg_model = EpsilonGreedyRecommender(similar_songs, n_iter=100)
        eg_model.apply_historical_feedback(feedback_data)
        eg_recommendations = eg_model.select_top_songs(top_n=10)
        print(f"Jumlah rekomendasi dihasilkan: {len(eg_recommendations)}")

        # Format respons
        recommendations = []
        for song_id, score in eg_recommendations:
            song_data = similar_songs[similar_songs['song_id'] == song_id].iloc[0]
            recommendations.append({
                'song_id': song_id,
                'track_name': song_data['track_name'],
                'track_artist': song_data['track_artist'],
                'uri': song_data['uri'],
                'playlist_genre': song_data['playlist_genre'],
                'score': float(score)
            })

        print("Rekomendasi berhasil dibuat")
        return jsonify({'epsilon_greedy_recommendations': recommendations}), 200

    except Exception as e:
        print(f"ERROR dalam recommend_from_liked: {str(e)}")
        traceback.print_exc()  # Cetak traceback lengkap
        return jsonify({'error': str(e)}), 500
@app.route('/feedback', methods=['POST'])
def feedback():
    if 'loggedin' not in session:
        return jsonify({'message': 'Login untuk memberikan feedback!'}), 401

    try:
        data = request.json
        song_id = data.get('song_id')
        
        # PERBAIKAN 3: Validasi input yang lebih ketat
        if song_id is None or 'liked' not in data:
            return jsonify({'error': 'song_id and liked status are required.'}), 400
        
        # Konversi 'liked' menjadi integer (1 atau 0)
        liked = 1 if data['liked'] else 0
        
        relevance_ts = data.get('relevance_ts')
        relevance_eg = data.get('relevance_eg')

        user_id = session.get('id')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT user_id FROM feedback WHERE user_id = %s AND song_id = %s', (user_id, song_id))
        existing_feedback = cursor.fetchone()
        
        if existing_feedback:
            # Logika UPDATE Anda
            cursor.execute('''
                UPDATE feedback 
                SET liked = %s, 
                    relevance_ts = COALESCE(%s, relevance_ts),
                    relevance_eg = COALESCE(%s, relevance_eg)
                WHERE user_id = %s AND song_id = %s
            ''', (liked, relevance_ts, relevance_eg, user_id, song_id))
        else:
            # Logika INSERT Anda
            cursor.execute('''
                INSERT INTO feedback (user_id, song_id, liked, relevance_ts, relevance_eg) 
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, song_id, liked, relevance_ts, relevance_eg))
            
        mysql.connection.commit()
        return jsonify({'message': 'Feedback berhasil disimpan'}), 200
    except Exception as e:
        mysql.connection.rollback() # Rollback jika terjadi error
        app.logger.error(f"Error in /feedback: {e}", exc_info=True)
        return jsonify({'error': 'An internal server error occurred.'}), 500
    
@app.route('/feedback', methods=['GET'])
def get_feedback():
    if 'loggedin' not in session:
        return jsonify({'message': 'Please log in!'}), 401

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
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
            users.user_id,
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
            evaluations[username] = {
                'user_id': row['user_id'],
                'metrics': {}
            }
        key = f"{row['algorithm']}_{row['metric_type']}_@{row['k_value']}"
        evaluations[username]['metrics'][key] = row['metric_score']

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