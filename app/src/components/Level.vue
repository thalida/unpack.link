<template>
  <div class="level">
    <Node
      v-for="(nodeUUID, index) in nodeUUIDs"
      :key="index"
      :nodeUUID="nodeUUID" />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import Node from '@/components/Node.vue';

@Component({
  components: {Node},
})
export default class Level extends Vue {
  @Prop() private nodeUUIDs!: any[];
}
</script>

<style scoped lang="scss">
.level {
  margin: 15px 0;
}
</style>
