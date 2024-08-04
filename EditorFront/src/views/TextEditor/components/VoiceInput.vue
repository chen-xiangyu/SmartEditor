<template>
  <div>
    <div>
      <!-- 按钮 -->
      <el-button type="primary" @click="recOpen">打开录音, 请求权限</el-button>
      <el-button type="success" @click="recStart">开始录音</el-button>
      <el-button type="warning" @click="recStop">结束录音</el-button>
    </div>
    <div style="padding-top: 5px">
      <!-- 波形绘制区域 -->
      <div style="border: 1px solid #ccc; display: inline-block; vertical-align: bottom">
        <div style="height: 100px; width: 300px;" ref="recwave"></div>
      </div>
    </div>
    <!-- <div style="padding: 10px;">
      <el-text class="mx-1" style="font-size: 25px;" type="warning">注意事项:</el-text> <br>
      <el-text class="mx-1">由于浏览器安全策略限制, http使用录音功能需要进行如下设置：</el-text><br>
      <el-text class="mx-1">&nbsp;&nbsp;&nbsp;&nbsp;Chrome/Edge (即Chromium内核浏览器): 访问chrome://flags/#unsafely-treat-insecure-origin-as-secure, 启用此项, 并在文本框中填入http://113.45.217.227</el-text><br>
      <el-text class="mx-1">&nbsp;&nbsp;&nbsp;&nbsp;Firefox: 访问about:config, 勾选"当我尝试修改底层首选项时警示我", 点击"接受风险并继续"。搜索框输入insecure, 然后回车搜索相关设置选项, media.devices.insecure.enabled改为true, media.getusermedia.insecure.enabled改为true。重新访问113.45.217.227即可。</el-text><br>
    </div> -->
    <div style="padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px;">
      <el-text class="mx-1" style="font-size: 20px; color: #f56c6c;" type="warning">注意事项:</el-text> 
      <br><br>
      <el-text class="mx-1" style="font-size: 12px;">由于浏览器安全策略限制, http使用录音功能需要进行如下设置：</el-text>
      <br><br>
      <el-text class="mx-1" style="font-size: 12px;">&nbsp;&nbsp;&nbsp;&nbsp;Chrome/Edge (即Chromium内核浏览器): 访问 <code style="background-color: #f2f2f2; padding: 2px 4px; border-radius: 4px;">chrome://flags/#unsafely-treat-insecure-origin-as-secure</code>, 启用此项, 并在文本框中填入 <code style="background-color: #f2f2f2; padding: 2px 4px; border-radius: 4px;">http://113.45.217.227</code></el-text>
      <br><br>
      <el-text class="mx-1" style="font-size: 12px;">&nbsp;&nbsp;&nbsp;&nbsp;Firefox: 访问 <code style="background-color: #f2f2f2; padding: 2px 4px; border-radius: 4px;">about:config</code>, 勾选 "当我尝试修改底层首选项时警示我", 点击 "接受风险并继续"。搜索框输入 <code style="background-color: #f2f2f2; padding: 2px 4px; border-radius: 4px;">insecure</code>, 然后回车搜索相关设置选项, <code style="background-color: #f2f2f2; padding: 2px 4px; border-radius: 4px;">media.devices.insecure.enabled</code> 改为 true, <code style="background-color: #f2f2f2; padding: 2px 4px; border-radius: 4px;">media.getusermedia.insecure.enabled</code> 改为 true。重新访问 113.45.217.227 即可。</el-text>
    </div>

  </div>
</template>

<script setup lang="ts" name="VoiceInput">
  import { ref } from 'vue'
  import Recorder from 'recorder-core'
  // import 'recorder-core/src/engine/mp3'
  // import 'recorder-core/src/engine/mp3-engine'
  import 'recorder-core/src/engine/wav'
  import 'recorder-core/src/extensions/waveview'
  import axios from "axios"
  import { ElMessage } from 'element-plus'

  const props = defineProps<{ 
    getVoiceResult: Function;
    showLoader: Function;
    closeLoader: Function;
    coins: number,
    fetchCoins: Function,
  }>()
  const recwave = ref(null)
  let rec = null
  let wave = null
  // let recBlob = null

  const recOpen = () => {
    rec = Recorder({
      type: 'wav',
      sampleRate: 16000,
      bitRate: 16,
      onProcess: (buffers, powerLevel, _bufferDuration, bufferSampleRate, _newBufferIdx, _asyncEnd) => {
        if (wave) wave.input(buffers[buffers.length - 1], powerLevel, bufferSampleRate)
      },
    })

    rec.open(
      () => {
        ElMessage({
          message: '成功获取权限，可以开始录音',
          type: 'success',
          plain: true,
        })
        console.log('录音已打开')
        if (recwave.value) {
          wave = Recorder.WaveView({ elem: recwave.value })
        }
      },
      (msg, isUserNotAllow) => {
        ElMessage({
          message: '无法获取权限，不能开始录音',
          type: 'error',
          plain: true,
        })
        console.log((isUserNotAllow ? 'UserNotAllow，' : '') + '无法录音:' + msg)
      }
    )
  }

  const recStart = () => {
    if (!rec) {
      console.error('未打开录音')
      return
    }
    rec.start()
    console.log('已开始录音')
  }

  const recStop = () => {
    if (!rec) {
      console.error('未打开录音')
      return
    }
    if (props.coins == 0) {
      ElMessage.error('硬币数量为0，无法使用AI功能，请尽快充值.')
      return 
    }
    rec.stop(
      (blob, duration) => {
        // recBlob = blob
        const localUrl = (window.URL || webkitURL).createObjectURL(blob)
        console.log('录音成功', blob, localUrl, '时长:' + duration + 'ms')
        ElMessage({
          message: '成功上传，稍后返回语音识别的结果',
          type: 'success',
          plain: true,
        })
        upload(blob)
        rec.close()
        rec = null
      },
      (err) => {
        console.error('结束录音出错：' + err)
        rec.close()
        rec = null
      }
    )
  }

  const upload = async (blob: any) => {
    try {
      console.log("on mounted")
      const formData = new FormData()
      formData.append('file', blob, 'voice.wav')
      props.showLoader()
      const response = await axios.post(
        `/voice-recognise/`,
        formData,
      )
      let res = response.data
      console.log(res)
      if (res.status){
        // // console.log(res.answer)
        // cardMsg.value = res.answer
        // isMultiMedia.value = true
        // visibleCard.value = true
        props.getVoiceResult(res.answer)
        props.fetchCoins()
      } else{
        ElMessage.error('非常抱歉，AI的回复在来的路上丢失了，请重新操作')
        console.log(res.error)
      }
      props.closeLoader()
      console.log('POST 请求成功：', response.data)
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
  }

</script>

<style lang="scss" scoped>
.mx-1 {
  margin-left: 0.25rem;
  margin-right: 0.25rem;
}
</style>