<template>
  <div class="portal-home">
    <header class="hero-shell">
      <div class="hero-copy">
        <p class="eyebrow">Coal Operations Command</p>
        <img :src="jinhaizediLogo" alt="淖尔壕智能化选煤厂" class="hero-logo" />
        <h1>淖尔壕智能化选煤厂</h1>
        <p class="hero-summary">旧版业务风入口，侧重表格、台账、录入和报表，适合功能核对与流程演示。</p>
        <div class="metric-row">
          <article v-for="item in coreMetrics" :key="item.label" class="metric-card">
            <span class="metric-label">{{ item.label }}</span>
            <strong class="metric-value">{{ item.value }}</strong>
            <small class="metric-note">{{ item.note }}</small>
          </article>
        </div>
        <div class="hero-actions">
          <router-link class="primary-link" to="/coal/dashboard">进入监控中心</router-link>
          <router-link class="secondary-link" to="/coal/production">查看生产管理</router-link>
        </div>
      </div>

      <div class="hero-panel">
        <div class="panel-topline">
          <span class="status-dot"></span>
          <span>实时运行总览</span>
        </div>
        <div class="time-cluster">
          <div class="time-text">{{ currentTime }}</div>
          <div class="date-text">{{ currentDate }}</div>
        </div>
        <div class="quick-status">
          <div v-for="item in runtimeStatus" :key="item.label" class="runtime-pill">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </div>
    </header>

    <main class="content-shell">
      <section class="section-card">
        <div class="section-head">
          <div>
            <span class="section-tag">Quick Entry</span>
            <h2>核心业务入口</h2>
          </div>
          <p>保留原始业务风格页面，优先覆盖常用管理模块。</p>
        </div>

        <div class="entry-grid">
          <router-link v-for="item in primaryEntries" :key="item.path" :to="item.path" class="entry-card">
            <div class="entry-body">
              <strong>{{ item.title }}</strong>
              <span>{{ item.desc }}</span>
            </div>
          </router-link>
        </div>
      </section>

      <section class="section-card">
        <div class="section-head">
          <div>
            <span class="section-tag">Main Modules</span>
            <h2>专题业务页面</h2>
          </div>
          <p>原有主要业务模块页面。</p>
        </div>

        <div class="topic-grid">
          <router-link v-for="item in topicEntries" :key="item.path" :to="item.path" class="topic-card">
            <div class="topic-title">{{ item.title }}</div>
            <p>{{ item.desc }}</p>
          </router-link>
        </div>
      </section>

      <section class="section-card extension-card">
        <div class="section-head">
          <div>
            <span class="section-tag">Extended Modules</span>
            <h2>扩展功能页面</h2>
          </div>
          <p>按功能清单补齐的扩展业务页，先完成页面、交互和演示数据，再逐步接入正式数据。</p>
        </div>

        <div class="topic-grid extension-grid">
          <router-link v-for="item in extensionEntries" :key="item.path" :to="item.path" class="topic-card">
            <div class="topic-title">{{ item.title }}</div>
            <p>{{ item.desc }}</p>
          </router-link>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import jinhaizediLogo from '../assets/jinhaizedi-logo.svg'
import { getPortalMetrics, type PortalMetricItem } from '../api/dashboard'

const currentTime = ref('')
const currentDate = ref('')

const runtimeStatus = [
  { label: '设备完好率', value: '98.5%' },
  { label: '质量达标率', value: '96.8%' },
  { label: '能耗偏差', value: '-2.3%' },
]

const fallbackCoreMetrics: PortalMetricItem[] = [
  { label: '今日入洗量', value: '5,200 t', note: '较昨日 +4.2%' },
  { label: '精煤产量', value: '3,400 t', note: '达成率 97.1%' },
  { label: '实时总功率', value: '850 kW', note: '峰段负荷可控' },
  { label: '当前排队车辆', value: '12 辆', note: '平均等待 16 分钟' },
]
const coreMetrics = ref<PortalMetricItem[]>(fallbackCoreMetrics)

const primaryEntries = [
  { path: '/coal/dashboard', title: '监控中心', desc: '总览、告警、关键指标和生产大屏' },
  { path: '/coal/production', title: '生产管理', desc: '计划、执行、工艺与统计' },
  { path: '/coal/equipment', title: '设备管理', desc: '设备台账、状态和维护' },
  { path: '/coal/quality', title: '质量管理', desc: '灰分、水分、硫分和分析' },
]

const topicEntries = [
  { path: '/coal/storage', title: '储装管理', desc: '入厂、销售、装车和库存' },
  { path: '/coal/energy', title: '消耗大屏', desc: '水、电、介质、药剂对比' },
  { path: '/coal/dispatch', title: '调度管理', desc: '当班事项、事故记录和遗留问题' },
  { path: '/coal/decision', title: '智能决策', desc: '工艺评估、预测与建议输出' },
  { path: '/coal/monitor', title: '平台监测', desc: '人员、环境、接口与性能监测' },
  { path: '/coal/settings', title: '系统设置', desc: '用户、角色、点位和审计' },
]

const extensionEntries = [
  { path: '/coal/process-flow', title: '工艺流程专项', desc: '节点状态、负荷、告警和处置建议' },
  { path: '/coal/safety-health', title: '安全与健康', desc: '人员安全、风险分级和健康闭环' },
  { path: '/coal/process-check', title: '生产技术检查', desc: '检查台账、工艺稽核与实验记录联动' },
  { path: '/coal/material-tracking', title: '原材料跟踪', desc: '入库、领用、出库和库存追踪' },
  { path: '/coal/quality-report', title: '质量报表', desc: '日报、周报、月报统一输出' },
  { path: '/coal/medium', title: '介质消耗', desc: '介耗统计、异常提醒和报表' },
  { path: '/coal/reagent', title: '药剂消耗', desc: '药剂用量、单耗和时段对比' },
  { path: '/coal/water', title: '水消耗', desc: '补水汇总、历史统计和异常提示' },
  { path: '/coal/power', title: '电力消耗', desc: '配电状态、电耗和告警' },
  { path: '/coal/grease', title: '油脂消耗', desc: '润滑领用、班报月报和异常追踪' },
  { path: '/coal/air', title: '用风量', desc: '风量采集、单耗测算和考核支撑' },
  { path: '/coal/planning', title: '生产计划统计', desc: '计划执行、指标汇总和报表' },
  { path: '/coal/mechanical', title: '机电设备管理', desc: '档案、动态数据和问题闭环' },
]

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    weekday: 'long',
  })
}

const loadPortalMetrics = async () => {
  try {
    const data = await getPortalMetrics()
    coreMetrics.value = data.metrics?.length ? data.metrics : fallbackCoreMetrics
  } catch {
    coreMetrics.value = fallbackCoreMetrics
  }
}

let timer = 0

onMounted(() => {
  updateTime()
  timer = window.setInterval(updateTime, 1000)
  loadPortalMetrics()
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style scoped>
.portal-home {
  min-height: 100vh;
  padding: 20px;
  background:
    radial-gradient(circle at top right, rgba(73, 146, 214, 0.14), transparent 22%),
    linear-gradient(180deg, #dde4ec 0%, #d1dae4 100%) !important;
  color: #16344e;
}

.hero-shell,
.section-card {
  width: min(100%, 1760px);
  margin: 0 auto 20px;
  border: 1px solid rgba(143, 163, 186, 0.38);
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(238, 242, 247, 0.96) 0%, rgba(230, 236, 243, 0.96) 100%) !important;
  box-shadow: 0 18px 40px rgba(77, 101, 126, 0.14);
}

.hero-shell {
  display: grid;
  grid-template-columns: 1.4fr 0.9fr;
  gap: 24px;
  padding: 28px;
}

.eyebrow,
.section-tag {
  margin: 0 0 10px;
  color: #3c73d6;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.hero-logo {
  width: 180px;
  margin-bottom: 10px;
}

.hero-copy h1 {
  margin: 0;
  font-size: 38px;
}

.hero-summary {
  max-width: 720px;
  color: rgba(38, 69, 97, 0.7);
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.metric-row {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(4, minmax(130px, 1fr));
  gap: 12px;
  max-width: 780px;
}

.metric-card {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(72, 123, 190, 0.2);
  background: linear-gradient(180deg, rgba(233, 240, 248, 0.94), rgba(223, 234, 245, 0.94));
}

.metric-label {
  display: block;
  color: #4f6d8e;
  font-size: 12px;
}

.metric-value {
  display: block;
  margin-top: 8px;
  font-size: 24px;
  color: #184f86;
  line-height: 1.2;
}

.metric-note {
  display: block;
  margin-top: 8px;
  color: #587aa3;
  font-size: 12px;
}

.primary-link,
.secondary-link {
  padding: 14px 18px;
  border-radius: 14px;
  text-decoration: none;
}

.primary-link {
  background: linear-gradient(135deg, #257cff, #21b7ff);
  color: #ffffff;
}

.secondary-link {
  background: rgba(219, 229, 241, 0.96);
  color: #2b5f9f;
}

.hero-panel {
  padding: 24px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(47, 69, 94, 0.98), rgba(52, 76, 102, 0.98));
  color: #f3f8ff;
}

.panel-topline {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(243, 248, 255, 0.8);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #19e2a8;
}

.time-cluster {
  margin: 28px 0 24px;
}

.time-text {
  font-size: 40px;
  font-weight: 700;
}

.date-text {
  margin-top: 8px;
  color: rgba(243, 248, 255, 0.72);
}

.quick-status {
  display: grid;
  gap: 12px;
}

.runtime-pill {
  display: flex;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
}

.section-card {
  padding: 24px 28px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0;
}

.section-head p {
  max-width: 660px;
  margin: 0;
  color: rgba(53, 82, 110, 0.7);
  line-height: 1.7;
}

.entry-grid,
.topic-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.topic-grid.extension-grid {
  grid-template-columns: repeat(4, 1fr);
}

.entry-card,
.topic-card {
  padding: 18px;
  border: 1px solid rgba(167, 184, 204, 0.42);
  border-radius: 18px;
  text-decoration: none;
  color: inherit;
  background: rgba(243, 246, 250, 0.96) !important;
}

.entry-body,
.topic-card p {
  display: grid;
  gap: 8px;
}

.entry-body span,
.topic-card p {
  color: rgba(83, 111, 138, 0.82);
}

.topic-title {
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #173b60;
}

@media (max-width: 1200px) {
  .hero-shell,
  .entry-grid,
  .topic-grid,
  .topic-grid.extension-grid {
    grid-template-columns: 1fr;
  }

  .metric-row {
    grid-template-columns: repeat(2, minmax(140px, 1fr));
    max-width: 520px;
  }

  .section-head,
  .hero-actions {
    flex-direction: column;
  }
}

@media (max-width: 720px) {
  .metric-row {
    grid-template-columns: 1fr;
    max-width: 340px;
  }
}
</style>
