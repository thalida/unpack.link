<template>
  <div class="home">
    <UrlInput :url="url" theme="fancy" />
  </div>
</template>

<script>
import UrlInput from '@/components/UrlInput.vue'

export default {
  name: 'home',
  components: { UrlInput },
  data: () => {
    return {
      'url': null,
    }
  },
  methods: {},
}
</script>

<style lang="scss">
.home {
  width: 80%;
  max-width: 600px;
  min-width: 300px;
  margin: 0 auto;
}
</style>
