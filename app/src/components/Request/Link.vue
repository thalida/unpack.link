<template>
    <div>
      <img v-if="favicon" :src="favicon" />
      {{link.target_node_url}}
      <hr />
    </div>
</template>

<script>
export default {
  name: 'Link',
  props: {
    'linkId': String,
  },
  computed: {
    link () {
      return this.$store.state.links[this.linkId]
    },
    sourceNodeUUID () {
      return this.link.source_node_uuid
    },
    targeNodeUUID () {
      return this.link.target_node_uuid
    },
    sourceNode () {
      return this.$store.getters.getNodeByUUID(this.sourceNodeUUID)
    },
    targetNode () {
      return this.$store.getters.getNodeByUUID(this.targeNodeUUID)
    },
    favicon () {
      if (
        typeof this.targetNode === 'undefined'
        || typeof this.targetNode.node_details === 'undefined'
        || typeof this.targetNode.node_details.data === 'undefined'
        || typeof this.targetNode.node_details.data.meta === 'undefined'
        ) {
          return
        }

      return this.targetNode.node_details.data.meta.favicon
    },
  },
  methods: {},
}
</script>

<style lang="scss"></style>
