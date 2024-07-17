<template>
  <el-container 
    style="height: 100vh; display: flex; flex-direction: column;" 
    ref="fileContRef" 
    @mousedown="notSee($event)" 
  >
    <ul 
      @mousedown="seeMenu()" 
      ref="menuRef"
      v-show="visibleMenu" 
      :style="{ 
        left: position.left + 'px', 
        top: position.top + 'px', 
        display: (visibleMenu ? 'grid' : 'none') 
      }" 
      class="context-menu"
    >
      <div v-for="(value, key) in AIList" :key="key" class="item"  @mousedown="getAIMeaage(key)">
        <svg class="remix">
          <use :xlink:href="`${remixiconUrl}#ri-${value.icon}`" />
        </svg>
        <span class="item-text">{{ value.name }}</span>
      </div>
    </ul>
    
    <el-card 
      v-if="visibleCard" 
      ref="cardRef"
      :style="cardStyle" 
    >
      <template v-if="visibleChart">
        <div :style="{ height: '400px', width: '680px' }">
          <EChart ref="chartRef" :option="chartOption" :width="'100%'" :height="'400px'"/>
        </div>
        <el-button type="primary" @mousedown="setChartImage()">插入</el-button>
      </template>
      
      <template v-else-if="visibleMindMap">
        <div :style="{ height: '400px', width: '680px' }">
          <MindMap ref="mindMapRef" :data="mindMapData" :width="'100%'" :height="'400px'"/>
        </div>
        <el-button type="primary" @mousedown="setMindMapImage()">插入</el-button>
      </template>
      <template v-else>
        <el-input
          v-model="cardMsg"
          :autosize="{ minRows: 1, maxRows: 16 }"
          type="textarea"
          :placeholder="textPrompt"
        />
        <template v-if="isMultiMedia">
          <el-button type="primary" @mousedown="copyText()">复制</el-button>
        </template>
        <template v-else>
          <el-button type="primary" @mousedown="replace()">替换</el-button>
          <el-button type="success" @mousedown="append()">追加</el-button>
        </template>
      </template>
      <el-button type="info" @mousedown="ignore()">舍弃</el-button>
    </el-card>

    <el-dialog
      v-model="visibleUploadDialog"
      title="上传文件"
      width="50%"
      @close="visibleUploadDialog = false"
    >
      <el-upload
        class="upload-demo"
        drag
        :before-upload="beforeUpload"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件放在此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
          </div>
        </template>
      </el-upload>
    </el-dialog>

    <el-dialog
      v-model="visibleVoiceInput"
      title="语音识别"
      width="50%"
      @close="visibleVoiceInput = false"
    >
      <VoiceInput :getVoiceResult="getVoiceResult"></VoiceInput>
    </el-dialog>

    <el-dialog
      v-model="visibleTextInput"
      :title="textTitle"
      width="50%"
      @close="visibleTextInput = false"
    >
      <el-input
        v-model="textInput"
        style="width: 100%"
        :autosize="{ minRows: 10, maxRows: 16 }"
        type="textarea"
        :placeholder="textPrompt"
      />
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @mousedown="getAIResponse">开始生成</el-button>
      </div>
    </el-dialog>

    <!-- <el-dialog
      v-model="visibleChart"
      title="可视化图表"
      width="50%"
      @close="visibleChart = false"
    >
      可视化图表
    </el-dialog> -->

    <el-header :class="{'expanded-menu' : isExpanded}">
      <el-menu mode="horizontal" :ellipsis="false">
        <el-menu-item class="logo-item">
          <img src="./logo.png" alt="Logo" class="logo" />
        </el-menu-item>
        <div class="flex-grow" />
        <el-menu-item @click="gotoUserProfile()">
          个人中心
          <svg class="remix">
            <use :xlink:href="`${remixiconUrl}#ri-${'arrow-right-s-line'}`" />
          </svg>
        </el-menu-item>
      </el-menu>
    </el-header>

    <el-container style="flex: 1;">
      <el-aside width="20%" style="height: 100%;">
        <Outline/>
      </el-aside>
      <el-main style="height: 100%;">
        <Menu 
          :editor="editor as Editor" 
          :showUploadDialog="showUploadDialog"
          :showVoiceInput="showVoiceInput"
          :showTextInput="showTextInput"
          :addImageByBase64="addImageByBase64"
          :autoTypography="autoTypography"
        />
        <!-- <SelectionBubbleMenu ref="bubbleRef" :editor="editor as Editor" :showDataModal="showDataModal" /> -->
        <editor-content 
          :editor="editor"
          @scroll="hasScroll()"
          @mousedown="notSee($event)"
          @mousemove="mouseMove()" 
          @mouseup="selectText($event)" 
          @paste="handlePaste"
        />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts" name="TextEditor">
  import { ref, reactive, computed, onMounted, onUnmounted } from "vue"
  import { useEditor, EditorContent, Editor } from "@tiptap/vue-3"
  import StarterKit from '@tiptap/starter-kit'
  import Highlight from '@tiptap/extension-highlight'
  import Subscript from '@tiptap/extension-subscript'
  import Superscript from '@tiptap/extension-superscript'
  import Underline from '@tiptap/extension-underline'
  import Placeholder from '@tiptap/extension-placeholder'
  import TaskItem from '@tiptap/extension-task-item'
  import TaskList from '@tiptap/extension-task-list'
  import Blockquote from '@tiptap/extension-blockquote'
  import Image from '@tiptap/extension-image'
  import Youtube from '@tiptap/extension-youtube'
  import { Markdown } from 'tiptap-markdown'
  import Table from '@tiptap/extension-table'
  import TableCell from '@tiptap/extension-table-cell'
  import TableHeader from '@tiptap/extension-table-header'
  import TableRow from '@tiptap/extension-table-row'

  import remixiconUrl from 'remixicon/fonts/remixicon.symbol.svg'
  import { UploadFilled } from '@element-plus/icons-vue'
  import MenuGroup from './components/MenuGroup.vue'
  import axios from "axios"
  import { ElMessage, formContextKey } from 'element-plus'
  import {RouterView,RouterLink,useRouter} from 'vue-router'

  import Menu from "./components/Menu.vue"
  import Outline from "./components/Outline.vue"
  import SelectionBubbleMenu from "./components/SelectionBubbleMenu.vue"
  import VoiceInput from "./components/VoiceInput.vue"
  import EChart from './components/EChart.vue'
  import MindMap from "./components/MindMap.vue"
  import MindElixir, { MindElixirInstance, Options, MindElixirData } from 'mind-elixir'

  import { useEditorStore } from '@/store'
  import { fa } from "element-plus/es/locales.mjs"
  // import { handlePaste } from "@tiptap/pm/tables"

  const router = useRouter()
  const editorStore = useEditorStore()
  // 编辑器
  const editor = useEditor({
    // content: "我正在使用 Vue.js 运行 Tiptap。",
    content: ``,
    extensions: [
      StarterKit,
      Highlight,
      Subscript,
      Superscript,
      Underline,
      Placeholder.configure({
        placeholder: '开始输入文本...'
      }),
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
      Image.configure({
        inline: true,
        allowBase64: true,
      }),
      Youtube.configure({
        inline: false,
        controls: true,
        nocookie: true,
        width: 480,
        height: 320,
      }),
      Markdown,
      Table.configure({
        resizable: true,
      }),
      TableRow,
      TableHeader,
      TableCell,

      // Blockquote.configure({
      //   HTMLAttributes: {
      //     class: "my-blockquote",
      //   },
      // })
    ],
    onUpdate({ editor }) {
      loadHeadings()
      editorStore.setEditorInstance(editor)
      // const selectionTmp = editor.state.selection
      // if (selectionTmp) {
      //   const { from, to} = selectionTmp
      //   oldContent = newContent
      //   newContent= editor.getText() || ''
      //   selectionStr.from = oldContent.slice(0, from - 1)
      //   selectionStr.to = oldContent.slice(to - 1)
      //   console.log("update", selectionStr.from, selectionStr.to)
      // }
    },
    onCreate({ editor }) {
      loadHeadings()
      editorStore.setEditorInstance(editor)
    },
  });
  // 监听粘贴事件
  const handlePaste = (event: ClipboardEvent) => {
    event.preventDefault()
    event.stopPropagation()
    // 获取粘贴内容
    const clipboardData: DataTransfer | null = event.clipboardData
    const pastedData: string = clipboardData ? clipboardData.getData('text') : ''
    // editor.value?.commands.insertContent(pastedData)
    editor.value?.commands.setContent(`${selectionStr.from}\n\n${pastedData}\n\n${selectionStr.to}`, true)
  }

  // 润色功能
  const AIList = reactive({
    'translate': {name: "翻译", icon: "translate"},
    'abstract': {name: "摘要", icon: "file-text-line"},
    'decorate': {name: "修饰", icon: "magic-line"},
    'continue-write': {name: "续写", icon: "edit-2-line"},
    'rewrite': {name: "病句改写", icon: "refresh-line"},
    'improve-write': {name: "改进写作", icon: "pencil-ruler-line"},
    'summarize': {name: "总结", icon: "book-2-fill"},
    'analysis': {name: "分析内容", icon: "bar-chart-fill"},
  })
  async function getAIMeaage(name: string){
    try {
      console.log("on mounted")
      const formData = new FormData()
      formData.append('question', selectionMsg)
      // let data = {
      //   question: selectionMsg
      // }
      const response = await axios.post(
        `/${name}/`,
        formData,
      )
      // accountError.value = response.data.error
      let res = response.data
      if (res.status){
        console.log(res.answer)
        cardMsg.value = res.answer
        isMultiMedia.value = false
        visibleCard.value = true
      } else{
        console.log(res.error)
      }
      console.log('POST 请求成功：', response.data)
      
    } catch (error) {
      console.error('POST 请求失败：', error)
      // throw error // 可选的抛出错误
    }
  }

  const fileContRef = ref(null)
  const visibleMenu = ref(false)
  const visibleCard = ref(false)
  const cardRef = ref()
  const menuRef = ref()
  const cardMsg = ref("")
  const position = ref({
    top: 0,
    left: 0
  })
  var hasMove = ref(false)
  var selectionMsg: any
  var selection: any
  var selectionStr = {from: "", to: ""}
  var oldContent = ""
  var newContent = ""
  // 获取选中的文字
  const selectText = (e: MouseEvent) => {
    const selectionTmp = editor.value?.state.selection
    if (selectionTmp) {
      const { from, to} = selectionTmp
      const currentContent = editor.value?.getText() || ''
      selectionStr.from = currentContent.slice(0, from - 1)
      selectionStr.to = currentContent.slice(to - 1)
      // console.log("in selectText", selectionStr.from, selectionStr.to)
    }
    selection = window.getSelection()
    if(selection != null && selectionMsg != selection){
      var content = selection.toString()
      if(content != ""){
          // var rect = fileContRef.value?.getBoundingClientRect()
          visibleMenu.value = true
          // alert(e.clientY)
          // alert(e.clientX)
          position.value.top =  e.clientY
          position.value.left = e.clientX
          selectionMsg = content
        }
      // alert(content)
    }
    else{
      selectionMsg = ""
    }
  }
  //鼠标移动
  const mouseMove = () => {
    hasMove.value = true
  }
  const isMouseNotInRect = (e: MouseEvent, rect: any) => {
    const { clientX: x, clientY: y } = e
    if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
      return true
    } else return false
  }

  //鼠标点击
  const notSee = (e: MouseEvent) => {
    visibleMenu.value = false
    // if (isMouseNotInRect(e, menuRef.value.$el.getBoundingClientRect())) visibleMenu.value = false
    if (isMouseNotInRect(e, cardRef.value.$el.getBoundingClientRect())) visibleCard.value = false
  }
  const seeMenu = () => {
    visibleMenu.value = true
    // selection.value=""
  }
  //滚轮滚动
  const hasScroll = () => {
    visibleMenu.value = false
    // window.getSelection().removeAllRanges()
  }
  const replace = () => {
    const selection = editor.value?.state.selection
    if (selection) { // 检查 selection 是否为 undefined
      const { from, to } = selection
      if (from !== to) { // 确保有选中的内容
        editor.value?.chain().focus().deleteRange({ from, to }).insertContent(cardMsg.value).run()
        visibleCard.value = false
      }
    } 
  }
  const append = () => {
    const selection = editor.value?.state.selection
    if (selection) { // 检查 selection 是否为 undefined
      const { from, to } = selection
      if (from !== to) { // 确保有选中的内容
        editor.value?.chain().focus().insertContentAt(to, cardMsg.value).run()
        visibleCard.value = false
      }
    } 
  }
  const ignore = () => {
    visibleCard.value = false
    visibleChart.value = false
  }
  const copyText = async () => {
    try {
      await navigator.clipboard.writeText(cardMsg.value)
      ElMessage({
        message: '已成功复制到粘贴板',
        type: 'success',
        plain: true,
      })
      visibleCard.value = false
      console.log('文本已复制到剪贴板')
    } catch (err) {
      console.error('复制失败:', err)
    }
  }

    // 获取标题（大纲）
  const loadHeadings = () => {
    const headings = [] as any[]
    if (!editor.value) return
    const transaction = editor.value.state.tr
    if (!transaction) return

    editor.value?.state.doc.descendants((node, pos) => {
      if (node.type.name === 'heading') {
        console.log(pos, node)
        const start = pos
        const end = pos + node.content.size
        // const end = pos + node
        const id = `heading-${headings.length + 1}`
        if (node.attrs.id !== id) {
          transaction?.setNodeMarkup(pos, undefined, {
            ...node.attrs,
            id
          })
        }

        headings.push({
          level: node.attrs.level,
          text: node.textContent,
          start,
          end,
          id
        })
      }
    })

    transaction?.setMeta('addToHistory', false)
    transaction?.setMeta('preventUpdate', true)

    editor.value?.view.dispatch(transaction)
    editorStore.setHeadings(headings)
  }

  function gotoUserProfile()
  {
    router.push({
      path: '/user-profile',
    })
  }

  const visibleUploadDialog = ref(false)
  const uploadUrl = ref("")
  const isMultiMedia = ref(false)
  const showUploadDialog = (params: any) => {
    visibleUploadDialog.value = true
    uploadUrl.value = params.url
  }
  const beforeUpload = async (file: any) => {
    ElMessage({
      message: '成功上传文件',
      type: 'success',
      plain: true,
    })
    visibleUploadDialog.value = false
    try {
      console.log("on mounted")
      const formData = new FormData()
      formData.append('file', file)
      const response = await axios.post(
        `/${uploadUrl.value}/`,
        formData,
      )
      let res = response.data
      console.log(res)
      if (res.status){
        // console.log(res.answer)
        cardMsg.value = res.answer
        isMultiMedia.value = true
        visibleCard.value = true
      } else{
        console.log(res.error)
      }
      console.log('POST 请求成功：', response.data)
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
    return false;
  }
  // 语音识别
  const visibleVoiceInput = ref(false)
  const showVoiceInput = (params: any) => {
    visibleVoiceInput.value = true
    uploadUrl.value = params.url
  }
  const getVoiceResult = (param: string) => {
    visibleVoiceInput.value = false
    cardMsg.value = param
    isMultiMedia.value = true
    visibleCard.value = true
  }

  const cardStyle = computed(() => {
    if (isMultiMedia.value) {
      return {
        maxWidth: '680px',
        left: '50%',
        top: '50%',
        transform: 'translate(-50%, -50%)',
        display: visibleCard.value ? 'grid' : 'none',
        position: 'absolute',
        zIndex: 1000,
      };
    } else {
      return {
        maxWidth: '680px',
        left: `${position.value.left}px`,
        top: `${position.value.top}px`,
        display: visibleCard.value ? 'grid' : 'none',
        position: 'absolute',
        zIndex: 1000,
      };
    }
  })

  // 文档撰写
  const visibleTextInput = ref(false)
  const textInput = ref("")
  const textPrompt = ref("")
  const textTitle = ref("")
  const showTextInput = (params: any) => {
    visibleTextInput.value = true
    uploadUrl.value = params.url
    textPrompt.value = params.prompt
    textTitle.value = params.title
  }
  const getAIResponse = async () => {
    if (!textInput.value) {
      ElMessage({
        message: '内容不能为空',
        type: 'error',
        plain: true,
      })
      return ;
    }
    visibleTextInput.value = false
    ElMessage({
      message: '成功发送',
      type: 'success',
      plain: true,
    })
    try {
      console.log("on mounted")
      const formData = new FormData()
      formData.append('question', textInput.value)
      const response = await axios.post(
        `/${uploadUrl.value}/`,
        formData,
      )
      // accountError.value = response.data.error
      let res = response.data
      if (res.status){
        console.log(res.answer)
        const chartStrs: string[] = ["make-bar", "make-pie", "make-line", "make-scatter"]
        if (chartStrs.includes(uploadUrl.value)) {
          handleAIChart(res.answer)
        } else if (uploadUrl.value === "make-mind-map") {
          console.log("mind")
          handleAIMindMap(res.answer)
        } else {
          handleAIDocument(res.answer)
        }

      } else{
        console.log(res.error)
      }
      console.log('POST 请求成功：', response.data)
      
    } catch (error) {
      console.error('POST 请求失败：', error)
      // throw error // 可选的抛出错误
    }
  }

  const handleAIDocument = (answer: string) => {
    cardMsg.value = answer
    isMultiMedia.value = true
    visibleCard.value = true
  } 
  const handleAIChart = (answer: object) => {
    visibleChart.value = true
    chartOption.value = answer
    visibleCard.value = true
    isMultiMedia.value = true
  }

  const addImageByBase64 = (base64String: string, fileName: string, fileType: string) => {
    const base64Src = `data:${fileType};base64,${base64String.split(',')[1]}`
    editor.value?.commands.setImage({
      src: base64Src,
      alt: fileName,
      title: fileName,
    })
  }

  // 可视化图表
  const visibleChart = ref(false)
  const chartRef = ref()
  const chartOption = ref({})

  const setChartImage = () => {
    editor.value?.commands.setImage({
      src: chartRef.value?.getChartBase64(),
      alt: chartRef.value?.title,
      title: chartRef.value?.title,
    })
    visibleChart.value = false
  }

  // 思维导图
  const visibleMindMap = ref(false)
  const mindMapRef = ref()
  const mindMapData = ref<MindElixirData | null>(null)
  // const setMindMapImage = () => {
  //   editor.value?.commands.setImage({
  //     src: mindMapRef.value?.exportAsBase64('png'),
  //     alt: "思维导图",
  //     title: "思维导图",
  //   })
  //   visibleMindMap.value = false
  // }
  const setMindMapImage = async () => {
  try {
    const base64Image = await mindMapRef.value?.exportAsBase64('png');
    if (base64Image) {
      editor.value?.commands.setImage({
        src: base64Image,
        alt: "思维导图",
        title: "思维导图",
      });
      visibleMindMap.value = false;
    } else {
      console.error('Failed to export mind map as base64.');
    }
  } catch (error) {
    console.error('Error setting mind map image:', error);
  }
};

  const handleAIMindMap = (answer: MindElixirData) => {
    visibleMindMap.value = true
    mindMapData.value = answer
    visibleCard.value = true
    isMultiMedia.value = true
  }

  // 自动排版
  const autoTypography = async (params: any) => {
    try {
      console.log("on mounted")
      const formData = new FormData()
      formData.append('question', editor.value?.getText() as string)
      const response = await axios.post(
        `/${params.url}/`,
        formData,
      )
      let res = response.data
      console.log(res.answer)
      if (res.status){
        editor.value?.commands.setContent(res.answer)

      } else{
        console.log(res.error)
      }
      console.log('POST 请求成功：', response.data)
      
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
  }

const isExpanded = ref(false);
const handleScroll = () => {
  isExpanded.value = window.scrollY > 0;
};
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
});
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
});
</script>

<style lang="scss" scoped>
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
  }
  .custom-modal {
    position: fixed;
    width: 500px;
    background-color: #fff;
    padding: 10px;
    border-radius: 4px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
    z-index: 1000; /* 确保弹出框在最上层 */
  }
  .custom-list {
    list-style-type: none;
    padding: 0;
  }

  .flex-grow {
    flex-grow: 1;
  }

  .menu-item {
    background: transparent;
    border: none;
    border-radius: 0.4rem;
    color: #333;
    cursor: pointer;
    height: 1.75rem;
    padding: 0.25rem;
    margin-right: 0.25rem;
    width: 1.75rem;

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

  .logo_item{
    display: flex;
    align-items: center;
    padding: 0 20px; /* 调整padding以获得适当的间距 */
  }

  .logo{
    height: 50px; /* 调整logo的高度 */
  }

  .expanded-menu {
    width: 100vw; /* 100% viewport width */
    position: fixed; /* 固定在页面顶部 */
    top: 0;
    left: 0;
    z-index: 1000; /* 确保位于其他内容之上 */
  }

  .context-menu {
    width: 240px; /* 调整宽度以适应两列布局 */
    margin: 0;
    background: #fff;
    z-index: 3000;
    position: absolute;
    list-style-type: none;
    padding: 5px; /* 调整填充 */
    border-radius: 6px; /* 增加圆角 */
    font-size: 16px;
    font-weight: 400;
    color: #333;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 优化阴影 */
    display: grid;
    grid-template-columns: 1fr 1fr; /* 两列布局 */
    gap: 10px; /* 增加项之间的间距 */
  }

  .context-menu .item {
    height: 40px; /* 增加高度 */
    display: flex; /* 使用弹性布局 */
    align-items: center; /* 垂直居中 */
    padding: 0 10px; /* 增加内边距 */
    color: rgb(29, 33, 41);
    cursor: pointer;
    border-radius: 4px; /* 增加圆角 */
    background-color: #f9f9f9; /* 添加背景色 */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 添加阴影 */
  }

  .context-menu .item-text {
    flex: 1; /* 占据剩余空间，使文本左对齐 */
    text-align: left; /* 确保文本左对齐 */
  }

  .context-menu .item:hover {
    background: rgb(229, 230, 235);
  }

  .remix {
    fill: currentColor;
    width: 1.5rem;
    height: 1.5rem;
    margin-right: 5px; /* 增加与文本的间距 */
  }
</style>

<style lang="scss">

.tiptap .bubble-menu {
    background-color: var(--white);
    border: 1px solid var(--gray-1);
    border-radius: 0.7rem;
    box-shadow: var(--shadow);
    display: flex;
    padding: 0.2rem;

    button {
      background-color: unset;

      &:hover {
        background-color: var(--gray-3);
      }

      &.is-active {
        background-color: var(--purple);

        &:hover {
          background-color: var(--purple-contrast);
        }
      }
    }
  }
b {
  font-weight: bold;
}
.ProseMirror {
  overflow-y: scroll;
}
.ProseMirror p {
  margin: 0;
}
.ProseMirror:focus {
  outline: none;
}
.tiptap p.is-editor-empty:first-child::before {
  color: #adb5bd;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

.tiptap {
  > * + * {
    margin-top: 0.75em;
  }

  ul {
    padding: 0 2rem;
    list-style: square;
  }
  ol {
    padding: 0 2rem;
    list-style: decimal;
  }
  table {
    border-collapse: collapse;
    table-layout: fixed;
    width: 100%;
    margin: 0;
    overflow: hidden;

    td,
    th {
      min-width: 1em;
      border: 2px solid #ced4da;
      padding: 3px 5px;
      vertical-align: top;
      box-sizing: border-box;
      position: relative;

      > * {
        margin-bottom: 0;
      }
    }

    th {
      font-weight: bold;
      text-align: left;
      background-color: #f1f3f5;
    }

    .selectedCell:after {
      z-index: 2;
      position: absolute;
      content: '';
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
      background: rgba(200, 200, 255, 0.4);
      pointer-events: none;
    }

    .column-resize-handle {
      position: absolute;
      right: -2px;
      top: 0;
      bottom: -2px;
      width: 4px;
      background-color: #adf;
      pointer-events: none;
    }

    p {
      margin: 0;
    }
  }
  pre {
    background: #0d0d0d;
    color: #fff;
    font-family: 'JetBrainsMono', monospace;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;

    code {
      color: inherit;
      padding: 0;
      background: none;
      font-size: 0.8rem;
    }

    .hljs-comment,
    .hljs-quote {
      color: #616161;
    }

    .hljs-variable,
    .hljs-template-variable,
    .hljs-attribute,
    .hljs-tag,
    .hljs-name,
    .hljs-regexp,
    .hljs-link,
    .hljs-name,
    .hljs-selector-id,
    .hljs-selector-class {
      color: #f98181;
    }
    .hljs-number,
    .hljs-meta,
    .hljs-built_in,
    .hljs-builtin-name,
    .hljs-literal,
    .hljs-type,
    .hljs-params {
      color: #fbbc88;
    }

    .hljs-string,
    .hljs-symbol,
    .hljs-bullet {
      color: #b9f18d;
    }

    .hljs-title,
    .hljs-section {
      color: #faf594;
    }

    .hljs-keyword,
    .hljs-selector-tag {
      color: #70cff8;
    }

    .hljs-emphasis {
      font-style: italic;
    }

    .hljs-strong {
      font-weight: 700;
    }
  }
}

.tableWrapper {
  overflow-x: auto;
}

.resize-cursor {
  cursor: ew-resize;
  cursor: col-resize;
}
ul[data-type="taskList"] {
    list-style: none;
    margin-left: 0;
    padding: 0;

    li {
      align-items: flex-start;
      display: flex;

      > label {
        flex: 0 0 auto;
        margin-right: 0.5rem;
        user-select: none;
      }

      > div {
        flex: 1 1 auto;
      }
    }

    input[type="checkbox"] {
      cursor: pointer;
    }

    ul[data-type="taskList"] {
      margin: 0;
    }
  }
  .my-blockquote {
    border-left: 3px solid var(--gray-3);
    margin: 1.5rem 0;
    padding-left: 1rem;
  }
</style>

