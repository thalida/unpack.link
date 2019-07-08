import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import About from './views/About.vue'
import Request from './views/Request.vue'
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
      name: 'request',
      path: '/request',
      props: (route) => ({ url: route.query.url }),
      component: Request,
    },
    {
      path: '*',
      name: '404',
      component: FourOhFour,
    },
  ]
})
