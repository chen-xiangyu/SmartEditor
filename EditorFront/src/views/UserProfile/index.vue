<template>
  <div class="page-container">
    <el-menu mode="horizontal" :ellipsis="false" style="background-color: #FCF5E4;" class="menu">
      <!-- <div class="flex-grow" /> -->
      <el-menu-item @click="gotoEditor()">
        <svg class="remix">
          <use :xlink:href="`${remixiconUrl}#ri-${'arrow-left-s-line'}`" />
        </svg>
        返回编辑器
      </el-menu-item>
    </el-menu>
    <div class="account-container">
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
    </div>
  </div>
</template>

<script setup lang="ts" name="UserProfile">
  import { reactive, ref, onMounted } from 'vue'
  import type { FormInstance, FormRules } from 'element-plus'
  import { ElMessage } from 'element-plus'
  import remixiconUrl from 'remixicon/fonts/remixicon.symbol.svg'
  import axios from 'axios'
  import {useRouter} from 'vue-router'

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

  const validateOldPassword = (_rule: any, value: any, callback: any) => {
    if (value === '') {
      // callback(new Error('请输入新密码'))
    } else {
      callback()
    }
  }
  const validateNewPassword = (_rule: any, value: any, callback: any) => {
    if (value === '') {
      // callback(new Error('请输入新密码'))
    } else if (value === formInfo.oldPassword) {
      callback(new Error('新密码要与旧密码不同'));
    } else {
      callback()
    }
  }
  const validateConfirmPassword = (_rule: any, value: any, callback: any) => {
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

  // function clearInput()
  // {
  //   formInfo.oldPassword = ''
  //   formInfo.newPassword = ''
  //   formInfo.confirmPassword = ''
  // }

  async function modifyPassword(formEl: FormInstance | undefined){
    if (!formEl) return

    oldPasswordError.value = ''

    formEl.validate(async (valid) => {
      if (valid) {
        const formData = new FormData()
        formData.append('oldPassword', formInfo.oldPassword)
        formData.append('newPassword', formInfo.newPassword)
        console.log('submit!')
        let res = await sendRequest(formData, '/modify-password/')
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


  async function sendRequest(formData: any, url: any) {

    try {
      console.log("开始发请求", formData)
      const response = await axios.post(
        url,
        formData,
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
      const formData = new FormData()
      formData.append('accessToken', formInfo.AccessToken)
      const response = await axios.post(
        '/set-access-token/',
        formData,
      )
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
  .page-container {
    width: 100vw;
    height: 100vh;
    background-color: #E9E3D3;
  }
  .account-container {
    padding-top: 5%;
  }
  .account {
    width: 40%;
    border: 1px solid #dddddd;
    border-radius: 30px;
    box-shadow: 10px 10px 20px #aaa;
    background-color: rgba($color: #fff, $alpha: 0.6);
    margin: 0 auto;
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