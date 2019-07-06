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
  nodes: any[] = [];
  links: any[] = [];
  linksByLevel: any[] = [];
  targetSources: any[] = [];
  requiredNodes: any[] = [];
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
    addLink(state, link) {
      Vue.set(state.links, state.links.length, link);
    },
    addNode(state, node) {
      if (node === null) {
        return;
      }

      Vue.set(state.nodes, node.node_uuid, node);
    },
    addLinkToLevel(state, {level, link}) {
      if (typeof state.linksByLevel[level] === 'undefined') {
        state.linksByLevel[level] = [];
      }

      // const foundLink
      // if (state.linksByLevel[level].includes(link)) {
      //   return;
      // }

      state.linksByLevel[level].push(link);
      Vue.set(state.linksByLevel, level, state.linksByLevel[level]);
    },
    addTargetSource(state, {targetUUID, sourceUUID}) {
      if (typeof state.targetSources[targetUUID] === 'undefined') {
        state.targetSources[targetUUID] = [];
      }

      if (state.targetSources[targetUUID].includes(sourceUUID)) {
        return;
      }

      if (sourceUUID) {
        state.targetSources[targetUUID].push(sourceUUID);
        Vue.set(state.targetSources, targetUUID, state.targetSources[targetUUID]);
      }
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
    resetLinksByLevel(state) {
      state.linksByLevel = [];
    },
    resetTargetSources(state) {
      state.targetSources = [];
    },
    resetRequiredNodes(state) {
      state.requiredNodes = [];
    },
  },
  actions: {
    resetState({ commit }) {
      commit('resetNodes');
      commit('resetLinks');
      commit('resetLinksByLevel');
      commit('resetTargetSources');
      commit('resetRequiredNodes');
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
    insertLink({ commit }, link) {
      const sourceUUID: string = (link.source) ? link.source.node_uuid : null;
      const targetUUID: string = link.target.node_uuid;
      const level: number = link.data.level;

      commit('addNode', link.source);
      commit('addNode', link.target);
      commit('addLink', link);
      commit('addLinkToLevel', { level, link });
      commit('addTargetSource', {targetUUID, sourceUUID});
    },
    addOneTo({ commit }, stateVar) {
      commit('add', {stateVar, n: 1});
    },
  },
});
