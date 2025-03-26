import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
// import 'bootstrap/dist/css/bootstrap.css';

// import 'bootstrap-icons/font/bootstrap-icons.css';


// Configure Axios to send credentials with requests
axios.defaults.withCredentials = true;

const app = createApp(App);

app.use(router);
app.mount('#app');