<template>
  <div class="bg-dark text-white min-vh-100">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Music Recommendation</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="showAllSongs">Beranda</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="showRecommendations">Rekomendasi</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="showLikedSongs">Liked Songs</a>
            </li>
          </ul>
          <span class="navbar-text me-3">
            {{ username }}
          </span>
          <button class="btn btn-outline-light" @click="logout">Logout</button>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <div class="container mt-5">
      <h2 class="text-center mb-4">Music Recommendation System</h2>
      
      <div v-if="showingLikedSongs">
        <!-- Liked Songs -->
        <h3 class="text-center mb-4">Liked Songs</h3>
        <ul class="list-group">
          <li v-for="(song, index) in likedSongsList" :key="index" class="list-group-item bg-dark text-white d-flex justify-content-between align-items-center">
            <span>{{ song.track_name }} - {{ song.track_artist }}</span>
            <button class="btn btn-outline-danger btn-sm" @click="unlikeSong(song)">
              <i class="bi bi-hand-thumbs-down"></i> Unlike
            </button>
          </li>
        </ul>
      </div>
      
      <div v-else-if="showingRecommendations">
        <!-- Recommendations -->
        <div class="text-center mt-4">
          <button class="btn btn-primary" @click="fetchRecommendations" :disabled="selectedSongs.length < 5">
            Get Recommendations
          </button>
        </div>

        <div class="row mt-4" v-if="showingRecommendations">
          <!-- Rekomendasi Thompson Sampling -->
          <div class="col-md-6" v-if="tsRecommendations.length">
            <h3 class="text-center mb-4">Recommended Songs (Thompson Sampling)</h3>
            <ul class="list-group">
              <li v-for="(song, index) in tsRecommendations" :key="index" class="list-group-item d-flex justify-content-between align-items-center bg-dark text-white">
                <span>{{ song.song }} - {{ song.artist }}</span>
                <div>
                  <button :class="{'btn btn-success btn-sm me-2': !song.liked, 'btn btn-outline-light btn-sm me-2': song.liked}" @click="giveFeedback(song.song, !song.liked)">
                    <i :class="song.liked ? 'bi bi-hand-thumbs-down' : 'bi bi-hand-thumbs-up'"></i> {{ song.liked ? 'Unlike' : 'Like' }}
                  </button>
                </div>
              </li>
            </ul>
            <div class="mt-3 text-center">
              <h4>Accuracy: {{ tsAccuracy.toFixed(2) }}</h4>
              <h4>HitRate@3: {{ tsHitrateAt3.toFixed(2) }}</h4>
            </div>
          </div>
          
          <!-- Rekomendasi Epsilon-Greedy -->
          <div class="col-md-6" v-if="epsilonGreedyRecommendations.length">
            <h3 class="text-center mb-4">Recommended Songs (Epsilon-Greedy)</h3>
            <ul class="list-group">
              <li v-for="(song, index) in epsilonGreedyRecommendations" :key="index" class="list-group-item d-flex justify-content-between align-items-center bg-dark text-white">
                <span>{{ song.song }} - {{ song.artist }}</span>
                <div>
                  <button :class="{'btn btn-success btn-sm me-2': !song.liked, 'btn btn-outline-light btn-sm me-2': song.liked}" @click="giveFeedback(song.song, !song.liked)">
                    <i :class="song.liked ? 'bi bi-hand-thumbs-down' : 'bi bi-hand-thumbs-up'"></i> {{ song.liked ? 'Unlike' : 'Like' }}
                  </button>
                </div>
              </li>
            </ul>
            <div class="mt-3 text-center">
              <h4>Accuracy: {{ epsilonGreedyAccuracy.toFixed(2) }}</h4>
              <h4>HitRate@3: {{ epsilonGreedyHitrateAt3.toFixed(2) }}</h4>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else>
        <!-- Beranda -->
        <div class="row justify-content-center">
          <div class="col-md-8 position-relative">
            <div class="input-group mb-3">
              <input 
                type="text" 
                class="form-control" 
                v-model="searchQuery" 
                @input="fetchSuggestions" 
                placeholder="Search for a song or artist...">
              <button class="btn btn-outline-light" type="button" @click="addSong">
                Add Song
              </button>
            </div>
            <ul v-if="suggestions.length" class="list-group suggestions-dropdown">
              <li 
                v-for="(suggestion, index) in suggestions" 
                :key="index" 
                class="list-group-item list-group-item-action bg-dark text-white"
                @click="selectSong(suggestion)">
                {{ suggestion.track_name }} - {{ suggestion.track_artist }}
              </li>
            </ul>
          </div>
        </div>
        
        <div v-if="selectedSongs.length" class="mt-4">
          <h3 class="text-center mb-4">Selected Songs</h3>
          <ul class="list-group">
            <li v-for="(song, index) in selectedSongs" :key="index" class="list-group-item bg-dark text-white d-flex justify-content-between align-items-center">
              <span>{{ song.track_name }} - {{ song.track_artist }}</span>
              <button class="btn btn-outline-danger btn-sm" @click="removeSong(index)">
                <i class="bi bi-dash"></i>
              </button>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- Pemutar Musik -->
      <div v-if="isPlaying" class="fixed-bottom bg-dark text-white p-3">
        <div class="container">
          <div class="row align-items-center">
            <div class="col">
              <p class="mb-0">Now Playing: {{ currentSong }}</p>
            </div>
            <div class="col-auto">
              <button class="btn btn-light btn-sm" @click="togglePlay">
                <i :class="isPaused ? 'bi bi-play' : 'bi bi-pause'"></i>
              </button>
              <button class="btn btn-light btn-sm" @click="stopPlayback">
                <i class="bi bi-stop"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Spotify Embed Player -->
      <iframe 
        v-if="currentSongUri" 
        :src="'https://open.spotify.com/embed/track/' + currentSongUri" 
        width="300" 
        height="80" 
        frameborder="0" 
        allowtransparency="true" 
        allow="encrypted-media">
      </iframe>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      searchQuery: '',
      suggestions: [],
      selectedSongs: [],
      cosineRecommendations: [],
      tsRecommendations: [],
      epsilonGreedyRecommendations: [],
      tsAccuracy: 0,
      epsilonGreedyAccuracy: 0,
      tsHitrateAt3: 0,
      epsilonGreedyHitrateAt3: 0,
      isPlaying: false,
      isPaused: false,
      currentSong: '',
      currentSongUri: '',
      username: '',
      showingRecommendations: false,
      showingLikedSongs: false,
      likedSongs: [],
      likedSongsList: [],
    };
  },
  methods: {
    playSong(uri) {
      this.currentSongUri = uri.split(':')[2]; // Extract track ID from URI
      this.isPlaying = true;
      this.isPaused = false;
    },
    togglePlay() {
      this.isPaused = !this.isPaused;
    },
    stopPlayback() {
      this.isPlaying = false;
      this.isPaused = false;
      this.currentSong = '';
      this.currentSongUri = '';
    },
    fetchSuggestions() {
      if (this.searchQuery.length < 2) {
        this.suggestions = [];
        return;
      }
      axios.get(`http://localhost:5000/search?query=${this.searchQuery}`)
        .then(response => {
          this.suggestions = response.data.suggestions;
        })
        .catch(error => {
          console.error("Error fetching suggestions:", error);
        });
    },
    selectSong(song) {
      this.searchQuery = `${song.track_name} - ${song.track_artist}`;
      this.selectedSongs.push(song);
      this.suggestions = [];
    },
    addSong() {
      if (this.searchQuery && this.suggestions.length) {
        const selected = this.suggestions[0];
        this.selectSong(selected);
        this.searchQuery = '';
      }
    },
    removeSong(index) {
      this.selectedSongs.splice(index, 1);
    },
    fetchRecommendations() {
      if (this.selectedSongs.length < 5) return;
      const songNames = this.selectedSongs.map(song => song.track_name);
      axios.post('http://localhost:5000/recommend', { song_names: songNames })
        .then(response => {
          this.cosineRecommendations = response.data.cosine_recommendations.map(song => ({ ...song, liked: this.likedSongs.includes(song.track_name) }));
          this.tsRecommendations = response.data.ts_recommendations.map(song => ({ ...song, liked: this.likedSongs.includes(song.song) }));
          this.epsilonGreedyRecommendations = response.data.epsilon_greedy_recommendations.map(song => ({ ...song, liked: this.likedSongs.includes(song.song) }));
          this.updateAccuracy();
          this.showingRecommendations = true;
          this.showingLikedSongs = false;
        })
        .catch(error => {
          console.error("Error fetching recommendations:", error);
        });
    },
    giveFeedback(song, liked) {
      axios.post('http://localhost:5000/feedback', { song_name: song, liked: liked })
        .then(response => {
          this.updateLikedStatus(song, liked);
          this.updateAccuracy();
        })
        .catch(error => {
          console.error("Error submitting feedback:", error);
        });
    },
    updateLikedStatus(songName, liked) {
      [this.cosineRecommendations, this.tsRecommendations, this.epsilonGreedyRecommendations].forEach(recommendations => {
        const song = recommendations.find(song => song.track_name === songName || song.song === songName);
        if (song) {
          song.liked = liked;
        }
      });
      if (liked) {
        this.likedSongs.push(songName);
      } else {
        this.likedSongs = this.likedSongs.filter(name => name !== songName);
      }
      this.fetchLikedSongs();
    },
    fetchLikedSongs() {
      axios.get('http://localhost:5000/feedback')
        .then(response => {
          const feedback = response.data;
          this.likedSongsList = feedback.filter(f => f.liked).map(f => {
            return {
              track_name: f.song_name,
              track_artist: f.artist_name // Assuming artist_name is part of feedback data
            };
          });
        })
        .catch(error => {
          console.error("Error fetching liked songs:", error);
        });
    },
    unlikeSong(song) {
      this.giveFeedback(song.track_name, false);
    },
    updateAccuracy() {
      axios.get('http://localhost:5000/feedback')
        .then(response => {
          const feedback = response.data;
          this.tsAccuracy = this.calculateAccuracy(this.tsRecommendations, feedback);
          this.epsilonGreedyAccuracy = this.calculateAccuracy(this.epsilonGreedyRecommendations, feedback);
          this.tsHitrateAt3 = this.calculateHitrateAt3(this.tsRecommendations, feedback);
          this.epsilonGreedyHitrateAt3 = this.calculateHitrateAt3(this.epsilonGreedyRecommendations, feedback);
          this.saveAccuracy();
        })
        .catch(error => {
          console.error("Error fetching feedback:", error);
        });
    },
    calculateAccuracy(recommendations, feedback) {
      const likedSongs = feedback.filter(f => f.liked).map(f => f.song_name);
      const recommendedLiked = recommendations.filter(rec => likedSongs.includes(rec.track_name || rec.song));
      return recommendedLiked.length / recommendations.length;
    },
    calculateHitrateAt3(recommendations, feedback) {
      const likedSongs = feedback.filter(f => f.liked).map(f => f.song_name);
      const top3Recommendations = recommendations.slice(0, 3);
      const recommendedLiked = top3Recommendations.filter(rec => likedSongs.includes(rec.track_name || rec.song));
      return recommendedLiked.length / 3;
    },
    saveAccuracy() {
      axios.post('http://localhost:5000/save_accuracy', {
        ts_accuracy: this.tsAccuracy,
        epsilon_greedy_accuracy: this.epsilonGreedyAccuracy,
        ts_hitrate_at_3: this.tsHitrateAt3,
        epsilon_greedy_hitrate_at_3: this.epsilonGreedyHitrateAt3
      })
        .then(response => {
          console.log("Accuracy saved successfully");
        })
        .catch(error => {
          console.error("Error saving accuracy:", error);
        });
    },
    showAllSongs() {
      this.showingRecommendations = false;
      this.showingLikedSongs = false;
    },
    showRecommendations() {
      this.showingRecommendations = true;
      this.showingLikedSongs = false;
    },
    showLikedSongs() {
      this.fetchLikedSongs();
      this.showingRecommendations = false;
      this.showingLikedSongs = true;
    },
    logout() {
      axios.post('http://localhost:5000/logout')
        .then(response => {
          if (response.status === 200) {
            this.$router.push('/login');
          }
        })
        .catch(error => {
          console.error("Error logging out:", error);
        });
    }
  },
  created() {
    axios.get('http://localhost:5000/profile')
      .then(response => {
        if (response.status === 200) {
          this.username = response.data.message.split(' ')[1];
        } else {
          this.$router.push('/login');
        }
      })
      .catch(error => {
        console.error("Error fetching profile:", error);
        this.$router.push('/login');
      });

    this.fetchLikedSongs();
  }
};
</script>

<style scoped>
html, body {
  height: 100%;
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  background-color: #121212;
  color: #ffffff;
}

.container {
  margin-top: 50px;
}

.suggestions-dropdown {
  position: absolute;
  width: 100%;
  z-index: 1000;
}

.bg-dark {
  background-color: #343a40 !important;
}

.text-white {
  color: #fff !important;
}

.btn-light {
  background-color: #f8f9fa;
  border-color: #f8f9fa;
  color: #212529;
}

.btn-outline-light {
  border-color: #f8f9fa;
  color: #f8f9fa;
}

.btn-outline-light:hover {
  background-color: #f8f9fa;
  color: #212529;
}

.btn-outline-danger {
  border-color: #dc3545;
  color: #dc3545;
}

.btn-outline-danger:hover {
  background-color: #dc3545;
  color: #fff;
}
</style>