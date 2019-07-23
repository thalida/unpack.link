<template>
    <div class="node">
      <Links
        v-if="renderLinks"
        direction="inbound"
        :node-uuid="nodeUuid" />

      <div
        class="node__wrapper"
        v-on:click="handleClick"
        v-on:keyup.enter="handleClick"
        tabindex="0">

        <!-- TWEETS -->
        <div
          v-if="nodeType === 'twitter' && twitterData !== null"
          class="node__contents node__contents--twitter">
          <Tweet
            :id="twitterData.id_str"
            :options="{
              theme: 'dark',
              conversation: 'none',
              cards: 'default',
            }" />
          <p class="node__url node__url--tiny">{{nodeUrl}}</p>
        </div>

        <!-- MEDIA (IMAGES, GIFS, ETC) -->
        <div
          v-else-if="nodeType === 'media'"
          class="node__contents node__contents--media">
          <img :src="nodeUrl" class="node__img-embed" />
          <p class="node__url node__url--tiny">{{nodeUrl}}</p>
        </div>

        <!-- WEBSITE -->
        <div
          v-else-if="nodeType === 'website' && websiteMeta !== null"
          class="node__contents node__contents--website">
          <img
            v-if="websiteMeta.favicon"
            class="node__favicon"
            :src="websiteMeta.favicon"
            :alt="websiteMeta.favicon_alt" />
          <div class="node__text">
            <span
              v-if="websiteMeta.title"
              class="node__title">
              {{websiteMeta.title}}
            </span>
            <p
              v-if="websiteMeta.description"
              class="node__description">
              {{websiteMeta.description}}
            </p>
            <p class="node__url node__url--tiny">{{nodeUrl}}</p>
          </div>
        </div>

        <!-- GENERIC: Just show the url if we don't have any data -->
        <div
          v-else
          class="node__contents node__contents--generic">
          <p class="node__url node__url--title">{{nodeUrl}}</p>
        </div>
      </div>

      <Links
        v-if="renderLinks"
        direction="outbound"
        :node-uuid="nodeUuid" />
    </div>
</template>

<script>
import { Tweet } from 'vue-tweet-embed'
import Links from '@/components/Links.vue'
export default {
  name: 'Node',
  props: {
    'nodeUuid': String,
    'renderLinks': Boolean,
  },
  components: { Tweet, Links },
  computed: {
    node () {
      return this.$store.getters.getNodeByUUID(this.nodeUuid)
    },
    nodeUrl () {
      return (this.node) ? this.node.node_url : null
    },
    nodeHasDetails () {
      const hasDetails = (
        typeof this.node !== 'undefined' &&
        typeof this.node.node_details !== 'undefined'
      )

      if (!hasDetails) {
        return false
      }

      if (this.node.node_details.is_error) {
        return false
      }

      return true
    },
    nodeType () {
      if (!this.nodeHasDetails) {
        return null
      }
      return this.node.node_details.node_type
    },
    twitterData () {
      if (this.nodeType !== 'twitter' || !this.nodeHasDetails) {
        return null
      }

      return this.node.node_details.data
    },
    websiteMeta () {
      if (this.nodeType !== 'website' || !this.nodeHasDetails) {
        return null
      }

      const hasMeta = (
        typeof this.node.node_details.data !== 'undefined' &&
        typeof this.node.node_details.data.meta !== 'undefined'
      )

      if (!hasMeta) {
        return null
      }

      const meta = this.node.node_details.data.meta
      return Object.assign({}, meta, {
        favicon_alt: `${meta.title} favicon`
      })
    },
  },
  methods: {
    handleClick () {
      if (this.nodeType === 'twitter' && this.twitterData !== null) {
        return
      }

      window.open(this.nodeUrl, '_blank')
    }
  },
}
</script>

<style lang="scss">
.node {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  margin: 30px -8px;

  &__wrapper {
    width: 100%;
    flex: 0 0 auto;
  }

  &__contents {
    display: flex;
    align-content: center;
    flex-direction: row;
    width: 100%;
    padding: 20px;
    border: 1px solid #fff;
    cursor: pointer;

    &--twitter {
      flex-direction: column;
      align-items: center;
      padding-left: 30px;
      & > div {
        width: 100%;
        text-align: center;
      }
    }

    &--media {
      flex-direction: column;
      text-align: center;
    }
  }

  &__titlebar {
    display: flex;
    flex-flow: row nowrap;
    align-items: flex-start;
  }

  &__favicon {
    flex: 0 0 auto;
    width: 16px;
    height: 16px;
    margin-top: 2px;
    margin-right: 10px;
    overflow: hidden;
  }

  &__title {
    font-size: 18px;
    font-weight: bold;
  }

  &__description {
    font-size: 14px;
    margin: 8px 0;
  }

  &__url {
    &--tiny {
      font-size: 12px;
      opacity: 0.5;
    }

    &--title {
      font-size: 18px;
      font-weight: bold;

      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .twitter-tweet {
    width: 100% !important;
  }
}
</style>
