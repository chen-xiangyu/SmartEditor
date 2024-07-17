<template>
  <div class="container">
    <AuthForm/>
  </div>
</template>

<script lang="ts" setup name="Login">
  import { reactive, ref } from 'vue'
  import type { FormInstance, FormRules } from 'element-plus'
  import axios from 'axios'
  // import { sinkListItem } from '@tiptap/pm/schema-list';
  import AuthForm from './components/AuthForm.vue'

  const signUpFormRef = ref<FormInstance>()
  const signUpForm = reactive({
    account: '',
    password: '',
  })
  let accountError = ref("")

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
  const rules = reactive<FormRules<typeof signUpForm>>({
    account: [{ validator: validateAccount, trigger: 'blur' }],
    password: [{ validator: validatePassword, trigger: 'blur' }],
  })

  function submitForm(formEl: FormInstance | undefined) {
    if (!formEl) return
    formEl.validate((valid) => {
      if (valid) {
        // account.validateState="error";
			  // account.validateMessage="erroraa";
        console.log('submit!')
        sendRequest()
      } else {
        console.log('error submit!')
      }
    })
    
  }
  async function sendRequest() {
    try {
      let data = {
        account: signUpForm.account,
        password: signUpForm.password
      }
      console.log("开始发请求", data)
      
      const response = await axios.post(
        'http://127.0.0.1:8000/index/',
        JSON.stringify(data),
      )
      accountError.value = response.data.error
      console.log('POST 请求成功：', response.data)
      return response.data // 可选的返回数据
    } catch (error) {
      console.error('POST 请求失败：', error)
      throw error // 可选的抛出错误
    }
  }
  
</script>

<style lang="scss" scoped>
  .container {
    display: flex;
    justify-content: flex-end; /* 将元素靠右对齐 */
    align-items: center; /* 垂直居中 */
    height: 100vh;
    background-image: url('@/assets/images/background.jpg');
    background-size: 100% 100%; /* 设置背景图片宽度和高度均为100% */
    background-position: center; /* 控制背景图片的位置，center表示居中 */
    background-repeat: no-repeat; /* 防止背景图片重复 */
  }

  .account {
    width: 400px;
    border: 1px solid #dddddd;
    border-radius: 30px;
    box-shadow: 10px 10px 20px #aaa;
    padding: 20px 40px;
    // background-color: #fff;
    background-color: rgba(255, 255, 255, 0.7);
    margin-right: 100px;
  }

  .account h2 {
    margin-top: 10px;
    margin-bottom: 15px;
    text-align: center;
    font-size: 2em;
    font-family: 'KaiTi', sans-serif;
  }
</style>
