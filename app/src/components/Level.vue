<template>
    <div v-if="level !== 0 && nodes" class="level">
      <h2 class="level__header">
        {{level}}° <span v-if="level === 1">away</span>
      </h2>
      <Node
        v-for="(nodeUUID, index) in nodes"
        :key="index"
        :node-uuid="nodeUUID"
        :render-links="renderLinks"
      />
    </div>
</template>

<script>
import Node from '@/components/Node.vue'
export default {
  name: 'Level',
  props: {
    'level': Number,
    'nodes': Array,
  },
  data () {
    return {
      renderLinks: true,
    }
  },
  components: { Node },
  computed: {},
  methods: {},
}
</script>

<style lang="scss">
.level {
  margin: 30px 0 60px;

  &__header {
    margin-bottom: 30px;
  }
}
</style>
