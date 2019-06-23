<template>
  <div class="fourOhFour">
      404
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';

@Component
export default class FourOhFour extends Vue {}
</script>

<style lang="scss">
.fourOhFour {
    background: purple;
}
</style>
