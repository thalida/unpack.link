<template>
 <div class="results" v-if="!isLoading">
    <RequestForm :url="requestedURL" />
    <p>node_stats: {{numNodesQueued}} : {{numNodesInProgress}} : {{numNodesFetched}}</p>
    <p>link_stats: {{numLinksFetched}}</p>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import axios from 'axios'
import io from 'socket.io-client'
import RequestForm from '@/components/RequestForm.vue'

const socket = io('0.0.0.0:5000')

export default {
  name: 'results',
  props: ['url'],
  components: { RequestForm },
  computed: {
    // },
    ...mapState({
      apiHost: 'apiHost',
      isLoading: 'isLoading',
      settings: 'settings',
      requestedURL: 'requestedURL',
      queue: 'queue',
      nodes: 'nodes',
      links: 'links',
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
            queueUniqueId: response.data.queue_unique_id,
          })
        })
        .then(() => {
          this.startListening()
          this.startQueue()
        })
    },

    startListening () {
      const queueUniqueId = this.queue.queueUniqueId
      console.log(`Listening on queue: ${queueUniqueId}`)

      socket.on(this.queue.eventKeys['FETCH:NODE:QUEUED'], (res) => {
        this.$store.dispatch('addOneTo', 'numNodesQueued')
        console.log('FETCH:NODE:QUEUED', res)
      })

      socket.on(this.queue.eventKeys['FETCH:NODE:IN_PROGRESS'], (res) => {
        this.$store.dispatch('addOneTo', 'numNodesInProgress')
        console.log('FETCH:NODE:IN_PROGRESS', res)
      })

      socket.on(this.queue.eventKeys['FETCH:NODE:COMPLETED'], (res) => {
        let node

        if (typeof res === 'object') {
          node = JSON.parse(JSON.stringify(res))
        } else {
          node = JSON.parse(res)
        }

        this.$store.dispatch('addNode', node)
        console.log('FETCH:NODE:COMPLETED', res)
      })

      socket.on(this.queue.eventKeys['STORE:LINK:COMPLETED'], (res) => {
        let link

        if (typeof res === 'object') {
          link = JSON.parse(JSON.stringify(res))
        } else {
          link = JSON.parse(res)
        }

        this.$store.dispatch('addLink', link)
        console.log('STORE:LINK:COMPLETED', res)
      })
    },

    startQueue () {
      const queueUniqueId = this.queue.queueUniqueId
      console.log(`Starting queue: ${queueUniqueId}`)
      const path = `${this.apiHost}/api/queue/${queueUniqueId}/start`
      return axios.post(path)
    },

    stopQueue () {
      const queueUniqueId = this.queue.queueUniqueId
      console.log(`Stopping queue: ${queueUniqueId}`)
      const path = `${this.apiHost}/api/queue/${queueUniqueId}/stop`
      return axios.post(path)
    },
  },
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
