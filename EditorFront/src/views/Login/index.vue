<template>
  <div class="container">
    <AuthForm class="auth-form"/>
  </div>
</template>

<script lang="ts" setup name="Login">
  import AuthForm from './components/AuthForm.vue'
</script>

<style lang="scss" scoped>
  .container {
    display: flex;
    justify-content: flex-end; /* 将元素靠右对齐 */
    align-items: center; /* 垂直居中 */
    height: 100vh;
    width: 100vw;
    background-image: url('@/assets/images/background.jpg');
    background-size: 100% 100%; /* 设置背景图片宽度和高度均为100% */
    background-position: center; /* 控制背景图片的位置，center表示居中 */
    background-repeat: no-repeat; /* 防止背景图片重复 */
  }
  
  .auth-form {
    margin-right: 5%;
  }
</style>
