<template>
	<div class="results" :if="!isLoading">
		<form id="input-form" @submit.prevent="onFormSubmit">
			<input
				v-model="inputRequestUrl"
				type="url"
				placeholder="http://"
				required />
			<button type="submit">unpack</button>
		</form>
    <p>node_stats: {{numNodesQueued}} : {{numNodesInProgress}} : {{numNodesFetched}}</p>
    <p>link_stats: {{numLinksFetched}}</p>
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

const socket = io('0.0.0.0:5000');


@Component({
  components: {Level},
})
export default class Results extends Vue {
  @Prop() private url!: string;
  inputRequestUrl: string | null = null;

  get apiHost() {
    return this.$store.state.apiHost;
  }

  get isLoading() {
    return this.$store.state.isLoading;
  }

  get settings() {
    return this.$store.state.settings;
  }

  get requestedURL() {
    return this.$store.state.requestedURL;
  }

  get queue() {
    return this.$store.state.queue;
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

  // @Watch('$route', { immediate: true, deep: true })
  // onUrlChange(newVal: any) {
  //   this.stopQueue();
  //   this.$store.dispatch('resetRequestState');
  // }

  beforeRouteLeave(to, from, next) {
    debugger;
  }

  created() {
    this.$store
      .dispatch('setupNewRequest', { url: this.url })
      .then(() => {
        this.inputRequestUrl = this.requestedURL;
        this.createQueue();
      });
  }

  createQueue() {
      const path = `${this.apiHost}/api/queue/create`;
      const params = {
        url: this.requestedURL,
        rules: this.settings.rules,
      };
      return axios
        .post(path, params)
        .then((response) => {
          return this.$store.dispatch('saveQueue', {
            eventKeys: response.data.event_keys,
            queueUniqueId: response.data.queue_unique_id,
          });
        })
        .then(() => {
          this.startListening();
          this.startQueue();
        });
  }

  startListening() {
    socket.on(this.queue.eventKeys!['FETCH:NODE:QUEUED'], (res: any) => {
      this.$store.dispatch('addOneTo', 'numNodesQueued');
      console.log('FETCH:NODE:QUEUED', res);
    });

    socket.on(this.queue.eventKeys!['FETCH:NODE:IN_PROGRESS'], (res: any) => {
      this.$store.dispatch('addOneTo', 'numNodesInProgress');
      console.log('FETCH:NODE:IN_PROGRESS', res);
    });

    socket.on(this.queue.eventKeys!['FETCH:NODE:COMPLETED'], (res: any) => {
      let node: any;

      if (typeof res === 'object') {
        node = JSON.parse(JSON.stringify(res));
      } else {
        node = JSON.parse(res);
      }

      this.$store.dispatch('addNode', node);
      console.log('FETCH:NODE:COMPLETED', res);
    });

    socket.on(this.queue.eventKeys!['STORE:LINK:COMPLETED'], (res: any) => {
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

  startQueue() {
    const queueUniqueId = this.queue.queueUniqueId;
    const path = `${this.apiHost}/api/queue/${queueUniqueId}/start`;
    return axios.post(path);
  }

  stopQueue() {
    const queueUniqueId = this.queue.queueUniqueId;
    const path = `${this.apiHost}/api/queue/${queueUniqueId}/stop`;
    return axios.post(path);
  }

  onFormSubmit() {
    this.$router.push({
      name: 'results',
      params: {
        url: this.inputRequestUrl as string,
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
