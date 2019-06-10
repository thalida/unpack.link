<template>
    <div class="map">
        Map
        <p>{{ url }}</p>
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
    host: string = 'http://0.0.0.0:5001';

    @Prop() private url!: string;

    constructor() {
        super();
    }

    created() {
        this.getEventKeys();
    }

    getEventKeys() {
        axios.get(`${this.host}/api/event_keys`, {params: {url: this.url}})
            .then(this.handleGetEventKeys);
    }

    handleGetEventKeys(response: any) {
        this.eventKeys = response.data;
        this.startListening();
        this.startUnpacking();
    }

    startListening() {
        if (this.eventKeys === null) {
            return;
        }

        socket.on(this.eventKeys!.TREE_UPDATE, this.handleTreeUpdate);
    }

    handleTreeUpdate(node: any) {
        console.log(node);
    }

    startUnpacking() {
        axios.post(`${this.host}/api/start`, {url: this.url});
    }
}
</script>

<style lang="scss">
.map {
    background: blue;
}
</style>
