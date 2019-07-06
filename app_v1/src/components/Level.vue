<template>
  <div class="level">
    <Link
      v-for="(link, index) in links"
      :key="index"
      :link="link" />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import Link from '@/components/Link.vue';

@Component({
  components: {Link},
})
export default class Level extends Vue {
  @Prop() private links!: any[];
}
</script>

<style scoped lang="scss">
.level {
  margin: 15px 0;
}
</style>
