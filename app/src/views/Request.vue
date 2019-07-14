<template>
 <div class="request" v-if="!isLoading">
    <UrlInput :url="requestedURL" />
    <p class="request__stats">
      <span class="request__stats__number">{{numLinksFetched}} links</span>
      across
      <span class="request__stats__number">{{numNodesQueued}} sites</span>
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
import Level from '@/components/Level.vue'

export default {
  name: 'request',
  props: ['url'],
  components: { UrlInput, Level },
  data: () => {
    return {
      socket: null,
    }
  },
  computed: {
    ...mapState({
      apiHost: 'apiHost',
      isLoading: 'isLoading',
      settings: 'settings',
      requestedURL: 'requestedURL',
      queue: 'queue',
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
    this.setup(this.url)
    window.addEventListener('unload', this.breakdown)
  },

  beforeRouteUpdate (to, from, next) {
    this.stopQueue()
    this.setup(to.query.url)
    next()
  },

  beforeRouteLeave (to, from, next) {
    this.breakdown()
    next()
  },

  methods: {
    setup (url) {
      this.$store
        .dispatch('setupResultsData', { url })
        .then(() => {
          this.createQueue()
        })
    },

    breakdown () {
      this.stopQueue()
      this.socket.close()
      this.$store.dispatch('resetResultsData')
    },

    createQueue () {
      const path = `${this.apiHost}/api/queue/create`
      const params = {
        url: this.requestedURL,
        rules: this.settings.rules,
      }
      return axios
        .post(path, params)
        .then((response) => {
          return this.$store.dispatch('saveQueue', {
            eventKeys: response.data.event_keys,
            requestId: response.data.request_id,
          })
        })
        .then(() => {
          this.$store.dispatch('addOneTo', 'numNodesQueued')
          this.startListening()
          this.startQueue()
        })
    },

    startListening () {
      const requestId = this.queue.requestId
      this.socket = io(`0.0.0.0:5000/${requestId}`)
      // console.log(`Listening on queue namespace: /${requestId}`)

      // this.socket.on(this.queue.eventKeys['REQUEST:QUEUED'], (res) => {
      //   console.log('REQUEST:QUEUED', res)
      // })

      // this.socket.on(this.queue.eventKeys['REQUEST:IN_PROGRESS'], (res) => {
      //   console.log('REQUEST:IN_PROGRESS', res)
      // })

      // this.socket.on(this.queue.eventKeys['REQUEST:COMPLETED'], (res) => {
      //   console.log('REQUEST:COMPLETED', res)
      // })

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

    stopQueue () {
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
