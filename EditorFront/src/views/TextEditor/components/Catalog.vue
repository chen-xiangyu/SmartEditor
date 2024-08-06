<template>
  <div class="catalog">
    <h2 class="text-gray-400">我的文档</h2>
    <div class="button-container">
      <div>
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
        <el-tooltip
          class="box-item"
          effect="dark"
          :content="'排序'"
          placement="top"
          hide-after="10"
        >
          <button class="menu-item" @click="toggleSortOrder()">
            <svg class="remix">
              <use :xlink:href="`${remixiconUrl}#ri-sort-desc`" />
            </svg>
          </button>
        </el-tooltip>
        <el-tooltip
          class="box-item"
          effect="dark"
          :content="'搜索'"
          placement="top"
          hide-after="10"
        >
          <button class="menu-item">
            <svg class="remix">
              <use :xlink:href="`${remixiconUrl}#ri-search-line`" />
            </svg>
          </button>
        </el-tooltip>
      </div>
    </div>

    <ul class="catalog__list">
      <li 
        v-for="(filename, index) in filenameList" 
        :key="index" 
        class="catalog__item" 
        :fid="filename.id"
      >
        <el-tooltip        
          class="box-item"
          effect="dark"
          placement="right"
          hide-after="10"
        >
          <template #content>
            最后修改于 {{ filename.last_modified }}<br /> 
            创建于 {{ filename.created_time }} <br />
            <template v-if="filename.is_shared">
              正在与：
              {{ filename.shared_with.slice(0, 3).join(', ') }}
              <span v-if="filename.shared_with.length > 3">...</span>
              共享
            </template>
          </template>
          <el-button
            text
            :class="{'catalog__button': true, 'catalog__button--active': filename.id === currentFileID}"
            @contextmenu.prevent="showDropdown($event, filename.id)"
            @click="getCurrentFile(filename.id)"
          >
            {{ filename.name }}
            <template v-if="filename.is_shared">
              <svg class="remix share-icon">
                <use :xlink:href="`${remixiconUrl}#ri-team-line`" />
              </svg>
            </template>
            <!-- <div class="button-content">
              <span>{{ filename.name }}</span>
              <template v-if="filename.is_shared">
                <svg class="remix share-icon">
                  <use :xlink:href="`${remixiconUrl}#ri-team-line`" />
                </svg>
              </template>
            </div> -->
          </el-button>
        </el-tooltip>
      </li>
    </ul>

    <ul 
      @mousedown="seeDropdown()" 
      ref="dropdownRef"
      v-show="visibleDropdown" 
      :style="{ 
        left: position.left + 'px', 
        top: position.top + 'px', 
        display: (visibleDropdown ? 'grid' : 'none') 
      }" 
      class="context-dropdown"
    >
      <div class="item" @mousedown="props.showRenameFile(getFileNameById(rightClickFileID), rightClickFileID)">
        <span class="item-text">重命名</span>
      </div>
      <div class="item" @mousedown="props.showDeleteFile(rightClickFileID)">
        <span class="item-text">删除</span>
      </div>
      <div class="item" @mousedown="props.showShareFile(rightClickFileID)">
        <span class="item-text">共享</span>
      </div>
      <!-- <div v-for="(value, key) in dropdownList" :key="key" class="item" @mousedown="value.action()">
        <span class="item-text">{{ value.name }}</span>
      </div> -->
    </ul>
  </div>
</template>

<script setup lang="ts" name="Catalog">
  import { onMounted, ref } from 'vue'
  import axios from "axios"
  import remixiconUrl from 'remixicon/fonts/remixicon.symbol.svg'

  const props = defineProps<{ 
    setCurrentContent: Function,
    showNewFile: Function,
    showRenameFile: Function,
    showDeleteFile: Function,
    showShareFile: Function,
  }>()

  const filenameList = ref([])
  const isAscending = ref(true)
  const currentFile = ref("")
  const currentFileID = ref(0)
  const rightClickFileID = ref(0)
  // const dropdownList = reactive({
  //   "rename": {name: "重命名", action: props.showRenameFile},
  //   "delete": {name: "删除", action: ()=>{}},
  //   "share": {name: "共享", action: ()=>{}},
  // })
  const getFileNameById = (id) => {
    const file = filenameList.value.find(file => file.id === id);
    return file ? file.name : null;
  };
  const getCatalog = async () => {
    try {
      console.log("catalog on mounted")
      const response = await axios.post(`/get-catalog/`)
      let res = response.data
      console.log(res)
      if (res.status) {
        filenameList.value = res.filenameList
        sortFilenameList()
        currentFile.value = res.currentFile
        currentFileID.value = res.currentFileID
        props.setCurrentContent(res.currentFile, res.currentFileID)
      } else {
        console.log(res.error)
      }
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
  }

  onMounted(() => {
    getCatalog()
  })

  const getCurrentFile = async (id: number) => {
    try {
      const formData = new FormData()
      formData.append("id", id.toString())
      const response = await axios.post(`/get-current-file/`, formData)
      let res = response.data
      if (res.status) {
        currentFile.value = res.content
        currentFileID.value = id
        props.setCurrentContent(res.content, id)
      } else {
        console.log(res.error)
      }
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
  }

  const showDropdown = (event, id: number) => {
    rightClickFileID.value = id
    console.log(id)
    position.value.top =  event.clientY - 40
    position.value.left = window.innerWidth * 0.05
    visibleDropdown.value = true
  }

  const position = ref({
    top: 0,
    left: 0
  })
  const dropdownRef = ref(null)
  const visibleDropdown = ref(false)
  const seeDropdown = () => {
    visibleDropdown.value = true
  }
  const closeDropdown = () => {
    visibleDropdown.value = false
  }

  const checkIfFileIsShared = (id: number) => {
    console.log("come check")
    const file = filenameList.value.find(file => file.id === id)
    return file ? file.is_shared : false
  }

  const sortFilenameList = () => {
    filenameList.value = filenameList.value.slice().sort((a, b) => {
      return isAscending.value ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name);
    });
  };

  const toggleSortOrder = () => {
    isAscending.value = !isAscending.value;
    sortFilenameList();
  };

  defineExpose({
    getCatalog,
    closeDropdown,
    checkIfFileIsShared,
    getCurrentFile,
  })
</script>

<style scoped lang="scss">
  .catalog {
    opacity: 0.75;
    border-radius: 0.5rem;
    padding: 0rem;
    height: 100%;
    overflow-y: auto;
    width: 100%;

    &__list {
      list-style: none;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      height: 100%;
      width: 100%;
      margin: 0;
    }

    .catalog__item {
      width: 100%;
    }

    .catalog__button {
      display: block;
      width: 100%;
      white-space: normal;
      text-align: left;
      position: relative;
      &:hover {
        // opacity: 0.1;
        background-color: #D9D9D9 !important;
        // background: #0ff;
      }

      .share-icon {
      width: 1rem;
      height: 1rem;
      fill: #1592FF;
      position: fixed; /* 设置图标为固定定位 */
      left: 15%; /* 设置图标靠右对齐 */
    }
    }
    .catalog__button--active {
      background-color: #D9D9D9;
    }
  }
  h2 {
    margin-top: 10px;
    margin-bottom: 10px;
    text-align: center;
    font-size: 1.5rem;
    font-family: 'KaiTi', sans-serif;
  }

  .catalog::-webkit-scrollbar {
    width: 10px;
  }

  .catalog::-webkit-scrollbar-thumb {
    background-color: #D2D2D3;
    border-radius: 10px;
    border: 2px solid transparent;
    background-clip: content-box;
  }

  .catalog::-webkit-scrollbar-thumb:hover {
    background-color: #BBBBBC;
  }

  .catalog::-webkit-scrollbar-track {
    background-color: #EAEAEB;
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
    margin: 0 5px;
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

  .context-dropdown {
    width: 90px; /* 调整宽度以适应一列布局 */
    margin: 0;
    background-color: #F3F5F7;
    z-index: 1200;
    position: absolute;
    list-style-type: none;
    padding: 0px; /* 调整填充 */
    border-radius: 6px; /* 增加圆角 */
    border: 1px solid #D4D4D4;
    font-size: 16px;
    font-weight: 400;
    color: #333;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 优化阴影 */
    display: grid;
    grid-template-columns: 1fr; /* 一列布局 */
    gap: 0px; /* 增加项之间的间距 */
  }

  .context-dropdown .item {
    height: 35px; /* 增加高度 */
    display: flex; /* 使用弹性布局 */
    align-items: center; /* 垂直居中 */
    padding: 0; /* 增加内边距 */
    margin: 0;
    color: #D9D9D9;
    cursor: pointer;
    border-radius: 5px; /* 增加圆角 */
    background-color: #EAEAEB; /* 添加背景色 */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 添加阴影 */
  }

  .context-dropdown .item-text {
    flex: 1; /* 占据剩余空间，使文本左对齐 */
    text-align: center; /* 确保文本左对齐 */
    font-size: 0.9rem;
    color: #333;
  }

  .context-dropdown .item:hover {
    background: rgb(205, 206, 210);
  }
</style>
