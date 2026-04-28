<template>
  <div class="density-screen">
    <header class="screen-head">
      <div class="screen-title">智能密控系统</div>
      <div class="screen-sub">末煤 3207 工艺流程 · 系统自检 {{ selfCheckStatus }}</div>
      <div class="screen-time">{{ currentTime }} · {{ weatherText }} · {{ dutyLeader }}</div>
    </header>

    <section class="top-controls">
      <el-segmented v-model="controlMode" :options="modeOptions" />
      <el-button class="alarm-entry" :class="{ pulse: alarmCount > 0 }" @click="alarmDrawer = true">
        告警 {{ alarmCount }}
      </el-button>
    </section>

    <section class="flow-shell">
      <aside class="metric-col">
        <div class="metric-box">
          <span>密度</span>
          <strong>{{ result?.predDensity ?? '--' }}</strong>
        </div>
        <div class="metric-box">
          <span>分流阀开度</span>
          <strong>{{ result?.predDiverter ?? '--' }}</strong>
        </div>
        <div class="metric-box">
          <span>补水阀开度</span>
          <strong>{{ result?.predWater ?? '--' }}</strong>
        </div>
        <div class="meter-box">
          <div class="meter-row">
            <span>密度计</span>
            <em :class="['meter-dot', densityMeterClass]"></em>
            <b>{{ densityMeterText }}</b>
          </div>
          <div class="meter-row">
            <span>磁性物含量计</span>
            <em :class="['meter-dot', magneticMeterClass]"></em>
            <b>{{ magneticMeterText }}</b>
          </div>
        </div>
      </aside>

      <div class="process-board">
        <svg class="process-svg" viewBox="0 0 1000 300" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <linearGradient id="pipeBlue" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stop-color="#6fe3ff" />
              <stop offset="100%" stop-color="#2f84ff" />
            </linearGradient>
            <linearGradient id="pipeGold" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stop-color="#ffe090" />
              <stop offset="100%" stop-color="#d59a21" />
            </linearGradient>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2.2" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <path class="flow-line flow-line--blue" :style="{ animationDuration: `${flowDurationBlue}s` }" d="M40 80 H360 L420 130 H950" />
          <path class="flow-line flow-line--gold" :style="{ animationDuration: `${flowDurationGold}s` }" d="M60 145 H280 L350 190 H780 L860 120 H960" />
          <path class="flow-line flow-line--green" :style="{ animationDuration: `${flowDurationGreen}s` }" d="M30 230 H260 L330 170 H520 L620 220 H950" />
          <rect class="equip-box" x="360" y="58" width="120" height="46" rx="22" />
          <rect class="equip-box" x="560" y="150" width="120" height="46" rx="22" />
          <rect class="equip-box" x="760" y="66" width="130" height="46" rx="22" />
          <text class="equip-text" x="420" y="86">重介旋流器</text>
          <text class="equip-text" x="620" y="178">再悬浮介质</text>
          <text class="equip-text" x="825" y="94">矸石缓冲槽</text>
          <circle class="flow-node" cx="220" cy="145" r="10" />
          <circle class="flow-node" cx="520" cy="170" r="10" />
          <circle class="flow-node" cx="860" cy="120" r="10" />
        </svg>
      </div>

      <aside class="metric-col">
        <div class="metric-box metric-box--green">
          <span>设定密度</span>
          <strong>{{ setpointText }}</strong>
        </div>
        <div class="metric-box metric-box--blue">
          <span>运行模式</span>
          <strong>{{ result?.mode || '演示回退' }}</strong>
        </div>
        <div class="metric-box metric-box--warn">
          <span>控制状态</span>
          <strong>{{ result?.stateName || '--' }}</strong>
        </div>
      </aside>
    </section>

    <section class="unit-grid">
      <DensityPredictCard
        v-for="row in overviewRows"
        :key="row.unit"
        :title="`密控系统设备-${row.unit}`"
        :predict="toNumber(row.density)"
        :setpoint="row.unit === '316' ? setpointClean : setpointMiddling"
      >
        <el-button class="outline-btn" :class="{ active: activeCommand[row.unit] === 'start' }" @click="controlAction('start', row.unit)">
          启动
        </el-button>
        <el-button class="outline-btn" :class="{ active: activeCommand[row.unit] === 'auto' }" @click="controlAction('auto', row.unit)">
          自动
        </el-button>
        <el-button class="outline-btn" :class="{ active: activeCommand[row.unit] === 'reset' }" @click="controlAction('reset', row.unit)">
          复位
        </el-button>
      </DensityPredictCard>
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
          <el-select v-model="selectedUnit" style="width: 140px" @change="applyTemplate">
            <el-option v-for="unit in densityUnits" :key="unit.value" :label="unit.label" :value="unit.value" />
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
import DensityPredictCard from '../../components/coal/DensityPredictCard.vue'
import {
  getSmartDensityOverview,
  predictSmartDensity,
  predictSmartDensitySetpoint,
  type SmartDensityPredictResult,
  type SmartDensityUnitDto,
} from '../../api/coal-business'

const densityUnits = [
  { label: '3207 主洗二段', value: '3207' },
  { label: '3208 主洗三段', value: '3208' },
  { label: '316 末煤系统', value: '316' },
]

type JsonRecord = Record<string, unknown>

const templates: Record<string, { dataLong: number[]; dataShort: number[]; params: JsonRecord }> = {
  '3207': {
    dataLong: [1.43, 1.42, 1.44, 1.45, 42, 11.8, 2850, 2180],
    dataShort: [1.43, 1.44, 43, 12, 0, 1],
    params: { water_switch: 0, update_ctrl: 1, density_setpoint: 1.43, run_state: 0 },
  },
  '3208': {
    dataLong: [1.47, 1.46, 1.48, 1.49, 46, 12.6, 2960, 2220],
    dataShort: [1.47, 1.48, 45, 13, 0, 1],
    params: { water_switch: 0, update_ctrl: 1, density_setpoint: 1.47, run_state: 0 },
  },
  '316': {
    dataLong: [1.38, 1.37, 1.39, 1.40, 38, 9.8, 2320, 1690],
    dataShort: [1.38, 1.39, 39, 10, 1, 1],
    params: { water_switch: 1, update_ctrl: 1, density_setpoint: 1.38, run_state: 0 },
  },
}

const selectedUnit = ref('3207')
const dataLongText = ref('')
const dataShortText = ref('')
const paramsText = ref('')
const overviewRows = ref<SmartDensityUnitDto[]>([])
const result = ref<SmartDensityPredictResult | null>(null)
const setpoint = ref<{ predMiddlingDensity: number; predCleanDensity: number; mode: string } | null>(null)
const loading = ref(false)
const chartEl = ref<HTMLElement | null>(null)
let chart: any = null
const currentTime = ref('')
let timer = 0
const controlMode = ref<'手动' | '自动' | '智能模型'>('智能模型')
const modeOptions = ['手动', '自动', '智能模型']
const weatherText = ref('晴 18~26℃')
const dutyLeader = ref('当班负责人：李工')
const selfCheckStatus = ref('正常')
const alarmDrawer = ref(false)
const alarmCount = ref(2)
const alarms = ref([
  { id: 'A-01', level: '中', text: '3208 补水阀反馈抖动，建议观察', time: '16:05:12' },
  { id: 'A-02', level: '高', text: '316 密度偏差超过阈值 0.08', time: '16:07:44' },
])
const activeCommand = ref<Record<string, 'start' | 'auto' | 'reset'>>({})

const setpointText = computed(() => {
  if (!setpoint.value) return '--'
  return `${setpoint.value.predMiddlingDensity} / ${setpoint.value.predCleanDensity}`
})
const setpointMiddling = computed(() => setpoint.value?.predMiddlingDensity ?? 1.42)
const setpointClean = computed(() => setpoint.value?.predCleanDensity ?? 1.36)
const densityValue = computed(() => Number(result.value?.predDensity ?? 0))
const magneticValue = computed(() => Number(result.value?.predWater ?? 0))
const densityMeterClass = computed(() => {
  if (densityValue.value >= 1.5 || densityValue.value <= 1.32) return 'warn'
  if (densityValue.value >= 1.47 || densityValue.value <= 1.35) return 'attention'
  return 'good'
})
const magneticMeterClass = computed(() => {
  if (magneticValue.value >= 14 || magneticValue.value <= 6) return 'warn'
  if (magneticValue.value >= 12 || magneticValue.value <= 8) return 'attention'
  return 'good'
})
const densityMeterText = computed(() => (densityMeterClass.value === 'good' ? '正常' : densityMeterClass.value === 'attention' ? '预警' : '异常'))
const magneticMeterText = computed(() => (magneticMeterClass.value === 'good' ? '正常' : magneticMeterClass.value === 'attention' ? '预警' : '异常'))
const flowBase = computed(() => {
  const diverter = Number(result.value?.predDiverter ?? 35)
  const water = Number(result.value?.predWater ?? 10)
  const speedFactor = Math.min(2.2, Math.max(0.6, (diverter + water) / 55))
  return Math.max(1.2, 4.4 - speedFactor)
})
const flowDurationBlue = computed(() => flowBase.value.toFixed(2))
const flowDurationGold = computed(() => (flowBase.value + 0.5).toFixed(2))
const flowDurationGreen = computed(() => (flowBase.value + 0.9).toFixed(2))

function toNumber(value: string) {
  const n = Number(String(value).replace(/[^\d.-]/g, ''))
  return Number.isFinite(n) ? n : 0
}

function controlAction(action: 'start' | 'auto' | 'reset', unit: string) {
  activeCommand.value[unit] = action
  const actionText = action === 'start' ? '启动' : action === 'auto' ? '自动' : '复位'
  ElMessage.success(`设备 ${unit} 已执行${actionText}指令（演示）`)
}

function updateTime() {
  currentTime.value = new Date().toLocaleString('zh-CN', { hour12: false })
}

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

async function loadOverview() {
  try {
    const data = await getSmartDensityOverview()
    overviewRows.value = data.units
    setpoint.value = data.setpoint
  } catch {
    overviewRows.value = [
      { unit: '3207', area: '主洗二段', status: '运行中', density: '1.43', diverter: '43%', water: '11.8', mode: '演示回退' },
      { unit: '3208', area: '主洗三段', status: '运行中', density: '1.47', diverter: '46%', water: '12.6', mode: '演示回退' },
      { unit: '316', area: '末煤系统', status: '待校正', density: '1.38', diverter: '38%', water: '9.8', mode: '演示回退' },
    ]
    setpoint.value = { predMiddlingDensity: 1.46, predCleanDensity: 1.38, mode: '演示回退' }
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
    const [predictResult, setpointResult] = await Promise.all([
      predictSmartDensity(payload),
      predictSmartDensitySetpoint({ data: payload.dataLong.slice(0, 3) }),
    ])
    result.value = predictResult
    setpoint.value = setpointResult
    await nextTick()
    renderChart()
    ElMessage.success(`智能密控 ${selectedUnit.value} 调用完成`)
  } catch (error: any) {
    ElMessage.error(error?.message || '智能密控调用失败')
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
      data: ['分流阀', '补水阀', '预测密度'],
      axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
      splitLine: { lineStyle: { color: INDUSTRIAL_CHART_COLORS.grid } },
    },
    grid: { left: '3%', right: '4%', top: '8%', bottom: '8%', containLabel: true },
    series: [
      {
        type: 'bar',
        data: [result.value.predDiverter, result.value.predWater, result.value.predDensity],
        itemStyle: {
          color: (params: any) => [INDUSTRIAL_CHART_COLORS.primary, INDUSTRIAL_CHART_COLORS.secondary, INDUSTRIAL_CHART_COLORS.warning][params.dataIndex],
          borderRadius: [8, 8, 0, 0],
        },
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
.density-screen {
  min-height: 100vh;
  padding: 14px 18px 20px;
  background: radial-gradient(circle at 50% 0%, rgba(71, 111, 163, 0.2), transparent 30%), #0a1220;
  color: #eaf6ff;
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
.screen-title { font-size: 24px; font-weight: 700; letter-spacing: 1px; }
.screen-sub { justify-self: center; color: #87c8ff; font-weight: 600; }
.screen-time { justify-self: end; color: #b8dfff; font-size: 13px; }
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
.flow-shell {
  display: grid;
  grid-template-columns: 240px 1fr 240px;
  gap: 12px;
  margin-bottom: 12px;
}
.metric-col { display: grid; gap: 10px; }
.metric-box {
  padding: 12px;
  border: 1px solid rgba(154, 188, 224, 0.22);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(7px);
}
.metric-box span { font-size: 12px; color: #8ec5ec; }
.metric-box strong { display: block; margin-top: 6px; font-size: 28px; color: #59d0ff; }
.metric-box--green strong { color: #58efbe; }
.metric-box--blue strong { color: #75b6ff; }
.metric-box--warn strong { color: #ffd666; }
.meter-box {
  padding: 10px 12px;
  border: 1px solid rgba(154, 188, 224, 0.22);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  display: grid;
  gap: 8px;
}
.meter-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  gap: 8px;
}
.meter-row span { font-size: 12px; color: #a9c5dc; }
.meter-row b { font-size: 12px; color: #d9e9f7; font-weight: 600; }
.meter-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.meter-dot.good { background: #3dd598; box-shadow: 0 0 8px rgba(61, 213, 152, 0.45); }
.meter-dot.attention { background: #fdb731; box-shadow: 0 0 8px rgba(253, 183, 49, 0.45); }
.meter-dot.warn { background: #ff6b6b; box-shadow: 0 0 8px rgba(255, 107, 107, 0.45); }
.process-board {
  position: relative;
  min-height: 220px;
  border: 1px solid rgba(154, 188, 224, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
  overflow: hidden;
}
.process-svg { width: 100%; height: 100%; min-height: 220px; }
.flow-line {
  fill: none;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: 8 6;
  animation: flowMove 3.5s linear infinite;
  filter: url(#glow);
}
.flow-line--blue { stroke: url(#pipeBlue); }
.flow-line--gold { stroke: url(#pipeGold); animation-duration: 4.1s; }
.flow-line--green { stroke: #64f7b9; animation-duration: 4.6s; }
.equip-box {
  fill: rgba(213, 235, 255, 0.22);
  stroke: rgba(162, 211, 255, 0.55);
  stroke-width: 1.2;
}
.equip-text {
  fill: #d6edff;
  font-size: 12px;
  text-anchor: middle;
  dominant-baseline: middle;
}
.flow-node {
  fill: #79d8ff;
  stroke: #d8f3ff;
  stroke-width: 1.2;
}
@keyframes flowMove {
  from { stroke-dashoffset: 0; }
  to { stroke-dashoffset: -56; }
}
.unit-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}
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
.panel-head { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 10px; }
.panel-head h2 { margin: 0; font-size: 18px; }
.panel-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 10px; }
.field { display: grid; gap: 6px; }
.field span { font-size: 12px; color: #9fc7ea; }
.field--full { grid-column: 1 / -1; }
.chart-box { height: 260px; }
.alarm-list {
  display: grid;
  gap: 10px;
}
.alarm-item {
  border: 1px solid rgba(255, 168, 168, 0.35);
  border-radius: 10px;
  background: rgba(255, 89, 89, 0.08);
  padding: 10px;
}
.alarm-item strong { color: #ffd2d2; }
.alarm-item p { margin: 6px 0; color: #fce9e9; }
.alarm-item small { color: #e8b8b8; }
@media (max-width: 1300px) {
  .flow-shell { grid-template-columns: 1fr; }
  .unit-grid, .form-grid { grid-template-columns: 1fr; }
}
</style>
