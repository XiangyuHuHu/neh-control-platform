<template>
  <div ref="screenShellRef" class="dashboard-screen">
    <div class="screen-canvas" :style="{ transform: `scale(${screenScale})` }">
    <section class="screen-header">
      <div class="header-weather">
        <span>{{ weather.city }}</span>
        <span>{{ weather.time }}</span>
        <strong>{{ weather.temp }}</strong>
        <span>{{ weather.text }}</span>
      </div>
      <div class="header-title" aria-hidden="true"></div>
      <div class="header-actions">
        <button v-for="item in actionTabs" :key="item.key" type="button" :class="{ active: activeAction === item.key }" @click="activeAction = item.key">
          {{ item.label }}
        </button>
      </div>
    </section>

      <section class="screen-grid">
      <article class="panel">
        <div class="panel-title">产销趋势</div>
        <div ref="trendChartRef" class="chart chart--small"></div>
      </article>

      <article class="panel panel--center">
        <div class="center-layout">
          <div class="center-top-values">
            <div v-for="item in siloLabels" :key="item.name" class="silo-label" :style="item.style">
              <strong>{{ item.name }}</strong>
              <span>{{ item.value }}</span>
            </div>
          </div>

          <div class="globe-shell">
            <div class="globe-ring"></div>
            <div class="globe-core">
              <h2>201入洗原煤量</h2>
              <strong>0吨</strong>
            </div>

            <div class="metric-float float-left">
              <span>硫分</span>
              <strong>1.14%</strong>
            </div>
            <div class="metric-float float-bottom">
              <span>灰分</span>
              <strong>17.11%</strong>
            </div>
            <div class="metric-float float-right">
              <span>全水分</span>
              <strong>29%</strong>
            </div>
            <div class="metric-float float-right-top">
              <span>发热量</span>
              <strong>3724KJ</strong>
            </div>
          </div>

          <div class="center-actions">
            <button type="button" @click="openConsumeModal('all')">消耗数据</button>
            <button type="button" @click="notify('已切换生产数据视图')">生产数据</button>
            <button type="button" @click="showDeviceLedger = true">设备KPI</button>
            <button type="button" @click="notify('已切换数据支持视图')">数据支持</button>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-title">实时仓位</div>
        <div ref="stockChartRef" class="chart chart--small"></div>
      </article>

      <article class="panel">
        <div class="panel-title">煤质化验</div>
        <div ref="qualityChartRef" class="chart chart--small"></div>
      </article>

      <article class="panel">
        <div class="panel-title">调度日报</div>
        <table class="mini-table">
          <thead>
            <tr>
              <th>汇报时间</th>
              <th>汇报内容</th>
              <th>汇报人</th>
              <th>接班人</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in dispatchRows" :key="item.time + item.reporter">
              <td>{{ item.time }}</td>
              <td>{{ item.content }}</td>
              <td>{{ item.reporter }}</td>
              <td>{{ item.receiver }}</td>
            </tr>
          </tbody>
        </table>
      </article>

      <article class="panel">
        <div class="panel-title">环境数据</div>
        <table class="mini-table">
          <thead>
            <tr>
              <th>仓名称</th>
              <th>类型</th>
              <th>实时值</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in envRows" :key="item.name">
              <td>{{ item.name }}</td>
              <td>{{ item.type }}</td>
              <td>{{ item.value }}</td>
            </tr>
          </tbody>
        </table>
      </article>

      <article class="panel">
        <div class="panel-title">设备信息</div>
        <div ref="deviceInfoPieRef" class="chart chart--small"></div>
      </article>
      </section>

    <el-dialog v-model="showDeviceLedger" title="台账树" width="88%" class="blue-dialog">
      <div class="ledger-layout">
        <aside class="ledger-tree">
          <div class="ledger-toolbar">
            <el-select v-model="ledgerMode" size="large">
              <el-option label="按系统" value="system" />
              <el-option label="按车间" value="workshop" />
            </el-select>
            <el-input v-model="ledgerKeyword" placeholder="输入关键字进行过滤" />
          </div>
          <el-tree
            :data="filteredLedgerTree"
            node-key="id"
            default-expand-all
            :expand-on-click-node="false"
            :current-node-key="selectedLedgerId"
            @node-click="handleLedgerSelect"
          />
        </aside>
        <section class="ledger-detail" v-if="selectedLedger">
          <div class="ledger-tabs">
            <button v-for="tab in ledgerTabs" :key="tab" type="button" :class="['ledger-tab', { active: activeLedgerTab === tab }]" @click="activeLedgerTab = tab">
              {{ tab }}
            </button>
          </div>
          <div class="ledger-card">
            <div class="device-hero">
              <div class="device-image"></div>
              <div class="device-meta">
                <div class="meta-row"><span>设备名称</span><strong>{{ selectedLedger.name }}</strong></div>
                <div class="meta-row"><span>规格型号</span><strong>{{ selectedLedger.model }}</strong></div>
                <div class="meta-row"><span>系统类型</span><strong>{{ selectedLedger.system }}</strong></div>
                <div class="meta-row"><span>当前状态</span><strong>{{ selectedLedger.status }}</strong></div>
              </div>
            </div>

            <div v-if="activeLedgerTab === '设备属性'" class="detail-grid">
              <div class="detail-cell"><span>安装位置</span><strong>{{ selectedLedger.location }}</strong></div>
              <div class="detail-cell"><span>设备类型</span><strong>{{ selectedLedger.type }}</strong></div>
              <div class="detail-cell"><span>使用部门</span><strong>{{ selectedLedger.department }}</strong></div>
              <div class="detail-cell"><span>投运日期</span><strong>{{ selectedLedger.startDate }}</strong></div>
            </div>
            <div v-else-if="activeLedgerTab === '技术参数'" class="detail-grid">
              <div v-for="item in selectedLedger.params" :key="item.label" class="detail-cell">
                <span>{{ item.label }}</span>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
            <table v-else-if="activeLedgerTab === '维修台账'" class="detail-table">
              <thead><tr><th>日期</th><th>类型</th><th>内容</th><th>执行人</th></tr></thead>
              <tbody>
                <tr v-for="item in selectedLedger.repairs" :key="item.date + item.type">
                  <td>{{ item.date }}</td>
                  <td>{{ item.type }}</td>
                  <td>{{ item.content }}</td>
                  <td>{{ item.user }}</td>
                </tr>
              </tbody>
            </table>
            <table v-else-if="activeLedgerTab === '设备部件'" class="detail-table">
              <thead><tr><th>部件</th><th>状态</th><th>寿命</th></tr></thead>
              <tbody>
                <tr v-for="item in selectedLedger.parts" :key="item.name">
                  <td>{{ item.name }}</td>
                  <td>{{ item.status }}</td>
                  <td>{{ item.life }}</td>
                </tr>
              </tbody>
            </table>
            <div v-else class="detail-grid">
              <div class="detail-cell"><span>近24小时运行时长</span><strong>{{ selectedLedger.runtime }}</strong></div>
              <div class="detail-cell"><span>平均温度</span><strong>{{ selectedLedger.avgTemp }}</strong></div>
              <div class="detail-cell"><span>平均振动</span><strong>{{ selectedLedger.avgVibration }}</strong></div>
              <div class="detail-cell"><span>健康评分</span><strong>{{ selectedLedger.health }}</strong></div>
            </div>
          </div>
        </section>
      </div>
    </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { INDUSTRIAL_CHART_COLORS, buildIndustrialLineStyle, echarts } from '../../utils/echarts'

type LedgerNode = {
  id: string
  label: string
  children?: LedgerNode[]
  ledgerKey?: string
}

type LedgerItem = {
  key: string
  name: string
  model: string
  system: string
  status: string
  location: string
  type: string
  department: string
  startDate: string
  runtime: string
  avgTemp: string
  avgVibration: string
  health: string
  params: Array<{ label: string; value: string }>
  repairs: Array<{ date: string; type: string; content: string; user: string }>
  parts: Array<{ name: string; status: string; life: string }>
}

const weather = {
  city: '鄂尔多斯市',
  time: '2025-01-13 11:30',
  temp: '-7°',
  text: '晴',
}

const actionTabs = [
  { key: 'all', label: '消耗数据' },
  { key: 'production', label: '生产数据' },
  { key: 'device', label: '设备KPI' },
  { key: 'support', label: '数据支持' },
]
const activeAction = ref('all')
const showDeviceLedger = ref(false)

const siloLabels = [
  { name: '501末原煤', value: '0吨', style: { left: '12%', top: '10%' } },
  { name: '3313末原煤', value: '0吨', style: { left: '34%', top: '4%' } },
  { name: '502末精煤', value: '0吨', style: { left: '58%', top: '4%' } },
  { name: '503块精煤', value: '0吨', style: { left: '78%', top: '10%' } },
  { name: '303块原煤', value: '0吨', style: { left: '8%', top: '36%' } },
  { name: '101原煤', value: '0吨', style: { left: '10%', top: '58%' } },
  { name: '3203', value: '0吨', style: { left: '84%', top: '42%' } },
]

const dispatchRows = [
  { time: '2025-01-13', content: '夜班正常交接', reporter: '刘丽媛', receiver: '杨慧洁' },
  { time: '2025-01-12', content: '中班正常交接', reporter: '张申立', receiver: '刘丽媛' },
  { time: '2025-01-12', content: '早班正常交接', reporter: '杨慧洁', receiver: '张申立' },
  { time: '2025-01-12', content: '夜班正常交接', reporter: '刘丽媛', receiver: '杨慧洁' },
  { time: '2025-01-11', content: '中班正常交接', reporter: '张申立', receiver: '刘丽媛' },
]

const envRows = [
  { name: '1#原煤仓', type: '温度', value: '26.4°C' },
  { name: '1#产品仓', type: '湿度', value: '63%' },
  { name: '3#产品仓', type: '粉尘', value: '0.12 mg/m³' },
]

const ledgerTabs = ['设备属性', '技术参数', '维修台账', '设备部件', '设备运行']
const activeLedgerTab = ref('设备属性')
const ledgerMode = ref('system')
const ledgerKeyword = ref('')
const selectedLedgerId = ref('100-pump')

const ledgers: LedgerItem[] = [
  {
    key: '100-pump',
    name: '100扫地泵',
    model: 'Y225M-6',
    system: '原煤仓上',
    status: '在用',
    location: '原煤仓上',
    type: '离心泵',
    department: '滨海金地',
    startDate: '2021-06-18',
    runtime: '21.6 h',
    avgTemp: '48.2°C',
    avgVibration: '1.8 mm/s',
    health: '92 分',
    params: [
      { label: '额定功率', value: '37 kW' },
      { label: '额定流量', value: '260 m³/h' },
      { label: '额定扬程', value: '28 m' },
      { label: '电压', value: '380 V' },
    ],
    repairs: [
      { date: '2026-04-10', type: '保养', content: '更换润滑油并紧固联轴器', user: '周洋' },
      { date: '2026-03-19', type: '检修', content: '处理进口法兰渗漏', user: '王强' },
    ],
    parts: [
      { name: '叶轮', status: '正常', life: '72%' },
      { name: '轴承', status: '关注', life: '58%' },
      { name: '机械密封', status: '正常', life: '81%' },
    ],
  },
]

const ledgerTree: LedgerNode[] = [
  {
    id: 'device-root',
    label: '设备树',
    children: [
      {
        id: 'workshop-1',
        label: '原煤仓上',
        children: [
          { id: '100-pump', label: '100扫地泵', ledgerKey: '100-pump' },
          { id: '101-belt', label: '101带式输送机' },
          { id: '102-remove', label: '102除铁器' },
          { id: '103-scraper', label: '103刮板输送机' },
        ],
      },
      { id: 'workshop-2', label: '原煤仓下' },
      { id: 'workshop-3', label: '筛分车间' },
      { id: 'workshop-4', label: '块煤车间' },
      { id: 'workshop-5', label: '末煤泵房' },
      { id: 'workshop-6', label: '浓缩车间' },
      { id: 'workshop-7', label: '压滤车间' },
      { id: 'workshop-8', label: '超高压车间' },
    ],
  },
]

const filteredLedgerTree = computed(() => {
  const keyword = ledgerKeyword.value.trim()
  if (!keyword) return ledgerTree

  const filterTree = (nodes: LedgerNode[]): LedgerNode[] =>
    nodes
      .map((node) => {
        const children = node.children ? filterTree(node.children) : []
        const matched = node.label.includes(keyword)
        if (matched || children.length > 0) return { ...node, children }
        return null
      })
      .filter(Boolean) as LedgerNode[]

  return filterTree(ledgerTree)
})

const selectedLedger = computed(() => ledgers.find((item) => item.key === selectedLedgerId.value) || ledgers[0])

const handleLedgerSelect = (node: LedgerNode) => {
  if (node.ledgerKey) selectedLedgerId.value = node.ledgerKey
}

const notify = (message: string) => {
  window.alert(message)
}

const openConsumeModal = (type: string) => {
  if (type === 'all') {
    window.location.href = '/coal/energy'
  }
}

const trendChartRef = ref<HTMLElement | null>(null)
const stockChartRef = ref<HTMLElement | null>(null)
const qualityChartRef = ref<HTMLElement | null>(null)
const deviceInfoPieRef = ref<HTMLElement | null>(null)
let trendChart: any = null
let stockChart: any = null
let qualityChart: any = null
let deviceInfoPie: any = null
const screenShellRef = ref<HTMLElement | null>(null)
const DESIGN_WIDTH = 1920
const DESIGN_HEIGHT = 1080
const screenScale = ref(1)

const syncScreenScale = () => {
  if (!screenShellRef.value) return
  const { width, height } = screenShellRef.value.getBoundingClientRect()
  const scale = Math.min(width / DESIGN_WIDTH, height / DESIGN_HEIGHT)
  screenScale.value = Number.isFinite(scale) && scale > 0 ? Math.max(scale, 0.56) : 1
}

const renderCharts = () => {
  if (trendChartRef.value) {
    trendChart ??= echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 26, left: 56, right: 20, bottom: 36 },
      xAxis: {
        type: 'category',
        data: ['01-06', '01-07', '01-08', '01-09', '01-10', '01-11', '01-12'],
        axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
        axisLine: { lineStyle: { color: '#37516d' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
        splitLine: { lineStyle: { color: INDUSTRIAL_CHART_COLORS.grid } },
      },
      series: [
        {
          name: '生产',
          type: 'line',
          data: [29907, 30361, 29061, 21478, 26422, 27764, 23174],
          ...buildIndustrialLineStyle(INDUSTRIAL_CHART_COLORS.primary),
        },
      ],
    })
  }

  if (stockChartRef.value) {
    stockChart ??= echarts.init(stockChartRef.value)
    stockChart.setOption({
      grid: { top: 26, left: 50, right: 20, bottom: 36 },
      xAxis: {
        type: 'category',
        data: ['1#原煤仓', '1#产品仓', '3#产品仓', '2#精煤仓', '4#产品仓', '5#原煤仓'],
        axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
        axisLine: { lineStyle: { color: '#37516d' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
        splitLine: { lineStyle: { color: INDUSTRIAL_CHART_COLORS.grid } },
        max: 100,
      },
      series: [
        {
          type: 'bar',
          data: [0, 0, 0, 0, 0, 0],
          itemStyle: { color: INDUSTRIAL_CHART_COLORS.warning },
          barWidth: 28,
        },
      ],
    })
  }

  if (qualityChartRef.value) {
    qualityChart ??= echarts.init(qualityChartRef.value)
    qualityChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { top: 0, textStyle: { color: INDUSTRIAL_CHART_COLORS.axis } },
      grid: { top: 30, left: 50, right: 20, bottom: 40 },
      xAxis: {
        type: 'category',
        data: ['01-06', '01-07', '01-08', '01-09', '01-10', '01-11', '01-12'],
        axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
        axisLine: { lineStyle: { color: '#37516d' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: INDUSTRIAL_CHART_COLORS.axis },
        splitLine: { lineStyle: { color: INDUSTRIAL_CHART_COLORS.grid } },
      },
      series: [
        {
          name: '灰分',
          type: 'line',
          data: [17.5, 17.2, 17.4, 17.8, 17.6, 17.3, 17.1],
          ...buildIndustrialLineStyle(INDUSTRIAL_CHART_COLORS.primary),
        },
        {
          name: '硫分',
          type: 'line',
          data: [1.1, 1.05, 1.13, 1.09, 1.14, 1.12, 1.1],
          ...buildIndustrialLineStyle(INDUSTRIAL_CHART_COLORS.secondary),
        },
      ],
    })
  }

  if (deviceInfoPieRef.value) {
    deviceInfoPie ??= echarts.init(deviceInfoPieRef.value)
    deviceInfoPie.setOption({
      legend: { right: 0, top: 'middle', orient: 'vertical', textStyle: { color: INDUSTRIAL_CHART_COLORS.axis } },
      series: [
        {
          type: 'pie',
          radius: ['52%', '74%'],
          center: ['35%', '52%'],
          data: [
            { value: 209, name: '在用', itemStyle: { color: INDUSTRIAL_CHART_COLORS.primary } },
            { value: 0, name: '备用', itemStyle: { color: INDUSTRIAL_CHART_COLORS.secondary } },
            { value: 0, name: '报废', itemStyle: { color: INDUSTRIAL_CHART_COLORS.warning } },
            { value: 0, name: '维修', itemStyle: { color: INDUSTRIAL_CHART_COLORS.critical } },
          ],
          label: { color: '#eaf6ff' },
        },
      ],
    })
  }
}

onMounted(() => {
  syncScreenScale()
  renderCharts()
  window.addEventListener('resize', syncScreenScale)
  window.addEventListener('resize', renderCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncScreenScale)
  window.removeEventListener('resize', renderCharts)
  trendChart?.dispose()
  stockChart?.dispose()
  qualityChart?.dispose()
  deviceInfoPie?.dispose()
})
</script>

<style scoped>
.dashboard-screen {
  height: calc(100vh - 80px);
  overflow: hidden;
  padding: 8px;
  background:
    radial-gradient(circle at center, rgba(38, 166, 255, 0.14), transparent 28%),
    #040914;
  color: #eaf6ff;
}

.screen-canvas {
  width: 1920px;
  height: 1080px;
  margin: 0 auto;
  transform-origin: top center;
}

.screen-header,
.screen-grid {
  width: 100%;
  margin: 0;
}

.screen-header {
  display: grid;
  grid-template-columns: 1fr 1.4fr 1fr;
  align-items: center;
  margin-bottom: 18px;
}

.header-weather,
.header-actions {
  display: flex;
  gap: 14px;
  align-items: center;
  color: rgba(234, 246, 255, 0.88);
}

.header-actions {
  justify-content: flex-end;
}

.header-actions button {
  height: 52px;
  padding: 0 24px;
  border: 0;
  background: rgba(18, 228, 255, 0.14);
  color: #17e3ff;
  cursor: pointer;
}

.header-actions button.active {
  background: #12dcff;
  color: #031423;
  font-weight: 700;
}

.header-title {
  text-align: center;
  min-height: 54px;
}

.screen-grid {
  display: grid;
  grid-template-columns: 0.72fr 1.44fr 0.72fr;
  grid-template-rows: 390px 310px 270px;
  gap: 10px;
}

.panel {
  position: relative;
  border: 1px solid rgba(40, 184, 255, 0.58);
  background: linear-gradient(180deg, rgba(8, 18, 41, 0.94), rgba(3, 8, 20, 0.92));
  box-shadow: inset 0 0 28px rgba(0, 180, 255, 0.08);
  overflow: hidden;
}

.panel::before,
.panel::after {
  content: '';
  position: absolute;
  width: 70px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #31e7ff);
  top: 10px;
}

.panel::before {
  left: 12px;
}

.panel::after {
  right: 12px;
}

.panel-title {
  padding: 16px 18px 8px;
  color: #12e3ff;
  font-size: 18px;
  font-weight: 700;
}

.chart {
  width: 100%;
  height: calc(100% - 50px);
}

.chart--small {
  min-height: 250px;
}

.panel--center {
  grid-row: 1 / span 3;
  padding-bottom: 16px;
  overflow-x: hidden;
  overflow-y: auto;
  padding-inline: clamp(12px, 1.6vw, 28px);
}

.center-layout {
  height: calc(100% - 42px);
  position: relative;
  display: grid;
  grid-template-rows: 1fr auto;
}

.center-top-values {
  position: relative;
  min-height: 120px;
  padding-inline: clamp(4px, 1vw, 12px);
  box-sizing: border-box;
}

.silo-label {
  position: absolute;
  display: grid;
  gap: 8px;
  color: #1fe4ff;
  text-align: center;
}

.silo-label strong {
  font-size: 20px;
}

.silo-label span {
  font-size: 18px;
  color: #fff;
}

.globe-shell {
  position: relative;
  margin: clamp(16px, 3vw, 40px) auto clamp(12px, 2vw, 18px);
  width: min(720px, 100%);
  aspect-ratio: 1;
  height: auto;
  max-height: min(720px, 58vh);
  box-sizing: border-box;
}

.globe-ring {
  position: absolute;
  inset: 15.28%;
  border-radius: 50%;
  border: 6px solid rgba(21, 226, 255, 0.8);
  box-shadow:
    0 0 34px rgba(21, 226, 255, 0.45),
    inset 0 0 34px rgba(21, 226, 255, 0.25);
}

.globe-core {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: min(47.22%, 340px);
  height: min(31.94%, 230px);
  max-width: 90%;
  border-radius: 999px;
  background: linear-gradient(180deg, rgba(25, 230, 255, 0.92), rgba(18, 149, 190, 0.88));
  display: grid;
  place-content: center;
  text-align: center;
  color: #05253b;
  box-shadow: 0 0 36px rgba(25, 230, 255, 0.38);
}

.globe-core h2 {
  margin: 0;
  font-size: clamp(18px, 2.6vw, 34px);
}

.globe-core strong {
  margin-top: 12px;
  font-size: clamp(28px, 5vw, 64px);
  font-weight: 500;
}

.metric-float {
  position: absolute;
  width: min(23.6%, 170px);
  height: min(16.1%, 116px);
  display: grid;
  place-content: center;
  text-align: center;
  background: linear-gradient(180deg, rgba(58, 240, 255, 0.36), rgba(33, 120, 156, 0.28));
  clip-path: polygon(50% 0%, 100% 35%, 100% 70%, 50% 100%, 0% 70%, 0% 35%);
  box-shadow: 0 0 24px rgba(58, 240, 255, 0.22);
}

.metric-float span {
  color: #d8faff;
}

.metric-float strong {
  font-size: 22px;
}

.float-left {
  left: 12.5%;
  bottom: 24.7%;
}

.float-bottom {
  left: 50%;
  bottom: 4.2%;
  transform: translateX(-50%);
}

.float-right {
  right: 12.5%;
  bottom: 24.7%;
}

.float-right-top {
  right: 22%;
  top: 24%;
}

.center-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  padding: 0 clamp(8px, 6vw, 180px) 10px;
  box-sizing: border-box;
}

.center-actions button {
  height: 72px;
  border: 2px solid rgba(22, 229, 255, 0.75);
  background: linear-gradient(180deg, rgba(12, 226, 255, 0.95), rgba(10, 169, 209, 0.9));
  color: #042136;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
}

.mini-table {
  width: calc(100% - 28px);
  margin: 0 14px 14px;
  border-collapse: collapse;
}

.mini-table th,
.mini-table td {
  padding: 14px 12px;
  text-align: left;
}

.mini-table thead th {
  background: rgba(112, 138, 230, 0.9);
  color: #fff;
  font-size: 14px;
}

.mini-table tbody tr:nth-child(odd) {
  background: rgba(17, 37, 83, 0.88);
}

.mini-table tbody tr:nth-child(even) {
  background: rgba(10, 27, 63, 0.88);
}

.blue-dialog :deep(.el-dialog) {
  background: rgba(6, 20, 52, 0.96);
  border: 3px solid rgba(60, 243, 255, 0.8);
  box-shadow: 0 0 30px rgba(60, 243, 255, 0.18);
}

.blue-dialog :deep(.el-dialog__title),
.blue-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #fff;
}

.ledger-layout {
  display: grid;
  grid-template-columns: 430px 1fr;
  gap: 16px;
  min-height: 620px;
}

.ledger-tree,
.ledger-detail {
  border: 1px solid rgba(93, 177, 255, 0.32);
  background: rgba(10, 30, 70, 0.88);
}

.ledger-tree {
  padding: 16px;
}

.ledger-toolbar {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 10px;
  margin-bottom: 16px;
}

.ledger-tree :deep(.el-tree) {
  background: transparent;
  color: #d9efff;
}

.ledger-tree :deep(.el-tree-node__content) {
  height: 34px;
}

.ledger-tree :deep(.el-tree--highlight-current .el-tree-node.is-current > .el-tree-node__content) {
  background: rgba(90, 144, 221, 0.65);
  color: #fff;
}

.ledger-detail {
  padding: 0 0 18px;
}

.ledger-tabs {
  display: flex;
  border-bottom: 1px solid rgba(93, 177, 255, 0.32);
}

.ledger-tab {
  height: 42px;
  padding: 0 16px;
  border: 0;
  border-right: 1px solid rgba(93, 177, 255, 0.18);
  background: transparent;
  color: rgba(217, 239, 255, 0.72);
  cursor: pointer;
}

.ledger-tab.active {
  color: #51d9ff;
  background: rgba(38, 79, 154, 0.28);
}

.ledger-card {
  padding: 18px;
}

.device-hero {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 18px;
  margin-bottom: 18px;
}

.device-image {
  width: 160px;
  height: 120px;
  border: 1px solid rgba(95, 180, 255, 0.3);
  background: linear-gradient(135deg, rgba(71, 139, 255, 0.45), rgba(14, 33, 76, 0.92));
}

.device-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  border-top: 1px solid rgba(95, 180, 255, 0.24);
  border-left: 1px solid rgba(95, 180, 255, 0.24);
}

.meta-row,
.detail-cell {
  display: grid;
  gap: 8px;
  padding: 14px 16px;
  border-right: 1px solid rgba(95, 180, 255, 0.24);
  border-bottom: 1px solid rgba(95, 180, 255, 0.24);
}

.meta-row span,
.detail-cell span {
  color: rgba(217, 239, 255, 0.72);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
}

.detail-table th,
.detail-table td {
  padding: 14px 12px;
  border: 1px solid rgba(95, 180, 255, 0.24);
}

@media (max-width: 1600px) {
  .screen-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }

  .globe-shell {
    width: min(720px, 100%);
    height: auto;
    aspect-ratio: 1;
    max-height: min(560px, 72vh);
  }

  .center-actions,
  .ledger-layout,
  .device-hero,
  .detail-grid,
  .device-meta {
    grid-template-columns: 1fr;
  }
}
</style>
