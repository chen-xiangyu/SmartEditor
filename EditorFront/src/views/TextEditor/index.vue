<template>
  <el-container 
    style="height: 100vh; width: 100vw; background-color: #FCF5E4;" 
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
          ref="cardMsgRef"
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
      <VoiceInput 
        :getVoiceResult="getVoiceResult" 
        :showLoader="showLoader"
        :closeLoader="closeLoader"
        :coins="coins"
        :fetchCoins="fetchCoins"
      >
      </VoiceInput>
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

    <el-dialog v-model="visibleNewFile" title="新建文档" width="500">
      <el-form :model="formNewFile">
        <el-form-item label="文档名:" label-width="80px">
          <el-input v-model="formNewFile.newFilename" autocomplete="off" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="visibleNewFile = false">取消</el-button>
          <el-button type="primary" @click="createNewFile">
            创建
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="visibleRenameFile" title="重命名" width="500">
      <el-form :model="formRenameFile">
        <el-form-item label="文档名:" label-width="80px">
          <el-input v-model="formRenameFile.newFilename" autocomplete="off" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="visibleRenameFile = false">取消</el-button>
          <el-button type="primary" @click="renameFile">
            修改
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="visibleDeleteFile" title="请确认是否删除" width="500">
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="visibleDeleteFile = false">取消</el-button>
          <el-button type="danger" @click="deleteFile">
            删除
          </el-button>
        </div>
      </template>
    </el-dialog>

    <Loader v-if="visibleLoader"/>

    <el-header style="padding: 0; height: 60px;">
      <el-menu mode="horizontal" :ellipsis="false" style="background-color: #FCF5E4;">
        <el-menu-item class="logo-item" style="background-color: inherit !important;">
          <img src="@/assets/images/logo.png" alt="Logo" class="logo" />
        </el-menu-item>
        <div class="flex-grow" />
        <el-menu-item style="background-color: inherit; padding: 0;">
          <span @click="rechargeCoinsClick" style="cursor: pointer; color: #606266;" class="coin-item">
            硬币：{{ coins }}个，点击充值
          </span>
        </el-menu-item>
        <el-menu-item>
          <el-dropdown>
            <template #default>
            <span class="el-dropdown-link">
              你好, {{ username }}
              <svg class="remix">
                <use :xlink:href="`${remixiconUrl}#ri-${'arrow-down-s-line'}`" />
              </svg>
            </span>
            </template>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="gotoUserProfile()">个人中心</el-dropdown-item>
                <el-dropdown-item @click="logout()">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-menu-item>
      </el-menu>

      <el-dialog v-model="rechargeDialogVisible" width="70%">
        <template #title>
          <span class="custom-dialog-title">充值</span>
        </template>
        <div class="recharge-panel">
          <div class="section-title">支付金额</div>
          <div class="amount-options">
            <div v-for="(option, index) in amountOptions" :key="index" :class="['amount-option', { selected: selectedAmount === option.value }]" @click="selectAmount(option.value)">
              <div>{{ option.label }}</div>
              <div>{{ option.price }}</div>
              <div v-if="selectedAmount === option.value" class="checkmark">✔</div>
            </div>
          </div>
          <div class="section-title">付款方式</div>
          <div class="payment-methods">
            <div v-for="(method, index) in paymentMethods" :key="index" :class="['payment-method', { selected: selectedPaymentMethod === method.value }]" @click="selectPaymentMethod(method.value)">
              <div>{{ method.label }}</div>
              <div v-if="selectedPaymentMethod === method.value" class="checkmark">✔</div>
            </div>
          </div>
        </div>
        <div slot="footer" class="dialog-footer">
          <el-button @click="rechargeDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="rechargeCoins">确 定</el-button>
        </div>
      </el-dialog>

      <el-dialog v-model="paymentDialogVisible" width="30%">
        <template #title>
          <span class="custom-dialog-title">支付</span>
        </template>
        <div class="payment-QR-code">
          <img src="@/assets/images/qr-code.png" alt="支付二维码">
        </div>
        <div slot="footer" class="dialog-footer">
          <el-button @click="paymentDialogVisible = false">取 消 支 付</el-button>
          <el-button type="primary" @click="confirmPayment">确 认 支 付</el-button>
        </div>
      </el-dialog>
    </el-header>

    <el-container style="width: 100vw;">

      <el-scrollbar style="height: calc(100vh - 60px); width: 18%;">
        <el-aside style="height: calc(100vh - 60px); background-color: #E4DCC8; width: 100%;">
          <Catalog
            ref="catalogRef"
            :setCurrentContent="setCurrentContent" 
            :showNewFile="showNewFile"
            :showRenameFile = "showRenameFile"
            :showDeleteFile = "showDeleteFile"
          />
        </el-aside>
      </el-scrollbar>

      <el-container style="width: 64%;">
        <el-header style="padding: 0;">
          <Menu 
            :editor="editor as Editor" 
            :showUploadDialog="showUploadDialog"
            :showVoiceInput="showVoiceInput"
            :showTextInput="showTextInput"
            :addImageByBase64="addImageByBase64"
            :autoTypography="autoTypography"
          />
        </el-header>

        <el-scrollbar style="height: calc(100vh - 60px - 4rem);">
          <el-main style="background-color: #FCF5E4;">
            <editor-content 
              class="editor-content"
              :editor="editor"
              @mousedown="notSee($event)"
              @mousemove="mouseMove()" 
              @mouseup="selectText($event)" 
              @paste="handlePaste"
            />
          </el-main>
        </el-scrollbar>
      </el-container>

      <el-scrollbar style="height: calc(100vh - 60px); width: 18%;">
        <el-aside style="height: calc(100vh - 60px); background-color: #E4DCC8; width: 100%;">
          <Outline/>
        </el-aside>
      </el-scrollbar>
    </el-container>


  </el-container>
</template>

<script setup lang="ts" name="TextEditor">
  import { ref, reactive, computed, onMounted, onBeforeUnmount } from "vue"
  import { useEditor, EditorContent, Editor } from "@tiptap/vue-3"
  import StarterKit from '@tiptap/starter-kit'
  import Highlight from '@tiptap/extension-highlight'
  import Subscript from '@tiptap/extension-subscript'
  import Superscript from '@tiptap/extension-superscript'
  import Underline from '@tiptap/extension-underline'
  import Placeholder from '@tiptap/extension-placeholder'
  import TaskItem from '@tiptap/extension-task-item'
  import TaskList from '@tiptap/extension-task-list'
  // import Blockquote from '@tiptap/extension-blockquote'
  import Image from '@tiptap/extension-image'
  import Youtube from '@tiptap/extension-youtube'
  import { Markdown } from 'tiptap-markdown'
  import Table from '@tiptap/extension-table'
  import TableCell from '@tiptap/extension-table-cell'
  import TableHeader from '@tiptap/extension-table-header'
  import TableRow from '@tiptap/extension-table-row'

  import remixiconUrl from 'remixicon/fonts/remixicon.symbol.svg'
  import { UploadFilled } from '@element-plus/icons-vue'
  import axios from "axios"
  import { ElMessage } from 'element-plus'
  import {useRouter} from 'vue-router'

  import Menu from "./components/Menu.vue"
  import Outline from "./components/Outline.vue"
  import VoiceInput from "./components/VoiceInput.vue"
  import EChart from './components/EChart.vue'
  import MindMap from "./components/MindMap.vue"
  import Loader from "./components/Loader.vue"
  import { MindElixirData } from 'mind-elixir'
  import Catalog  from "./components/Catalog.vue"

  // import { useEditorStore } from '@/store'
  import { useEditorStore } from '../../store'
// import { colCount } from "@tiptap/pm/tables"
  // import { fa } from "element-plus/es/locales.mjs"
  // import { handlePaste } from "@tiptap/pm/tables"
  const router = useRouter()
  const editorStore = useEditorStore()
// 编辑器
  const savedContent = localStorage.getItem('editorContent');
  const editor = useEditor({
    // content: "我正在使用 Vue.js 运行 Tiptap。",
    // content: `` || savedContent,
    content: ``,
    extensions: [
      StarterKit,
      Highlight.configure({
        multicolor: true,
      }),
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
    ],
    onUpdate({ editor }) {
      loadHeadings()
      editorStore.setEditorInstance(editor)
      const content = editor.getHTML();
      localStorage.setItem('editorContent', content);
      // console.log(content);
      isUpdate.value = true
    },
    onCreate({ editor }) {
      loadHeadings()
      editorStore.setEditorInstance(editor)
    },
  });
  onMounted(() => {
    fetchCoins()
  })
  

  // 监听粘贴事件
  const handlePaste = (event: ClipboardEvent) => {
    event.preventDefault()
    event.stopPropagation()
    // 获取粘贴内容
    const clipboardData: DataTransfer | null = event.clipboardData
    const pastedData: string = clipboardData ? clipboardData.getData('text') : ''
    // editor.value?.commands.insertContent(pastedData)
    // editor.value?.commands.insertContent("hello")
    let { from, to } = editor.value?.state.selection || { from: 0, to: 0 };
    // console.log(from, "@@@", to, "@@@", pastedData.length)
    from = Math.max(to - pastedData.length - 1, 0)
    editor.value?.chain().focus().deleteRange({ from, to }).insertContent(pastedData).run()
    // editor.value?.commands.setContent(`${selectionStr.from}\n\n${pastedData}\n\n${selectionStr.to}`, true)
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
    if (coins.value == 0) {
      ElMessage.error('硬币数量为0，无法使用AI功能，请尽快充值.')
      return 
    }
    try {
      console.log("on mounted")
      const formData = new FormData()
      formData.append('question', selectionMsg)
      showLoader()
      const response = await axios.post(
        `/${name}/`,
        formData,
      )
      // accountError.value = response.data.error
      let res = response.data
      if (res.status){
        // console.log(res.answer)
        cardMsg.value = res.answer
        isMultiMedia.value = false
        visibleCard.value = true
        fetchCoins()
      } else{
        ElMessage.error('非常抱歉，AI的回复在来的路上丢失了，请重新操作')
        console.log(res.error)
      }
      closeLoader()
      console.log('POST 请求成功：', response.data)
      
    } catch (error) {
      console.error('POST 请求失败：', error)
      // throw error // 可选的抛出错误
    }
  }

  // 获取硬币数量
  const fetchCoins = () => {
    axios.get('/get-coins/')
      .then((response) => {
        coins.value = response.data.coins
      })
      .catch((error) => {
        console.error('获取硬币数量失败：', error)
      })
  }
  const coins = ref(null)
  const rechargeDialogVisible = ref(false)
  const selectedAmount = ref('10')
  const selectedPaymentMethod = ref('wechat')
  const paymentDialogVisible = ref(false)

  // 充值金额选项
  const amountOptions = [
    { label: '10硬币', price: '¥10', value: '10' },
    { label: '30硬币', price: '¥30', value: '30' },
    { label: '50硬币', price: '¥50', value: '50' },
    { label: '100硬币', price: '¥100', value: '100' },
  ]

  // 支付方式选项
  const paymentMethods = [
    { label: '微信', value: 'wechat' },
    { label: '支付宝', value: 'alipay' },
  ]
  // 选择充值金额
  const selectAmount = (value) => {
    selectedAmount.value = value
  }

  // 选择支付方式
  const selectPaymentMethod = (value) => {
    selectedPaymentMethod.value = value
  }

  // 充值硬币
  const rechargeCoinsClick = () => {
    rechargeDialogVisible.value = true
  }
  const rechargeCoins = async () => {
    let amount=parseInt(selectedAmount.value)
    if (amount <= 0) {
      ElMessage.error('充值金额必须大于0')
      return
    }
    rechargeDialogVisible.value = false
    paymentDialogVisible.value = true
  }
  const confirmPayment = async () => {
    let amount = parseInt(selectedAmount.value)
    try {
      const formData = new FormData()
      formData.append('amount', amount.toString())
      const response = await axios.post('/recharge/', formData)
      let res = response.data
      if(res.status){
        ElMessage.success('充值成功')
        fetchCoins()
      } else{
        ElMessage.error('充值失败')
      }
      console.log('POST 请求成功：', response.data)
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
    paymentDialogVisible.value = false
  }

  const fileContRef = ref(null)
  const visibleMenu = ref(false)
  const visibleCard = ref(false)
  const username = ref(localStorage.getItem('account'))
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
    console.log("nosee")
    visibleMenu.value = false
    catalogRef.value.closeDropdown()
    // if (isMouseNotInRect(e, menuRef.value.$el.getBoundingClientRect())) visibleMenu.value = false
    if (isMouseNotInRect(e, cardRef.value.$el.getBoundingClientRect())) visibleCard.value = false

  }
  const seeMenu = () => {
    visibleMenu.value = true
    // selection.value=""
  }
  //滚轮滚动
  // const hasScroll = () => {
  //   visibleMenu.value = false
  //   // window.getSelection().removeAllRanges()
  // }
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
  const cardMsgRef = ref()
  const copyText = async () => {
    cardMsgRef.value.select()
    document.execCommand('copy');
    ElMessage({
      message: '已成功复制到粘贴板',
      type: 'success',
      plain: true,
    })
    visibleCard.value = false
    // try {
    //   await navigator.clipboard.writeText(cardMsg.value)
    //   ElMessage({
    //     message: '已成功复制到粘贴板',
    //     type: 'success',
    //     plain: true,
    //   })
    //   visibleCard.value = false
    //   console.log('文本已复制到剪贴板')
    // } catch (err) {
    //   console.error('复制失败:', err)
    // }
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

  function logout()
  {
    localStorage.removeItem('account')
    localStorage.removeItem('token')
    router.push("/login")
  }


  const visibleUploadDialog = ref(false)
  const uploadUrl = ref("")
  const isMultiMedia = ref(false)
  const showUploadDialog = (params: any) => {
    visibleUploadDialog.value = true
    uploadUrl.value = params.url
  }
  const beforeUpload = async (file: any) => {
    if (coins.value == 0) {
      ElMessage.error('硬币数量为0，无法使用AI功能，请尽快充值.')
      return 
    }
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
      showLoader()
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
        fetchCoins()
      } else{
        ElMessage.error('非常抱歉，AI的回复在来的路上丢失了，请重新操作')
        console.log(res.error)
      }
      closeLoader()
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
    closeLoader()
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
    if (coins.value == 0) {
      ElMessage.error('硬币数量为0，无法使用AI功能，请尽快充值.')
      return 
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
      showLoader()
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
        fetchCoins()
      } else{
        ElMessage.error('非常抱歉，AI的回复在来的路上丢失了，请重新操作')
        console.log(res.error)
      }
      closeLoader()
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
      visibleCard.value = false;
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
    if (coins.value == 0) {
      ElMessage.error('硬币数量为0，无法使用AI功能，请尽快充值.')
      return 
    }
    try {
      console.log("on mounted")
      const formData = new FormData()
      formData.append('question', editor.value?.getText() as string)
      showLoader()
      const response = await axios.post(
        `/${params.url}/`,
        formData,
      )
      let res = response.data
      console.log(res.answer)
      if (res.status){
        editor.value?.commands.setContent(res.answer)
        loadHeadings()
        fetchCoins()
        isUpdate.value = true
      } else{
        ElMessage.error('非常抱歉，AI的回复在来的路上丢失了，请重新操作')
        console.log(res.error)
      }
      closeLoader()
      console.log('POST 请求成功：', response.data)
      
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
  }

  const visibleLoader = ref(false)
  const showLoader = () => {
    visibleLoader.value = true
    visibleUploadDialog.value = false
    visibleTextInput.value = false
    visibleVoiceInput.value = false
  }
  const closeLoader = () => {
    visibleLoader.value = false
  }

  const currentFileID = ref(0)
  const isUpdate = ref(false)
  const setCurrentContent = (content: string, id: number) => {
    editor.value?.commands.setContent(content)
    currentFileID.value = id
  }

  // let saveInterval = null
  let saveInterval = setInterval(async ()  => {
    if (isUpdate.value) {
      const content = editor.value?.getHTML()
      try {
        console.log("update file")
        const formData = new FormData()
        formData.append('id', currentFileID.value.toString())
        formData.append('content', content)
        const response = await axios.post(
          `/update-file/`,
          formData,
        )
        let res = response.data
        console.log(res.answer)
        if (res.status){
          isUpdate.value = false
          console.log(isUpdate.value)
        } else{
          console.log(res.error)
        }
        console.log('POST 请求成功：', response.data)
      } catch (error) {
        console.error('POST 请求失败：', error)
      }
    }
  }, 2000);

  const catalogRef = ref(null)

  const visibleNewFile = ref(false)
  const formNewFile = ref({
    newFilename: ''
  })
  const showNewFile = () => {
    visibleNewFile.value = true
  }

  const createNewFile = async () => {
    try {
      const formData = new FormData()
      formData.append('filename', formNewFile.value.newFilename)
      const response = await axios.post(
        `/create-file/`,
        formData,
      )
      let res = response.data
      console.log(res.answer)
      if (res.status){
        catalogRef.value.getCatalog()
      } else{

      }
      console.log('POST 请求成功：', response.data)
      
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
    visibleNewFile.value = false
    formNewFile.value.newFilename = ""
  }

  const visibleRenameFile = ref(false)
  const formRenameFile = ref({
    newFilename: ''
  })
  const rightClickFileID = ref(0)
  const showRenameFile = (oldName: string, id: number) => {
    formRenameFile.value.newFilename = oldName
    visibleRenameFile.value = true
    rightClickFileID.value = id
  }

  const renameFile = async () => {
    try {
      const formData = new FormData()
      formData.append('filename', formRenameFile.value.newFilename)
      formData.append('id', rightClickFileID.value.toString())
      const response = await axios.post(
        `/rename-file/`,
        formData,
      )
      let res = response.data
      console.log(res.answer)
      if (res.status){
        catalogRef.value.getCatalog()
      } else{
      }
      console.log('POST 请求成功：', response.data)
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
    visibleRenameFile.value = false
  }

  const visibleDeleteFile = ref(false)
  const showDeleteFile = (id: number) => {
    visibleDeleteFile.value = true
    rightClickFileID.value = id
  }
  const deleteFile = async () => {
    try {
      const formData = new FormData()
      formData.append('id', rightClickFileID.value.toString())
      const response = await axios.post(
        `/delete-file/`,
        formData,
      )
      let res = response.data
      console.log(res.answer)
      if (res.status){
        catalogRef.value.getCatalog()
      } else{
      }
      console.log('POST 请求成功：', response.data)
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
    visibleDeleteFile.value = false
  }
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

  .menu-outer {
    height: 4rem;
    width: 80%;
    margin-bottom: 5px;
  }
  .menu-inner {
    position: fixed;
    top: 60px;
    width: 80%;
    z-index: 1000;
  }

  .el-dropdown-link {
    border: none !important;
    outline: none !important;
    cursor: pointer;
    display: flex;
    align-items: center;
  }

  .context-menu {
    width: 220px; /* 调整宽度以适应两列布局 */
    margin: 0;
    background: #EAEAEB;
    z-index: 1000;
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
    height: 35px; /* 增加高度 */
    display: flex; /* 使用弹性布局 */
    align-items: center; /* 垂直居中 */
    padding: 0 10px; /* 增加内边距 */
    color: #D9D9D9;
    cursor: pointer;
    border-radius: 4px; /* 增加圆角 */
    background-color: #f9f9f9; /* 添加背景色 */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 添加阴影 */
  }

  .context-menu .item-text {
    flex: 1; /* 占据剩余空间，使文本左对齐 */
    text-align: left; /* 确保文本左对齐 */
    font-size: 0.9rem;
    color: #333;
  }

  .context-menu .item:hover {
    background: rgb(205, 206, 210);
  }

  .remix {
    fill: #333;
    width: 1.1rem;
    height: 1.1rem;
    margin-right: 5px; /* 增加与文本的间距 */
  }

  .custom-dialog-title {
    font-size: 20px; 
    font-weight: bold; 
  }

  .recharge-panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
  }

  .section-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 10px;
    align-self: flex-start;
  }

  .amount-options, .payment-methods {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
    width: 100%;
  }

  .amount-option, .payment-method {
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 20px;
    margin: 0 10px;
    text-align: center;
    cursor: pointer;
    position: relative;
    flex: 1;
    font-size: 20px;
  }

  .amount-option.selected, .payment-method.selected {
    border-color: #409EFF;
    background-color: #E6F7FF;
  }

  .checkmark {
    position: absolute;
    top: 5px;
    right: 5px;
    color: #409EFF;
  }

  .payment-QR-code {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 300px;
  }

  .payment-QR-code img {
    max-width: 100%;
    max-height: 100%;
  }

  .coin-item {
    padding: 0 20px;
  }
  .coin-item:hover {
    background-color: #ECF5FF;
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
.ProseMirror{
    max-height: 100%; /* 设置编辑区域的最大高度 */
    overflow-y: auto /* 启用垂直滚动条 */
  }

  /* 自定义滚动条样式 */
  .ProseMirror::-webkit-scrollbar {
    display: none;
    width: 12px; /* 滚动条宽度 */
  }

  .ProseMirror::-webkit-scrollbar-track {
    background: #faedd1; /* 滚动条轨道颜色 */
  }

  .ProseMirror::-webkit-scrollbar-thumb {
    background-color: #E2DCCD; /* 滚动条滑块颜色 */
    border-radius: 10px; /* 滑块圆角 */
    border: 3px solid #FCF5E4; /* 滑块的边框颜色，使其看起来像内嵌在轨道中 */
  }

  .ProseMirror::-webkit-scrollbar-thumb:hover {
    background-color: #555; /* 滑块悬停时的颜色 */
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
  code {
    background-color: #EAEAEB;
    border-radius: 0.4rem;
    color: #9AC47C;
    font-size: 0.85rem;
    padding: 0.25em 0.3em;
  }
  ol {
    padding: 0 2rem;
    list-style: decimal;
  }
  table {
    border-collapse: collapse;
    table-layout: fixed;
    width: 80%;
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
    background: #EAEAEB;
    color: #fff;
    font-family: 'JetBrainsMono', monospace;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;

    code {
      color: #77A0BE;
      // background-color: #FCF5E4;
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

