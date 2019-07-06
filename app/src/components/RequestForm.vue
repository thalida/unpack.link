<template>
    <form id="input-form" @submit.prevent="onFormSubmit">
    <router-link to="/">Home</router-link>
    <router-link to="/about">About</router-link>
    <input
        v-model="inputUrl"
        type="url"
        placeholder="http://"
        required />
    <button type="submit">unpack</button>
    </form>
</template>

<script>
export default {
  name: 'RequestForm',
  props: {
    'url': String,
  },
  data () {
    return {
      inputUrl: this.url,
    }
  },
  methods: {
    onFormSubmit (e) {
      this.$router.push({
        name: 'results',
        query: {
          url: this.inputUrl,
        },
      })
    }
  }
}
</script>

<style lang="scss"></style>
