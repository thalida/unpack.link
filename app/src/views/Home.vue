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

  .form {
    position: relative;

    &:before {
      content: "";
      width: 100%;
      height: 100%;
      position: absolute;
      top: 8px;
      left: 8px;
      background: #2538FF;
      z-index: -1;
    }
  }
}
</style>
