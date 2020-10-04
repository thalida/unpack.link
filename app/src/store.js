import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const isDevelopment = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  strict: isDevelopment,
  state: {
    apiHost: (isDevelopment) ? `http://${window.location.hostname}:5000` : '',
    nodeStatusOptions: ['found', 'queued', 'running', 'fetched'],
    defaultNode: {
      node_uuid: null,
      node_url: null,
      node_details: null,
      isSelected: false,
      levels: [],
    },
    nodeStats: {},
    nodes: {},
    links: {},
    settings: {
      rules: {
        max_link_depth: 2,
        force_from_db: false,
        force_from_web: false,
      },
    },
  },
  getters: {
    getSelectedNodeUUIDs: (state) => {
      const nodeUUIDs = Object.keys(state.nodes)
      const selectedNodes = nodeUUIDs.filter((nodeUUID) => {
        const node = state.nodes[nodeUUID]
        return node.isSelected
      })
      return selectedNodes
    },
    getNodesByMinLevel: (state, getters) => {
      const nodeUUIDs = Object.keys(state.nodes)

      if (nodeUUIDs.length <= 0) {
        return
      }

      console.log(getters.getSelectedNodeUUIDs)

      const nodesByMinLevel = nodeUUIDs.reduce((outputArr, nodeUUID) => {
        const levels = state.nodes[nodeUUID].levels
        const minLevel = Math.min(...levels)

        outputArr[minLevel] = outputArr[minLevel] || []
        outputArr[minLevel].push(nodeUUID)
        return outputArr
      }, [])
      return nodesByMinLevel
    },
    getNodeByUUID: (state) => (nodeUUID, useDefaultNode) => {
      let foundNode = state.nodes[nodeUUID]

      if (useDefaultNode && (
        typeof foundNode === 'undefined' ||
        foundNode === null
      )) {
        foundNode = Object.assign({}, state.defaultNode)
      }

      return foundNode
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
        const origStatus = state.nodes[nodeUUID].status
        shouldUpdateStatusCounts = status && (origStatus !== status)
        node = Object.assign({}, state.nodes[nodeUUID], node)
      }

      let defaultNodeClone = JSON.parse(JSON.stringify(state.defaultNode))
      node = Object.assign({}, defaultNodeClone, node)

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
    // eslint-disable-next-line camelcase
    addNodeLevel (state, { node_uuid, level }) {
      // eslint-disable-next-line camelcase
      const nodeUUID = node_uuid

      if (!(nodeUUID in state.nodes)) {
        return
      }

      let node = state.nodes[nodeUUID]

      if (node.levels && node.levels.includes(level)) {
        return
      }

      node.levels = node.levels || []
      node.levels.push(level)
      Vue.set(state.nodes, nodeUUID, node)
    },
    resetResultsData (state) {
      state.nodes = {}
      state.links = {}
      state.nodeStats = {}
    },
  },
})
