import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const isDevelopment = process.env.NODE_ENV !== 'production';

class State {
  apiHost: string = (isDevelopment) ? `http://${window.location.hostname}:5001` : '';
  isLoading: boolean = true;
  requestedURL: string | null = null;
  nodeEventKeys: any | null = null;
  nodes: any = {};
  links: any[] = [];
  numNodesQueued: number = 0;
  numNodesInProgress: number = 0;
  numNodesFetched: number = 0;
  numLinksFetched: number = 0;
  settings: any = {
    rules: {
      max_link_depth: 2,
      // force_from_db: false,
    },
  };
}

const initState: any = new State();

export default new Vuex.Store({
  strict: isDevelopment,
  state: initState,
  mutations: {
    setIsLoading(state, status) {
      state.isLoading = status;
    },
    setRequestedUrl(state, url) {
      state.requestedURL = url;
    },
    setNodeEventKeys(state, nodeEventKeys) {
      state.nodeEventKeys = Object.assign({}, nodeEventKeys);
    },
    addNode(state, node) {
      const node_uuid = node.node_uuid
      if (node_uuid in state.nodes) {
        return
      }

      Vue.set(state.nodes, node.node_uuid, node);
      state.numNodesFetched += 1;
    },
    addLink(state, link) {
      Vue.set(state.links, state.links.length, link);
      state.numLinksFetched += 1;
    },
    add(state, {stateVar, n}) {
      n = n || 1;
      state[stateVar] += n;
    },
    resetNodes(state) {
      state.nodes = [];
    },
    resetLinks(state) {
      state.links = [];
    },
  },
  actions: {
    resetState({ commit }) {
      commit('resetNodes');
      commit('resetLinks');
    },
    setupNewRequest({ commit, dispatch }, { url }) {
      commit('setIsLoading', true);
      commit('setRequestedUrl', url);
      dispatch('getEventKeys').then(() => {
        commit('setIsLoading', false);
      });
    },
    getEventKeys({ commit, state }) {
      const path = `${state.apiHost}/api/node_event_keys`;
      const params = { url: state.requestedURL };
      return axios
        .get(path, {params})
        .then((response) => {
          commit('setNodeEventKeys', response.data);
        });
    },
    addNode({ commit }, node) {
      commit('addNode', node);
    },
    addLink({ commit }, link) {
      commit('addLink', link);
    },
    addOneTo({ commit }, stateVar) {
      commit('add', {stateVar, n: 1});
    },
  },
});
