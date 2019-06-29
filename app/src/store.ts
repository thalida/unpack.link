import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const isDevelopment = process.env.NODE_ENV !== 'production';

class State {
  apiHost: string;
  isLoading: boolean;
  requestedURL: string | null;
  nodeEventKeys: any | null;
  nodes: any[];
  links: any[];
  linksByLevel: any[];
  targetSources: any[];
  requiredNodes: any[];
  numLinks: number;
  numFetchedLinks: number;
  settings: any;

  constructor() {
    this.apiHost = (isDevelopment) ? `http://${window.location.hostname}:5001` : '';
    this.isLoading = true;
    this.requestedURL = null;
    this.nodeEventKeys = null;
    this.nodes = [];
    this.links = [];
    this.linksByLevel = [];
    this.targetSources = [];
    this.requiredNodes = [];
    this.numLinks = 0;
    this.numFetchedLinks = 0;
    this.settings = {
      rules: {
        max_link_depth: 2,
        // force_from_web: true,
      },
    };
  }
}

export default new Vuex.Store({
  strict: isDevelopment,
  state: new State(),
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
    addNToNumLinks(state, n) {
      n = n || 1;
      state.numLinks += n;
    },
    addNToNumFetchedLinks(state, n) {
      n = n || 1;
      state.numFetchedLinks += n;
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
    incrementNumLinks({ commit }) {
      commit('addNToNumLinks', 1);
    },
    incrementNumFetchedLinks({ commit }) {
      commit('addNToNumFetchedLinks', 1);
    },
  },
});
