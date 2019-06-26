import Vue from 'vue';
import Vuex from 'vuex';
import axios from 'axios';

Vue.use(Vuex);

const isDevelopment = process.env.NODE_ENV !== 'production';

class State {
  apiHost: string;
  isLoading: boolean;
  requestedURL: string | null;
  eventKeys: any | null;
  nodes: any[];
  links: any[];
  linksByLevel: any[];
  targetSources: any[];
  requiredNodes: any[];
  settings: any;

  constructor() {
    this.apiHost = (isDevelopment) ? `http://${window.location.hostname}:5001` : '';
    this.isLoading = true;
    this.requestedURL = null;
    this.eventKeys = null;
    this.nodes = [];
    this.links = [];
    this.linksByLevel = [];
    this.targetSources = [];
    this.requiredNodes = [];
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
    setEventKeys(state, eventKeys) {
      state.eventKeys = Object.assign({}, eventKeys);
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
      const path = `${state.apiHost}/api/event_keys`;
      const params = { url: state.requestedURL };
      return axios
        .get(path, {params})
        .then((response) => {
          commit('setEventKeys', response.data);
        });
    },
    insertLink({ commit }, link) {
      const sourceUUID: string = (link.source) ? link.source.node_uuid : null;
      const targetUUID: string = link.target.node_uuid;
      const level: number = link.state.level;

      commit('addNode', link.source);
      commit('addNode', link.target);
      commit('addLink', link);
      commit('addLinkToLevel', { level, link });
      commit('addTargetSource', {targetUUID, sourceUUID});
    },
  },
});
