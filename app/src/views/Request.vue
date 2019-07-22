<template>
 <div class="request" v-if="!isLoading">
    <UrlInput :url="requestedUrl" />
    <Node
      :node-uuid="originNodeUUID"
      :node-url="originNodeUrl" />
    <p class="request__stats">
      found <span class="request__stats__number">{{nodeStats.queued}}</span> sites
    </p>
    <Level
      v-for="(links, level) in linksByLevel"
      :key="level"
      :level="level"
      :links="links"
      />
  </div>
</template>

<script>
import { mapState } from 'vuex'
import axios from 'axios'
import io from 'socket.io-client'

import UrlInput from '@/components/UrlInput.vue'
import Node from '@/components/Node.vue'
import Level from '@/components/Level.vue'

export default {
  name: 'request',
  props: ['url'],
  components: { UrlInput, Node, Level },
  data: () => {
    return {
      isLoading: true,
      socket: null,
      queue: null,
      originNodeUUID: null,
      originNodeUrl: null,
      requestStatus: null,
    }
  },
  computed: {
    requestedUrl () {
      return this.url
    },
    ...mapState({
      apiHost: 'apiHost',
      settings: 'settings',
      nodes: 'nodes',
      nodeStats: 'nodeStats',
      links: 'links',
      linksByLevel: 'linksByLevel',
    }),
  },

  created () {
    this.$store
      .dispatch('setupResultsData', { url: this.requestedUrl })
      .then(() => {
        this.createQueue()
        window.addEventListener('unload', this.breakdown)
        this.isLoading = false
      })
  },

  beforeDestroy () {
    this.stopListening()
    this.stopQueue()
  },

  methods: {
    createQueue () {
      const path = `${this.apiHost}/api/queue/create`
      const params = {
        url: this.requestedUrl,
        rules: this.settings.rules,
      }
      return axios
        .post(path, params)
        .then((response) => {
          this.queue = Object.assign({}, {
            eventKeys: response.data.event_keys,
            requestId: response.data.request_id,
            node_uuid: response.data.node_uuid,
            node_url: response.data.node_url,
          })

          this.originNodeUUID = this.queue.node_uuid
          this.originNodeUrl = this.queue.node_url

          this.$store.dispatch('setNodeWithStatus', {
            node_uuid: this.queue.node_uuid,
            node_url: this.queue.node_url,
            status: 'queued'
          })

          this.startListening()
          this.startQueue()
        })
    },

    startListening () {
      // console.log(`Listening on queue namespace: /${this.queue.requestId}`)
      const requestId = this.queue.requestId
      this.socket = io(`0.0.0.0:5000/${requestId}`)
      this.requestStatus = 'listening'

      this.socket.on(this.queue.eventKeys['REQUEST:QUEUED'], (res) => {
        // console.log('REQUEST:QUEUED', res)
        this.requestStatus = 'queued'
      })

      this.socket.on(this.queue.eventKeys['REQUEST:IN_PROGRESS'], (res) => {
        // console.log('REQUEST:IN_PROGRESS', res)
        this.requestStatus = 'running'
      })

      this.socket.on(this.queue.eventKeys['REQUEST:COMPLETED'], (res) => {
        // console.log('REQUEST:COMPLETED', res)
        this.requestStatus = 'completed'
      })

      // this.socket.on(this.queue.eventKeys['REQUEST:HEARTBEAT'], (res) => {
      //   console.log('REQUEST:HEARTBEAT', res)
      // })

      this.socket.on(this.queue.eventKeys['NODE:QUEUED'], (res) => {
        // console.log('NODE:QUEUED', res)
        let node = res
        node.status = 'queued'
        this.$store.dispatch('setNodeWithStatus', node)
      })

      this.socket.on(this.queue.eventKeys['NODE:IN_PROGRESS'], (res) => {
        // console.log('NODE:IN_PROGRESS', res)
        let node = res
        node.status = 'running'
        this.$store.dispatch('setNodeWithStatus', node)
      })

      this.socket.on(this.queue.eventKeys['NODE:COMPLETED'], (res) => {
        // console.log('NODE:COMPLETED', res)
        let node = res
        node.status = 'fetched'
        this.$store.dispatch('setNodeWithStatus', node)
      })

      this.socket.on(this.queue.eventKeys['LINK:COMPLETED'], (res) => {
        console.log('LINK:COMPLETED', res)
        this.$store.dispatch('addLink', res)
      })
    },

    startQueue () {
      // console.log(`Starting queue: ${this.queue.requestId}`)
      const requestId = this.queue.requestId
      const path = `${this.apiHost}/api/queue/${requestId}/start`
      return axios.post(path)
    },

    stopListening () {
      if (this.socket === null) {
        return
      }

      this.socket.close()
    },

    stopQueue () {
      if (
        typeof this.queue === 'undefined' ||
        this.queue === null ||
        typeof this.queue.requestId === 'undefined' ||
        this.queue.requestId === null
      ) {
        return
      }

      // console.log(`Stopping queue: ${this.queue.requestId}`)
      const requestId = this.queue.requestId
      const path = `${this.apiHost}/api/queue/${requestId}/stop`
      return axios.post(path)
    },
  },
}
</script>

<style lang="scss">
.request {
  width: 80%;
  max-width: 600px;
  min-width: 300px;
  margin: 0 auto;

  &__stats {
    font-size: 14px;

    &__number {
      font-weight: bold;
    }
  }
}
</style>
