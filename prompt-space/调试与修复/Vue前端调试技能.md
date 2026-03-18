# 🛠️ Claude Code Skill: Vue 3 前端调试

**适用场景**：Vue 组件错误、路由问题、状态管理异常

---

## 1. 适用场景

- Vue 组件渲染错误
- Pinia 状态管理问题
- Vue Router 路由异常
- API 请求失败
- 组件通信问题

---

## 2. 前置条件

```bash
# 检查 Node.js 版本
node -v  # 应 >= 18.0.0

# 检查依赖安装
npm install

# 启动开发服务器
npm run dev
```

---

## 3. 执行步骤

### Step 1: 浏览器开发者工具配置

```javascript
// 安装 Vue DevTools 浏览器扩展
// Chrome: Vue.js devtools
// Firefox: Vue.js devtools

// 开启 Source Map (vite.config.js)
export default defineConfig({
  build: {
    sourcemap: true
  }
})
```

### Step 2: 开启 Vue 错误捕获

```javascript
// main.js
const app = createApp(App)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('全局错误:', err)
  console.error('组件:', instance)
  console.error('信息:', info)
}

// 警告处理
app.config.warnHandler = (msg, instance, trace) => {
  console.warn('Vue 警告:', msg)
  console.warn('组件:', instance)
  console.warn('追踪:', trace)
}

app.use(createPinia())
app.use(router)
app.mount('#app')
```

### Step 3: 检查 API 请求封装

```javascript
// utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  timeout: 15000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 200 || res.code === '0') {
      return res
    }
    ElMessage.error(res.msg || '请求失败')
    return Promise.reject(new Error(res.msg || '请求失败'))
  },
  (error) => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default request
```

### Step 4: 检查 Pinia 状态管理

```javascript
// stores/user.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getProfile } from '@/api/user'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref({})
  const isLoggedIn = computed(() => !!token.value)

  // Actions
  async function doLogin(credentials) {
    const res = await login(credentials)
    token.value = res.data.token
    localStorage.setItem('token', token.value)

    // 获取用户信息
    await fetchUserInfo()

    return res
  }

  async function fetchUserInfo() {
    const res = await getProfile()
    userInfo.value = res.data
  }

  function doLogout() {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    router.push('/login')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    doLogin,
    fetchUserInfo,
    doLogout
  }
})
```

### Step 5: 检查 Vue Router 配置

```javascript
// router/index.js
const router = createRouter({
  history: createWebHistory(),
  routes: [
    // ...路由配置
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 需要登录的路由
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
    return
  }

  // 已登录用户访问登录页
  if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
    return
  }

  next()
})

export default router
```

### Step 6: 常见问题排查

#### 问题1: `Cannot read properties of undefined`
```vue
<script setup>
// 使用可选链操作符
const userName = userInfo.value?.name || '未登录'

// 或使用 v-if 条件渲染
<template v-if="userInfo">
  {{ userInfo.name }}
</template>
</script>
```

#### 问题2: Pinia store 为空
```javascript
// 确保在 setup 外部使用
const userStore = useUserStore()  // ❌ 错误：在 setup 外
const userStore = useUserStore()  // ✅ 正确：在 setup 内
```

#### 问题3: API 请求 401
```javascript
// 检查 Token 是否正确传递
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

---

## 4. 验证方法

- [ ] Vue DevTools 能够正常显示组件树
- [ ] Pinia 状态正确显示
- [ ] API 请求能够正确发送和接收
- [ ] 路由跳转正常
- [ ] 错误信息在控制台清晰显示

---

## 5. 常见问题 (FAQ)

**Q: 组件更新但不渲染?**
A: 使用 ` reactive()` 或 `ref()` 包裹数据，避免直接修改对象属性

**Q: API 跨域问题?**
A: 配置 Vite proxy 或后端 CORS

**Q: 如何调试异步操作?**
A: 在 Chrome DevTools 中使用 Async 标签页

---

## 6. 相关资源

- [Vue 3 文档](https://vuejs.org/)
- [Pinia 文档](https://pinia.vuejs.org/)
- [Vue Router 文档](https://router.vuejs.org/)

---

## 执行指令

> 请执行 **Vue前端调试技能**，诊断并修复前端问题：{具体错误描述}
