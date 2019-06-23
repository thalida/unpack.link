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
  nodesByLevel: any[];
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
    this.nodesByLevel = [];
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
    addNodeToLevel(state, {level, node_uuid}) {
      if (typeof state.nodesByLevel[level] === 'undefined') {
        state.nodesByLevel[level] = [];
      }

      if (state.nodesByLevel[level].includes(node_uuid)) {
        return;
      }

      state.nodesByLevel[level].push(node_uuid);
      Vue.set(state.nodesByLevel, level, state.nodesByLevel[level]);
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
    resetNodesByLevel(state) {
      state.nodesByLevel = [];
    },
    resetTargetSources(state) {
      state.targetSources = [];
    },
    resetRequiredNodes(state) {
      state.requiredNodes = [];
    },
  },
  actions: {
    handleNewRequestUrl({ commit, dispatch }, { url }) {
      commit('setIsLoading', true);
      commit('setRequestedUrl', url);
      dispatch('getEventKeys').then(() => {
        // commit('resetNodes');
        // commit('resetLinks');
        // commit('resetNodesByLevel');
        // commit('resetTargetSources');
        // commit('resetRequiredNodes');
        commit('setIsLoading', false);
      });
    },
    startUnpacking({ state }) {
      const path = `${state.apiHost}/api/start`;
      const params = {
        url: state.requestedURL,
        rules: state.settings.rules,
      };
      return axios.post(path, params);
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
    insertLink({ commit, state }, link) {
      const sourceUUID: string = (link.source) ? link.source.node_uuid : null;
      const targetUUID: string = link.target.node_uuid;
      const level: number = link.state.level;

      commit('addNode', link.source);
      commit('addNode', link.target);
      commit('addLink', link);
      commit('addNodeToLevel', { level, node_uuid: targetUUID });
      commit('addTargetSource', {targetUUID, sourceUUID});
    },
  },
});
