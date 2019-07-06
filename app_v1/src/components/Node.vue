<template>
  <div class="node">
    {{nodes[nodeUUID].node_url}}
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';

@Component
export default class Node extends Vue {
  @Prop() private nodeUUID!: any[];

  get nodes() {
    return this.$store.state.nodes;
  }
}
</script>

<style scoped lang="scss">
.node {
  padding: 0 10px;
}
</style>
