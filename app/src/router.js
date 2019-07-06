import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import About from './views/About.vue'
import Results from './views/Results.vue'
import FourOhFour from './views/404.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      name: 'home',
      path: '/',
      component: Home,
    },
    {
      name: 'about',
      path: '/about',
      component: About,
    },
    {
      name: 'results',
      path: '/results',
      props: (route) => ({ url: route.query.url }),
      component: Results,
    },
    {
      path: '*',
      name: '404',
      component: FourOhFour,
    },
  ]
})
