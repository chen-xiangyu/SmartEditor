<template>
  <div class="account bg-light">
    <h2 v-if="isSignUp">注册</h2>
    <h2 v-else>登录</h2>
    <el-form ref="formRef" :model="formInfo" :rules="rules" label-width="auto">
      <el-form-item label="账号" prop="account" :error="accountError">
        <el-input v-model="formInfo.account" autocomplete="off" />
      </el-form-item>
      <el-form-item label="密码" prop="password" :error="passwordError">
        <el-input v-model="formInfo.password" type="password" autocomplete="off" />
      </el-form-item>
      <el-form-item v-if="isSignUp" label="确认密码" prop="confirmPassword">
        <el-input v-model="formInfo.confirmPassword" type="password" autocomplete="off" />
      </el-form-item>
      <el-form-item>
        <template v-if="isSignUp">
          <el-button type="primary" @click="signUp(formRef)">
            注册
          </el-button>
          <el-button type="info" @click="isSignUp = false, clearInput()">
            去登录
          </el-button>
        </template>
        <template v-else>
          <el-button type="primary" @click="signIn(formRef)">
            登录
          </el-button>
          <el-button type="info" @click="isSignUp = true, clearInput()">
            去注册
          </el-button>
        </template>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts" name="AuthForm">
  import { reactive, ref } from 'vue'
  import type { FormInstance, FormRules } from 'element-plus'
  import axios from 'axios'
  import {RouterView,RouterLink,useRouter} from 'vue-router'
  import { json } from 'stream/consumers';

  const router = useRouter()
  let isSignUp = ref(false)

  const formRef = ref<FormInstance>()
  const formInfo = reactive({
    account: '',
    password: '',
    confirmPassword: '',
  })
  let accountError = ref('')
  let passwordError = ref('')

  const validateAccount = (rule: any, value: any, callback: any) => {
    if (value === '') {
      callback(new Error('请输入账号'))
    } else {
      callback()
    }
  }
  const validatePassword = (rule: any, value: any, callback: any) => {
    if (value === '') {
      callback(new Error('请输入密码'))
    } else {
      callback()
    }
  }
  const validateConfirmPassword = (rule: any, value: any, callback: any) => {
    if (value === '') {
      callback(new Error('请输入确认密码'))
    } else if (value !== formInfo.password) {
      callback(new Error('两次输入的密码不一致'));
    } else {
      callback();
    }
  }
  const rules = reactive<FormRules<typeof formInfo>>({
    account: [{ validator: validateAccount, trigger: 'change' }],
    password: [{ validator: validatePassword, trigger: 'change' }],
    confirmPassword: [{ validator: validateConfirmPassword, trigger: 'change' }],
  })

  function clearInput()
  {
    formInfo.account = ''
    formInfo.password = ''
    formInfo.confirmPassword = ''
  }

  async function signUp(formEl: FormInstance | undefined) {
    if (!formEl) return

    formEl.validate(async (valid) => {
      if (valid) {
        let data = {
          account: formInfo.account,
          password: formInfo.password,
        }
        console.log('submit!')
        let res = await sendRequest(data, '/sign-up/')
        console.log("sign up", res)
        if (res.status) 
        {
          localStorage.setItem("account", res.account);
          localStorage.setItem("token", res.token);
          router.replace({
            path: '/editor',
          })
          console.log("成功")
        }
        else {
          if (res.etype === 1) accountError.value = res.error
          else if (res.etype === 2) passwordError.value = res.error
        }
      } else {
        console.log('error submit!')
      }
    })
  }
  async function signIn(formEl: FormInstance | undefined) {
    if (!formEl) return

    formEl.validate(async (valid) => {
      if (valid) {
        let data = {
          account: formInfo.account,
          password: formInfo.password,
        }
        console.log('submit!')
        let res = await sendRequest(data, '/sign-in/')
        console.log("sign in", res)
        if (res.status) 
        {
          localStorage.setItem("account", res.account);
          localStorage.setItem("token", res.token);
          router.replace({
            path: '/editor',
          })
          console.log("成功")
        }
        else {
          if (res.etype === 1) accountError.value = res.error
          else if (res.etype === 2) passwordError.value = res.error
        }
      } else {
        console.log('error submit!')
      }
    })
  }

  async function sendRequest(data: any, url: any) {
    accountError.value = ''
    passwordError.value = ''
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
</script>
  
<style lang="scss" scoped>
  .account {
    width: 400px;
    border: 1px solid #dddddd;
    border-radius: 30px;
    box-shadow: 10px 10px 20px #aaa;

    float: right;
    margin-right: 100px;
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
</style>