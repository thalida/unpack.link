<template>
  <div class="home">
    <UrlForm :url="url" theme="fancy" />
  </div>
</template>

<script>
import UrlForm from '@/components/UrlForm.vue'

export default {
  name: 'home',
  components: { UrlForm },
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
