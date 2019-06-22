import Vue from 'vue';
import Router from 'vue-router';
import Home from './views/Home.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import(/* webpackChunkName: 'about' */ './views/About.vue'),
    },
    {
      path: '/:url(.*)',
      name: 'results',
      props: (route) => ({ url: route.params.url }),
      component: () => import(/* webpackChunkName: 'results' */ './views/Results.vue'),
    },
    {
      path: '*',
      name: '404',
      component: () => import(/* webpackChunkName: '404' */ './views/404.vue'),
    },
  ],
});
