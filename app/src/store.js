import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const isDevelopment = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  strict: isDevelopment,
  state: {
    apiHost: (isDevelopment) ? `http://${window.location.hostname}:5000` : '',
    nodes: {},
    nodeStatusOptions: ['queued', 'running', 'fetched'],
    nodeStats: {},
    links: {},
    linksByLevel: [],
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
    setNode (state, node) {
      Vue.set(state.nodes, node.node_uuid, node)
    },
    setNodeStatus (state, node) {
      const nodeUUID = node.node_uuid
      const status = node.status
      if (
        !(nodeUUID in state.nodes) ||
        state.nodeStatusOptions.indexOf(status) < 0
      ) {
        return
      }

      state.nodes[nodeUUID].status = status
      Vue.set(state.nodes, nodeUUID, state.nodes[nodeUUID])

      const statusCounts = (typeof state.nodeStats[status] === 'undefined') ? 1 : state.nodeStats[status] + 1
      Vue.set(state.nodeStats, status, statusCounts)
    },
    addLink (state, link) {
      const linkID = `${link.source_node_uuid}:${link.target_node_uuid}`
      const newLevel = link.level

      // If the link already exists
      if (linkID in state.links) {
        // Get the current level and check if the new level is farther away
        // (ex. level 1 is closer than level 5)
        const currLevel = state.links[linkID].level
        if (newLevel >= currLevel) {
          return
        }

        // The new level is closer, so let's remove the old link (we'll add it back in later)
        state.linksByLevel[currLevel] = state.linksByLevel[currLevel].filter((value) => value !== linkID)
        Vue.delete(state.links, linkID)
      }

      // Add the link to the collection of all links
      Vue.set(state.links, linkID, link)

      // Setup a new level collection if one doesn't exist yet
      if (typeof state.linksByLevel[newLevel] === 'undefined') {
        state.linksByLevel[newLevel] = []
      }

      // Add this link (by id) to the new level
      state.linksByLevel[newLevel].push(linkID)
      Vue.set(state.linksByLevel, newLevel, state.linksByLevel[newLevel])

      // Yas! We've added a new link!
      state.numLinksFetched = Object.keys(state.links).length
    },
    resetResultsData (state) {
      state.nodes = {}
      state.links = {}
      state.linksByLevel = []
      state.nodeStats = {}
    },
  },
  actions: {
    setupResultsData ({ commit }, { url }) {
      return new Promise((resolve) => {
        commit('resetResultsData')
        resolve()
      })
    },
    setNodeWithStatus ({ commit }, node) {
      commit('setNode', node)
      commit('setNodeStatus', {
        node_uuid: node.node_uuid,
        status: node.status,
      })
    },
    addLink ({ commit }, link) {
      commit('addLink', link)
    },
  },
})
