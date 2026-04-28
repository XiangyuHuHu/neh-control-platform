<template>
  <div class="coal-home">
    <header class="hero-shell">
      <div class="hero-copy">
        <p class="eyebrow">平台总入口</p>
        <h1>淖尔壕智能化选煤厂</h1>
        <p class="hero-summary">核心指标采用“接口优先 + 兜底数据”模式，便于现场前后平滑切换。</p>
        <div class="metric-row">
          <article v-for="item in displayMetrics" :key="item.label" class="metric-card" :class="`metric-card--${item.tone}`">
            <span class="metric-label">{{ item.label }}</span>
            <div class="metric-mainline">
              <strong class="metric-value">{{ item.main }}</strong>
              <span class="metric-unit">{{ item.unit }}</span>
            </div>
            <svg class="metric-sparkline" viewBox="0 0 120 28" preserveAspectRatio="none" aria-hidden="true">
              <polyline :points="item.sparkline" />
            </svg>
            <small class="metric-note">{{ item.note }}</small>
          </article>
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
            <span class="section-tag">核心入口</span>
            <h2>主要业务页面</h2>
          </div>
          <p>用于日常展示和操作的核心页面入口。</p>
        </div>
        <div class="entry-grid">
          <router-link v-for="item in primaryEntries" :key="item.path" :to="item.path" class="entry-card">
            <strong>{{ item.title }}</strong>
            <span>{{ item.desc }}</span>
          </router-link>
        </div>
      </section>

      <section class="section-card">
        <div class="section-head">
          <div>
            <span class="section-tag">专题模块</span>
            <h2>专题业务页面</h2>
          </div>
          <p>覆盖储装、能耗、调度、决策、巡检和系统设置。</p>
        </div>
        <div class="topic-grid">
          <router-link v-for="item in topicEntries" :key="item.path" :to="item.path" class="topic-card">
            <div class="topic-title">{{ item.title }}</div>
            <p>{{ item.desc }}</p>
          </router-link>
        </div>
      </section>

      <section class="section-card">
        <div class="section-head">
          <div>
            <span class="section-tag">最新需求</span>
            <h2>新增专题页</h2>
          </div>
          <p>对应最新需求文件中的生产计划、销售统计、排班及各类消耗管理功能。</p>
        </div>
        <div class="topic-grid extension-grid">
          <router-link v-for="item in extensionEntries" :key="item.path" :to="item.path" class="topic-card">
            <div class="topic-title">{{ item.title }}</div>
            <p>{{ item.desc }}</p>
          </router-link>
        </div>
      </section>

      <section class="section-card">
        <div class="section-head">
          <div>
            <span class="section-tag">平台能力</span>
            <h2>数据治理与集成</h2>
          </div>
          <p>覆盖数据治理、数据集成和数据接入等平台能力。</p>
        </div>
        <div class="topic-grid">
          <router-link v-for="item in platformEntries" :key="item.path" :to="item.path" class="topic-card">
            <div class="topic-title">{{ item.title }}</div>
            <p>{{ item.desc }}</p>
          </router-link>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { coalExtensionEntriesForHome, coalPlatformEntries, coalPrimaryEntries, coalTopicEntries } from './coalNav'
import { getPortalMetrics, type PortalMetricItem } from '../../api/dashboard'

const currentTime = ref('')
const currentDate = ref('')

const runtimeStatus = ref([
  { label: '设备完好率', value: '97.4%' },
  { label: '质量达标率', value: '96.8%' },
  { label: '能耗偏差', value: '-1.9%' },
])

const fallbackCoreMetrics: PortalMetricItem[] = [
  { label: '今日入洗量', value: '5,200 t', note: '较昨日 +4.2%' },
  { label: '精煤产量', value: '3,400 t', note: '达成率 97.1%' },
  { label: '实时总功率', value: '850 kW', note: '峰段负荷可控' },
  { label: '全厂设备综合效率（OEE）', value: '92.4 %', note: '综合设备可用率与工况折算' },
]
const coreMetrics = ref<PortalMetricItem[]>(fallbackCoreMetrics)

type MetricTone = 'cyan' | 'blue' | 'green' | 'gold' | 'warn'

const resolveMetricTone = (label: string): MetricTone => {
  if (label.includes('入洗量')) {
    return 'cyan'
  }
  if (label.includes('产量')) {
    return 'blue'
  }
  if (label.includes('功率') || label.includes('能耗')) {
    return 'green'
  }
  if (label.includes('OEE') || label.includes('效率')) {
    return 'gold'
  }
  if (label.includes('风险') || label.includes('异常') || label.includes('告警')) {
    return 'warn'
  }
  return 'cyan'
}

const splitMetricValue = (value: string) => {
  const matched = value.match(/^\s*([+-]?\d[\d,.]*)\s*(.*)$/)
  if (!matched) {
    return { main: value, unit: '' }
  }
  return { main: matched[1], unit: matched[2] || '' }
}

const buildSparkline = (seedText: string) => {
  const total = Array.from(seedText).reduce((acc, ch) => acc + ch.charCodeAt(0), 0)
  const points: string[] = []
  for (let i = 0; i < 12; i += 1) {
    const x = (120 / 11) * i
    const wave = Math.sin((total + i * 13) * 0.12) * 6 + Math.cos((total + i * 7) * 0.08) * 2
    const y = Math.max(3, Math.min(25, 14 - wave))
    points.push(`${x.toFixed(1)},${y.toFixed(1)}`)
  }
  return points.join(' ')
}

const displayMetrics = computed(() =>
  coreMetrics.value.map((item) => {
    const parsed = splitMetricValue(item.value)
    return {
      ...item,
      main: parsed.main,
      unit: parsed.unit,
      tone: resolveMetricTone(item.label),
      sparkline: buildSparkline(`${item.label}|${item.value}`),
    }
  }),
)

const primaryEntries = coalPrimaryEntries.map((item) => ({ path: item.path, title: item.label, desc: item.desc || '' }))
const topicEntries = coalTopicEntries.map((item) => ({ path: item.path, title: item.label, desc: item.desc || '' }))
const platformEntries = coalPlatformEntries.map((item) => ({ path: item.path, title: item.label, desc: item.desc || '' }))
const extensionEntries = coalExtensionEntriesForHome.map((item) => ({ path: item.path, title: item.label, desc: item.desc || '' }))

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
.coal-home {
  min-height: 100vh;
  padding: 20px;
  background: radial-gradient(circle at top right, rgba(53, 166, 255, 0.16), transparent 22%), #07111b;
  color: #eaf6ff;
}

.hero-shell,
.section-card {
  width: min(100%, 1800px);
  margin: 0 auto 20px;
  border: 1px solid rgba(106, 188, 255, 0.14);
  border-radius: 24px;
  background: rgba(8, 19, 30, 0.9);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.24);
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
  color: #7bc8ff;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.hero-copy h1 {
  margin: 0;
  font-size: 38px;
}

.hero-summary {
  max-width: 760px;
  margin: 12px 0 0;
  color: rgba(227, 239, 250, 0.72);
  line-height: 1.8;
}

.metric-row {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(4, minmax(130px, 1fr));
  gap: 12px;
  max-width: 820px;
}

.metric-card {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(125, 203, 255, 0.22);
  border-left: 3px solid var(--metric-accent, #5ec8ff);
  background: linear-gradient(145deg, rgba(18, 39, 57, 0.9), rgba(13, 27, 42, 0.92));
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02);
}

.metric-card--cyan {
  --metric-accent: #48c9ff;
}

.metric-card--green {
  --metric-accent: #5af2b7;
}

.metric-card--blue {
  --metric-accent: #66b3ff;
}

.metric-card--gold {
  --metric-accent: #ffd666;
}

.metric-card--warn {
  --metric-accent: #ffb84d;
}

.metric-label {
  display: block;
  color: #9cc7eb;
  font-size: 12px;
}

.metric-mainline {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-top: 8px;
}

.metric-value {
  display: inline-block;
  font-size: 28px;
  line-height: 1.1;
  color: var(--metric-accent, #e6f8ff);
  text-shadow: 0 0 12px rgba(65, 196, 255, 0.2);
}

.metric-unit {
  font-size: 13px;
  color: rgba(230, 248, 255, 0.6);
}

.metric-sparkline {
  display: block;
  width: 100%;
  height: 28px;
  margin-top: 6px;
  opacity: 0.95;
}

.metric-sparkline polyline {
  fill: none;
  stroke: var(--metric-accent, #4fcfff);
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.metric-note {
  display: block;
  margin-top: 6px;
  color: #78abd7;
  font-size: 12px;
}

.hero-summary {
  max-width: 760px;
  color: rgba(227, 239, 250, 0.74);
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.primary-link,
.secondary-link {
  padding: 12px 18px;
  border-radius: 12px;
  text-decoration: none;
}

.primary-link {
  background: linear-gradient(135deg, #3acbff, #148bff);
  color: #031423;
  font-weight: 700;
}

.secondary-link {
  border: 1px solid rgba(125, 203, 255, 0.22);
  color: #dceeff;
}

.hero-panel {
  padding: 22px;
  border: 1px solid rgba(106, 188, 255, 0.12);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(7, 23, 38, 0.96), rgba(10, 18, 28, 0.96));
}

.panel-topline {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #7bc8ff;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #18f0bf;
  box-shadow: 0 0 12px rgba(24, 240, 191, 0.8);
}

.time-cluster {
  margin: 24px 0;
}

.time-text {
  font-size: 42px;
  font-weight: 700;
}

.date-text {
  margin-top: 10px;
  color: rgba(227, 239, 250, 0.72);
}

.quick-status {
  display: grid;
  gap: 12px;
}

.runtime-pill {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid rgba(125, 203, 255, 0.12);
  border-radius: 14px;
  background: rgba(18, 33, 49, 0.72);
}

.runtime-pill span {
  color: rgba(227, 239, 250, 0.72);
}

.content-shell {
  width: min(100%, 1800px);
  margin: 0 auto;
}

.section-card {
  padding: 24px 28px 28px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0;
}

.section-head p {
  margin: 0;
  color: rgba(227, 239, 250, 0.68);
}

.entry-grid,
.topic-grid {
  display: grid;
  gap: 16px;
}

.entry-grid {
  grid-template-columns: repeat(4, 1fr);
}

.topic-grid {
  grid-template-columns: repeat(3, 1fr);
}

.entry-card,
.topic-card {
  display: block;
  padding: 18px;
  border: 1px solid rgba(125, 203, 255, 0.12);
  border-radius: 18px;
  background: rgba(13, 25, 38, 0.88);
  text-decoration: none;
  color: #eaf6ff;
  transition: transform 0.18s ease, border-color 0.18s ease;
}

.entry-card:hover,
.topic-card:hover {
  transform: translateY(-2px);
  border-color: rgba(87, 216, 255, 0.3);
}

.entry-card strong,
.topic-title {
  display: block;
  margin-bottom: 10px;
  font-size: 18px;
}

.entry-card span,
.topic-card p {
  color: rgba(227, 239, 250, 0.68);
  line-height: 1.7;
}

.extension-grid {
  grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 1280px) {
  .hero-shell,
  .entry-grid,
  .topic-grid,
  .extension-grid {
    grid-template-columns: 1fr 1fr;
  }

  .metric-row {
    grid-template-columns: repeat(2, minmax(140px, 1fr));
    max-width: 560px;
  }
}

@media (max-width: 900px) {
  .hero-shell,
  .entry-grid,
  .topic-grid,
  .extension-grid {
    grid-template-columns: 1fr;
  }

  .section-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .metric-row {
    grid-template-columns: 1fr;
    max-width: 340px;
  }
}
</style>
