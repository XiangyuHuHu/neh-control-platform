<template>
  <div class="reagent-screen">
    <header class="screen-head">
      <div class="screen-title">智能密控与加药系统</div>
      <div class="screen-sub">杨家村选煤厂 · 全连接协同控制 · 自检 {{ selfCheckStatus }}</div>
      <div class="screen-time">{{ currentTime }} · {{ weatherText }} · {{ dutyLeader }}</div>
    </header>

    <section class="top-controls">
      <el-segmented v-model="controlMode" :options="modeOptions" />
      <el-button class="alarm-entry" :class="{ pulse: alarmCount > 0 }" @click="alarmDrawer = true">
        告警 {{ alarmCount }}
      </el-button>
    </section>

    <section class="top-layout">
      <aside class="side-col">
        <div class="logic-status">
          <span>卷积层</span>
          <em class="flow-dot"></em>
          <span>注意力层</span>
          <em class="flow-dot"></em>
          <span>全连接</span>
        </div>
        <div class="side-box">
          <span>预测泵频</span>
          <strong>{{ result?.predPump ?? '--' }}</strong>
        </div>
        <div class="side-box">
          <span>备用泵</span>
          <strong>{{ result?.predBackupPump ?? '--' }}</strong>
        </div>
        <div class="side-box">
          <span>阀门建议</span>
          <strong>{{ result?.valveMN ?? '--' }}</strong>
        </div>
      </aside>

      <div class="center-board">
        <svg class="network-svg" viewBox="0 0 1000 320" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <radialGradient id="nodeFill" cx="50%" cy="40%" r="70%">
              <stop offset="0%" stop-color="#66d6ff" stop-opacity="0.6" />
              <stop offset="100%" stop-color="#0a2b59" stop-opacity="0.22" />
            </radialGradient>
          </defs>
          <g class="link-layer">
            <path class="net-link" :style="{ animationDuration: `${linkDurationMain}s` }" d="M170 84 C250 84, 280 130, 360 130" />
            <path class="net-link" :style="{ animationDuration: `${linkDurationMain}s` }" d="M170 84 C250 84, 280 220, 360 220" />
            <path class="net-link net-link--gold" :style="{ animationDuration: `${linkDurationGold}s` }" d="M360 130 C470 130, 520 88, 620 88" />
            <path class="net-link net-link--gold" :style="{ animationDuration: `${linkDurationGold}s` }" d="M360 220 C470 220, 520 168, 620 168" />
            <path class="net-link" :style="{ animationDuration: `${linkDurationMain}s` }" d="M620 88 C730 88, 760 130, 860 130" />
            <path class="net-link" :style="{ animationDuration: `${linkDurationMain}s` }" d="M620 168 C730 168, 760 210, 860 210" />
          </g>
          <g class="node-layer">
            <circle class="net-node big" cx="170" cy="84" r="54" />
            <text class="node-text" x="170" y="84">分流阀开度</text>
            <circle class="net-node big" cx="170" cy="236" r="54" />
            <text class="node-text" x="170" y="236">补水阀开度</text>
            <circle class="net-node mid" cx="360" cy="130" r="42" />
            <text class="node-text" x="360" y="130">特征层</text>
            <circle class="net-node mid" cx="360" cy="220" r="42" />
            <text class="node-text" x="360" y="220">注意力层</text>
            <circle class="net-node mid" cx="620" cy="88" r="46" />
            <text class="node-text" x="620" y="88">全连接</text>
            <circle class="net-node mid" cx="620" cy="168" r="46" />
            <text class="node-text" x="620" y="168">时间记忆层</text>
            <circle class="net-node big" cx="860" cy="130" r="52" />
            <text class="node-text" x="860" y="130">密控输出</text>
            <circle class="net-node big" cx="860" cy="230" r="52" />
            <text class="node-text" x="860" y="230">加药输出</text>
          </g>
        </svg>
      </div>

      <aside class="side-col">
        <div class="tank-box">
          <span>药剂余量</span>
          <div class="tank">
            <div class="wave" :style="{ height: `${reagentLevel}%`, animationDuration: `${waveDuration}s` }"></div>
          </div>
        </div>
        <div class="side-box side-box--green">
          <span>状态</span>
          <strong>{{ result?.stateName ?? '--' }}</strong>
        </div>
        <div class="side-box side-box--blue">
          <span>模式</span>
          <strong>{{ result?.mode || '演示回退' }}</strong>
        </div>
        <div class="side-box side-box--warn">
          <span>选中单元</span>
          <strong>{{ selectedUnit }}</strong>
        </div>
      </aside>
    </section>

    <section class="unit-grid">
      <article v-for="row in overviewRows" :key="row.unit" class="unit-card">
        <header>
          <h3>加药系统设备-{{ row.unit }}</h3>
          <span class="status-dot" :class="{ warn: row.status !== '运行中' }"></span>
        </header>
        <div class="metric-row">
          <div><label>泵频</label><strong>{{ row.pump }}</strong></div>
          <div><label>备用泵</label><strong>{{ row.backupPump }}</strong></div>
          <div><label>阀门</label><strong>{{ row.valve }}</strong></div>
        </div>
        <div class="state-line">状态：{{ row.status }}，{{ row.mode }}</div>
        <footer>
          <el-button class="outline-btn" :class="{ active: activeCommand[row.unit] === 'start' }" @click="controlAction('start', row.unit)">
            启动
          </el-button>
          <el-button class="outline-btn" :class="{ active: activeCommand[row.unit] === 'auto' }" @click="controlAction('auto', row.unit)">
            自动
          </el-button>
          <el-button class="outline-btn" :class="{ active: activeCommand[row.unit] === 'reset' }" @click="controlAction('reset', row.unit)">
            复位
          </el-button>
        </footer>
      </article>
    </section>

    <el-drawer v-model="alarmDrawer" title="实时告警抽屉" size="360px">
      <div class="alarm-list">
        <div v-for="a in alarms" :key="a.id" class="alarm-item">
          <strong>{{ a.level }}</strong>
          <p>{{ a.text }}</p>
          <small>{{ a.time }}</small>
        </div>
      </div>
    </el-drawer>

    <section class="debug-panel">
      <div class="panel-head">
        <h2>算法联调区</h2>
        <div class="panel-actions">
          <el-select v-model="selectedUnit" style="width: 160px" @change="applyTemplate">
            <el-option v-for="unit in reagentUnits" :key="unit.value" :label="unit.label" :value="unit.value" />
          </el-select>
          <el-button @click="applyTemplate">载入模板</el-button>
          <el-button @click="loadOverview">刷新概览</el-button>
          <el-button type="primary" :loading="loading" @click="runPredict">调用模型</el-button>
        </div>
      </div>
      <div class="form-grid">
        <label class="field">
          <span>长周期数据数组</span>
          <el-input v-model="dataLongText" type="textarea" :rows="5" />
        </label>
        <label class="field">
          <span>短周期数据数组</span>
          <el-input v-model="dataShortText" type="textarea" :rows="5" />
        </label>
        <label class="field field--full">
          <span>参数对象</span>
          <el-input v-model="paramsText" type="textarea" :rows="5" />
        </label>
      </div>
      <div ref="chartEl" class="chart-box"></div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { echarts, INDUSTRIAL_CHART_COLORS } from '../../utils/echarts'
import {
  getSmartReagentOverview,
  predictSmartReagent,
  type SmartReagentPredictResult,
  type SmartReagentUnitDto,
} from '../../api/coal-business'

const reagentUnits = [
  { label: '601 末煤一号', value: '601' },
  { label: '602 末煤二号', value: '602' },
  { label: '5201 块煤一号', value: '5201' },
  { label: '5202 块煤二号', value: '5202' },
]

type JsonRecord = Record<string, unknown>

const templates: Record<string, { dataLong: number[]; dataShort: number[]; params: JsonRecord }> = {
  '601': {
    dataLong: [1.43, 0.42, 18.5, 42, 1, 2850, 11.8],
    dataShort: [1.43, 0.41, 18, 40, 0],
    params: { pumpNumber: 1, backupPumpNumber: 0, density_setpoint: 1.43, update_ctrl: 1, run_state: 0 },
  },
  '602': {
    dataLong: [1.45, 0.44, 20.1, 45, 0, 2960, 12.6],
    dataShort: [1.45, 0.43, 20, 44, 0],
    params: { pumpNumber: 2, backupPumpNumber: 0, density_setpoint: 1.45, update_ctrl: 1, run_state: 0 },
  },
  '5201': {
    dataLong: [1.40, 0.38, 16.2, 38, 1, 2320, 9.6],
    dataShort: [1.40, 0.37, 16, 37, 1],
    params: { pumpNumber: 5, backupPumpNumber: 1, density_setpoint: 1.40, update_ctrl: 1, run_state: 0 },
  },
  '5202': {
    dataLong: [1.41, 0.39, 17.4, 40, 0, 2400, 9.8],
    dataShort: [1.41, 0.38, 17, 39, 0],
    params: { pumpNumber: 6, backupPumpNumber: 0, density_setpoint: 1.41, update_ctrl: 1, run_state: 0 },
  },
}

const selectedUnit = ref('601')
const dataLongText = ref('')
const dataShortText = ref('')
const paramsText = ref('')
const overviewRows = ref<SmartReagentUnitDto[]>([])
const result = ref<SmartReagentPredictResult | null>(null)
const loading = ref(false)
const chartEl = ref<HTMLElement | null>(null)
let chart: any = null
const currentTime = ref('')
let timer = 0
const controlMode = ref<'手动' | '自动' | '智能模型'>('智能模型')
const modeOptions = ['手动', '自动', '智能模型']
const weatherText = ref('晴 18~26℃')
const dutyLeader = ref('当班负责人：王工')
const selfCheckStatus = ref('正常')
const alarmDrawer = ref(false)
const alarmCount = ref(1)
const alarms = ref([{ id: 'R-01', level: '中', text: '602 药剂库存低于 30%，建议补药', time: '16:18:32' }])
const activeCommand = ref<Record<string, 'start' | 'auto' | 'reset'>>({})
const pumpValue = computed(() => Number(result.value?.predPump ?? 35))
const reagentLevel = computed(() => Math.max(18, Math.min(88, 100 - pumpValue.value)))
const waveDuration = computed(() => Math.max(1.2, 4.5 - pumpValue.value / 20).toFixed(2))
const linkDurationMain = computed(() => Math.max(1.4, 3.8 - pumpValue.value / 24).toFixed(2))
const linkDurationGold = computed(() => (Number(linkDurationMain.value) + 0.8).toFixed(2))

function applyTemplate() {
  const template = templates[selectedUnit.value]
  dataLongText.value = JSON.stringify(template.dataLong, null, 2)
  dataShortText.value = JSON.stringify(template.dataShort, null, 2)
  paramsText.value = JSON.stringify(template.params, null, 2)
}

function parseArray(text: string, label: string): number[] {
  const parsed: unknown = JSON.parse(text)
  if (!Array.isArray(parsed)) {
    throw new Error(`${label} 必须是数组`)
  }
  return parsed.map((value, index) => {
    const numericValue = Number(value)
    if (!Number.isFinite(numericValue)) {
      throw new Error(`${label} 第 ${index + 1} 项不是有效数字`)
    }
    return numericValue
  })
}

function parseObject(text: string): JsonRecord {
  const parsed: unknown = JSON.parse(text)
  if (!parsed || Array.isArray(parsed) || typeof parsed !== 'object') {
    throw new Error('参数对象必须是 JSON 对象')
  }
  return parsed as JsonRecord
}

function controlAction(action: 'start' | 'auto' | 'reset', unit: string) {
  activeCommand.value[unit] = action
  const actionText = action === 'start' ? '启动' : action === 'auto' ? '自动' : '复位'
  ElMessage.success(`设备 ${unit} 已执行${actionText}指令（演示）`)
}

function updateTime() {
  currentTime.value = new Date().toLocaleString('zh-CN', { hour12: false })
}

async function loadOverview() {
  try {
    const data = await getSmartReagentOverview()
    overviewRows.value = data.units
  } catch {
    overviewRows.value = [
      { unit: '601', area: '末煤一号加药泵', status: '运行中', pump: '42', backupPump: '0', valve: '18', mode: '演示回退' },
      { unit: '602', area: '末煤二号加药泵', status: '运行中', pump: '45', backupPump: '0', valve: '20', mode: '演示回退' },
      { unit: '5201', area: '块煤一号加药泵', status: '待观察', pump: '38', backupPump: '1', valve: '16', mode: '演示回退' },
      { unit: '5202', area: '块煤二号加药泵', status: '运行中', pump: '40', backupPump: '0', valve: '17', mode: '演示回退' },
    ]
  }
}

async function runPredict() {
  try {
    loading.value = true
    const payload = {
      unit: selectedUnit.value,
      dataLong: parseArray(dataLongText.value, '长周期数据'),
      dataShort: parseArray(dataShortText.value, '短周期数据'),
      params: parseObject(paramsText.value),
    }
    result.value = await predictSmartReagent(payload)
    await nextTick()
    renderChart()
    ElMessage.success(`智能加药 ${selectedUnit.value} 调用完成`)
  } catch (error: any) {
    ElMessage.error(error?.message || '智能加药调用失败')
  } finally {
    loading.value = false
  }
}

function renderChart() {
  if (!chartEl.value || !result.value) return
  if (!chart) {
    chart = echarts.init(chartEl.value)
  }
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['主泵', '备用泵', '阀门'],
      axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
      splitLine: { lineStyle: { color: INDUSTRIAL_CHART_COLORS.grid } },
    },
    grid: { left: '3%', right: '4%', top: '8%', bottom: '8%', containLabel: true },
    series: [{
      type: 'line',
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color: '#00f2f1' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0,242,241,0.30)' },
          { offset: 1, color: 'rgba(0,242,241,0.02)' },
        ]),
      },
    ],
  }, true)
}

const handleResize = () => chart?.resize()

onMounted(async () => {
  updateTime()
  timer = window.setInterval(updateTime, 1000)
  applyTemplate()
  await loadOverview()
  await runPredict()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chart?.dispose()
  clearInterval(timer)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.reagent-screen {
  min-height: 100vh;
  padding: 14px 18px 20px;
  background: radial-gradient(circle at 50% 0%, rgba(71, 111, 163, 0.2), transparent 30%), #0a1220;
  color: #e8f6ff;
}
.screen-head {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  margin-bottom: 12px;
  padding: 10px 16px;
  border: 1px solid rgba(154, 188, 224, 0.25);
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(8px);
}
.screen-title { font-size: 24px; font-weight: 700; }
.screen-sub { justify-self: center; color: #82c5ff; }
.screen-time { justify-self: end; color: #b6deff; font-size: 13px; }
.top-controls {
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.alarm-entry {
  border: 1px solid rgba(255, 120, 120, 0.5);
  background: rgba(255, 90, 90, 0.08);
  color: #ffd6d6;
}
.alarm-entry.pulse { animation: pulse 1.6s ease-in-out infinite; }
@keyframes pulse {
  0%,100% { box-shadow: 0 0 0 rgba(255, 107, 107, 0); }
  50% { box-shadow: 0 0 12px rgba(255, 107, 107, 0.45); }
}
.top-layout {
  display: grid;
  grid-template-columns: 220px 1fr 220px;
  gap: 12px;
  margin-bottom: 12px;
}
.side-col { display: grid; gap: 10px; }
.logic-status {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #cadff3;
  font-size: 12px;
  padding: 8px 10px;
  border: 1px solid rgba(154, 188, 224, 0.2);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
}
.flow-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00f2f1;
  box-shadow: 0 0 8px rgba(0, 242, 241, 0.6);
  animation: blink 1.4s infinite;
}
@keyframes blink {
  0%,100% { opacity: 0.3; transform: scale(0.85); }
  50% { opacity: 1; transform: scale(1); }
}
.side-box {
  padding: 12px;
  border: 1px solid rgba(154, 188, 224, 0.22);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(7px);
}
.side-box span { font-size: 12px; color: #8bbde4; }
.side-box strong { display: block; margin-top: 6px; font-size: 28px; color: #58d2ff; }
.side-box--green strong { color: #58efbe; }
.side-box--blue strong { color: #76b7ff; }
.side-box--warn strong { color: #ffd666; }
.tank-box {
  padding: 12px;
  border: 1px solid rgba(154, 188, 224, 0.22);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
}
.tank-box span { color: #9dbcd8; font-size: 12px; }
.tank {
  margin-top: 8px;
  height: 66px;
  border: 1px solid rgba(145, 185, 226, 0.35);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(4, 14, 25, 0.85);
}
.wave {
  height: 62%;
  background: linear-gradient(180deg, rgba(0, 242, 241, 0.32), rgba(0, 242, 241, 0.12));
  border-radius: 30% 30% 0 0;
  animation: waveMove 2.8s ease-in-out infinite;
}
@keyframes waveMove {
  0%,100% { transform: translateX(-6%); }
  50% { transform: translateX(6%); }
}
.center-board {
  position: relative;
  min-height: 250px;
  border: 1px solid rgba(154, 188, 224, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
}
.network-svg { width: 100%; height: 100%; min-height: 250px; }
.net-link {
  fill: none;
  stroke: #56d4ff;
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-dasharray: 6 5;
  animation: linkFlow 3.2s linear infinite;
}
.net-link--gold { stroke: #ffcd6f; animation-duration: 4.4s; }
.net-node {
  fill: url(#nodeFill);
  stroke: rgba(128, 207, 255, 0.72);
  stroke-width: 1.2;
  filter: drop-shadow(0 0 8px rgba(74, 175, 255, 0.45));
}
.net-node.mid { fill: rgba(84, 175, 255, 0.24); }
.node-text {
  fill: #d8efff;
  font-size: 12px;
  text-anchor: middle;
  dominant-baseline: middle;
  font-weight: 600;
}
@keyframes linkFlow {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -44; }
}
.unit-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}
.unit-card {
  padding: 12px;
  border: 1px solid rgba(154, 188, 224, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(7px);
}
.unit-card header { display: flex; justify-content: space-between; align-items: center; }
.unit-card h3 { margin: 0; font-size: 15px; color: #b8dcff; }
.status-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: #4cff9e; box-shadow: 0 0 10px rgba(76, 255, 158, 0.8);
}
.status-dot.warn { background: #ff9f43; box-shadow: 0 0 10px rgba(255, 159, 67, 0.8); }
.metric-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin: 10px 0 8px;
}
.metric-row label { display: block; font-size: 12px; color: #8fb6db; }
.metric-row strong { font-size: 22px; }
.state-line { font-size: 12px; color: #92bcdf; margin-bottom: 8px; }
.unit-card footer { display: flex; gap: 8px; }
.outline-btn {
  border: 1px solid rgba(126, 185, 239, 0.55);
  background: transparent;
  color: #d5eaff;
}
.outline-btn.active {
  background: rgba(0, 242, 241, 0.18);
  border-color: rgba(0, 242, 241, 0.8);
  color: #ebfdff;
}
.debug-panel {
  padding: 14px;
  border: 1px solid rgba(154, 188, 224, 0.22);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(7px);
}
.panel-head { display: flex; justify-content: space-between; gap: 10px; align-items: center; margin-bottom: 10px; }
.panel-head h2 { margin: 0; font-size: 18px; }
.panel-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 10px; }
.field { display: grid; gap: 6px; }
.field span { font-size: 12px; color: #9bc4e8; }
.field--full { grid-column: 1 / -1; }
.chart-box { height: 260px; }
.alarm-list { display: grid; gap: 10px; }
.alarm-item {
  border: 1px solid rgba(255, 168, 168, 0.35);
  border-radius: 10px;
  background: rgba(255, 89, 89, 0.08);
  padding: 10px;
}
.alarm-item strong { color: #ffd2d2; }
.alarm-item p { margin: 6px 0; color: #fce9e9; }
.alarm-item small { color: #e8b8b8; }
@media (max-width: 1400px) {
  .top-layout, .unit-grid, .form-grid { grid-template-columns: 1fr; }
}
</style>
