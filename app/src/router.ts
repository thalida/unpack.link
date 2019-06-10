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
      path: '/map',
      name: 'map',
      component: () => import(/* webpackChunkName: "map" */ './views/Map.vue'),
      props: (route) => ({ url: route.query.url }),
      beforeEnter: (to, from, next) => {
        if (
          typeof to.query === 'undefined'
          || to.query === null
          || typeof to.query.url === 'undefined'
          || to.query.url === null
        ) {
          return next('/');
        }

        const url: string = to.query.url.toString() || '';
        const urlLen: number = url.length;
        if (typeof url === 'string' && urlLen > 0) {
          return next();
        }

        return next('/');
      },
    },
    {
      path: '/about',
      name: 'about',
      component: () => import(/* webpackChunkName: "about" */ './views/About.vue'),
    },
  ],
});
