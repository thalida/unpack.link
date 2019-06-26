<template>
  <div class="link">
    {{link}}
    <!-- {{nodes[nodeUUID].node_url}} -->
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';

@Component
export default class Link extends Vue {
  @Prop() private link!: any[];

  // get nodes() {
  //   return this.$store.state.nodes;
  // }
}
</script>

<style scoped lang="scss">
.link {
  padding: 0 10px;
}
</style>
