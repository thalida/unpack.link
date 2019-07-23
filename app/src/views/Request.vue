<template>
 <div class="request" v-if="!isLoading">
    <UrlForm :url="requestedUrl" />
    <Node
      v-if="request.node.node_uuid"
      :node-uuid="request.node.node_uuid"
      :render-links="renderLinks"
      />
    <p class="request__stats">
      found <span class="request__stats__number">{{nodeStats.queued}}</span> sites
    </p>
    <Level
      v-for="(nodes, level) in nodesByLevel"
      :key="level"
      :level="level"
      :nodes="nodes"
      />
  </div>
</template>

<script>
import { mapState } from 'vuex'
import axios from 'axios'
import io from 'socket.io-client'

import UrlForm from '@/components/UrlForm.vue'
import Node from '@/components/Node.vue'
import Level from '@/components/Level.vue'

export default {
  name: 'request',
  props: ['url'],
  components: { UrlForm, Node, Level },
  data: () => {
    return {
      isLoading: true,
      socket: null,
      request: {
        node: {
          node_uuid: null,
          node_url: null,
        },
        status: null,
      },
      renderLinks: true,
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
      nodesByLevel: 'nodesByLevel',
    }),
  },

  created () {
    this.$store.commit('resetResultsData')
    this.createQueue()
    window.addEventListener('unload', this.breakdown)
    this.isLoading = false
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
          this.request = Object.assign({}, {
            eventKeys: response.data.event_keys,
            requestId: response.data.request_id,
            node: {
              node_uuid: response.data.node_uuid,
              node_url: response.data.node_url,
            }
          })

          this.$store.commit('updateNode', {
            node_uuid: this.request.node.node_uuid,
            node_url: this.request.node.node_url,
            node_type: 'origin',
            status: 'queued',
          })

          this.$store.commit('addNodeToLevel', {
            node: this.request.node,
            level: 0
          })

          this.startListening()
          this.startQueue()
        })
    },

    startListening () {
      // console.log(`Listening on queue namespace: /${this.request.requestId}`)
      const requestId = this.request.requestId
      this.socket = io(`0.0.0.0:5000/${requestId}`)
      this.request.status = 'listening'

      this.socket.on(this.request.eventKeys['REQUEST:QUEUED'], (res) => {
        // console.log('REQUEST:QUEUED', res)
        this.request.status = 'queued'
      })

      this.socket.on(this.request.eventKeys['REQUEST:IN_PROGRESS'], (res) => {
        // console.log('REQUEST:IN_PROGRESS', res)
        this.request.status = 'running'
      })

      this.socket.on(this.request.eventKeys['REQUEST:COMPLETED'], (res) => {
        // console.log('REQUEST:COMPLETED', res)
        this.request.status = 'completed'
      })

      // this.socket.on(this.request.eventKeys['REQUEST:HEARTBEAT'], (res) => {
      //   console.log('REQUEST:HEARTBEAT', res)
      // })

      this.socket.on(this.request.eventKeys['NODE:QUEUED'], (res) => {
        // console.log('NODE:QUEUED', res)
        let node = res
        node.status = 'queued'
        this.$store.commit('updateNode', node)
      })

      this.socket.on(this.request.eventKeys['NODE:IN_PROGRESS'], (res) => {
        // console.log('NODE:IN_PROGRESS', res)
        let node = res
        node.status = 'running'
        this.$store.commit('updateNode', node)
      })

      this.socket.on(this.request.eventKeys['NODE:COMPLETED'], (res) => {
        // console.log('NODE:COMPLETED', res)
        let node = res
        node.status = 'fetched'
        this.$store.commit('updateNode', node)
      })

      this.socket.on(this.request.eventKeys['LINK:COMPLETED'], (res) => {
        // console.log('LINK:COMPLETED', res)

        const link = res
        const sourceNode = {
          node_uuid: res.source_node_uuid,
          node_url: res.source_node_url,
        }
        const targetNode = {
          node_uuid: res.target_node_uuid,
          node_url: res.target_node_url,
        }

        this.$store.commit('addLink', link)
        this.$store.commit('updateNode', sourceNode)
        this.$store.commit('updateNode', targetNode)
        this.$store.commit('addNodeToLevel', {
          node: targetNode,
          level: link.level
        })
      })
    },

    startQueue () {
      // console.log(`Starting queue: ${this.request.requestId}`)
      const requestId = this.request.requestId
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
        typeof this.request === 'undefined' ||
        this.request === null ||
        typeof this.request.requestId === 'undefined' ||
        this.request.requestId === null
      ) {
        return
      }

      // console.log(`Stopping queue: ${this.request.requestId}`)
      const requestId = this.request.requestId
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
