<template>
  <div class="report-page">
    <CoalQuickBar
      title="经营分析报表"
      subtitle="统一承接生产、质量、能源和设备报表，全部改为中文说明，便于后续直接接正式数据。"
    />

    <section class="hero">
      <div>
        <p class="eyebrow">报表中心</p>
        <h1>综合报表分析</h1>
        <p class="hero-text">当前版本以演示数据验证页面结构、图表和明细表，后续直接替换成正式接口即可。</p>
      </div>
      <div class="hero-actions">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          :class="['tab-btn', { active: activeReport === tab.key }]"
          @click="activeReport = tab.key"
        >
          {{ tab.label }}
        </button>
        <el-button type="primary" @click="exportReport">导出报表</el-button>
      </div>
    </section>

    <section class="chart-row">
      <article class="panel">
        <div class="panel-head">
          <h2>{{ currentState.leftTitle }}</h2>
        </div>
        <div ref="leftChartRef" class="chart-box"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <h2>{{ currentState.rightTitle }}</h2>
        </div>
        <div ref="rightChartRef" class="chart-box"></div>
      </article>
    </section>

    <section class="panel table-panel">
      <div class="panel-head">
        <div>
          <h2>{{ currentState.tableTitle }}</h2>
          <p>报表明细与上方图表联动，便于做成果展示和验收。</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th v-for="column in currentState.columns" :key="column.prop">{{ column.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in currentState.tableData" :key="index">
              <td v-for="column in currentState.columns" :key="column.prop">
                <template v-if="column.type === 'tag'">
                  <span class="badge" :class="getTagClass(String(row[column.prop]))">{{ row[column.prop] }}</span>
                </template>
                <template v-else-if="column.type === 'progress'">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: `${Number(row[column.prop])}%`, background: getProgressColor(Number(row[column.prop])) }"></div>
                  </div>
                </template>
                <template v-else>
                  {{ row[column.prop] }}
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import CoalQuickBar from '../../components/coal/CoalQuickBar.vue'
import { echarts } from '../../utils/echarts'

type ReportKey = 'production' | 'quality' | 'energy' | 'equipment'
type Column = { prop: string; label: string; type?: 'tag' | 'progress' }
type ReportState = {
  leftTitle: string
  rightTitle: string
  tableTitle: string
  columns: Column[]
  tableData: Array<Record<string, string | number>>
  leftOption: Record<string, unknown>
  rightOption: Record<string, unknown>
}

const tabs = [
  { key: 'production' as ReportKey, label: '生产报表' },
  { key: 'quality' as ReportKey, label: '质量报表' },
  { key: 'energy' as ReportKey, label: '能源报表' },
  { key: 'equipment' as ReportKey, label: '设备报表' },
]

const chartTheme = {
  axisLabel: { color: '#9bb7d5' },
  axisLine: { lineStyle: { color: '#203447' } },
  splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
}

const activeReport = ref<ReportKey>('production')
const leftChartRef = ref<HTMLElement | null>(null)
const rightChartRef = ref<HTMLElement | null>(null)
let leftChart: any = null
let rightChart: any = null

const reportStates: Record<ReportKey, ReportState> = {
  production: {
    leftTitle: '日产量趋势',
    rightTitle: '产品结构占比',
    tableTitle: '生产日报明细',
    columns: [
      { prop: 'date', label: '日期' },
      { prop: 'plan', label: '计划产量' },
      { prop: 'actual', label: '实际产量' },
      { prop: 'completion', label: '完成率', type: 'progress' },
      { prop: 'remark', label: '备注' },
    ],
    tableData: [
      { date: '04-14', plan: 12603, actual: 24980, completion: 68.5, remark: '设备巡检期间短时降负荷' },
      { date: '04-15', plan: 12603, actual: 26480, completion: 71.1, remark: '生产平稳，回收率正常' },
      { date: '04-16', plan: 12603, actual: 26463, completion: 70.9, remark: '停车检修，产量受限' },
    ],
    leftOption: {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['04-14', '04-15', '04-16'], ...chartTheme },
      yAxis: { type: 'value', ...chartTheme },
      series: [{ type: 'line', smooth: true, data: [24980, 26480, 26463], itemStyle: { color: '#57d8ff' } }],
    },
    rightOption: {
      tooltip: { trigger: 'item' },
      series: [{ type: 'pie', radius: ['40%', '72%'], data: [{ value: 39, name: '精煤' }, { value: 31, name: '中煤' }, { value: 30, name: '矸石及其他' }] }],
    },
  },
  quality: {
    leftTitle: '质量指标趋势',
    rightTitle: '质量等级分布',
    tableTitle: '质量化验记录',
    columns: [
      { prop: 'sample', label: '样品名称' },
      { prop: 'ash', label: '灰分' },
      { prop: 'moisture', label: '水分' },
      { prop: 'result', label: '结论', type: 'tag' },
    ],
    tableData: [
      { sample: '湿混', ash: '39.6%', moisture: '36.7%', result: '合格' },
      { sample: '干后煤泥', ash: '40.57%', moisture: '27%', result: '合格' },
      { sample: '混配样', ash: '40.1%', moisture: '30.2%', result: '关注' },
    ],
    leftOption: {
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#dbe7ff' } },
      xAxis: { type: 'category', data: ['湿混', '干后煤泥', '混配样'], ...chartTheme },
      yAxis: { type: 'value', ...chartTheme },
      series: [
        { name: '灰分', type: 'line', data: [39.6, 40.57, 40.1], itemStyle: { color: '#57d8ff' } },
        { name: '水分', type: 'line', data: [36.7, 27, 30.2], itemStyle: { color: '#25d39c' } },
      ],
    },
    rightOption: {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['合格', '关注', '异常'], ...chartTheme },
      yAxis: { type: 'value', ...chartTheme },
      series: [{ type: 'bar', data: [2, 1, 0], itemStyle: { color: '#57d8ff' }, barWidth: 36 }],
    },
  },
  energy: {
    leftTitle: '月度能源成本',
    rightTitle: '单位产量单耗',
    tableTitle: '能源费用月报',
    columns: [
      { prop: 'month', label: '月份' },
      { prop: 'electricity', label: '电力费用' },
      { prop: 'water', label: '用水费用' },
      { prop: 'medicine', label: '药剂费用' },
      { prop: 'unit', label: '单耗' },
    ],
    tableData: [
      { month: '1 月', electricity: '8.2 万', water: '1.1 万', medicine: '0.9 万', unit: '12.4' },
      { month: '2 月', electricity: '7.8 万', water: '1.0 万', medicine: '0.8 万', unit: '12.1' },
      { month: '3 月', electricity: '8.5 万', water: '1.2 万', medicine: '0.9 万', unit: '12.7' },
    ],
    leftOption: {
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#dbe7ff' } },
      xAxis: { type: 'category', data: ['1 月', '2 月', '3 月'], ...chartTheme },
      yAxis: { type: 'value', ...chartTheme },
      series: [
        { name: '电力', type: 'bar', data: [8.2, 7.8, 8.5], itemStyle: { color: '#57d8ff' } },
        { name: '用水', type: 'bar', data: [1.1, 1.0, 1.2], itemStyle: { color: '#21d4a4' } },
      ],
    },
    rightOption: {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['1 月', '2 月', '3 月'], ...chartTheme },
      yAxis: { type: 'value', ...chartTheme },
      series: [{ type: 'line', smooth: true, data: [12.4, 12.1, 12.7], itemStyle: { color: '#ffc857' } }],
    },
  },
  equipment: {
    leftTitle: '设备状态分布',
    rightTitle: '报警类型统计',
    tableTitle: '设备运行周报',
    columns: [
      { prop: 'device', label: '设备名称' },
      { prop: 'runtime', label: '运行时长' },
      { prop: 'alarm', label: '报警次数' },
      { prop: 'health', label: '健康度', type: 'progress' },
      { prop: 'status', label: '状态', type: 'tag' },
    ],
    tableData: [
      { device: '主破碎机', runtime: '1560 h', alarm: 1, health: 92, status: '正常' },
      { device: '转载皮带', runtime: '2340 h', alarm: 2, health: 85, status: '关注' },
      { device: '压滤机', runtime: '890 h', alarm: 4, health: 68, status: '告警' },
    ],
    leftOption: {
      tooltip: { trigger: 'item' },
      series: [{ type: 'pie', radius: ['40%', '72%'], data: [{ value: 45, name: '正常' }, { value: 8, name: '关注' }, { value: 3, name: '告警' }] }],
    },
    rightOption: {
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['振动异常', '温度异常', '电流过载'], ...chartTheme },
      yAxis: { type: 'value', ...chartTheme },
      series: [{ type: 'bar', data: [3, 2, 1], itemStyle: { color: '#ff7b72' }, barWidth: 36 }],
    },
  },
}

const currentState = computed(() => reportStates[activeReport.value])

const renderCharts = () => {
  if (leftChartRef.value) {
    leftChart ??= echarts.init(leftChartRef.value)
    leftChart.setOption(currentState.value.leftOption)
  }
  if (rightChartRef.value) {
    rightChart ??= echarts.init(rightChartRef.value)
    rightChart.setOption(currentState.value.rightOption)
  }
}

const getTagClass = (value: string) => {
  if (value === '合格' || value === '正常') return 'good'
  if (value === '关注') return 'warn'
  return 'bad'
}

const getProgressColor = (value: number) => {
  if (value >= 90) return '#21d4a4'
  if (value >= 75) return '#ffc857'
  return '#ff7b72'
}

const exportReport = () => {
  ElMessage.success(`${tabs.find((tab) => tab.key === activeReport.value)?.label || '当前'}已导出`)
}

watch(activeReport, async () => {
  await nextTick()
  renderCharts()
})

onMounted(async () => {
  await nextTick()
  renderCharts()
  window.addEventListener('resize', renderCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderCharts)
  leftChart?.dispose()
  rightChart?.dispose()
})
</script>

<style scoped>
.report-page {
  min-height: 100vh;
  padding: 0 20px 24px;
  background: #091019;
  color: #eef6ff;
}

.hero,
.chart-row,
.table-panel {
  width: min(100%, 1680px);
  margin: 0 auto 16px;
}

.hero,
.panel {
  border: 1px solid rgba(96, 183, 255, 0.12);
  border-radius: 18px;
  background: rgba(8, 19, 30, 0.92);
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #7ecfff;
  font-size: 12px;
  letter-spacing: 0.12em;
}

.hero h1,
.panel-head h2 {
  margin: 0;
}

.hero-text,
.panel-head p {
  margin: 10px 0 0;
  color: rgba(227, 239, 250, 0.66);
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 10px 16px;
  border: 1px solid rgba(96, 183, 255, 0.18);
  border-radius: 12px;
  background: rgba(10, 23, 36, 0.86);
  color: rgba(227, 239, 250, 0.78);
  cursor: pointer;
}

.tab-btn.active {
  color: #57d8ff;
  border-color: rgba(87, 216, 255, 0.4);
  box-shadow: 0 0 0 1px rgba(87, 216, 255, 0.1) inset;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.panel {
  padding: 24px;
}

.chart-box {
  height: 320px;
}

.table-wrap {
  overflow-x: auto;
}

.table-wrap table {
  width: 100%;
  border-collapse: collapse;
}

.table-wrap th,
.table-wrap td {
  padding: 14px 12px;
  border-bottom: 1px solid rgba(96, 183, 255, 0.08);
  text-align: left;
}

.table-wrap th {
  color: #7ecfff;
  font-size: 13px;
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.badge.good {
  background: rgba(33, 212, 164, 0.16);
  color: #21d4a4;
}

.badge.warn {
  background: rgba(255, 200, 87, 0.16);
  color: #ffc857;
}

.badge.bad {
  background: rgba(255, 123, 114, 0.16);
  color: #ff7b72;
}

.progress-bar {
  width: 90px;
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: inherit;
}

@media (max-width: 1100px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
  }
}
</style>
