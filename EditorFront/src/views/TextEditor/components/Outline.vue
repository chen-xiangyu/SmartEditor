<template>
  <div class="outline">
    <h2 class="text-gray-400">大纲</h2>
    <ul class="outline__list">
      <li v-for="(heading, index) in headings" :key="index" :class="`outline__item outline__item--${heading.level}`">
        <el-popover
          trigger="click"
          placement="right"
        >
          <template #reference>
            <el-button
              @click="handleHeadingClick(heading.text)"
              text
              class="outline__button"
            >
              {{ heading.text }}
              <el-icon v-if="heading.icon"><component :is="heading.icon"/></el-icon>
            </el-button>
          </template>
          <!-- 如果需要弹出内容，请在这里添加 -->
        </el-popover>
      </li>
    </ul>
  </div>
</template>


<script setup lang="ts" name="Outline">
  // import { h, ref, type Component } from 'vue'

  // import { useEditorStore } from '@/store'
  import { useEditorStore } from '../../../store'
  import { storeToRefs } from 'pinia'

  const editorStore = useEditorStore()
  const { headings } = storeToRefs(editorStore)
  /**
   * 左侧区域
   */
  const handleHeadingClick = (data: any) => {
    editorStore.setActiveHeading(data)
  }
</script>

<style scoped lang="scss">
  .outline {
    opacity: 0.75;
    border-radius: 0.5rem;
    padding: 0rem;
    // background: rgba(black, 0.1);
    height: 100%;
    overflow-y: auto; /* 添加滚动条 */

    &__list {
      list-style: none;
      // font-size: 18px;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: flex-start; /* 左对齐 */
      height:100%;
    }


    &__item {
      // width: 100%;

      &:hover {
        opacity: 0.5;
      }
      &--1 {
        padding-left: 0.5rem;
        font-size: 23px;
      }
      &--2 {
        padding-left: 1.5rem;
      }

      &--3 {
        padding-left: 2.5rem;
      }

      &--4 {
        padding-left: 3.5rem;
      }

      &--5 {
        padding-left: 4.5rem;
      }
    }

    .outline__button {
      display: block;
      width: 100%;
      white-space: normal; /* 允许换行 */
      text-align: left; /* 确保文本左对齐 */
    }
  }
  h2 {
    margin-top: 10px;
    margin-bottom: 15px;
    text-align: center;
    font-size: 2rem;
    font-family: 'KaiTi', sans-serif;
  }

  .outline::-webkit-scrollbar {
    width: 10px;
  }

  .outline::-webkit-scrollbar-thumb {
    background-color: #888; /* 滚动条的颜色 */
    border-radius: 10px;
    border: 2px solid transparent;
    background-clip: content-box; /* 修正滚动条颜色的边距 */
  }

  .outline::-webkit-scrollbar-thumb:hover {
    background-color: #555; /* 滚动条悬停时的颜色 */
  }

  .outline::-webkit-scrollbar-track {
    background-color: #E4DCC8; /* 滚动条轨道的颜色 */
    border-radius: 10px;
  }
</style>