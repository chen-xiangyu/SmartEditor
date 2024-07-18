import { createApp } from 'vue'

import App from './App.vue'
import router from './router/index'
import { createPinia } from 'pinia'
import axios from 'axios'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const pinia=createPinia()
const app = createApp(App)



axios.defaults.baseURL = 'http://localhost:8000';  // 替换成你的后端服务地址
axios.interceptors.request.use(
    config => {
      // 从 localStorage 获取用户名和 token
      const account = localStorage.getItem('account');
      const token = localStorage.getItem('token'); // 假设这里的 token 变量名与后端使用的一致
  
      // 如果用户名和 token 都存在，则设置请求头
      if (account && token) {
        // config.headers.common['Token'] = `Bearer ${token}`;
        // config.headers.common['Account'] = account;
        config.headers['Token'] = token;
        config.headers['Account'] = account;
      }
      return config;
    },
    error => {
      return Promise.reject(error);
    }
  );
app.use(router)
app.use(pinia)
app.use(ElementPlus)
app.mount('#app')
