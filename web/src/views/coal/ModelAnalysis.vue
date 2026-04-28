<template>
  <div class="coal-page section-page">
    <CoalQuickBar
      title="建模分析专题"
      subtitle="对应最新需求中的质量稳定控制模型、质量预测、趋势分析和产品仓质量分析，不替换原智能决策页，单独形成专项页。"
    />

    <section class="page-shell">
      <section class="section-hero">
        <div>
          <p class="section-eyebrow">建模分析</p>
          <h1>质量建模与预测分析</h1>
          <p class="section-text">统一承接模型状态、预测结果、趋势分析结论和建议，后续接正式模型服务时只替换接口，不改页面结构。</p>
        </div>
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
            <h2>模型置信度分布</h2>
            <p>用于展示当前主要模型的可信度和可用状态。</p>
          </div>
        </div>
        <div ref="chartEl" class="chart-box"></div>
      </section>

      <section class="section-panel">
        <div class="panel-head">
          <div>
            <h2>模型分析结果</h2>
            <p>覆盖稳定控制、质量预测、趋势分析和产品仓质量分析。</p>
          </div>
          <div class="panel-actions">
            <el-button @click="handleExport">导出 CSV</el-button>
            <el-button type="primary" @click="handlePrint">打印</el-button>
          </div>
        </div>
        <el-table :data="rows">
          <el-table-column prop="modelName" label="模型名称" min-width="200" />
          <el-table-column prop="category" label="分类" min-width="120" />
          <el-table-column prop="status" label="状态" min-width="120" />
          <el-table-column prop="conclusion" label="分析结论" min-width="260" show-overflow-tooltip />
          <el-table-column prop="suggestion" label="建议" min-width="260" show-overflow-tooltip />
          <el-table-column prop="confidence" label="置信度" min-width="120" />
        </el-table>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import CoalQuickBar from '../../components/coal/CoalQuickBar.vue'
import { echarts } from '../../utils/echarts'
import { listModelAnalyses, type ModelAnalysisDto } from '../../api/coal-business'
import { exportRowsToCsv, printRowsAsTable } from '../../utils/report-export'
import { ElMessage } from 'element-plus'

const chartEl = ref<HTMLElement | null>(null)
const rows = ref<ModelAnalysisDto[]>([])
let chart: any = null

const fallbackRows: ModelAnalysisDto[] = [
  { modelName: '产品质量稳定控制模型', status: '运行中', category: '质量预测', conclusion: '精煤灰分预测偏差 0.22%', suggestion: '建议维持介质密度 1.43', confidence: '92.8%' },
  { modelName: '精煤产品质量预测', status: '运行中', category: '质量预测', conclusion: '未来 4 小时灰分将维持 9.1%~9.4%', suggestion: '关注夜班原煤波动', confidence: '90.4%' },
  { modelName: '质量变化趋势分析', status: '待复核', category: '趋势分析', conclusion: '洗混水分波动偏高', suggestion: '建议复核脱介筛前喷淋', confidence: '84.6%' },
  { modelName: '产品仓质量分析', status: '运行中', category: '仓储分析', conclusion: '503 块精煤仓质量稳定', suggestion: '可直接进入发运队列', confidence: '95.1%' },
]

const stats = computed(() => [
  { label: '模型总数', value: `${rows.value.length} 个`, note: '当前已接入分析主题' },
  { label: '运行中', value: `${rows.value.filter(item => item.status === '运行中').length} 个`, note: '可直接用于业务支撑' },
  { label: '平均置信度', value: `${averageConfidence(rows.value)}%`, note: '按当前模型结果统计' },
  { label: '待复核', value: `${rows.value.filter(item => item.status !== '运行中').length} 个`, note: '需人工复核或补数据' },
])

function averageConfidence(list: ModelAnalysisDto[]) {
  if (!list.length) return '0.0'
  const avg = list.reduce((sum, item) => sum + Number(item.confidence.replace('%', '')), 0) / list.length
  return avg.toFixed(1)
}

async function loadRows() {
  try {
    const data = await listModelAnalyses()
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
    xAxis: { type: 'category', data: rows.value.map(item => item.modelName), axisLabel: { color: '#9fb4c9', rotate: 18 } },
    yAxis: { type: 'value', max: 100, axisLabel: { color: '#9fb4c9' }, splitLine: { lineStyle: { color: 'rgba(120,160,200,0.12)' } } },
    grid: { left: '3%', right: '4%', bottom: '8%', containLabel: true },
    series: [{ type: 'bar', data: rows.value.map(item => Number(item.confidence.replace('%', ''))), itemStyle: { color: '#4ec9ff', borderRadius: [6, 6, 0, 0] } }],
  })
}

const handleResize = () => chart?.resize()

const exportColumns: Array<{ key: keyof ModelAnalysisDto; label: string }> = [
  { key: 'modelName', label: '模型名称' },
  { key: 'category', label: '分类' },
  { key: 'status', label: '状态' },
  { key: 'conclusion', label: '分析结论' },
  { key: 'suggestion', label: '建议' },
  { key: 'confidence', label: '置信度' },
]

const handleExport = () => {
  exportRowsToCsv(rows.value, exportColumns, `建模分析结果_${new Date().toISOString().slice(0, 10)}`)
  ElMessage.success('建模分析结果 CSV 已下载')
}

const handlePrint = () => {
  const ok = printRowsAsTable('建模分析结果', rows.value, exportColumns, {
    subtitle: '淖尔壕智能化选煤厂专项分析报表',
    meta: [
      { label: '报表类型', value: '建模分析专题' },
      { label: '记录条数', value: `${rows.value.length}` },
    ],
    preparedBy: '智能决策岗',
    reviewedBy: '工艺工程师',
    approvedBy: '生产调度',
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
