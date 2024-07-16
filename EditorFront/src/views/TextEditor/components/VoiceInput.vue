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

  const props = defineProps<{ getVoiceResult: Function }>()
  const recwave = ref(null)
  let rec = null
  let wave = null
  let recBlob = null

  const recOpen = () => {
    rec = Recorder({
      type: 'wav',
      sampleRate: 16000,
      bitRate: 16,
      onProcess: (buffers, powerLevel, bufferDuration, bufferSampleRate, newBufferIdx, asyncEnd) => {
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
    rec.stop(
      (blob, duration) => {
        recBlob = blob
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
      } else{
        console.log(res.error)
      }
      console.log('POST 请求成功：', response.data)
    } catch (error) {
      console.error('POST 请求失败：', error)
    }
  }

</script>

<style lang="scss" scoped>

</style>