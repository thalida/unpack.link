<template>
  <div class="home">
    <router-link to="/about">About</router-link>
    <RequestForm :url="url" />
  </div>
</template>

<script>
import RequestForm from '@/components/RequestForm.vue'

export default {
  name: 'home',
  components: { RequestForm },
  data: () => {
    return {
      'url': null,
    }
  },
  methods: {},
}
</script>

<style lang="scss"></style>
