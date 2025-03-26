// import axios from 'axios';

// const api = axios.create({
//     baseURL: 'http://localhost:5000/',
//     headers: {
//         'Content-Type': 'application/json',
//     },
// });


// const setAuthToken = (token) => {
//     if (token) {
//         api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
//         localStorage.setItem('token', token);
//     } else {
//         delete api.defaults.headers.common['Authorization'];
//         localStorage.removeItem('token');
//     }
// };


// const token = localStorage.getItem('token');
// if (token) {
//     setAuthToken(token);
// }

// export const login = async (username, password) => {
//     try {
//         const response = await api.post('/login', { username, password });
//         setAuthToken(response.data.token);
//         return response.data;
//     } catch (error) {
//         throw error.response.data;
//     }
// };

// export const register = async (username, password, email, nama) => {
//     try {
//         const response = await api.post('/register', { username, password, email, nama });
//         return response.data;
//     } catch (error) {
//         throw error.response.data;
//     }
// };

// // Search songs API call
// export const searchSongs = async (query) => {
//     try {
//         const response = await api.get(`/search?query=${query}`);
//         return response.data.suggestions;
//     } catch (error) {
//         throw new Error('Search failed');
//     }
// };

// // Get recommendations API call
// export const getRecommendations = async (songNames) => {
//     try {
//         const response = await api.post('/recommend', { song_names: songNames });
//         return response.data;
//     } catch (error) {
//         throw new Error('Recommendation failed');
//     }
// };

// // Submit feedback API call
// export const submitFeedback = async (songName, liked) => {
//     try {
//         const response = await api.post('/feedback', { song_name: songName, liked });
//         return response.data;
//     } catch (error) {
//         throw new Error('Feedback submission failed');
//     }
// };