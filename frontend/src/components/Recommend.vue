<template>
  <div class="main-container">
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">
          <i class="bi bi-soundwave me-2"></i>
          MusicRecommender
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="showHome" :class="{ 'active': currentView === 'home' }">
                <i class=" me-1"></i> Beranda
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="showRecommendations"
                :class="{ 'active': currentView === 'recommendations' }">
                <i class="me-1"></i> Rekomendasi
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="showLikedSongs"
                :class="{ 'active': currentView === 'liked' }">
                <i class="me-1"></i> Lagu Favorit
              </a>
            </li>
          </ul>
          <div class="d-flex align-items-center">
            <span class="navbar-text me-3">
              <i class="bi bi-person-circle me-1"></i> {{ username }}
            </span>
            <button class="btn btn-logout" @click="logout">
              <i class="bi bi-box-arrow-right me-1"></i> Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="container mt-4 content-fade-in">

      <div v-if="currentView === 'home'">
        <section class="mb-5">
          <div class="search-card">
            <div class="card-body p-lg-5">
              <h2 class="card-title mb-2 fw-bold">Jelajahi Dunia Musik</h2>
              <p class="text-muted mb-4">Temukan dan pilih lagu favorit untuk memulai petualangan musik Anda.</p>
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-search"></i></span>
                <input type="text" class="form-control search-card" v-model="searchQuery" @input="fetchSuggestions"
                  placeholder="Cari judul lagu atau nama artis..." @keyup.enter="addSong">
                <button class="btn btn-primary-custom" type="button" @click="addSong">Pilih</button>
              </div>
              <div v-if="suggestions.length" class="suggestions-dropdown">
                <ul class="list-group">
                  <li v-for="(suggestion, index) in suggestions" :key="index" class="list-group-item"
                    @click="selectSong(suggestion)">
                    {{ suggestion.track_name }} - <small>{{ suggestion.track_artist }}</small>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section v-if="selectedSongs.length" class="mb-5 content-fade-in">
          <h4 class="section-title">Lagu Pilihan Anda ({{ selectedSongs.length }})</h4>
          <div class="selected-songs-container">
            <div v-for="(song, index) in selectedSongs" :key="index" class="song-pill">
              <i class="bi bi-music-note-beamed me-2"></i>
              <span>{{ song.track_name }}</span>
              <button class="btn-remove-pill" @click="removeSong(index)">&times;</button>
            </div>
          </div>
          <button class="btn btn-primary-custom w-100 mt-3 py-3" @click="fetchRecommendations"
            :disabled="selectedSongs.length < 3">
            <i class="bi bi-magic me-2"></i> Dapatkan Rekomendasi Dari Pilihan Ini
          </button>
        </section>

        <section class="mb-4">
          <h4 class="section-title">Daftar Lagu Berdasarkan Genre</h4>
          <div class="accordion" id="genreAccordion">
            <div class="accordion-item" v-for="(songs, genre, index) in allSongsByGenre" :key="index">
              <h2 class="accordion-header" :id="'heading' + index">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                  :data-bs-target="'#collapse' + index">
                  {{ genre }} <span class="badge-genre ms-2">{{ songs.length }} lagu</span>
                </button>
              </h2>
              <div :id="'collapse' + index" class="accordion-collapse collapse" :aria-labelledby="'heading' + index"
                data-bs-parent="#genreAccordion">
                <div class="accordion-body">
                  <div class="row g-3">
                    <div class="col-12 col-md-6" v-for="song in songs" :key="song.song_id">
                      <div class="genre-song-card">
                        <div>
                          <div class="fw-bold text-white">{{ song.track_name }}</div>
                          <div class="text-muted small">{{ song.track_artist }}</div>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                          <button class="btn-icon" @click="playSong(song.uri)" title="Play"><i
                              class="bi bi-play-fill"></i></button>
                          <button class="btn-icon"
                            @click.stop="addLikedSongs(song.song_id, !likedSongs.includes(song.song_id))"
                            :title="likedSongs.includes(song.song_id) ? 'Unlike' : 'Like'">
                            <i
                              :class="likedSongs.includes(song.song_id) ? 'bi bi-heart-fill text-danger' : 'bi bi-heart'"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div v-if="currentView === 'recommendations'">
        <section class="mb-5">
          <h2 class="display-5 fw-bold mb-3">Direkomendasikan untuk Anda</h2>
          <p class="text-muted fs-5">Lagu-lagu ini kami pilih berdasarkan selera musik Anda.</p>

          <div v-if="isLoadingRecommended" class="text-center py-5">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status"></div>
          </div>

          <div v-else-if="!likedSongsRecommendations.length" class="empty-state-card">
            <i class="bi bi-music-note-list display-1 text-primary"></i>
            <h4 class="mt-3">Belum Ada Rekomendasi</h4>
            <p class="text-muted">Sukai lebih banyak lagu untuk mendapatkan rekomendasi yang lebih akurat.</p>
            <button class="btn btn-primary-custom mt-3" @click="showHome"><i
                class="bi bi-house-door-fill me-2"></i>Jelajahi Lagu</button>
          </div>

          <div v-else class="recommendation-row">
            <div class="song-card" v-for="song in likedSongsRecommendations" :key="song.song_id">
              <div class="song-card-image">
                <i class="bi bi-music-note-beamed"></i>
                <div class="play-overlay" @click="playSong(song.uri)"> <i class="bi bi-play-fill"></i> </div>
              </div>
              <div class="song-card-body">
                <h5 class="song-title">{{ song.track_name }}</h5>
                <p class="song-artist">{{ song.track_artist }}</p>
                <button class="btn-like" @click.stop="giveFeedback(song.song_id, !song.liked)">
                  <i :class="song.liked ? 'bi bi-heart-fill' : 'bi bi-heart'"></i>
                </button>
              </div>
            </div>
          </div>
        </section>

        <hr class="my-5 hr-styled">

        <section>
          <h3 class="section-title">Bandingkan Algoritma Rekomendasi</h3>
          <p class="text-muted mb-4">Pilih minimal 5 lagu untuk membandingkan hasil dari Thompson Sampling &
            Epsilon-Greedy.</p>

          <div class="search-card mb-4">
            <div class="card-body">
              <div class="input-group">
                <span class="input-group-text"><i class="bi bi-search"></i></span>
                <input type="text" class="form-control" v-model="searchQuery" @input="fetchSuggestions"
                  placeholder="Cari lagu untuk ditambahkan..." @keyup.enter="addSong">
              </div>
              <div v-if="suggestions.length" class="suggestions-dropdown">
                <ul class="list-group">
                  <li v-for="(suggestion, index) in suggestions" :key="index" class="list-group-item"
                    @click="selectSong(suggestion)">
                    {{ suggestion.track_name }} - <small>{{ suggestion.track_artist }}</small>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div v-if="selectedSongs.length" class="mb-4">
            <div class="selected-songs-container">
              <div v-for="(song, index) in selectedSongs" :key="index" class="song-pill">
                <i class="bi bi-music-note-beamed me-2"></i>
                <span>{{ song.track_name }}</span>
                <button class="btn-remove-pill" @click="removeSong(index)">&times;</button>
              </div>
            </div>
            <button class="btn btn-primary-custom w-100 mt-3 py-3" @click="fetchRecommendations"
              :disabled="selectedSongs.length < 3">
              <i class="bi bi-magic me-2"></i> Bandingkan Hasil Rekomendasi
            </button>
          </div>
        </section>

        <div v-if="showResults" class="row mt-5 content-fade-in">
          <div class="col-lg-6 mb-4">
            <div class="card result-card is-success h-100">
              <div class="card-header">
                <h4><i class="bi bi-graph-up-arrow me-2"></i>Thompson Sampling</h4>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-custom">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Lagu</th>
                        <th class="text-center">Aksi</th>
                        <th>Relevansi</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(song, index) in tsRecommendations" :key="index">
                        <td>{{ index + 1 }}</td>
                        <td>
                          <div class="fw-bold">{{ song.track_name }}</div>
                          <small class="text-muted">{{ song.track_artist }}</small>
                        </td>
                        <td class="action-buttons text-center">
                          <button class="btn-icon" @click="playSong(song.uri)"><i
                              class="bi bi-play-circle-fill"></i></button>
                          <button class="btn-icon" @click="giveFeedback(song.song_id, !song.liked)">
                            <i :class="song.liked ? 'bi bi-heart-fill text-danger' : 'bi bi-heart'"></i>
                          </button>
                        </td>
                        <td>
                          <select class="form-select form-select-sm" v-model="song.relevance_ts"
                            @change="submitRank(song, 'ts')">
                            <option v-for="n in getRelevanceOptions(index + 1)" :key="n" :value="n">{{ n }}</option>
                          </select>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-6 mb-4">
            <div class="card result-card is-warning h-100">
              <div class="card-header">
                <h4><i class="bi bi-dice-5 me-2"></i>Epsilon-Greedy</h4>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-custom">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Lagu</th>
                        <th class="text-center">Aksi</th>
                        <th>Relevansi</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(song, index) in epsilonGreedyRecommendations" :key="index">
                        <td>{{ index + 1 }}</td>
                        <td>
                          <div class="fw-bold">{{ song.track_name }}</div>
                          <small class="text-muted">{{ song.track_artist }}</small>
                        </td>
                        <td class="action-buttons text-center">
                          <button class="btn-icon" @click="playSong(song.uri)"><i
                              class="bi bi-play-circle-fill"></i></button>
                          <button class="btn-icon" @click="giveFeedback(song.song_id, !song.liked)">
                            <i :class="song.liked ? 'bi bi-heart-fill text-danger' : 'bi bi-heart'"></i>
                          </button>
                        </td>
                        <td>
                          <select class="form-select form-select-sm" v-model="song.relevance_eg"
                            @change="submitRank(song, 'eg')">
                            <option v-for="n in getRelevanceOptions(index + 1)" :key="n" :value="n">{{ n }}</option>
                          </select>
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

      <div v-if="currentView === 'liked'">
        <section class="mb-5">
          <h2 class="display-5 fw-bold mb-3"><i class=" me-2 text-danger"></i>Lagu Favorit Anda</h2>
          <div v-if="!likedSongsList.length" class="empty-state-card">
            <i class="bi bi-emoji-frown display-1 text-primary"></i>
            <h4 class="mt-3">Koleksi Masih Kosong</h4>
            <p class="text-muted">Tekan ikon hati pada lagu yang Anda suka untuk menambahkannya di sini.</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-custom">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Judul Lagu</th>
                  <th>Artis</th>
                  <th>Genre</th>
                  <th class="text-end">Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(song, index) in likedSongsList" :key="song.song_id">
                  <td>{{ index + 1 }}</td>
                  <td>{{ song.track_name }}</td>
                  <td>{{ song.track_artist }}</td>
                  <td><span class="badge-genre">{{ song.playlist_genre }}</span></td>
                  <td class="text-end">
                    <button class="btn-icon" @click="playSong(song.uri)" title="Play"><i
                        class="bi bi-play-circle-fill"></i></button>
                    <button class="btn-icon text-danger" @click="unlikeLikedSong(song)" title="Unlike"><i
                        class="bi bi-trash-fill"></i></button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>

    </main>
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
      likedSongsRecommendations: [],
      isLoadingRecommended: false,
      showResults: false,
      showSpotifyPlayer: false
    };
  },
  methods: {
    playSong(uri) {
      // Jika URI sudah dalam format spotify:track:xxx, ekstrak ID-nya
      const trackId = uri.includes('spotify:track:')
        ? uri.split(':')[2]
        : uri;

      // Cari lagu di semua sumber data
      const song = [
        ...this.tsRecommendations,
        ...this.epsilonGreedyRecommendations,
        ...this.allSongs,
        ...this.likedSongsList,
        ...this.selectedSongs
      ].find(s =>
        s.uri === uri ||
        s.track_uri === uri ||
        (s.uri && s.uri.includes(trackId)) ||
        (s.track_uri && s.track_uri.includes(trackId))
      );

      if (song) {
        this.currentSongUri = trackId;
        this.currentSong = song.track_name || song.trackName || song.name;
        this.currentArtist = song.track_artist || song.artistName || song.artist;
        this.isPlaying = true;
        this.isPaused = false;
        this.showSpotifyPlayer = true; // Otomatis tampilkan player

        // Scroll ke player
        setTimeout(() => {
          const playerElement = document.querySelector('.fixed-bottom');
          if (playerElement) {
            playerElement.scrollIntoView({ behavior: 'smooth' });
          }
        }, 100);
      } else {
        console.error("Song not found for URI:", uri);
        toast.error("Lagu tidak ditemukan");
      }
    },

    togglePlay() {
      if (!this.currentSongUri) return;

      this.isPaused = !this.isPaused;
      if (this.isPaused) {
        toast.info("Paused: " + this.currentSong);
      } else {
        toast.info("Playing: " + this.currentSong);
      }
    },

    stopPlayback() {
      this.isPlaying = false;
      this.isPaused = false;
      this.currentSong = '';
      this.currentArtist = '';
      this.currentSongUri = '';
      this.showSpotifyPlayer = false;
      toast.info("Playback stopped");
    },
    addLikedSongs(songId, liked) {
      axios.post('http://localhost:5000/feedback', {
        song_id: songId,
        liked: liked
      }, { withCredentials: true })
        .then(() => {
          this.updateLikedStatus(songId, liked);
          toast.success(liked ? 'Lagu ditambahkan ke favorit' : 'Lagu dihapus dari favorit');
        })
        .catch(error => {
          console.error("Error updating liked status:", error);
          toast.error('Gagal memperbarui status lagu');
        });
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

    showRecommendations() {
      this.currentView = 'recommendations';
      this.showResults = false; // Sembunyikan hasil rekomendasi manual

      // Kosongkan data rekomendasi manual sebelumnya
      this.selectedSongs = [];
      this.tsRecommendations = [];
      this.epsilonGreedyRecommendations = [];

      // PANGGILAN OTOMATIS ke backend
      this.fetchRecommendationsFromLiked();
    },

    fetchRecommendationsFromLiked() {
      this.isLoadingRecommended = true;
      console.log('Memulai permintaan rekomendasi...');

      axios.get('http://localhost:5000/recommend_from_liked', {
        withCredentials: true,
        params: {
          _: new Date().getTime() // Cache buster
        }
      })
        .then(response => {
          console.log('Respons API:', response);
          if (response.data?.epsilon_greedy_recommendations) {
            this.likedSongsRecommendations = response.data.epsilon_greedy_recommendations.map(song => ({
              ...song,
              liked: this.likedSongs.includes(song.song_id)
            }));
          } else {
            console.warn('Format respons tidak valid:', response.data);
          }
        })
        .catch(error => {
          console.error('Detail error:', {
            message: error.message,
            response: error.response?.data,
            status: error.response?.status
          });

          if (error.response?.data?.error) {
            toast.error(`Server error: ${error.response.data.error}`);
          } else {
            toast.error('Gagal memuat rekomendasi. Coba lagi nanti.');
          }
        })
        .finally(() => {
          this.isLoadingRecommended = false;
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

    giveFeedback(songId, liked) { // `liked` di sini sudah boolean (true/false)
      axios.post('http://localhost:5000/feedback', {
        song_id: songId,
        liked: liked // Kirim boolean langsung
      }, { withCredentials: true })
        .then(() => {
          this.updateLikedStatus(songId, liked);
          this.fetchLikedSongs(); // Muat ulang daftar lagu yang disukai
          this.updateAccuracy();
        })
        .catch(error => {
          console.error("Error submitting feedback:", error);
          toast.error("Gagal menyimpan feedback.");
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
      const autoRecSong = this.likedSongsRecommendations.find(song => song.song_id === songId);
      if (autoRecSong) {
        autoRecSong.liked = liked;
      }
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

<style>
/* Import Font Poppins */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Variabel Warna Global */
:root {
  --bg-color: #1E1E2F;
  --card-bg: #2A2A3D;
  --border-color: #4A4A5D;
  --text-color: #FFFFFF;
  --text-muted: #ccc9c9;
  --primary-color: #58A6FF;
  --primary-hover: #79C0FF;
  --accent-danger: #F85149;
  --accent-success: #3FB950;
}

/* Terapkan background ke seluruh halaman */
body {
  background-color: var(--bg-color);
  color: var(--text-color);
  font-family: 'Poppins', sans-serif;
}
</style>

<style scoped>
/*
  Style .main-container tidak lagi membutuhkan background-color
  karena sudah di-handle oleh 'body' di style global.
*/
.main-container {
  min-height: 100vh;
}

/* Animasi Fade In untuk Konten */
.content-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Garis Pemisah dengan Gaya */
.hr-styled {
  border: none;
  height: 1px;
  background-image: linear-gradient(to right, rgba(68, 75, 87, 0), rgba(68, 75, 87, 0.75), rgba(68, 75, 87, 0));
}

/* Judul Section yang Elegan */
.section-title {
  color: var(--text-color);
  font-weight: 600;
  margin-bottom: 1.5rem;
  border-left: 4px solid var(--primary-color);
  padding-left: 1rem;
}

/* Navbar dengan Efek Kaca (Glassmorphism) */
.navbar {
  background-color: rgba(30, 30, 47, 0.8) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
}

.navbar-brand {
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--text-color) !important;
}

.text-muted {
  color: var(--text-muted) !important;
}

.nav-link {
  color: var(--text-muted) !important;
  font-weight: 500;
  transition: color 0.3s ease;
  border-radius: 6px;
  padding: 0.5rem 1rem !important;
}

.nav-link.active,
.nav-link:hover {
  color: var(--primary-color) !important;
  background-color: rgba(88, 166, 255, 0.1);
}

.navbar-text {
  color: var(--text-muted);
}

.btn-logout {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  transition: all 0.3s ease;
}

.btn-logout:hover {
  background-color: var(--accent-danger);
  border-color: var(--accent-danger);
  color: var(--text-color);
}

/* Tombol Utama yang Menonjol */
.btn-primary-custom {
  background-color: var(--primary-color);
  border: none;
  color: #0D1117;
  font-weight: 600;
  transition: all 0.3s ease;
  padding: 0.8rem 1.5rem;
  border-radius: 6px;
}

.btn-primary-custom:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(88, 166, 255, 0.2);
}

.btn-primary-custom:disabled {
  background-color: var(--border-color);
  color: var(--text-muted);
  cursor: not-allowed;
}

/* Kartu Pencarian */
.search-card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.search-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.form-control,
.input-group-text {
  background-color: var(--bg-color) !important;
  border: 1px solid var(--border-color) !important;
  color: var(--text-color) !important;
  padding: 0.8rem 1rem;
  height: 50px;
}

.form-control:focus {
  background-color: var(--bg-color) !important;
  box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.25) !important;
  border-color: var(--primary-color) !important;
}

.input-group-text {
  border-right: none !important;
}

.form-control {
  border-left: none !important;
}

.input-group .btn-primary-custom {
  border-radius: 0 6px 6px 0;
}

/* Dropdown Saran Lagu */
.suggestions-dropdown {
  position: absolute;
  z-index: 1000;
  width: calc(100% - 4rem);
  margin-top: 0.5rem;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background-color: var(--card-bg);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.suggestions-dropdown .list-group-item {
  background-color: transparent;
  color: var(--text-color);
  border: none;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.suggestions-dropdown .list-group-item:last-child {
  border-bottom: none;
}

.suggestions-dropdown .list-group-item:hover {
  background-color: var(--primary-color);
  color: var(--bg-color);
}

/* Pill Lagu Pilihan */
.selected-songs-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.song-pill {
  display: inline-flex;
  align-items: center;
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.song-pill:hover {
  transform: translateY(-2px);
  border-color: var(--primary-color);
}

.btn-remove-pill {
  background: none;
  border: none;
  color: var(--text-muted);
  margin-left: 0.5rem;
  padding: 0;
  line-height: 1;
}

.btn-remove-pill:hover {
  color: var(--accent-danger);
}


/* Kartu Lagu untuk Rekomendasi */
.recommendation-row {
  display: flex;
  overflow-x: auto;
  padding-bottom: 1rem;
  gap: 1.5rem;
}

.song-card {
  flex: 0 0 200px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.song-card:hover {
  transform: translateY(-5px);
  border-color: var(--primary-color);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.song-card-image {
  height: 180px;
  background: linear-gradient(45deg, var(--bg-color), var(--card-bg));
  border-radius: 12px 12px 0 0;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 4rem;
  color: var(--text-muted);
  position: relative;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s ease;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 3rem;
  border-radius: 12px 12px 0 0;
}

.song-card:hover .play-overlay {
  opacity: 1;
}

.song-card-body {
  padding: 1rem;
  position: relative;
}

.song-title {
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.25rem;
  color: var(--text-color);
}

.song-artist {
  font-size: 0.85rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-like {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.2rem;
  transition: all 0.3s;
}

.btn-like .bi-heart-fill {
  color: var(--accent-danger);
}

.btn-like:hover {
  color: var(--text-color);
  transform: scale(1.1);
}

/* Tabel Kustom */
.table-custom {
  --bs-table-bg: transparent;
  --bs-table-border-color: var(--border-color);
  --bs-table-color: var(--text-color);
  --bs-table-hover-bg: rgba(88, 166, 255, 0.05);
  border-collapse: separate;
  border-spacing: 0 0.5rem;
}

.table-custom thead th {
  border: none;
  font-weight: 600;
  color: var(--text-muted);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding-bottom: 1rem;
}

.table-custom tbody tr {
  background: var(--card-bg);
  transition: all 0.2s ease-in-out;
}

.table-custom tbody tr:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  z-index: 1;
  position: relative;
}

.table-custom td,
.table-custom th {
  border: none;
  vertical-align: middle;
}

.table-custom td:first-child {
  border-radius: 8px 0 0 8px;
  padding-left: 1.5rem;
}

.table-custom td:last-child {
  border-radius: 0 8px 8px 0;
  padding-right: 1.5rem;
}


.badge-genre {
  background-color: rgba(88, 166, 255, 0.15);
  color: var(--primary-color);
  padding: 0.4em 0.8em;
  border-radius: 20px;
  font-weight: 500;
  font-size: 0.8rem;
}

/* Tombol Ikon */
.btn-icon {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.3rem;
  transition: color 0.3s, transform 0.3s;
}

.btn-icon:hover {
  color: var(--primary-color);
  transform: scale(1.1);
}

.text-danger {
  color: var(--accent-danger) !important;
}

/* Accordion Kustom */
.accordion {
  --bs-accordion-bg: transparent;
  --bs-accordion-border-color: var(--border-color);
  --bs-accordion-btn-color: var(--text-color);
  --bs-accordion-active-color: var(--primary-color);
  --bs-accordion-active-bg: rgba(88, 166, 255, 0.1);
  --bs-accordion-btn-focus-box-shadow: none;
}

.accordion-item {
  background-color: transparent !important;
  border: 1px solid var(--border-color) !important;
  border-radius: 8px !important;
  margin-bottom: 1rem;
  overflow: hidden;
}

.accordion-button {
  font-weight: 500;
}

.accordion-body {
  background-color: var(--bg-color);
}

.genre-song-card {
  background-color: var(--card-bg);
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.genre-song-card:hover {
  border-left-color: var(--primary-color);
  background-color: #30363d;
}

/* Tampilan State Kosong */
.empty-state-card {
  background-color: var(--card-bg);
  padding: 3rem;
  border-radius: 12px;
  text-align: center;
  border: 1px dashed var(--border-color);
}

/* Kartu Hasil Rekomendasi */
.result-card {
  background-color: var(--card-bg) !important;
  border: 1px solid var(--border-color);
  border-radius: 12px !important;
  overflow: hidden;
}

.result-card.is-success {
  border-color: var(--accent-success);
}

.result-card.is-warning {
  border-color: var(--accent-warning);
}

.result-card .card-header {
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
}

.result-card.is-success .card-header {
  background-color: rgba(63, 185, 80, 0.1);
  color: var(--accent-success);
}

.result-card.is-warning .card-header {
  background-color: rgba(210, 153, 34, 0.1);
  color: var(--accent-warning);
}

.result-card .card-body {
  padding: 0.5rem;
}

.result-card .table-responsive {
  max-height: 800px;
}

/* Select Form */
.form-select {
  background-color: var(--bg-color) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%238B949E' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m2 5 6 6 6-6'/%3e%3c/svg%3e");
}

.form-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.25rem rgba(88, 166, 255, 0.25);
}

/* Scrollbar Kustom */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-color);
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary-color);
}
</style>