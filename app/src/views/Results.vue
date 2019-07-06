<template>
	<div class="results" :if="!isLoading">
		<form id="input-form" @submit.prevent>
			<input
				v-model="requestedURL"
				type="url"
				placeholder="http://"
				required />
			<button type="submit" @click="onFormSubmit">unpack</button>
		</form>
    <p>node_stats: {{numNodesQueued}} : {{numNodesInProgress}} : {{numNodesFetched}}</p>
    <p>link_stats: {{numLinksFetched}}</p>
    <br /><br /><br /><br />
    {{links}}
    <br /><br /><br /><br />
    {{nodes}}
    <!-- <div class="tree">
      <Level
        v-for="(links, level) in linksByLevel"
        :key="level"
        :links="links"
      />
    </div> -->
	</div>
</template>

<script lang="ts">
import { Vue, Component, Prop, Watch } from 'vue-property-decorator';
import axios from 'axios';
import io from 'socket.io-client';
import Level from '@/components/Level.vue';

const socket = io('0.0.0.0:5001');


@Component({
  components: {Level},
})
export default class Results extends Vue {
  @Prop() private url!: string;

  created() {
    this.$store.dispatch('setupNewRequest', { url: this.url });
  }

  get apiHost() {
    return this.$store.state.apiHost;
  }

  get settings() {
    return this.$store.state.settings;
  }

  get requestedURL() {
    return this.$store.state.requestedURL;
  }

  set requestedURL(newUrl) {
    this.$store.commit('setRequestedURL', newUrl);
  }

  get nodeEventKeys() {
    return this.$store.state.nodeEventKeys;
  }

  get isLoading() {
    return this.$store.state.isLoading;
  }

  get nodes() {
    return this.$store.state.nodes;
  }

  get links() {
    return this.$store.state.links;
  }

  get numNodesQueued() {
    return this.$store.state.numNodesQueued;
  }

  get numNodesInProgress() {
    return this.$store.state.numNodesInProgress;
  }

  get numNodesFetched() {
    return this.$store.state.numNodesFetched;
  }

  get numLinksFetched() {
    return this.$store.state.numLinksFetched;
  }

  @Watch('nodeEventKeys', {immediate: true})
  onNodeEventKeysChanged(newValue: any) {
    if (typeof newValue === 'undefined' || newValue === null) {
      return;
    }
    this.startListening();
    this.startUnpacking();
  }

  startListening() {
    socket.on(this.nodeEventKeys!['FETCH:NODE:QUEUED'], (res: any) => {
      this.$store.dispatch('addOneTo', 'numNodesQueued');
      console.log('FETCH:NODE:QUEUED', res);
    });

    socket.on(this.nodeEventKeys!['FETCH:NODE:IN_PROGRESS'], (res: any) => {
      this.$store.dispatch('addOneTo', 'numNodesInProgress');
      console.log('FETCH:NODE:IN_PROGRESS', res);
    });

    socket.on(this.nodeEventKeys!['FETCH:NODE:COMPLETED'], (res: any) => {
      let node: any;

      if (typeof res === 'object') {
        node = JSON.parse(JSON.stringify(res));
      } else {
        node = JSON.parse(res);
      }

      this.$store.dispatch('addNode', node);
      console.log('FETCH:NODE:COMPLETED', res);
    });

    socket.on(this.nodeEventKeys!['STORE:LINK:COMPLETED'], (res: any) => {
      let link: any;

      if (typeof res === 'object') {
        link = JSON.parse(JSON.stringify(res));
      } else {
        link = JSON.parse(res);
      }

      this.$store.dispatch('addLink', link);
      console.log('STORE:LINK:COMPLETED', res);
    });
  }

  startUnpacking() {
    const path = `${this.apiHost}/api/start`;
    const params = {
      url: this.requestedURL,
      rules: this.settings.rules,
    };
    return axios.post(path, params);
  }

  formatLink(rawLink: any) {
    let link = null;

    if (typeof rawLink === 'object') {
      link = JSON.parse(JSON.stringify(rawLink));
    } else {
      link = JSON.parse(rawLink);
    }

    link.hasSource = typeof link.source !== 'undefined' && link.source !== null;
    link.hasTarget = typeof link.target !== 'undefined' && link.target !== null;

    return link;
  }

  onFormSubmit() {
    this.$store.dispatch('resetState');
    this.$router.push({
      name: 'results',
      params: {
        url: this.requestedURL as string,
      },
    });
  }
}
</script>

<style lang="scss">
.tree {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-gap: 10px;
  grid-auto-rows: minmax(100px, auto);
}
</style>
