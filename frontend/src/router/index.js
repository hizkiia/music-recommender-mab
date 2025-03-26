import { createRouter, createWebHistory } from 'vue-router';
import Login from './components/Login.vue';
import Register from './components/Register.vue';
import Recommend from './components/Recommend.vue';
import Admin from './components/Admin.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/register',
        name: 'Register',
        component: Register
    },
    {
        path: '/recommend',
        name: 'Recommend',
        component: Recommend
    },
    {
        path: '/admin',
        name: 'Admin',
        component: Admin
    },
    {
        path: '*',
        redirect: '/login'
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;