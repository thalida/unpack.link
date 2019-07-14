<template>
    <div v-if="links">
      <h2>{{level}}</h2>
      <Link
        v-for="(linkId, index) in links"
        :key="index"
        :link-id="linkId"
      />
    </div>
</template>

<script>
import Link from '@/components/Request/Link.vue'
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

<style lang="scss"></style>
