<template>
    <div class="link">
      <div
        v-if="nodeType === 'twitter'"
        class="link__contents link__contents--twitter">
        <Tweet
          :id="twitterData.id_str"
          :options="{
            theme: 'dark',
            conversation: 'none',
            cards: 'default',
          }" />
        <p class="link__url">{{targetNodeUrl}}</p>
      </div>
      <div
        v-else-if="nodeType === 'media'"
        class="link__contents link__contents--media"
        v-on:click="handleClick"
        v-on:keyup.enter="handleClick"
        tabindex="0">
        <img v-if="targetNodeUrl" :src="targetNodeUrl" class="link__img-embed" />
        <p class="link__url">{{targetNodeUrl}}</p>
      </div>
      <div
        v-else
        class="link__contents link__contents--website"
        v-on:click="handleClick"
        v-on:keyup.enter="handleClick"
        tabindex="0">
        <div class="link__titlebar">
          <img
            v-if="websiteMeta.favicon"
            class="link__favicon"
            :src="websiteMeta.favicon"
            :alt="websiteMeta.favicon_alt" />
          <span
            v-if="websiteMeta.title"
            class="link__title">
            {{websiteMeta.title}}
          </span>
        </div>
        <p class="link__url">{{targetNodeUrl}}</p>
      </div>
      <div class="link__related link__related--to-node">
        <span class="link__related__count">{{totalLinksToTargetNode}}</span>
        <svg width="16px" height="16px" viewBox="0 0 16 16" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
            <g id="Symbols" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                <g id="site-card-outside-checkmark" transform="translate(-35.000000, -37.000000)" fill="#FFFFFF" fill-rule="nonzero">
                    <g id="site">
                        <g id="Group" transform="translate(31.000000, 0.000000)">
                            <g id="from" transform="translate(0.000000, 8.000000)">
                                <path d="M12.32,39.3744 L12.32,45 L11.68,45 L11.68,39.3744 L9.664,41.384 L9.2096,40.9296 L11.7696,38.3696 C11.8296853,38.30902 11.911476,38.2749445 11.9968,38.2749445 C12.082124,38.2749445 12.1639147,38.30902 12.224,38.3696 L14.784,40.9296 L14.3296,41.384 L12.32,39.3744 Z M20,30.28 L20,41.8 C20,42.5069245 19.4269245,43.08 18.72,43.08 L14.24,43.08 L14.24,42.44 L18.72,42.44 C19.0734622,42.44 19.36,42.1534622 19.36,41.8 L19.36,32.84 L4.64,32.84 L4.64,41.8 C4.64,42.1534622 4.92653776,42.44 5.28,42.44 L9.76,42.44 L9.76,43.08 L5.28,43.08 C4.57307552,43.08 4,42.5069245 4,41.8 L4,30.28 C4,29.5730755 4.57307552,29 5.28,29 L18.72,29 C19.4269245,29 20,29.5730755 20,30.28 Z M19.36,30.28 C19.36,29.9265378 19.0734622,29.64 18.72,29.64 L5.28,29.64 C4.92653776,29.64 4.64,29.9265378 4.64,30.28 L4.64,32.2 L19.36,32.2 L19.36,30.28 Z M6.24,30.28 L5.6,30.28 C5.42326888,30.28 5.28,30.4232689 5.28,30.6 L5.28,31.24 C5.28,31.4167311 5.42326888,31.56 5.6,31.56 L6.24,31.56 C6.41673112,31.56 6.56,31.4167311 6.56,31.24 L6.56,30.6 C6.56,30.4232689 6.41673112,30.28 6.24,30.28 Z M8.16,30.28 L7.52,30.28 C7.34326888,30.28 7.2,30.4232689 7.2,30.6 L7.2,31.24 C7.2,31.4167311 7.34326888,31.56 7.52,31.56 L8.16,31.56 C8.33673112,31.56 8.48,31.4167311 8.48,31.24 L8.48,30.6 C8.48,30.4232689 8.33673112,30.28 8.16,30.28 Z M10.08,30.28 L9.44,30.28 C9.26326888,30.28 9.12,30.4232689 9.12,30.6 L9.12,31.24 C9.12,31.4167311 9.26326888,31.56 9.44,31.56 L10.08,31.56 C10.2567311,31.56 10.4,31.4167311 10.4,31.24 L10.4,30.6 C10.4,30.4232689 10.2567311,30.28 10.08,30.28 Z" id="Shape"></path>
                            </g>
                        </g>
                    </g>
                </g>
            </g>
        </svg>
      </div>
      <div class="link__related link__related--from-node">
        <span class="link__related__count">{{totalLinksFromTargetNode}}</span>
        <svg width="16px" height="17px" viewBox="0 0 16 17" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
            <g id="Symbols" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                <g id="site-card-outside-checkmark" transform="translate(-280.000000, -37.000000)" fill="#FFFFFF" fill-rule="nonzero">
                    <g id="site">
                        <g id="Group" transform="translate(31.000000, 0.000000)">
                            <g id="to" transform="translate(245.000000, 8.000000)">
                                <path d="M14.336,42.216 L14.7904,42.6704 L12.2304,45.2304 C12.1703147,45.29098 12.088524,45.3250555 12.0032,45.3250555 C11.917876,45.3250555 11.8360853,45.29098 11.776,45.2304 L9.216,42.6704 L9.6704,42.216 L11.68,44.2256 L11.68,38.6 L12.32,38.6 L12.32,44.2256 L14.336,42.216 Z M20,30.28 L20,41.8 C20,42.5069245 19.4269245,43.08 18.72,43.08 L16.16,43.08 L16.16,42.44 L18.72,42.44 C19.0734622,42.44 19.36,42.1534622 19.36,41.8 L19.36,32.84 L4.64,32.84 L4.64,41.8 C4.64,42.1534622 4.92653776,42.44 5.28,42.44 L7.84,42.44 L7.84,43.08 L5.28,43.08 C4.57307552,43.08 4,42.5069245 4,41.8 L4,30.28 C4,29.5730755 4.57307552,29 5.28,29 L18.72,29 C19.4269245,29 20,29.5730755 20,30.28 Z M19.36,30.28 C19.36,29.9265378 19.0734622,29.64 18.72,29.64 L5.28,29.64 C4.92653776,29.64 4.64,29.9265378 4.64,30.28 L4.64,32.2 L19.36,32.2 L19.36,30.28 Z M6.24,30.28 L5.6,30.28 C5.42326888,30.28 5.28,30.4232689 5.28,30.6 L5.28,31.24 C5.28,31.4167311 5.42326888,31.56 5.6,31.56 L6.24,31.56 C6.41673112,31.56 6.56,31.4167311 6.56,31.24 L6.56,30.6 C6.56,30.4232689 6.41673112,30.28 6.24,30.28 Z M8.16,30.28 L7.52,30.28 C7.34326888,30.28 7.2,30.4232689 7.2,30.6 L7.2,31.24 C7.2,31.4167311 7.34326888,31.56 7.52,31.56 L8.16,31.56 C8.33673112,31.56 8.48,31.4167311 8.48,31.24 L8.48,30.6 C8.48,30.4232689 8.33673112,30.28 8.16,30.28 Z M10.08,30.28 L9.44,30.28 C9.26326888,30.28 9.12,30.4232689 9.12,30.6 L9.12,31.24 C9.12,31.4167311 9.26326888,31.56 9.44,31.56 L10.08,31.56 C10.2567311,31.56 10.4,31.4167311 10.4,31.24 L10.4,30.6 C10.4,30.4232689 10.2567311,30.28 10.08,30.28 Z" id="Shape"></path>
                            </g>
                        </g>
                    </g>
                </g>
            </g>
        </svg>
      </div>
    </div>
</template>

<script>
import { Tweet } from 'vue-tweet-embed'
export default {
  name: 'Link',
  props: {
    'linkId': String,
  },
  components: { Tweet },
  computed: {
    link () {
      return this.$store.state.links[this.linkId]
    },
    targeNodeUUID () {
      return this.link.target_node_uuid
    },
    targetNodeUrl () {
      return this.link.target_node_url
    },
    targetNode () {
      return this.$store.getters.getNodeByUUID(this.targeNodeUUID)
    },
    nodeType () {
      if (typeof this.targetNode === 'undefined') {
        return null
      }
      return this.targetNode.node_details.node_type
    },
    nodeHasDetails () {
      const hasDetails = (
        typeof this.targetNode !== 'undefined' &&
        typeof this.targetNode.node_details !== 'undefined'
      )

      if (!hasDetails) {
        return false
      }

      if (this.targetNode.node_details.is_error) {
        return false
      }

      return true
    },
    twitterData () {
      if (this.nodeType !== 'twitter' || !this.nodeHasDetails) {
        return {}
      }

      return this.targetNode.node_details.data
    },
    websiteMeta () {
      if (this.nodeType !== 'website' || !this.nodeHasDetails) {
        return {}
      }

      const hasMeta = (
        typeof this.targetNode.node_details.data !== 'undefined' &&
        typeof this.targetNode.node_details.data.meta !== 'undefined'
      )

      if (!hasMeta) {
        return {}
      }

      const meta = this.targetNode.node_details.data.meta

      return Object.assign({}, meta, {
        favicon_alt: `${meta.title} favicon`
      })
    },
    linksToTargetNode () {
      return this.$store.getters.getLinksByTargetUUID(this.targeNodeUUID)
    },
    totalLinksToTargetNode () {
      return this.linksToTargetNode.length
    },
    linksFromTargetNode () {
      return this.$store.getters.getLinksBySourceUUID(this.targeNodeUUID)
    },
    totalLinksFromTargetNode () {
      return this.linksFromTargetNode.length
    },
  },
  methods: {
    handleClick () {
      window.open(this.targetNodeUrl, '_blank')
    }
  },
}
</script>

<style lang="scss">
.link {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  margin: 30px 0;

  &__contents {
    display: flex;
    align-content: center;
    flex-direction: column;
    width: 100%;
    padding: 15px 30px;
    border: 1px solid #fff;
    cursor: pointer;

    &--twitter {
      align-items: center;
      & > div {
        width: 100%;
      }
    }
  }

  &__titlebar {
    display: flex;
    align-items: center;
  }

  &__favicon {
    width: 16px;
    height: 16px;
    margin-right: 4px;
    overflow: hidden;
  }

  &__title {}

  &__img-embed {
    flex: 0 1 auto;
    align-self: flex-start;
  }

  &__url {
    font-size: 12px;
    opacity: 0.5;
  }

  &__related {
    z-index: 1;
    width: 16px;
    background-color: #000;
    line-height: 1;
    text-align: center;
    font-size: 14px;

    &__count {
      display: block;
      padding: 8px 0;
    }

    &--to-node {
      order: -1;
      margin-right: -8px;
    }

    &--from-node {
      order: 1;
      margin-left: -8px;
    }
  }

  .twitter-tweet {
    width: 100% !important;
  }
}
</style>
