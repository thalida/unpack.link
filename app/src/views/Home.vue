<template>
  <div class="home">
    <UrlInput :url="url" />
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
  width: 50%;
  margin: 0 auto;
}
</style>
