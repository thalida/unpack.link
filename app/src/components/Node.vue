<template>
    <div
      class="node"
      :class="[
        (renderCheckmark) ? 'node--with-checkmark' : ''
      ]">
      <div
        class="node__checkbox"
        v-if="renderCheckmark">
        <input
          :id="checkboxID"
          :name="checkboxID"
          class="node__checkbox__input"
          v-model="isSelected"
          type="checkbox"
          />
        <label
          class="node__checkbox__label"
          :for="checkboxID">
        </label>
      </div>

      <div class="node__wrapper">
        <Links
          v-if="renderLinks"
          direction="inbound"
          :node-uuid="nodeUuid" />

        <div
          class="node__details"
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
    'renderCheckmark': Boolean,
  },
  components: { Tweet, Links },
  computed: {
    node () {
      return this.$store.getters.getNodeByUUID(this.nodeUuid, true)
    },
    nodeUrl () {
      return this.node.node_url
    },
    checkboxID () {
      return `${this.node.node_uuid}-checkbox`
    },
    isSelected: {
      get () {
        return this.node.isSelected
      },
      set (value) {
        this.$store.commit('updateNode', {
          node_uuid: this.nodeUuid,
          isSelected: value
        })
      }
    },
    nodeHasDetails () {
      const hasDetails = (
        this.node !== null &&
        this.node.node_details !== null
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
      window.open(this.nodeUrl, '_blank')
    },
  },
}
</script>

<style lang="scss">
$checkboxDiameter: 32px;
$checkboxMargin: 8px;

.node {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  margin: 30px -8px;

  &__checkbox {
    position: relative;
    display: block;
    width: $checkboxDiameter;
    height: $checkboxDiameter;

    &__input {
      opacity: 0;
    }

    &__label {
      position: absolute;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      display: flex;
      justify-content: center;
      align-items: center;

      &:before {
        height: 100%;
        width: 100%;
        border: 1px solid white;
        border-radius: 50%;
      }

      &:after {
        height: 20%;
        width: 40%;
        margin-top: -5%;
        border-left: 1px solid white;
        border-bottom: 1px solid white;
        transform: rotate(-45deg);
      }

      &:before,
      &:after {
        content: "";
        display: block;
        position: absolute;
        opacity: 0.5;
        transition: all 300ms ease;
      }
    }

    &__input:checked + &__label:before {
      background-color: #2538FF;
      border: 1px solid #2538FF;
    }

    &__input:checked + &__label:after {
      border-left-width: 2px;
      border-bottom-width: 2px;
    }

    &__input:checked + &__label:before,
    &__input:checked + &__label:after {
      opacity: 1;
    }

    &__input:focus + &__label:before {
      outline: rgb(59, 153, 252) auto 5px;
    }
  }

  &__wrapper {
    display: flex;
    flex: 0 0 auto;
    flex-direction: row;
    align-items: center;

    width: 100%;
  }

  &__details {
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

  &--with-checkmark {
    justify-content: space-between;
    .node__wrapper {
      width: 90%
    }
  }

  .twitter-tweet {
    width: 100% !important;
  }
}
</style>
