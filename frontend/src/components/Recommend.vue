<template>
  <div class="bg-dark text-white min-vh-100">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-deepblue">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Music Recommendation</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
          aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="showHome" :class="{ 'active': currentView === 'home' }">
                <i class="bi bi-house-door me-1"></i> Beranda
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="showRecommendations"
                :class="{ 'active': currentView === 'recommendations' }">
                <i class="bi bi-music-note-list me-1"></i> Rekomendasi
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="showLikedSongs"
                :class="{ 'active': currentView === 'liked' }">
                <i class="bi bi-heart me-1"></i> Liked Songs
              </a>
            </li>
          </ul>
          <div class="d-flex align-items-center">
            <span class="navbar-text me-3">
              <i class="bi bi-person-circle me-1"></i> {{ username }}
            </span>
            <button class="btn btn-outline-light" @click="logout">
              <i class="bi bi-box-arrow-right me-1"></i> Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="container mt-4">
      <!-- Home View -->
      <div v-if="currentView === 'home'">
        <div class="row mb-4">
          <div class="col-12">
            <div class="card bg-dark text-white border-secondary">
              <div class="card-body">
                <h3 class="card-title"><i class="bi bi-search me-2"></i>Cari Lagu</h3>
                <div class="input-group mb-3">
                  <input type="text" class="form-control bg-secondary text-white border-secondary" v-model="searchQuery"
                    @input="fetchSuggestions" placeholder="Search for a song or artist..." @keyup.enter="addSong">
                  <button class="btn btn-primary" type="button" @click="addSong">
                    <i class="bi bi-plus-lg"></i> Add
                  </button>
                </div>
                <div v-if="suggestions.length" class="suggestions-dropdown">
                  <ul class="list-group">
                    <li v-for="(suggestion, index) in suggestions" :key="index"
                      class="list-group-item list-group-item-action bg-secondary text-white"
                      @click="selectSong(suggestion)">
                      {{ suggestion.track_name }} - {{ suggestion.track_artist }}
                      <span class="badge bg-primary float-end">{{ suggestion.playlist_genre }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedSongs.length" class="row mb-4">
          <div class="col-12">
            <div class="card bg-dark text-white border-secondary">
              <div class="card-body">
                <h4 class="card-title"><i class="bi bi-list-check me-2"></i>Lagu yang dipilih ({{ selectedSongs.length
                }})</h4>
                <div class="d-flex flex-wrap gap-2">
                  <div v-for="(song, index) in selectedSongs" :key="index" class="card bg-secondary text-white"
                    style="width: 18rem;">
                    <div class="card-body">
                      <h5 class="card-title">{{ song.track_name }}</h5>
                      <h6 class="card-subtitle mb-2">{{ song.track_artist }}</h6>
                      <p class="card-text">
                        <span class="badge bg-info me-1">{{ song.playlist_genre }}</span>
                        <span class="badge bg-warning">{{ song.playlist_subgenre }}</span>
                      </p>
                      <button class="btn btn-sm btn-outline-danger" @click="removeSong(index)">
                        <i class="bi bi-trash"></i> Hapus
                      </button>
                    </div>
                  </div>
                </div>
                <button class="btn btn-primary mt-3" @click="fetchRecommendations" :disabled="selectedSongs.length < 3">
                  <i class="bi bi-stars me-1"></i> Dapatkan Rekomendasi
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <h3 class="mb-3"><i class="bi bi-collection me-2"></i>Cari berdasarkan genre</h3>
            <div class="accordion" id="genreAccordion">
              <div class="accordion-item bg-dark text-white border-secondary"
                v-for="(songs, genre, index) in allSongsByGenre" :key="index">
                <h2 class="accordion-header" :id="'heading' + index">
                  <button class="accordion-button bg-dark text-white" type="button" data-bs-toggle="collapse"
                    :data-bs-target="'#collapse' + index" :aria-expanded="index === 0 ? 'true' : 'false'"
                    :aria-controls="'collapse' + index">
                    {{ genre }} ({{ songs.length }} lagu)
                  </button>
                </h2>
                <div :id="'collapse' + index" class="accordion-collapse collapse" :class="{ 'show': index === 0 }"
                  :aria-labelledby="'heading' + index" data-bs-parent="#genreAccordion">
                  <div class="accordion-body">
                    <div v-if="songs.length === 0" class="text-center py-3">
                      Tidak ada lagu untuk genre ini
                    </div>
                    <div v-else class="row row-cols-1 row-cols-md-3 row-cols-lg-4 g-4">
                      <div class="col" v-for="(song, songIndex) in songs" :key="songIndex">
                        <div class="card h-100 bg-secondary text-white">
                          <div class="card-body">
                            <h5 class="card-title">{{ song.track_name }}</h5>
                            <h6 class="card-subtitle mb-2 ">{{ song.track_artist }}</h6>
                            <p class="card-text">
                              <span class="badge bg-primary me-1">{{ song.playlist_genre }}</span>
                              <span class="badge bg-warning">{{ song.playlist_subgenre }}</span>
                            </p>
                            <div class="d-flex justify-content-between">
                              <button class="btn btn-sm btn-outline-light" @click="playSong(song.uri)">
                                <i class="bi bi-play"></i> Play
                              </button>
                              <button class="btn btn-sm"
                                :class="likedSongs.includes(song.song_id) ? 'btn-danger' : 'btn-outline-success'"
                                @click="addLikedSongs(song.song_id, !likedSongs.includes(song.song_id))">
                                <i :class="likedSongs.includes(song.song_id) ? 'bi bi-heart-fill' : 'bi bi-heart'"></i>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations View -->
      <div v-if="currentView === 'recommendations'">
        <div class="row mb-4">
          <div class="col-12">
            <div class="card bg-dark text-white border-secondary">
              <div class="card-body">
                <h3 class="card-title"><i class="bi bi-magic me-2"></i>Rekomendasi Musik</h3>
                <p class="">Pilih 5 lagu favorit kamu</p>

                <div class="input-group mb-3">
                  <input type="text" class="form-control bg-secondary text-white border-secondary" v-model="searchQuery"
                    @input="fetchSuggestions" placeholder="Search for a song or artist..." @keyup.enter="addSong">
                  <button class="btn btn-primary" type="button" @click="addSong">
                    <i class="bi bi-plus-lg"></i> Tambah
                  </button>
                </div>

                <div v-if="suggestions.length" class="suggestions-dropdown">
                  <ul class="list-group">
                    <li v-for="(suggestion, index) in suggestions" :key="index"
                      class="list-group-item list-group-item-action bg-secondary text-white"
                      @click="selectSong(suggestion)">
                      {{ suggestion.track_name }} - {{ suggestion.track_artist }}
                    </li>
                  </ul>
                </div>

                <div v-if="selectedSongs.length" class="mt-3">
                  <h5>Lagu yang dipilih:</h5>
                  <div class="d-flex flex-wrap gap-2">
                    <span v-for="(song, index) in selectedSongs" :key="index" class="badge bg-primary p-2">
                      {{ song.track_name }}
                      <button class="btn btn-sm btn-outline-light ms-2" @click.stop="removeSong(index)">
                        <i class="bi bi-x"></i>
                      </button>
                    </span>
                  </div>
                </div>

                <button class="btn btn-primary mt-3" @click="fetchRecommendations" :disabled="selectedSongs.length < 3">
                  <i class="bi bi-stars me-1"></i> Dapatkan Rekomendasi
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showResults" class="row">
          <!-- Thompson Sampling Recommendations -->
          <div class="col-md-6 mb-4">
            <div class="card bg-dark text-white border-success">
              <div class="card-header bg-success text-white">
                <h4><i class="bi bi-graph-up-arrow me-2"></i>Thompson Sampling</h4>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-dark table-hover">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Judul</th>
                        <th>Artis</th>
                        <th>Aksi</th>
                        <th>Relevansi</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(song, index) in tsRecommendations" :key="index">
                        <td>{{ index + 1 }}</td>
                        <td>{{ song.track_name }}</td>
                        <td>{{ song.track_artist }}</td>
                        <td>
                          <button class="btn btn-sm me-2" :class="song.liked ? 'btn-danger' : 'btn-success'"
                            @click="giveFeedback(song.song_id, !song.liked)">
                            <i :class="song.liked ? 'bi bi-hand-thumbs-down' : 'bi bi-hand-thumbs-up'"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-light" @click="playSong(song.uri)">
                            <i class="bi bi-play"></i>
                          </button>
                        </td>
                        <td>
                          <select class="form-select" v-model="song.relevance_ts" @change="submitRank(song, 'ts')">
                            <option v-for="n in getRelevanceOptions(index + 1)" :key="n" :value="n">{{ n }}</option>
                          </select>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="card-footer">
                <div class="row">
                  <div class="col">
                    <div class="progress">
                      <div class="progress-bar bg-success" role="progressbar"
                        :style="{ width: (tsAccuracy * 100) + '%' }" :aria-valuenow="tsAccuracy * 100" aria-valuemin="0"
                        aria-valuemax="100">
                        Precision: {{ (tsAccuracy * 100).toFixed(1) }}%
                      </div>
                    </div>
                  </div>

                </div>
                <button class="btn btn-primary" @click="submitFeedback('ts')">
                  <i class="bi bi-save me-1"></i> Submit Feedback
                </button>
              </div>
            </div>
          </div>

          <!-- Epsilon-Greedy Recommendations -->
          <div class="col-md-6 mb-4">
            <div class="card bg-dark text-white border-warning">
              <div class="card-header bg-warning text-dark">
                <h4><i class="bi bi-dice-5 me-2"></i>Epsilon-Greedy</h4>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-dark table-hover">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Judul</th>
                        <th>Artis</th>
                        <th>Aksi</th>
                        <th>Relevansi</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(song, index) in epsilonGreedyRecommendations" :key="index">
                        <td>{{ index + 1 }}</td>
                        <td>{{ song.track_name }}</td>
                        <td>{{ song.track_artist }}</td>
                        <td>
                          <button class="btn btn-sm me-2" :class="song.liked ? 'btn-danger' : 'btn-success'"
                            @click="giveFeedback(song.song_id, !song.liked)">
                            <i :class="song.liked ? 'bi bi-hand-thumbs-down' : 'bi bi-hand-thumbs-up'"></i>
                          </button>
                          <button class="btn btn-sm btn-outline-light" @click="playSong(song.uri)">
                            <i class="bi bi-play"></i>
                          </button>
                        </td>
                        <td>
                          <select class="form-select" v-model="song.relevance_eg" @change="submitRank(song, 'eg')">
                            <option v-for="n in getRelevanceOptions(index + 1)" :key="n" :value="n">{{ n }}</option>
                          </select>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="card-footer">
                <div class="row">
                  <div class="col">
                    <div class="progress">
                      <div class="progress-bar bg-warning" role="progressbar"
                        :style="{ width: (epsilonGreedyAccuracy * 100) + '%' }"
                        :aria-valuenow="epsilonGreedyAccuracy * 100" aria-valuemin="0" aria-valuemax="100">
                        Precision: {{ (epsilonGreedyAccuracy * 100).toFixed(1) }}%
                      </div>
                    </div>
                  </div>
                </div>
                <button class="btn btn-primary" @click="submitFeedback('eg')">
                  <i class="bi bi-save me-1"></i> Submit Feedback
                </button>
              </div>
            </div>
          </div>


        </div>
      </div>

      <!-- Liked Songs View -->

      <div v-if="currentView === 'liked'">
        <div class="row">
          <div class="col-12">
            <div class="card bg-dark text-white border-danger">
              <div class="card-header bg-danger text-white">
                <h3><i class="bi bi-heart-fill me-2"></i>Lagu yang Disukai</h3>
              </div>
              <div class="card-body">
                <div v-if="likedSongsList.length === 0" class="text-center py-5">
                  <i class="bi bi-music-note-beamed display-4 text-muted"></i>
                  <h4 class="mt-3 text-muted">Belum ada lagu yang disukai</h4>
                </div>
                <div v-else>
                  <div class="table-responsive">
                    <table class="table table-dark table-hover">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>Judul Lagu</th>
                          <th>Artis</th>
                          <th>Genre</th>
                          <th>Aksi</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(song, index) in likedSongsList" :key="song.song_id">
                          <td>{{ index + 1 }}</td>
                          <td>{{ song.track_name }}</td>
                          <td>{{ song.track_artist }}</td>
                          <td>
                            <span class="badge bg-primary">{{ song.playlist_genre }}</span>
                          </td>
                          <td>
                            <button class="btn btn-sm btn-danger me-2" @click="unlikeLikedSong(song)">
                              <i class="bi bi-heartbreak"></i> Unlike
                            </button>
                            <button class="btn btn-sm btn-outline-light" @click="playSong(song.uri)">
                              <i class="bi bi-play"></i> Play
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Music Player -->
      <div v-if="currentSongUri" class="fixed-bottom bg-dark text-white p-3 border-top border-secondary">
        <div class="container">
          <div class="row align-items-center">
            <div class="col-md-8">
              <h5 class="mb-0">Now Playing: {{ currentSong }}</h5>
              <p class="mb-0 text-muted">{{ currentArtist }}</p>
            </div>
            <div class="col-md-4 text-end">
              <button class="btn btn-light btn-sm me-2" @click="togglePlay">
                <i :class="isPaused ? 'bi bi-play' : 'bi bi-pause'"></i>
              </button>
              <button class="btn btn-light btn-sm me-2" @click="stopPlayback">
                <i class="bi bi-stop"></i>
              </button>
              <button class="btn btn-outline-light btn-sm" @click="showSpotifyPlayer = !showSpotifyPlayer">
                <i class="bi bi-spotify"></i>
              </button>
            </div>
          </div>
          <div v-if="showSpotifyPlayer" class="row mt-3">
            <div class="col-12">
              <iframe :src="'https://open.spotify.com/embed/track/' + currentSongUri" width="100%" height="80"
                frameborder="0" allowtransparency="true" allow="encrypted-media">
              </iframe>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';

export default {
  data() {
    return {
      searchQuery: '',
      suggestions: [],
      selectedSongs: [],
      tsRecommendations: [],
      epsilonGreedyRecommendations: [],
      tsAccuracy: 0,
      epsilonGreedyAccuracy: 0,
      epsilonGreedyHitrateAt3: 0,
      isPlaying: false,
      isPaused: false,
      currentSong: '',
      currentArtist: '',
      currentSongUri: '',
      username: '',
      currentView: 'home',
      likedSongs: [],
      likedSongsList: [],
      allFeedback: [], // Store all feedback data including relevance
      allSongs: [],
      allSongsByGenre: {},
      showResults: false,
      showSpotifyPlayer: false
    };
  },
  methods: {
    playSong(uri) {
      const song = [...this.tsRecommendations, ...this.epsilonGreedyRecommendations, ...this.allSongs].find(s =>
        s.uri === uri || (s.track_uri && s.track_uri === uri)
      );

      if (song) {
        this.currentSongUri = uri.split(':')[2];
        this.currentSong = song.track_name || song.song;
        this.currentArtist = song.track_artist || song.artist;
        this.isPlaying = true;
        this.isPaused = false;
      }
    },

    togglePlay() {
      this.isPaused = !this.isPaused;
    },

    stopPlayback() {
      this.isPlaying = false;
      this.isPaused = false;
      this.currentSong = '';
      this.currentArtist = '';
      this.currentSongUri = '';
    },
    getRelevanceOptions(position) {
      if (position <= 2) return 5; // Positions 1-2 have options 1-5
      if (position <= 4) return 4; // Positions 3-4 have options 1-4
      if (position <= 6) return 3; // Positions 5-6 have options 1-3
      return 2; // All other positions have options 1-2
    },
    fetchSuggestions() {
      if (this.searchQuery.length < 2) {
        this.suggestions = [];
        return;
      }
      axios.get(`http://localhost:5000/search?query=${this.searchQuery}`)
        .then(response => {
          this.suggestions = response.data.suggestions.map(suggestion => ({
            ...suggestion,
            song_id: suggestion.song_id
          }));
        })
        .catch(error => {
          console.error("Error fetching suggestions:", error);
        });
    },

    selectSong(song) {
      if (song && song.song_id) {
        if (!this.selectedSongs.some(s => s.song_id === song.song_id)) {
          this.selectedSongs.push(song);
        }
        this.searchQuery = '';
        this.suggestions = [];
      } else {
        console.error("Selected song does not have song_id:", song);
      }
    },

    addSong() {
      if (this.searchQuery && this.suggestions.length) {
        this.selectSong(this.suggestions[0]);
      }
    },

    removeSong(index) {
      this.selectedSongs.splice(index, 1);
    },

    fetchRecommendations() {
      if (this.selectedSongs.length < 3) return;

      const songIds = this.selectedSongs.map(song => song.song_id);

      axios.post('http://localhost:5000/recommend', { song_ids: songIds })
        .then(response => {
          // Initialize recommendations with relevance values from feedback if they exist
          this.tsRecommendations = response.data.ts_recommendations.map(song => {
            const feedback = this.allFeedback.find(f => f.song_id === song.song_id);
            return {
              ...song,
              relevance_ts: feedback ? feedback.relevance_ts : 0,
              liked: this.likedSongs.includes(song.song_id)
            };
          });

          this.epsilonGreedyRecommendations = response.data.epsilon_greedy_recommendations.map(song => {
            const feedback = this.allFeedback.find(f => f.song_id === song.song_id);
            return {
              ...song,
              relevance_eg: feedback ? feedback.relevance_eg : 0,
              liked: this.likedSongs.includes(song.song_id)
            };
          });

          this.updateAccuracy();
          this.currentView = 'recommendations';
          this.showResults = true;
        })
        .catch(error => {
          console.error("Error fetching recommendations:", error);
        });
    },

    submitRank(song, algorithm) {
      const data = {
        song_id: song.song_id,
        liked: song.liked
      };

      // Add the correct relevance field based on algorithm
      if (algorithm === 'ts') {
        data.relevance_ts = song.relevance_ts;
      } else if (algorithm === 'eg') {
        data.relevance_eg = song.relevance_eg;
      }

      axios.post('http://localhost:5000/feedback', data, { withCredentials: true })
        .then(() => {
          toast.success(`Feedback untuk ${song.track_name} disimpan`);
          this.updateAccuracy();
        })
        .catch(error => {
          console.error("Error saving feedback:", error);
          toast.error("Gagal menyimpan feedback");
        });
    },

    // Remove submitFeedback method if not needed, or implement it:
    submitFeedback(algorithm) {
      const recommendations = algorithm === 'ts'
        ? this.tsRecommendations
        : this.epsilonGreedyRecommendations;

      const promises = recommendations.map(song => {
        const data = {
          song_id: song.song_id,
          liked: song.liked
        };

        if (algorithm === 'ts') {
          data.relevance_ts = song.relevance_ts;
        } else {
          data.relevance_eg = song.relevance_eg;
        }

        return axios.post('http://localhost:5000/feedback', data, { withCredentials: true });
      });

      Promise.all(promises)
        .then(() => {
          toast.success('Feedback berhasil disimpan!');
          this.updateAccuracy();
          this.saveAccuracy();
        })
        .catch(error => {
          console.error("Error submitting feedback:", error);
          toast.error('Gagal menyimpan feedback');
        });
    },

    giveFeedback(songId, liked) {
      axios.post('http://localhost:5000/feedback', {
        song_id: songId,
        liked: liked
      }, { withCredentials: true })
        .then(() => {
          this.updateLikedStatus(songId, liked);
          this.fetchLikedSongs();
          this.updateAccuracy();
        })
        .catch(error => {
          console.error("Error submitting feedback:", error);
        });
    },

    updateLikedStatus(songId, liked) {
      // Update status in recommendations
      [this.tsRecommendations, this.epsilonGreedyRecommendations].forEach(recommendations => {
        const song = recommendations.find(song => song.song_id === songId);
        if (song) {
          song.liked = liked;
        }
      });

      // Update likedSongs array
      if (liked) {
        if (!this.likedSongs.includes(songId)) {
          this.likedSongs.push(songId);
        }
      } else {
        this.likedSongs = this.likedSongs.filter(id => id !== songId);
      }
    },

    fetchLikedSongs() {
      axios.get('http://localhost:5000/feedback', { withCredentials: true })
        .then(response => {
          this.allFeedback = response.data; // Store all feedback data

          this.likedSongsList = response.data
            .filter(song => song.liked)
            .map(song => ({
              song_id: song.song_id,
              track_name: song.track_name,
              track_artist: song.track_artist,
              playlist_genre: song.playlist_genre,
              uri: song.uri
            }));

          this.likedSongs = response.data
            .filter(song => song.liked)
            .map(song => song.song_id);
        })
        .catch(error => {
          console.error("Error fetching liked songs:", error);
        });
    },

    unlikeLikedSong(song) {
      this.giveFeedback(song.song_id, false);
    },

    updateAccuracy() {
      axios.get('http://localhost:5000/feedback', { withCredentials: true })
        .then(response => {
          const likedSongs = response.data
            .filter(feedback => feedback.liked)
            .map(feedback => feedback.song_id);

          this.tsAccuracy = this.calculatePrecision(this.tsRecommendations, likedSongs);
          this.epsilonGreedyAccuracy = this.calculatePrecision(this.epsilonGreedyRecommendations, likedSongs);
          this.epsilonGreedyHitrateAt3 = this.calculateHitrate(this.epsilonGreedyRecommendations.slice(0, 3), likedSongs);
        })
        .catch(error => {
          console.error("Error updating accuracy:", error);
        });
    },

    calculatePrecision(recommendations, likedSongs) {
      if (!recommendations?.length) return 0;
      const hits = recommendations.filter(rec => likedSongs.includes(rec.song_id)).length;
      return hits / recommendations.length;
    },

    calculateHitrate(recommendations, likedSongs) {
      if (!recommendations?.length) return 0;
      const hits = recommendations.filter(rec => likedSongs.includes(rec.song_id)).length;
      return hits > 0 ? 1 : 0;
    },

    saveAccuracy() {
      axios.get('http://localhost:5000/feedback', { withCredentials: true })
        .then(response => {
          const feedback = response.data;
          const likedSongs = feedback.filter(f => f.liked).map(f => f.song_id);

          const calculateNDCGAtK = (recommendations, feedbackData, algoName, k = 10) => {
            const getRelevance = (song_id) => {
              const feedbackItem = feedbackData.find(f => f.song_id === song_id);
              if (!feedbackItem) return 0;

              if (algoName === "Thompson Sampling") {
                return feedbackItem.relevance_ts || 0;
              } else if (algoName === "Epsilon-Greedy") {
                return feedbackItem.relevance_eg || 0;
              }
              return 0;
            };

            const dcg = recommendations.slice(0, k).reduce((acc, song, idx) => {
              const relevance = getRelevance(song.song_id);
              return acc + relevance / Math.log2(idx + 2);
            }, 0);

            const idealRelevance = [5, 5, 4, 4, 3, 3, 2, 2, 1, 1];
            const idcg = idealRelevance.slice(0, k).reduce((acc, relevance, idx) => {
              return acc + relevance / Math.log2(idx + 2);
            }, 0);

            return dcg / idcg || 0;
          };

          const calculateAP = (recommendations, relevantSongs, k) => {
            const topK = recommendations.slice(0, k);
            let sumPrecision = 0;
            let relevantCount = 0;

            topK.forEach((song, idx) => {
              if (relevantSongs.includes(song.song_id)) {
                relevantCount++;
                sumPrecision += relevantCount / (idx + 1);
              }
            });

            return relevantCount > 0 ? sumPrecision / Math.min(relevantSongs.length, k) : 0;
          };

          const buildEvaluations = (algoName, recommendations) => {
            const evals = [];
            [1, 3, 5, 10].forEach(k => {
              const topK = recommendations.slice(0, k);
              const relevant = topK.filter(song => likedSongs.includes(song.song_id));

              const precision = relevant.length / k;
              const hitrate = relevant.length > 0 ? 1 : 0;
              const ap = calculateAP(recommendations, likedSongs, k);
              const ndcg = calculateNDCGAtK(topK, feedback, algoName, k);

              evals.push(
                { algorithm: algoName, metric_type: "Precision@K", k: k, score: precision },
                { algorithm: algoName, metric_type: "HitRate@K", k: k, score: hitrate },
                { algorithm: algoName, metric_type: "AP@K", k: k, score: ap },
                { algorithm: algoName, metric_type: "nDCG@K", k: k, score: ndcg }
              );
            });
            return evals;
          };

          const evaluations = [
            ...buildEvaluations("Thompson Sampling", this.tsRecommendations),
            ...buildEvaluations("Epsilon-Greedy", this.epsilonGreedyRecommendations)
          ];

          return axios.post('http://localhost:5000/save_accuracy', { evaluations }, { withCredentials: true });
        })
        .then(() => {
          console.log("Accuracy saved successfully");
        })
        .catch(error => {
          console.error("Error saving accuracy:", error);
        });
    },

    showHome() {
      this.currentView = 'home';
      this.showResults = false;
    },

    showRecommendations() {
      this.currentView = 'recommendations';
      this.showResults = false;
    },

    showLikedSongs() {
      this.currentView = 'liked';
      this.fetchLikedSongs();
    },

    logout() {
      axios.post('http://localhost:5000/logout', {}, { withCredentials: true })
        .then(() => {
          this.$router.push('/login');
        })
        .catch(error => {
          console.error("Error logging out:", error);
        });
    },

    fetchAllSongsByGenre() {
      axios.get('http://localhost:5000/all-songs-by-genre')
        .then(response => {
          this.allSongsByGenre = response.data;
        })
        .catch(error => {
          console.error("Error fetching songs by genre:", error);
        });
    }
  },
  created() {
    axios.get('http://localhost:5000/profile', { withCredentials: true })
      .then(response => {
        if (response.status === 200) {
          this.username = response.data.message.split(' ')[1];
          this.fetchLikedSongs();
          this.fetchAllSongsByGenre();
        } else {
          this.$router.push('/login');
        }
      })
      .catch(error => {
        console.error("Error fetching profile:", error);
        this.$router.push('/login');
      });
  }
};
</script>

<style scoped>
.bg-dark {
  background-color: #0e0f11 !important;
}

.bg-secondary {
  background-color: #1b1d20 !important;
}

.bg-primary {
  background-color: #5c6ac4 !important;
}

.bg-deepblue {
  background-color: #2e3548 !important;
}

.bg-info {
  background-color: #4fa3d1 !important;
}

.bg-warning {
  background-color: #f3c969 !important;
}

.bg-success {
  background-color: #45b29a !important;
}

.bg-danger {
  background-color: #f45b69 !important;
}

.navbar {
  padding: 0.8rem 1rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.navbar-brand {
  font-weight: 700;
  font-size: 1.5rem;
  color: #f0f0f0 !important;
}

.nav-link {
  font-weight: 500;
  transition: all 0.3s ease;
  color: #cfd8dc !important;
}

.nav-link:hover,
.nav-link.active {
  color: #ffffff !important;
  transform: translateY(-2px);
}

.card {
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
  background-color: #1b1d20 !important;
}

.card:hover {
  transform: translateY(-5px);
}

.btn-primary {
  background-color: #5c6ac4;
  border-color: #5c6ac4;
}

.btn-primary:hover {
  background-color: #4b59a6;
  border-color: #4b59a6;
}

.btn-outline-light:hover {
  color: #212121 !important;
  background-color: #ffffff !important;
  border-color: #ffffff !important;
}

.badge {
  font-weight: 500;
  font-size: 0.85rem;
}

.table-hover tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.accordion-button:not(.collapsed) {
  background-color: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}

.accordion-button:focus {
  box-shadow: none;
  border-color: transparent;
}

.progress {
  height: 22px;
  border-radius: 5px;
}

.progress-bar {
  font-weight: 500;
  font-size: 0.85rem;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #1b1d20;
}

::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #5c6ac4;
}
</style>
