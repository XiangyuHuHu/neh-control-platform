<template>
  <div class="coal-page section-page">
    <CoalQuickBar
      title="质量报表中心"
      subtitle="把最新需求里的日报、周报、月报独立成报表中心，保留原报表页作为综合分析入口。"
    />

    <section class="page-shell">
      <section class="section-hero">
        <div>
          <p class="section-eyebrow">质量报表</p>
          <h1>日报周报月报中心</h1>
          <p class="section-text">按报表周期管理质量报表生成、审核和汇总，便于后续直连打印和正式报表接口。</p>
        </div>
      </section>

      <section class="section-panel filters">
        <el-select v-model="filterCycle" clearable placeholder="报表周期" style="width:180px">
          <el-option label="日报" value="日报" />
          <el-option label="周报" value="周报" />
          <el-option label="月报" value="月报" />
        </el-select>
        <el-button type="primary" @click="loadRows">查询</el-button>
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
            <h2>报表状态分布</h2>
            <p>用于验收日报、周报、月报的生成和审核流程。</p>
          </div>
        </div>
        <div ref="chartEl" class="chart-box"></div>
      </section>

      <section class="section-panel">
        <div class="panel-head">
          <div>
            <h2>质量报表列表</h2>
            <p>保留报表名称、日期、状态、责任人和摘要字段。</p>
          </div>
          <div class="panel-actions">
            <el-button @click="handleExport">导出 CSV</el-button>
            <el-button type="primary" @click="handlePrint">打印</el-button>
          </div>
        </div>
        <el-table :data="rows">
          <el-table-column prop="cycle" label="周期" min-width="100" />
          <el-table-column prop="reportDate" label="报表日期" min-width="120" />
          <el-table-column prop="reportName" label="报表名称" min-width="180" />
          <el-table-column prop="status" label="状态" min-width="120" />
          <el-table-column prop="owner" label="责任人" min-width="100" />
          <el-table-column prop="summary" label="摘要" min-width="280" show-overflow-tooltip />
        </el-table>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import CoalQuickBar from '../../components/coal/CoalQuickBar.vue'
import { echarts } from '../../utils/echarts'
import { listQualityReportCenter, type QualityReportCenterDto } from '../../api/coal-business'
import { exportRowsToCsv, printRowsAsTable } from '../../utils/report-export'
import { ElMessage } from 'element-plus'

const filterCycle = ref('')
const rows = ref<QualityReportCenterDto[]>([])
const chartEl = ref<HTMLElement | null>(null)
let chart: any = null

const fallbackRows: QualityReportCenterDto[] = [
  { cycle: '日报', reportDate: '2026-04-15', reportName: '煤质情况统计报表', status: '已生成', owner: '于思源', summary: '湿混：Mt 36.7%，Mad 9.17%，Aad 39.6%，St,ad 0.4%，Qnet,ar 2253' },
  { cycle: '日报', reportDate: '2026-04-15', reportName: '煤质情况统计报表', status: '已生成', owner: '于思源', summary: '干后煤泥：Mt 27%，Mad 6.44%，Aad 40.57%，St,ad 0.36%，Qnet,ar 2678' },
  { cycle: '周报', reportDate: '2026-04-13', reportName: '煤质周度汇总', status: '待审核', owner: '质量科', summary: '本周全硫稳定在 0.35%~0.42%，热值波动可控' },
]

const stats = computed(() => [
  { label: '报表总数', value: `${rows.value.length} 份`, note: '当前筛选结果' },
  { label: '已生成', value: `${rows.value.filter(item => item.status === '已生成').length} 份`, note: '可直接查看或导出' },
  { label: '待审核', value: `${rows.value.filter(item => item.status === '待审核').length} 份`, note: '待质量负责人审核' },
  { label: '编制中', value: `${rows.value.filter(item => item.status === '编制中').length} 份`, note: '待补充分析内容' },
])

async function loadRows() {
  try {
    const data = await listQualityReportCenter({ cycle: filterCycle.value })
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
  const categories = ['已生成', '待审核', '编制中']
  const values = categories.map(key => rows.value.filter(item => item.status === key).length)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: categories, axisLabel: { color: '#9fb4c9' } },
    yAxis: { type: 'value', axisLabel: { color: '#9fb4c9' }, splitLine: { lineStyle: { color: 'rgba(120,160,200,0.12)' } } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    series: [{ type: 'bar', data: values, itemStyle: { color: '#2fe0a5', borderRadius: [6, 6, 0, 0] } }],
  })
}

const handleResize = () => chart?.resize()
const exportColumns: Array<{ key: keyof QualityReportCenterDto; label: string }> = [
  { key: 'cycle', label: '周期' },
  { key: 'reportDate', label: '报表日期' },
  { key: 'reportName', label: '报表名称' },
  { key: 'status', label: '状态' },
  { key: 'owner', label: '责任人' },
  { key: 'summary', label: '摘要' },
]

const handleExport = () => {
  exportRowsToCsv(rows.value, exportColumns, `质量报表中心_${new Date().toISOString().slice(0, 10)}`)
  ElMessage.success('质量报表 CSV 已下载')
}

const handlePrint = () => {
  const ok = printRowsAsTable('质量报表列表', rows.value, exportColumns, {
    subtitle: '金海泽地选煤厂质量报表中心',
    meta: [
      { label: '筛选周期', value: filterCycle.value || '全部' },
      { label: '记录条数', value: `${rows.value.length}` },
    ],
    preparedBy: '质量科',
    reviewedBy: '质检主任',
    approvedBy: '总工办',
  })
  if (!ok) {
    ElMessage.warning('浏览器拦截了打印窗口，请允许弹窗后重试')
    return
  }
  ElMessage.success('已打开打印预览')
}

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
.panel-actions{display:flex;gap:8px;align-items:center}
.panel-head h2{margin:0;font-size:24px}
.panel-head p{margin:8px 0 0;color:#8fa8bc}
.chart-box{height:320px}
@media (max-width: 1200px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width: 768px){.stats-grid{grid-template-columns:1fr}}
</style>
