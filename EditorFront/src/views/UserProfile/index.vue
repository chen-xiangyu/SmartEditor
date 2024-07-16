<template>
  <el-menu mode="horizontal" :ellipsis="false">
    <!-- <div class="flex-grow" /> -->
    
    <el-menu-item @click="gotoEditor()">
      <svg class="remix">
        <use :xlink:href="`${remixiconUrl}#ri-${'arrow-left-s-line'}`" />
      </svg>
      返回编辑器
    </el-menu-item>
  </el-menu>
  <div class="account bg-light">
    <h2>个人信息</h2>
    <el-form ref="formRef" :model="formInfo" :rules="rules" label-width="auto">
      <el-form-item label="账号" prop="account">
        <el-input v-model="formInfo.account" autocomplete="off" disabled />
      </el-form-item>
      <el-form-item label="旧密码" prop="oldPassword" :error="oldPasswordError">
        <el-input v-model="formInfo.oldPassword" type="password" autocomplete="off" />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="formInfo.newPassword" type="password" autocomplete="off" />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword" class="input-button">
        <el-input v-model="formInfo.confirmPassword" type="password" autocomplete="off" />
        <el-button type="primary" @click="modifyPassword(formRef)">
          修改密码
        </el-button>
      </el-form-item>
      <el-form-item label="访问令牌" prop="AccessToken" class="input-button">
        <el-input v-model="formInfo.AccessToken" autocomplete="off" />
        <el-button type="primary" @click="setAccessToken()">
          设置访问令牌
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts" name="UserProfile">
  import { reactive, ref, onMounted } from 'vue'
  import type { FormInstance, FormRules } from 'element-plus'
  import { ElMessage } from 'element-plus'
  import remixiconUrl from 'remixicon/fonts/remixicon.symbol.svg'
  import axios from 'axios'
  import {RouterView,RouterLink,useRouter} from 'vue-router'

  const router = useRouter()

  const formRef = ref<FormInstance>()
  const formInfo = reactive({
    account: '',
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
    AccessToken: '',
  })

  let oldPasswordError = ref('')

  const validateOldPassword = (rule: any, value: any, callback: any) => {
    if (value === '') {
      // callback(new Error('请输入新密码'))
    } else {
      callback()
    }
  }
  const validateNewPassword = (rule: any, value: any, callback: any) => {
    if (value === '') {
      // callback(new Error('请输入新密码'))
    } else if (value === formInfo.oldPassword) {
      callback(new Error('新密码要与旧密码不同'));
    } else {
      callback()
    }
  }
  const validateConfirmPassword = (rule: any, value: any, callback: any) => {
    if (value === '') {
      // callback(new Error('请输入确认密码'))
    } else if (value !== formInfo.newPassword) {
      callback(new Error('两次输入的密码不一致'));
    } else {
      callback();
    }
  }
  const rules = reactive<FormRules<typeof formInfo>>({
    oldPassword: [{ validator: validateOldPassword, trigger: 'change' }],
    newPassword: [{ validator: validateNewPassword, trigger: 'change' }],
    confirmPassword: [{ validator: validateConfirmPassword, trigger: 'change' }],
  })

  function clearInput()
  {
    formInfo.oldPassword = ''
    formInfo.newPassword = ''
    formInfo.confirmPassword = ''
  }

  async function modifyPassword(formEl: FormInstance | undefined){
    if (!formEl) return

    oldPasswordError.value = ''

    formEl.validate(async (valid) => {
      if (valid) {
        let data = {
          oldPassword: formInfo.oldPassword,
          newPassword: formInfo.newPassword,
        }
        console.log('submit!')
        let res = await sendRequest(data, '/modify-password/')
        console.log("sign up", res)
        if (res.status) 
        {
          formInfo.oldPassword = ''
          formInfo.newPassword = ''
          formInfo.confirmPassword = ''

          ElMessage({
            message: res.message,
            type: 'success',
          })
          console.log("成功")
        }
        else oldPasswordError.value = res.error
      } else {
        console.log('error submit!')
      }
    })
  }


  async function sendRequest(data: any, url: any) {

    try {
      console.log("开始发请求", data)
      const response = await axios.post(
        url,
        JSON.stringify(data),
      )
      console.log('POST 请求成功：', response.data)
      return response.data
    } catch (error) {
      console.error('POST 请求失败：', error)
      throw error // 可选的抛出错误
    }
  }
  async function setAccessToken(){
    try {
      console.log("on mounted")
      let data = {
        accessToken: formInfo.AccessToken,
      }
      const response = await axios.post(
        '/set-access-token/',
        JSON.stringify(data),
      )
      // accountError.value = response.data.error
      let res = response.data
      if (res.status){
        ElMessage({
          message: res.message,
          type: 'success',
        })
      } else{
        console.log(res.error)
      }
      console.log('POST 请求成功：', response.data)
      
    } catch (error) {
      console.error('POST 请求失败：', error)
      // throw error // 可选的抛出错误
    }
  }
  onMounted(async() => {
    try {
      console.log("on mounted")
      const response = await axios.post(
        '/user-profile/',
      )
      // accountError.value = response.data.error
      let res = response.data
      if (res.status){
        formInfo.account = res.account,
        formInfo.AccessToken = res.accessToken
      } else{
        console.log(res.error)
      }
      console.log('POST 请求成功：', response.data)
      
    } catch (error) {
      console.error('POST 请求失败：', error)
      // throw error // 可选的抛出错误
    }
  })

  function gotoEditor(){
    router.push({
      path: '/editor',
    })
  }
</script>

<style lang="scss" scoped>
  .account {
    width: 600px;
    border: 1px solid #dddddd;
    border-radius: 30px;
    box-shadow: 10px 10px 20px #aaa;

    margin: 100px auto;
    padding: 20px 40px;
  }

  .account h2 {
    margin-top: 10px;
    margin-bottom: 15px;
    text-align: center;
    font-size: 2em;
    font-family: 'KaiTi', sans-serif;
  }

  .input-button {
    display: flex; /* 使用Flexbox布局 */
    align-items: center; /* 垂直居中对齐 */
  }
  .input-button .el-input {
    flex: 1; /* 输入框自动填充剩余空间 */
    margin-right: 10px; /* 可选：增加右侧间距 */
  }
  .remix {
    fill: currentColor;
    width: 1.5rem;
    height: 1.5rem;
  }
</style>