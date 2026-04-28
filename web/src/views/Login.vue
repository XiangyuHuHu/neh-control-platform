<template>
  <div class="login-page">
    <div class="login-background">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
    </div>
    <div class="login-container">
      <div class="login-left">
        <div class="system-info">
          <div class="logo">
            <el-icon size="48"><OfficeBuilding /></el-icon>
          </div>
          <h1 class="system-name">淖尔壕智能化选煤厂</h1>
          <p class="system-subtitle">Coal Preparation Plant Integrated Management Platform</p>
          <div class="system-features">
            <div class="feature-item">
              <el-icon><TrendCharts /></el-icon>
              <span>智能生产管理</span>
            </div>
            <div class="feature-item">
              <el-icon><Cpu /></el-icon>
              <span>设备监测运维</span>
            </div>
            <div class="feature-item">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据分析洞察</span>
            </div>
            <div class="feature-item">
              <el-icon><MagicStick /></el-icon>
              <span>智能辅助决策</span>
            </div>
          </div>
        </div>
      </div>
      <div class="login-right">
        <div class="login-card">
          <div class="card-header">
            <h2>用户登录</h2>
            <p>请输入您的账号信息</p>
          </div>
          <el-form ref="loginFormRef" :model="loginForm" :rules="rules" class="login-form">
            <el-form-item prop="username">
              <el-input v-model="loginForm.username" placeholder="请输入用户名" size="large" :prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item v-if="showCaptcha" prop="captcha">
              <el-input
                v-model="loginForm.captcha"
                placeholder="请输入验证码"
                size="large"
                :prefix-icon="CircleCheck"
                style="width: 60%"
              />
              <div class="captcha-code" @click="refreshCaptcha">{{ captchaText }}</div>
            </el-form-item>
            <el-form-item>
              <div class="form-options">
                <el-checkbox v-model="loginForm.remember">记住密码</el-checkbox>
                <a href="#" class="forgot-link">忘记密码？</a>
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading" @click="handleLogin" class="login-btn">
                {{ loading ? '登录中...' : '登 录' }}
              </el-button>
            </el-form-item>
          </el-form>
          <div class="card-footer">
            <span>还没有账号？</span>
            <a href="#">联系管理员</a>
          </div>
        </div>
        <div class="login-tips">
          <p>默认账号：admin / admin123（全权限演示）；开启 API 认证后可使用 viewer / viewer123（只读）</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { setApiBasicAuth } from '../api/http'
import {
  CircleCheck,
  Cpu,
  DataAnalysis,
  Lock,
  MagicStick,
  OfficeBuilding,
  TrendCharts,
  User,
} from '@element-plus/icons-vue'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)
const showCaptcha = ref(false)
const captchaText = ref('')

const loginForm = reactive({
  username: '',
  password: '',
  captcha: '',
  remember: false,
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
  ],
}

const generateCaptcha = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
  let result = ''
  for (let i = 0; i < 4; i += 1) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

const refreshCaptcha = () => {
  captchaText.value = generateCaptcha()
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    if (showCaptcha.value && loginForm.captcha.toLowerCase() !== captchaText.value.toLowerCase()) {
      ElMessage.error('验证码错误')
      refreshCaptcha()
      return
    }

    loading.value = true
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))

      const okAdmin = loginForm.username === 'admin' && loginForm.password === 'admin123'
      const okViewer = loginForm.username === 'viewer' && loginForm.password === 'viewer123'
      if (okAdmin || okViewer) {
        setApiBasicAuth(loginForm.username, loginForm.password)
        ElMessage.success('登录成功，欢迎回来')
        router.push('/coal/dashboard')
      } else {
        showCaptcha.value = true
        refreshCaptcha()
        ElMessage.error('用户名或密码错误')
      }
    } catch (error) {
      ElMessage.error('登录失败，请稍后重试')
    } finally {
      loading.value = false
    }
  })
}

refreshCaptcha()
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #0a1628;
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  inset: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 30% 20%, rgba(0,200,255,0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 80%, rgba(0,119,255,0.1) 0%, transparent 50%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(0,200,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,200,255,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.login-container {
  position: relative;
  display: flex;
  min-height: 100vh;
}

.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.system-info {
  text-align: center;
  max-width: 500px;
}

.logo {
  width: 100px;
  height: 100px;
  margin: 0 auto 30px;
  background: linear-gradient(135deg, rgba(0,200,255,0.2), rgba(0,119,255,0.2));
  border: 2px solid rgba(0,200,255,0.3);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #00c8ff;
}

.system-name {
  font-size: 36px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 10px;
  background: linear-gradient(90deg, #00c8ff, #fff, #00c8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-size: 200% 100%;
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%,
  100% {
    background-position: -100% 0;
  }
  50% {
    background-position: 100% 0;
  }
}

.system-subtitle {
  font-size: 14px;
  color: rgba(255,255,255,0.5);
  margin-bottom: 50px;
  letter-spacing: 2px;
}

.system-features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  background: rgba(0,200,255,0.05);
  border: 1px solid rgba(0,200,255,0.1);
  border-radius: 8px;
  color: rgba(255,255,255,0.8);
  font-size: 14px;
  transition: all 0.3s;
}

.feature-item:hover {
  background: rgba(0,200,255,0.1);
  border-color: rgba(0,200,255,0.3);
  transform: translateY(-2px);
}

.feature-item .el-icon {
  font-size: 20px;
  color: #00c8ff;
}

.login-right {
  width: 500px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-card {
  width: 100%;
  background: rgba(0,200,255,0.03);
  border: 1px solid rgba(0,200,255,0.15);
  border-radius: 12px;
  padding: 40px;
  backdrop-filter: blur(10px);
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h2 {
  font-size: 24px;
  color: #00c8ff;
  margin-bottom: 8px;
}

.card-header p {
  font-size: 14px;
  color: rgba(255,255,255,0.5);
}

.login-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(0,200,255,0.2);
  box-shadow: none;
  padding: 8px 15px;
}

.login-form :deep(.el-input__wrapper:hover),
.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #00c8ff;
}

.login-form :deep(.el-input__inner) {
  color: #fff;
  height: 40px;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: rgba(255,255,255,0.4);
}

.login-form :deep(.el-input__prefix .el-icon) {
  color: rgba(255,255,255,0.5);
}

.captcha-code {
  width: 38%;
  height: 40px;
  line-height: 40px;
  background: linear-gradient(135deg, #1a3a5c, #0d1f35);
  border: 1px solid rgba(0,200,255,0.3);
  border-radius: 4px;
  text-align: center;
  color: #00c8ff;
  font-size: 18px;
  font-weight: bold;
  letter-spacing: 4px;
  cursor: pointer;
  margin-left: 2%;
  user-select: none;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.form-options :deep(.el-checkbox__label) {
  color: rgba(255,255,255,0.6);
}

.forgot-link {
  color: #00c8ff;
  text-decoration: none;
  font-size: 14px;
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  background: linear-gradient(135deg, #00c8ff, #0077ff);
  border: none;
  border-radius: 8px;
}

.login-btn:hover {
  background: linear-gradient(135deg, #00d8ff, #0088ff);
}

.card-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0,200,255,0.1);
  color: rgba(255,255,255,0.5);
  font-size: 14px;
}

.card-footer a {
  color: #00c8ff;
  text-decoration: none;
  margin-left: 5px;
}

.card-footer a:hover {
  text-decoration: underline;
}

.login-tips {
  margin-top: 20px;
  padding: 10px 20px;
  background: rgba(0,200,255,0.05);
  border: 1px solid rgba(0,200,255,0.1);
  border-radius: 6px;
}

.login-tips p {
  color: rgba(255,255,255,0.4);
  font-size: 12px;
  text-align: center;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #00c8ff;
  border-color: #00c8ff;
}
</style>
