<template>
  <form class="form" @submit.prevent="onFormSubmit">
    <input
        class="form__input"
        v-model="inputUrl"
        type="url"
        placeholder="http://"
        required />
    <button class="form__button" type="submit">
      <svg width="18px" height="11px" viewBox="0 0 18 11" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
          <g id="Try-#3---Cleaned---Outside-Checkmark" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
              <g id="Results" transform="translate(-299.000000, -48.000000)" fill="#FFFFFF" fill-rule="nonzero" stroke="#FFFFFF">
                  <g id="small-input" transform="translate(32.000000, 30.000000)">
                      <g id="input">
                          <path d="M283.905337,23.4803765 L279.42496,19 L278.970522,19.4544382 L282.906853,23.3843684 L268,23.3843684 L268,24.0244222 L282.906853,24.0244222 L278.970522,27.960753 L279.42496,28.4151912 L283.905337,23.9348147 C283.965922,23.8747243 284,23.7929268 284,23.7075956 C284,23.6222644 283.965922,23.5404669 283.905337,23.4803765 Z" id="Path"></path>
                      </g>
                  </g>
              </g>
          </g>
      </svg>
    </button>
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
        name: 'request',
        query: {
          url: this.inputUrl,
        },
      })
    }
  }
}
</script>

<style lang="scss">
.form {
  height: 48px;
  margin: 30px 0;
  border: 1px solid white;

  &__input {
    width: calc(100% - 32px);
    height: 48px;
    padding: 15px;
    border: 0;
    background: transparent;
    color: #fff;
    font: 16px/1.5 'Share', 'Arial', 'serif';
  }

  &__button {
    height: 48px;
    width: 32px;
    background: transparent;
    border: 0;
  }
}
</style>
