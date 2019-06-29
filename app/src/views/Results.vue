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
    {{numFetchedLinks}} / {{numLinks}}
    <div class="tree">
      <Level
        v-for="(links, level) in linksByLevel"
        :key="level"
        :links="links"
      />
    </div>
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

  get eventKeys() {
    return this.$store.state.eventKeys;
  }

  get isLoading() {
    return this.$store.state.isLoading;
  }

  get linksByLevel() {
    return this.$store.state.linksByLevel;
  }

  get numLinks() {
    return this.$store.state.numLinks;
  }

  get numFetchedLinks() {
    return this.$store.state.numFetchedLinks;
  }

  @Watch('eventKeys', {immediate: true})
  onEventKeysChanged(newValue: any) {
    if (typeof newValue === 'undefined' || newValue === null) {
      return;
    }
    this.startListening();
    this.startUnpacking();
  }

  startListening() {
    socket.on(this.eventKeys!.LINK_FETCH_START, (rawLink: any) => {
      this.$store.dispatch('incrementNumLinks');
    });
    socket.on(this.eventKeys!.LINK_FETCH_SUCCESS, (rawLink: any) => {
      this.$store.dispatch('incrementNumFetchedLinks');
      this.$store.dispatch('insertLink', this.formatLink(rawLink));
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
