<template>
  <div class="home">
    <form id="input-form" @submit.prevent>
      <input
        v-model="url"
        type="url"
        placeholder="http://"
        required />
      <button type="submit" @click="handleSubmit">unpack</button>
    </form>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';

@Component
export default class Home extends Vue {
  url: string | null = null;

  handleSubmit() {
    this.$router.push({
      name: 'map',
      query: {
        url: this.url as string,
      },
    });
  }
}
</script>

<style lang="scss"></style>
