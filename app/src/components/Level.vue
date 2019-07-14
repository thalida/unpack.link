<template>
    <div v-if="links" class="level">
      <h2 class="level__header">
        {{level}}° <span v-if="level === 1">away</span>
      </h2>
      <Link
        v-for="(linkId, index) in links"
        :key="index"
        :link-id="linkId"
      />
    </div>
</template>

<script>
import Link from '@/components/Link.vue'
export default {
  name: 'Level',
  props: {
    'level': Number,
    'links': Array,
  },
  components: { Link },
  computed: {},
  methods: {},
}
</script>

<style lang="scss">
.level {
  margin: 30px 0 60px;

  &__header {
    margin-bottom: 30px;
  }
}
</style>
