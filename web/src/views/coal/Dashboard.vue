<template>
  <div class="business-page">
    <section class="page-header">
      <div>
        <p class="page-tag">综合数据</p>
        <h1>综合数据总览</h1>
        <p class="page-desc">保留业务总览页，用于日常查看指标、台账和调度信息；大屏展示单独通过入口打开。</p>
      </div>
      <div class="page-actions">
        <el-button @click="router.push('/coal/production')">生产分析</el-button>
        <el-button @click="router.push('/coal/dispatch')">调度管理</el-button>
        <el-button type="primary" @click="router.push('/coal/dashboard-screen')">查看综合大屏</el-button>
      </div>
    </section>

    <section class="kpi-grid">
      <article v-for="item in kpis" :key="item.label" class="kpi-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.note }}</small>
      </article>
    </section>

    <section class="content-grid">
      <article class="panel panel--wide">
        <div class="panel-head">
          <div>
            <h2>入洗与产销趋势</h2>
            <p>最近 7 天的入洗量、精煤量和销量变化。</p>
          </div>
        </div>
        <div ref="trendChartRef" class="chart-box"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>仓位状态</h2>
            <p>关键仓位当前占用情况。</p>
          </div>
        </div>
        <div ref="stockChartRef" class="chart-box chart-box--small"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>煤质指标</h2>
            <p>灰分、硫分和全水分趋势。</p>
          </div>
        </div>
        <div ref="qualityChartRef" class="chart-box chart-box--small"></div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>调度日报</h2>
            <p>班组交接和日常调度摘要。</p>
          </div>
        </div>
        <el-table :data="dispatchRows" class="data-table">
          <el-table-column prop="time" label="时间" width="120" />
          <el-table-column prop="content" label="内容" min-width="220" />
          <el-table-column prop="reporter" label="汇报人" width="120" />
          <el-table-column prop="receiver" label="接班人" width="120" />
        </el-table>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>环境数据</h2>
            <p>重点仓位与区域环境监控。</p>
          </div>
        </div>
        <el-table :data="envRows" class="data-table">
          <el-table-column prop="name" label="监测点" min-width="140" />
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="value" label="当前值" width="120" />
          <el-table-column prop="status" label="状态" width="100" />
        </el-table>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { echarts } from '../../utils/echarts'
import { useIotHub } from '../../composables/useIotHub'

const router = useRouter()
const iotHub = useIotHub()

const getRealtimeValue = (tagCode: string, fallback: number, digits = 1) => {
  const live = iotHub.getTagValue(tagCode)
  if (!live || typeof live.value !== 'number') return fallback.toFixed(digits)
  return live.value.toFixed(digits)
}

const abnormalCount = computed(
  () => Object.values(iotHub.realtimeMap.value).filter((item) => item.quality !== 'GOOD').length,
)

const kpis = computed(() => [
  {
    label: '今日入洗原煤',
    value: `${getRealtimeValue('coal.feed.daily', 2900, 0)} 吨`,
    note: '来自 IOT 汇总点位',
  },
  {
    label: '今日精煤产量',
    value: `${getRealtimeValue('coal.product.daily', 2180, 0)} 吨`,
    note: '按实时点位估算',
  },
  {
    label: '综合单耗',
    value: getRealtimeValue('coal.energy.unit', 12.1, 1),
    note: '按吨煤折算',
  },
  {
    label: '待处理告警',
    value: `${abnormalCount.value || 2} 项`,
    note: '质量异常点位统计',
  },
])

const dispatchRows = [
  { time: '2025-01-13', content: '夜班正常交接，主洗系统运行稳定。', reporter: '刘丽媛', receiver: '杨慧洁' },
  { time: '2025-01-12', content: '中班产量达标，产品仓切换完成。', reporter: '张申立', receiver: '刘丽媛' },
  { time: '2025-01-12', content: '早班入洗原煤波动，已调整密度。', reporter: '杨慧洁', receiver: '张申立' },
]

const envRows = computed(() => {
  const temp = iotHub.getTagValue('coal.env.raw.temperature')
  const humidity = iotHub.getTagValue('coal.env.product.humidity')
  const dust = iotHub.getTagValue('coal.env.product.dust')
  return [
    { name: '1号原煤仓', type: '温度', value: `${temp?.value?.toFixed?.(1) || '26.4'}°C`, status: temp?.quality === 'GOOD' ? '正常' : '关注' },
    { name: '1号产品仓', type: '湿度', value: `${humidity?.value?.toFixed?.(0) || '63'}%`, status: humidity?.quality === 'GOOD' ? '正常' : '关注' },
    { name: '3号产品仓', type: '粉尘', value: `${dust?.value?.toFixed?.(2) || '0.12'} mg/m³`, status: dust?.quality === 'GOOD' ? '正常' : '关注' },
  ]
})

const trendChartRef = ref<HTMLElement | null>(null)
const stockChartRef = ref<HTMLElement | null>(null)
const qualityChartRef = ref<HTMLElement | null>(null)

let trendChart: any = null
let stockChart: any = null
let qualityChart: any = null

const renderCharts = () => {
  if (trendChartRef.value) {
    trendChart ??= echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { top: 0, textStyle: { color: '#dbe7ff' } },
      grid: { top: 32, left: 48, right: 20, bottom: 32 },
      xAxis: {
        type: 'category',
        data: ['01-06', '01-07', '01-08', '01-09', '01-10', '01-11', '01-12'],
        axisLabel: { color: '#9bb7d5' },
        axisLine: { lineStyle: { color: '#203447' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#9bb7d5' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series: [
        { name: '入洗量', type: 'bar', data: [2800, 2315, 2500, 2840, 2960, 2200, 2900], itemStyle: { color: '#7c47ff' } },
        { name: '精煤量', type: 'line', smooth: true, data: [2100, 1805, 1875, 2130, 2220, 1693, 2180], itemStyle: { color: '#3db2ff' } },
        { name: '销量', type: 'line', smooth: true, data: [2050, 1980, 1760, 2080, 2150, 1700, 2105], itemStyle: { color: '#ffd75e' } },
      ],
    })
  }

  if (stockChartRef.value) {
    stockChart ??= echarts.init(stockChartRef.value)
    stockChart.setOption({
      grid: { top: 18, left: 42, right: 20, bottom: 32 },
      xAxis: {
        type: 'category',
        data: ['1#原煤仓', '1#产品仓', '3#产品仓', '2#精煤仓'],
        axisLabel: { color: '#9bb7d5' },
        axisLine: { lineStyle: { color: '#203447' } },
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: { color: '#9bb7d5' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series: [
        { type: 'bar', data: [72, 64, 24, 51], barWidth: 32, itemStyle: { color: '#53c7ff', borderRadius: [8, 8, 0, 0] } },
      ],
    })
  }

  if (qualityChartRef.value) {
    qualityChart ??= echarts.init(qualityChartRef.value)
    qualityChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { top: 0, textStyle: { color: '#dbe7ff' } },
      grid: { top: 32, left: 48, right: 20, bottom: 32 },
      xAxis: {
        type: 'category',
        data: ['01-06', '01-07', '01-08', '01-09', '01-10', '01-11', '01-12'],
        axisLabel: { color: '#9bb7d5' },
        axisLine: { lineStyle: { color: '#203447' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#9bb7d5' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series: [
        { name: '灰分', type: 'line', smooth: true, data: [17.5, 17.2, 17.4, 17.8, 17.6, 17.3, 17.1], itemStyle: { color: '#45cbff' } },
        { name: '硫分', type: 'line', smooth: true, data: [1.1, 1.05, 1.13, 1.09, 1.14, 1.12, 1.1], itemStyle: { color: '#7eff8b' } },
        { name: '全水分', type: 'line', smooth: true, data: [28.6, 28.9, 29.1, 29.3, 29.0, 28.8, 29.0], itemStyle: { color: '#ffd75e' } },
      ],
    })
  }
}

onMounted(() => {
  iotHub.subscribe({ pageKey: 'coal-dashboard', intervalMs: 5000 })
  renderCharts()
  window.addEventListener('resize', renderCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderCharts)
  trendChart?.dispose()
  stockChart?.dispose()
  qualityChart?.dispose()
})
</script>

<style scoped>
.business-page {
  min-height: 100vh;
  padding: 24px 20px 28px;
  background: #091019;
  color: #eef6ff;
}

.page-header,
.kpi-grid,
.content-grid {
  width: min(100%, 1680px);
  margin: 0 auto 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px 30px;
  border: 1px solid rgba(96, 183, 255, 0.12);
  border-radius: 20px;
  background: rgba(8, 19, 30, 0.92);
}

.page-tag {
  margin: 0 0 10px;
  color: #7ecfff;
  font-size: 12px;
  letter-spacing: 0.12em;
}

.page-header h1,
.panel-head h2 {
  margin: 0;
}

.page-desc,
.panel-head p {
  margin: 10px 0 0;
  color: rgba(227, 239, 250, 0.68);
  line-height: 1.7;
}

.page-actions {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.kpi-card,
.panel {
  border: 1px solid rgba(96, 183, 255, 0.12);
  border-radius: 18px;
  background: rgba(8, 19, 30, 0.92);
}

.kpi-card {
  padding: 20px;
}

.kpi-card span {
  display: block;
  color: rgba(227, 239, 250, 0.62);
  font-size: 13px;
}

.kpi-card strong {
  display: block;
  margin-top: 14px;
  font-size: 34px;
  color: #f3faff;
}

.kpi-card small {
  display: block;
  margin-top: 10px;
  color: #67d8ff;
}

.content-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 16px;
}

.panel {
  padding: 24px;
}

.panel--wide {
  grid-column: 1 / -1;
}

.panel-head {
  margin-bottom: 18px;
}

.chart-box {
  height: 320px;
}

.chart-box--small {
  height: 280px;
}

.data-table :deep(.el-table),
.data-table :deep(.el-table__inner-wrapper),
.data-table :deep(.el-table tr),
.data-table :deep(.el-table th.el-table__cell),
.data-table :deep(.el-table td.el-table__cell) {
  background: transparent;
  color: #eef6ff;
}

.data-table :deep(.el-table__header th.el-table__cell) {
  color: #7ecfff;
}

@media (max-width: 1200px) {
  .kpi-grid,
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .page-header {
    flex-direction: column;
  }

  .page-actions {
    flex-wrap: wrap;
  }
}
</style>
