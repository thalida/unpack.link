<template>
    <div class="node">
      <!-- Twitter -->
      <div
        v-if="nodeType === 'twitter'"
        class="node__wrapper">
        <!-- Has tweet data -->
        <div
          v-if="twitterData !== null"
          class="node__contents node__contents--twitter">
          <Tweet
            :id="twitterData.id_str"
            :options="{
              theme: 'dark',
              conversation: 'none',
              cards: 'default',
            }" />
          <p class="node__url">{{nodeUrl}}</p>
        </div>
        <!-- Does NOT have tweet data -->
        <div
          v-else
          class="node__contents node__contents--twitter">
          <p class="node__url node__url--large">{{nodeUrl}}</p>
        </div>
      </div>

      <!-- Media/Image -->
      <div
        v-else-if="nodeType === 'media'"
        class="node__contents node__contents--media"
        v-on:click="handleClick"
        v-on:keyup.enter="handleClick"
        tabindex="0">
        <img :src="nodeUrl" class="node__img-embed" />
        <p class="node__url">{{nodeUrl}}</p>
      </div>

      <!-- Website -->
      <div
        v-else
        class="node__wrapper"
        v-on:click="handleClick"
        v-on:keyup.enter="handleClick"
        tabindex="0">
        <!-- Has meta data -->
        <div
          v-if="websiteMeta !== null"
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
            <p class="node__url node__url--inline">{{nodeUrl}}</p>
          </div>
        </div>
        <!-- Does NOT have meta data -->
        <div
          v-else
          class="node__contents node__contents--website">
          <p class="node__url node__url--large">{{nodeUrl}}</p>
        </div>
      </div>
    </div>
</template>

<script>
import { Tweet } from 'vue-tweet-embed'
export default {
  name: 'Node',
  props: {
    'nodeUuid': String,
    'nodeUrl': String,
  },
  components: { Tweet },
  computed: {
    node () {
      return this.$store.getters.getNodeByUUID(this.nodeUuid)
    },
    nodeType () {
      if (typeof this.node === 'undefined') {
        return null
      }
      return this.node.node_details.node_type
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
      window.open(this.nodeUrl, '_blank')
    }
  },
}
</script>

<style lang="scss">
.node {
  display: flex;
  flex: 0 0 auto;
  width: 100%;

  &__wrapper {
    width: 100%;
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
    font-size: 12px;
    opacity: 0.5;

    &--large {
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
