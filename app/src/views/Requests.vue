<template>
 <div class="results" v-if="!isLoading">
    <RequestForm :url="requestedURL" />
    <h1>Requests</h1>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import axios from 'axios'
import io from 'socket.io-client'

export default {
  name: 'requests',
  data: () => {
    return {
      socket: null,
    }
  },
  computed: {},

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
          this.startListening()
          this.startQueue()
        })
    },

    startListening () {
      const requestId = this.queue.requestId
      this.socket = io(`0.0.0.0:5000/${requestId}`)
      console.log(`Listening on queue namespace: /${requestId}`)

      this.socket.on(this.queue.eventKeys['FETCH:NODE:QUEUED'], (res) => {
        this.$store.dispatch('addOneTo', 'numNodesQueued')
        console.log('FETCH:NODE:QUEUED', res)
      })

      this.socket.on(this.queue.eventKeys['FETCH:NODE:IN_PROGRESS'], (res) => {
        this.$store.dispatch('addOneTo', 'numNodesInProgress')
        console.log('FETCH:NODE:IN_PROGRESS', res)
      })

      this.socket.on(this.queue.eventKeys['FETCH:NODE:COMPLETED'], (res) => {
        let node

        if (typeof res === 'object') {
          node = JSON.parse(JSON.stringify(res))
        } else {
          node = JSON.parse(res)
        }

        this.$store.dispatch('addNode', node)
        console.log('FETCH:NODE:COMPLETED', res)
      })

      this.socket.on(this.queue.eventKeys['STORE:LINK:COMPLETED'], (res) => {
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
      const requestId = this.queue.requestId
      console.log(`Starting queue: ${requestId}`)
      const path = `${this.apiHost}/api/queue/${requestId}/start`
      return axios.post(path)
    },

    stopQueue () {
      const requestId = this.queue.requestId
      console.log(`Stopping queue: ${requestId}`)
      const path = `${this.apiHost}/api/queue/${requestId}/stop`
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
