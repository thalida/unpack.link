<template>
  <div class="link">
    <span :class="{'exists-already': link.data.is_already_in_path}">
      {{link.target.node_url}}
    </span>
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
.exists-already {
  text-decoration: line-through;
}
</style>
