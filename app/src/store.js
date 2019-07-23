import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const isDevelopment = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  strict: isDevelopment,
  state: {
    apiHost: (isDevelopment) ? `http://${window.location.hostname}:5000` : '',
    nodeStatusOptions: ['found', 'queued', 'running', 'fetched'],
    nodeStats: {},
    nodes: {},
    nodesByLevel: [],
    links: {},
    settings: {
      rules: {
        max_link_depth: 1,
        force_from_db: false,
        force_from_web: false,
      },
    },
  },
  getters: {
    getNodeByUUID: (state) => (nodeUUID) => {
      return state.nodes[nodeUUID]
    },
    getLinksBySourceUUID: (state) => (findNodeUUID) => {
      const linkIds = Object.keys(state.links)
      const matchingIds = linkIds.filter((linkId) => {
        const linkParts = linkId.split(':')
        const currNodeSourceUUID = linkParts[0]
        return currNodeSourceUUID === findNodeUUID
      })
      return matchingIds
    },
    getLinksByTargetUUID: (state) => (findNodeUUID) => {
      const linkIds = Object.keys(state.links)
      const matchingIds = linkIds.filter((linkId) => {
        const linkParts = linkId.split(':')
        const currNodeTargetUUID = linkParts[1]
        return currNodeTargetUUID === findNodeUUID
      })
      return matchingIds
    },
  },
  mutations: {
    updateNode (state, node) {
      const nodeUUID = node.node_uuid
      const status = node.status

      if (status && state.nodeStatusOptions.indexOf(status) < 0) {
        return
      }

      let shouldUpdateStatusCounts = false
      if (nodeUUID in state.nodes) {
        const currStatus = state.nodes[nodeUUID].status
        shouldUpdateStatusCounts = status && (currStatus !== status)
        node = Object.assign({}, state.nodes[nodeUUID], node)
      }

      if (shouldUpdateStatusCounts) {
        const statusCounts = (typeof state.nodeStats[status] === 'undefined') ? 1 : state.nodeStats[status] + 1
        Vue.set(state.nodeStats, status, statusCounts)
      }

      Vue.set(state.nodes, nodeUUID, node)
    },
    addLink (state, link) {
      const linkID = `${link.source_node_uuid}:${link.target_node_uuid}`
      if (linkID in state.links) {
        return
      }

      // Add the link to the collection of all links
      Vue.set(state.links, linkID, link)

      // Yas! We've added a new link!
      state.numLinksFetched = Object.keys(state.links).length
    },
    addNodeToLevel (state, { node, level }) {
      const nodeUUID = node.node_uuid

      if (!(nodeUUID in state.nodes)) {
        return
      }

      // Get the current level and check if the new level is farther away
      // (ex. level 1 is closer than level 5)
      const currLevel = state.nodes[nodeUUID].level
      if (typeof currLevel !== 'undefined' && level >= currLevel) {
        return
      }

      // The new level is closer, so let's remove the old link (we'll add it back in later)
      if (typeof state.nodesByLevel[currLevel] !== 'undefined') {
        state.nodesByLevel[currLevel] = state.nodesByLevel[currLevel].filter((value) => value !== nodeUUID)
      }

      // Setup a new level collection if one doesn't exist yet
      if (typeof state.nodesByLevel[level] === 'undefined') {
        state.nodesByLevel[level] = []
      }

      // Add this link (by id) to the new level
      const nodeWithLevel = Object.assign({}, state.nodes[nodeUUID], { level })
      state.nodesByLevel[level].push(nodeUUID)
      Vue.set(state.nodesByLevel, level, state.nodesByLevel[level])
      Vue.set(state.nodes, nodeUUID, nodeWithLevel)
    },
    resetResultsData (state) {
      state.nodes = {}
      state.links = {}
      state.nodesByLevel = []
      state.nodeStats = {}
    },
  },
  actions: {},
})
