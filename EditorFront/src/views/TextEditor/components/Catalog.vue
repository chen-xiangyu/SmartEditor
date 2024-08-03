<template>
  <div class="catalog">
    <h2 class="text-gray-400">我的文档</h2>
    <div class="button-container">
      <el-tooltip
        class="box-item"
        effect="dark"
        :content="'新建文档'"
        placement="top"
        hide-after="10"
      >
        <button class="menu-item" @click="props.showNewFile()">
          <svg class="remix">
            <use :xlink:href="`${remixiconUrl}#ri-sticky-note-add-line`" />
          </svg>
        </button>
      </el-tooltip>
    </div>

    <ul class="catalog__list">
      <li 
        v-for="(filename, index) in filenameList" 
        :key="index" 
        class="catalog__item" 
        :fid="filename.id"
      >
        <el-button
          text
          :class="{'catalog__button': true, 'catalog__button--active': filename.id === currentFileID}"
          @contextmenu.prevent="handleRightClick"
          @click="getCurrentFile(filename.id)"
        >
          {{ filename.name }}
        </el-button>

      </li>
    </ul>
  </div>
</template>


<script setup lang="ts" name="Catalog">
  import { onMounted, ref, reactive } from 'vue'
  import axios from "axios"
  import remixiconUrl from 'remixicon/fonts/remixicon.symbol.svg'

  const props = defineProps<{ 
    setCurrentContent: Function,
    showNewFile: Function,
    // currentFileID: number,
  }>()

  const filenameList = ref([])
  const currentFile = ref("")
  const currentFileID = ref(0)

  const getCatalog = async () => {
    try {
      console.log("catalog on mounted")
      const response = await axios.post(
        `/get-catalog/`,
      )
      let res = response.data
      console.log(res.answer)
      if (res.status){
        filenameList.value = res.filenameList
        currentFile.value = res.currentFile
        currentFileID.value = res.currentFileID
        props.setCurrentContent(res.currentFile, res.currentFileID)
      } else{
        console.log(res.error)
      }
      console.log('POST 请求成功：', response.data)
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
  }

  onMounted(() => {
    getCatalog()
  })

  const handleRightClick = () => {
    console.log("左键")
  }

  const getCurrentFile = async (id: number) => {
    try {
      const formData = new FormData()
      formData.append("id", id.toString())
      const response = await axios.post(
        `/get-current-file/`,
        formData,
      )
      let res = response.data
      console.log(res.answer)
      if (res.status){
        currentFile.value = res.content
        currentFileID.value = id
        props.setCurrentContent(res.content, id)
      } else{
        console.log(res.error)
      }
      console.log('POST 请求成功：', response.data)
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
  }

  defineExpose({
    getCatalog
  })
</script>

<style scoped lang="scss">
  .catalog {
    opacity: 0.75;
    border-radius: 0.5rem;
    padding: 0rem;
    // background: rgba(black, 0.1);
    height: 100%;
    overflow-y: auto; /* 添加滚动条 */
    width: 100%;

    &__list {
      list-style: none;
      // font-size: 18px;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: flex-start; /* 左对齐 */
      height:100%;
      width: 100%;
      margin: 0;
    }

    .catalog__item {
      width: 100%;
    }

    .catalog__button {
      display: block;
      width: 100%;
      white-space: normal; /* 允许换行 */
      text-align: left; /* 确保文本左对齐 */
      &:hover {
        opacity: 0.5;
        background-color: #0ff;
      }
    }
    .catalog__button--active {
      background-color: #cccccc; /* 当前文件背景颜色 */
    }
  }
  h2 {
    margin-top: 10px;
    margin-bottom: 15px;
    text-align: center;
    font-size: 2rem;
    font-family: 'KaiTi', sans-serif;
  }

  .catalog::-webkit-scrollbar {
    width: 10px;
  }

  .catalog::-webkit-scrollbar-thumb {
    background-color: #888; /* 滚动条的颜色 */
    border-radius: 10px;
    border: 2px solid transparent;
    background-clip: content-box; /* 修正滚动条颜色的边距 */
  }

  .catalog::-webkit-scrollbar-thumb:hover {
    background-color: #555; /* 滚动条悬停时的颜色 */
  }

  .catalog::-webkit-scrollbar-track {
    background-color: #E4DCC8; /* 滚动条轨道的颜色 */
    border-radius: 10px;
  }

  .button-container {
    display: flex;
    justify-content: center;
  }

  .menu-item {
    background: transparent;
    border: none;
    border-radius: 0.4rem;
    color: #333;
    cursor: pointer;
    height: 1.6rem;
    padding: 0.12rem;
    margin: 0 auto;
    width: 1.6rem;

    svg {
      fill: currentColor;
      height: 100%;
      width: 100%;
    }

    &.is-active,
    &:hover {
      background-color: #d6d6d6;
    }
  }
</style>