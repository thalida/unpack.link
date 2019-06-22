<template>
	<div class="map">
		<form id="input-form" @submit.prevent>
			<input
				v-model="inputUrl"
				type="url"
				placeholder="http://"
				required />
			<button type="submit" @click="handleFormSubmit">unpack</button>
		</form>
    <div v-for="(links, level) in levels" :key="level" class="level">
      <span v-for="(link, index) in links" :key="index" class="link">
        <span v-if="link['source'] === null">
          Primary url: {{ link['target']['node_url'] }}
        </span>
        <span v-else-if="link['state']['is_already_in_path']">
          <strike>
            {{ link['state']['weight'] }}
            {{ link['target']['node_url'] }} from
            {{ link['source']['node_url'] }}
          </strike>
        </span>
        <span v-else>
            {{ link['state']['weight'] }}
            {{ link['target']['node_url'] }} from
            {{ link['source']['node_url'] }}
        </span>
      </span>
    </div>
	</div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import axios from 'axios';
import io from 'socket.io-client';

const socket = io('0.0.0.0:5001');

interface EventKeys {
  TREE_UPDATE: string;
  TREE_INIT: string;
}

@Component
export default class Results extends Vue {
  eventKeys: EventKeys | null = null;
  inputUrl: string | null = null;
  host: string = 'http://0.0.0.0:5001';
  levels: any[] = [];

  @Prop() private url!: string;

  created() {
    this.getEventKeys();
    this.inputUrl = this.url;
  }

  getEventKeys() {
    axios.get(`${this.host}/api/event_keys`, {params: {url: this.url}})
      .then(this.handleGetEventKeys);
  }

  startListening() {
    if (this.eventKeys === null) {
      return;
    }

    socket.on(this.eventKeys!.TREE_UPDATE, this.handleTreeUpdate);
  }

  startUnpacking() {
    const packet = {
      url: this.url,
      rules: {
        max_link_depth: 2,
        // force_from_web: true,
      },
    };
    axios.post(`${this.host}/api/start`, packet);
  }

  handleGetEventKeys(response: any) {
    this.eventKeys = response.data;
    this.startListening();
    this.startUnpacking();
  }

  handleTreeUpdate(node: any) {
    const formattedNode = this.formatNode(node);
    const level: number = formattedNode.state.level;

    if (typeof this.levels[level] === 'undefined') {
      this.levels[level] = [];
    }

    this.levels[level].push(formattedNode);
    Vue.set(this.levels, level, this.levels[level]);
    // console.log(formattedNode);
  }

  handleFormSubmit() {
    this.$router.push({
      name: 'results',
      params: {
        url: this.inputUrl as string,
      },
    });
  }

  formatNode(node: any) {
    let formattedNode = null;

    if (typeof node === 'object') {
      formattedNode = JSON.parse(JSON.stringify(node));
    } else {
      formattedNode = JSON.parse(node);
    }

    formattedNode.hasSource = typeof formattedNode.source !== 'undefined' && formattedNode.source !== null;
    formattedNode.hasTarget = typeof formattedNode.target !== 'undefined' && formattedNode.target !== null;

    return formattedNode;
  }
}
</script>

<style lang="scss">
.level {
  margin: 15px 0;
}
.link {
  padding: 0 10px;
}
</style>
