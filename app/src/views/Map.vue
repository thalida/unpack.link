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
		<div v-for="(link, index) in links" v-bind:key="index">
			<span v-if="link.hasSource">{{ link['source']['node_url'] }}</span>
			to
			<span v-if="link.hasTarget">{{ link['target']['node_url'] }}</span>
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
export default class Map extends Vue {
  eventKeys: EventKeys | null = null;
  inputUrl: string | null = null;
  host: string = 'http://0.0.0.0:5001';
  links: any[] = [];

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
    axios.post(`${this.host}/api/start`, {url: this.url});
  }

  handleGetEventKeys(response: any) {
    this.eventKeys = response.data;
    this.startListening();
    this.startUnpacking();
  }

  handleTreeUpdate(node: any) {
    const formattedNode = this.formatNode(node);
    this.links.push(formattedNode);
  }

  handleFormSubmit() {
    this.$router.push({
      name: 'map',
      query: {
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

<style lang="scss"></style>
