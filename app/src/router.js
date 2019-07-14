import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Request from './views/Request.vue'

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
      name: 'request',
      path: '/request',
      props: (route) => ({ url: route.query.url }),
      component: Request,
    },
  ]
})
