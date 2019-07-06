import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const isDevelopment = process.env.NODE_ENV !== 'production';

class State {
  apiHost: string = (isDevelopment) ? `http://${window.location.hostname}:5001` : '';
  isLoading: boolean = true;
  requestedURL: string | null = null;
  queue: any | null = null;
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
    setQueue(state, queue) {
      state.queue = Object.assign({}, queue);
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
    setDefaultRequestStates(state) {
      state.nodes = [];
      state.links = [];
      state.queue = null;
      state.numNodesQueued = 0;
      state.numNodesInProgress = 0;
      state.numNodesFetched = 0;
      state.numLinksFetched = 0;
    },
  },
  actions: {
    resetRequestState({ commit }) {
      return new Promise((resolve) => {
        commit('setDefaultRequestStates');
        resolve();
      });
    },
    setupNewRequest({ commit }, { url }) {
      return new Promise((resolve) => {
        commit('setIsLoading', true);
        commit('setDefaultRequestStates');
        commit('setRequestedUrl', url);
        resolve();
      });
    },
    saveQueue({ commit }, { eventKeys, queueUniqueId }) {
      return new Promise((resolve) => {
        commit('setQueue', { eventKeys, queueUniqueId });
        resolve('foobar');
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
