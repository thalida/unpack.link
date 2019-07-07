import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const isDevelopment = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  strict: isDevelopment,
  state: {
    apiHost: (isDevelopment) ? `http://${window.location.hostname}:5000` : '',
    requestIds: {

    },
    isLoading: true,
    requestedURL: null,
    queue: null,
    nodes: {},
    links: [],
    numNodesQueued: 0,
    numNodesInProgress: 0,
    numNodesFetched: 0,
    numLinksFetched: 0,
    settings: {
      rules: {
        max_link_depth: 2,
        // force_from_db: false,
      },
    },
  },
  mutations: {
    setIsLoading (state, status) {
      state.isLoading = status
    },
    setRequestedUrl (state, url) {
      state.requestedURL = url
    },
    setQueue (state, queue) {
      state.queue = Object.assign({}, queue)
    },
    addNode (state, node) {
      const nodeUUID = node.node_uuid
      if (nodeUUID in state.nodes) {
        return
      }

      Vue.set(state.nodes, node.node_uuid, node)
      state.numNodesFetched += 1
    },
    addLink (state, link) {
      Vue.set(state.links, state.links.length, link)
      state.numLinksFetched += 1
    },
    add (state, { stateVar, n }) {
      n = n || 1
      state[stateVar] += n
    },
    resetResultsData (state) {
      state.nodes = []
      state.links = []
      state.queue = null
      state.numNodesQueued = 0
      state.numNodesInProgress = 0
      state.numNodesFetched = 0
      state.numLinksFetched = 0
    },
  },
  actions: {
    setupResultsData ({ commit }, { url }) {
      return new Promise((resolve) => {
        commit('setIsLoading', true)
        commit('resetResultsData')
        commit('setRequestedUrl', url)
        commit('setIsLoading', false)
        resolve()
      })
    },
    resetResultsData ({ commit }) {
      return new Promise((resolve) => {
        commit('resetResultsData')
        resolve()
      })
    },
    saveQueue ({ commit }, { eventKeys, requestId }) {
      return new Promise((resolve) => {
        commit('setQueue', { eventKeys, requestId })
        resolve('foobar')
      })
    },
    addNode ({ commit }, node) {
      commit('addNode', node)
    },
    addLink ({ commit }, link) {
      commit('addLink', link)
    },
    addOneTo ({ commit }, stateVar) {
      commit('add', { stateVar, n: 1 })
    },
  },
})
