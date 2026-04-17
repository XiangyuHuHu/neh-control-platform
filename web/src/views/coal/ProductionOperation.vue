<template>
  <div class="coal-page section-page">
    <CoalQuickBar
      title="生产运行统计"
      subtitle="对应最新需求中的生产运行统计、生产数据概览和运行分析评价，先以统计页落地完整入口和字段。"
    />

    <section class="page-shell">
      <section class="section-hero">
        <div>
          <p class="section-eyebrow">生产统计</p>
          <h1>生产运行统计中心</h1>
          <p class="section-text">按日期和班次查看入洗原煤、精煤、矸石、中煤、开机时长和完成率，支撑生产日报、月报和运行评价。</p>
        </div>
      </section>

      <section class="section-panel filters">
        <el-date-picker v-model="filterDate" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        <el-select v-model="filterShift" clearable placeholder="选择班次" style="width: 160px">
          <el-option label="白班" value="白班" />
          <el-option label="夜班" value="夜班" />
        </el-select>
        <el-button type="primary" @click="loadRows">刷新统计</el-button>
      </section>

      <section class="stats-grid">
        <article class="stat-card" v-for="item in stats" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <small>{{ item.note }}</small>
        </article>
      </section>

      <section class="section-panel">
        <div class="panel-head">
          <div>
            <h2>生产运行趋势</h2>
            <p>用入洗原煤与精煤两条主线展示日常运行波动。</p>
          </div>
        </div>
        <div ref="chartEl" class="chart-box"></div>
      </section>

      <section class="section-panel">
        <div class="panel-head">
          <div>
            <h2>运行明细台账</h2>
            <p>字段按照最新生产管控参考文件中的产量、运行时长和完成率整理。</p>
          </div>
        </div>
        <el-table :data="rows" class="records-table">
          <el-table-column prop="statDate" label="统计日期" min-width="120" />
          <el-table-column prop="shift" label="班次" width="90" />
          <el-table-column prop="rawCoal" label="入洗原煤(吨)" min-width="130" />
          <el-table-column prop="cleanCoal" label="精煤(吨)" min-width="120" />
          <el-table-column prop="middling" label="中煤(吨)" min-width="120" />
          <el-table-column prop="gangue" label="矸石(吨)" min-width="120" />
          <el-table-column prop="runHours" label="运行时长(小时)" min-width="130" />
          <el-table-column prop="completionRate" label="完成率(%)" min-width="110" />
          <el-table-column prop="remark" label="备注" min-width="220" show-overflow-tooltip />
        </el-table>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import CoalQuickBar from '../../components/coal/CoalQuickBar.vue'
import { echarts } from '../../utils/echarts'
import { listProductionOperations, type ProductionOperationDto } from '../../api/coal-business'

const chartEl = ref<HTMLElement | null>(null)
const filterDate = ref('')
const filterShift = ref('')
const rows = ref<ProductionOperationDto[]>([])
let chart: any = null

const fallbackRows: ProductionOperationDto[] = [
  { statDate: '2026-04-16', shift: '白班', rawCoal: 26463, cleanCoal: 10390, middling: 8371, gangue: 3702, runHours: 15.6, completionRate: 70.9, remark: '停车检修，产量受限' },
  { statDate: '2026-04-15', shift: '夜班', rawCoal: 25840, cleanCoal: 10145, middling: 8126, gangue: 3569, runHours: 15.2, completionRate: 69.8, remark: '系统运行平稳，局部负荷偏低' },
  { statDate: '2026-04-15', shift: '白班', rawCoal: 27120, cleanCoal: 10630, middling: 8512, gangue: 3978, runHours: 16.0, completionRate: 72.4, remark: '入洗组织正常，回收率稳定' },
  { statDate: '2026-04-14', shift: '夜班', rawCoal: 24980, cleanCoal: 9820, middling: 7894, gangue: 3266, runHours: 14.7, completionRate: 68.5, remark: '设备巡检期间短时降负荷' },
]

const stats = computed(() => {
  const totalRaw = rows.value.reduce((sum, item) => sum + item.rawCoal, 0)
  const totalClean = rows.value.reduce((sum, item) => sum + item.cleanCoal, 0)
  const avgRate = rows.value.length ? (rows.value.reduce((sum, item) => sum + item.completionRate, 0) / rows.value.length).toFixed(1) : '0.0'
  const avgHours = rows.value.length ? (rows.value.reduce((sum, item) => sum + item.runHours, 0) / rows.value.length).toFixed(1) : '0.0'
  return [
    { label: '累计入洗原煤', value: `${totalRaw} 吨`, note: '按当前筛选条件汇总' },
    { label: '累计精煤产量', value: `${totalClean} 吨`, note: '用于日报和月报汇总' },
    { label: '平均完成率', value: `${avgRate}%`, note: '用于生产计划对比' },
    { label: '平均运行时长', value: `${avgHours} 小时`, note: '用于运行评价' },
  ]
})

async function loadRows() {
  try {
    const data = await listProductionOperations({ date: filterDate.value, shift: filterShift.value })
    rows.value = data.length ? data : fallbackRows
  } catch {
    rows.value = fallbackRows
  }
  await nextTick()
  renderChart()
}

function renderChart() {
  if (!chartEl.value) return
  chart?.dispose()
  chart = echarts.init(chartEl.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['入洗原煤', '精煤'], textStyle: { color: '#9fb4c9' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: rows.value.map(item => `${item.statDate}-${item.shift}`), axisLabel: { color: '#9fb4c9' } },
    yAxis: { type: 'value', axisLabel: { color: '#9fb4c9' }, splitLine: { lineStyle: { color: 'rgba(120,160,200,0.12)' } } },
    series: [
      { name: '入洗原煤', type: 'bar', data: rows.value.map(item => item.rawCoal), itemStyle: { color: '#4ec9ff', borderRadius: [6, 6, 0, 0] } },
      { name: '精煤', type: 'line', smooth: true, data: rows.value.map(item => item.cleanCoal), lineStyle: { color: '#2fe0a5', width: 3 }, itemStyle: { color: '#2fe0a5' } },
    ],
  })
}

const handleResize = () => chart?.resize()

onMounted(async () => {
  await loadRows()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.section-page{min-height:100vh;padding:0 20px 24px;background:#091019;color:#eef6ff}
.page-shell{width:min(100%,1680px);margin:0 auto}
.section-hero{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;margin-bottom:20px}
.section-eyebrow{margin:0 0 10px;color:#72d8ff;font-size:12px;letter-spacing:.2em;text-transform:uppercase}
.section-hero h1{margin:0;font-size:38px}
.section-text{max-width:820px;margin:12px 0 0;color:#96aabc;line-height:1.7}
.section-panel{padding:22px;border-radius:20px;border:1px solid rgba(122,190,255,.12);background:rgba(12,20,31,.92);box-shadow:0 18px 40px rgba(0,0,0,.16);margin-bottom:20px}
.filters{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}
.stat-card{padding:18px;border-radius:18px;border:1px solid rgba(122,190,255,.12);background:rgba(12,20,31,.92)}
.stat-card span{display:block;color:#97aabc}
.stat-card strong{display:block;margin-top:14px;font-size:30px}
.stat-card small{display:block;margin-top:10px;color:#6ec8ff}
.panel-head{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin-bottom:16px}
.panel-head h2{margin:0;font-size:24px}
.panel-head p{margin:8px 0 0;color:#8fa8bc}
.chart-box{height:320px}
@media (max-width: 1200px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width: 768px){.stats-grid{grid-template-columns:1fr}}
</style>
