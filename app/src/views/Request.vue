<template>
 <div class="request" v-if="!isLoading">
    <UrlInput :url="requestedUrl" />
    <p class="request__stats">
      <span class="request__stats__number">{{numLinksFetched}} links</span>
      across
      <span class="request__stats__number">{{numNodesQueued}} sites</span>
    </p>
    <Node
      :node-uuid="requestedUUID"
      :node-url="requestedUrl" />
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
      requestedUUID: null,
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
      links: 'links',
      linksByLevel: 'linksByLevel',
      numNodesQueued: 'numNodesQueued',
      numNodesInProgress: 'numNodesInProgress',
      numLinksFetched: 'numLinksFetched',
      numNodesFetched: 'numNodesFetched',
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
          })

          this.startListening()
          this.startQueue()

          this.$store.dispatch('addOneTo', 'numNodesQueued')
        })
    },

    startListening () {
      const requestId = this.queue.requestId
      this.socket = io(`0.0.0.0:5000/${requestId}`)
      this.requestStatus = 'listening'
      // console.log(`Listening on queue namespace: /${requestId}`)

      this.socket.on(this.queue.eventKeys['REQUEST:QUEUED'], (res) => {
        this.requestStatus = 'queued'
        // console.log('REQUEST:QUEUED', res)
      })

      this.socket.on(this.queue.eventKeys['REQUEST:IN_PROGRESS'], (res) => {
        this.requestStatus = 'in_progress'
        // console.log('REQUEST:IN_PROGRESS', res)
      })

      this.socket.on(this.queue.eventKeys['REQUEST:COMPLETED'], (res) => {
        this.requestStatus = 'completed'
        // console.log('REQUEST:COMPLETED', res)
      })

      // this.socket.on(this.queue.eventKeys['REQUEST:HEARTBEAT'], (res) => {
      //   console.log('REQUEST:HEARTBEAT', res)
      // })

      this.socket.on(this.queue.eventKeys['NODE:QUEUED'], (res) => {
        this.$store.dispatch('addOneTo', 'numNodesQueued')
        // console.log('NODE:QUEUED', res)
      })

      this.socket.on(this.queue.eventKeys['NODE:IN_PROGRESS'], (res) => {
        this.$store.dispatch('addOneTo', 'numNodesInProgress')
        // console.log('NODE:IN_PROGRESS', res)
      })

      this.socket.on(this.queue.eventKeys['NODE:COMPLETED'], (res) => {
        this.$store.dispatch('addNode', res)
        // console.log('NODE:COMPLETED', res)
      })

      this.socket.on(this.queue.eventKeys['LINK:COMPLETED'], (res) => {
        this.$store.dispatch('addLink', res)
        // console.log('LINK:COMPLETED', res)
      })
    },

    startQueue () {
      const requestId = this.queue.requestId
      const path = `${this.apiHost}/api/queue/${requestId}/start`
      // console.log(`Starting queue: ${requestId}`)
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

      const requestId = this.queue.requestId
      const path = `${this.apiHost}/api/queue/${requestId}/stop`
      // console.log(`Stopping queue: ${requestId}`)
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
