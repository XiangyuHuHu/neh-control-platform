<template>
  <div class="coal-page section-page">
    <CoalQuickBar
      title="安全与健康专项"
      subtitle="独立承接人员安全、区域健康指标和风险闭环，避免与巡检总览页面混用。"
    />

    <section class="page-shell">
      <section class="section-hero">
        <div>
          <p class="section-eyebrow">安全与健康</p>
          <h1>安全风险与健康状态中心</h1>
          <p class="section-text">覆盖各区域关键风险等级、健康指标和责任闭环，为值班和调度提供专项视图。</p>
        </div>
      </section>

      <section class="section-panel filters">
        <el-select v-model="filterLevel" clearable placeholder="风险等级" style="width:180px">
          <el-option label="高风险" value="高风险" />
          <el-option label="中风险" value="中风险" />
          <el-option label="低风险" value="低风险" />
        </el-select>
        <el-button type="primary" @click="handleQuery">查询</el-button>
        <el-button @click="handleRefresh">刷新</el-button>
        <span class="refresh-note">自动刷新：30 秒（最近更新：{{ lastUpdatedText }}）</span>
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
            <h2>风险等级分布</h2>
            <p>用于跟踪高、中、低风险事项数量。</p>
          </div>
        </div>
        <div ref="chartEl" class="chart-box"></div>
      </section>

      <section class="section-panel">
        <div class="panel-head">
          <div>
            <h2>安全与健康清单</h2>
            <p>支持打印和导出，便于班前会和专项复盘。</p>
          </div>
          <div class="panel-actions">
            <el-button @click="handleExport">导出 CSV</el-button>
            <el-button type="primary" @click="handlePrint">打印</el-button>
          </div>
        </div>
        <el-table :data="pagedRows" @row-click="openDetail">
          <el-table-column prop="area" label="区域" min-width="140" />
          <el-table-column prop="metricType" label="指标类型" min-width="120" />
          <el-table-column prop="level" label="风险等级" min-width="110">
            <template #default="{ row }">
              <el-tag :type="levelTagType(row.level)" effect="dark">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="120">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)" effect="plain">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="value" label="当前值" min-width="120" />
          <el-table-column prop="risk" label="风险描述" min-width="220" show-overflow-tooltip />
          <el-table-column prop="owner" label="责任人" min-width="100" />
          <el-table-column prop="rectificationNo" label="整改单号" min-width="150" />
          <el-table-column prop="closureStatus" label="闭环状态" min-width="110" />
          <el-table-column prop="updateTime" label="更新时间" min-width="160" />
        </el-table>
        <div class="pager-wrap">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="rows.length"
            layout="total, prev, pager, next"
            background
          />
        </div>
      </section>
    </section>

    <el-drawer v-model="detailVisible" title="风险详情" size="40%">
      <el-descriptions :column="1" border v-if="selectedRow">
        <el-descriptions-item label="区域">{{ selectedRow.area }}</el-descriptions-item>
        <el-descriptions-item label="指标类型">{{ selectedRow.metricType }}</el-descriptions-item>
        <el-descriptions-item label="风险等级">
          <el-tag :type="levelTagType(selectedRow.level)" effect="dark">{{ selectedRow.level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTagType(selectedRow.status)" effect="plain">{{ selectedRow.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="当前值">{{ selectedRow.value }}</el-descriptions-item>
        <el-descriptions-item label="风险描述">{{ selectedRow.risk }}</el-descriptions-item>
        <el-descriptions-item label="责任人">{{ selectedRow.owner }}</el-descriptions-item>
        <el-descriptions-item label="整改单号">{{ selectedRow.rectificationNo }}</el-descriptions-item>
        <el-descriptions-item label="完成时限">{{ selectedRow.deadline }}</el-descriptions-item>
        <el-descriptions-item label="闭环状态">{{ selectedRow.closureStatus }}</el-descriptions-item>
        <el-descriptions-item label="复盘结论">{{ selectedRow.reviewConclusion }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ selectedRow.updateTime }}</el-descriptions-item>
      </el-descriptions>
      <div class="drawer-actions" v-if="selectedRow">
        <el-button type="primary" @click="openRectificationDialog">派发整改</el-button>
        <el-button @click="markForReview">标记复核</el-button>
      </div>
    </el-drawer>

    <el-dialog v-model="rectificationDialogVisible" title="派发整改" width="520px">
      <el-form label-width="100px">
        <el-form-item label="责任人">
          <el-input v-model="rectificationForm.owner" placeholder="请输入责任人" />
        </el-form-item>
        <el-form-item label="完成时限">
          <el-input v-model="rectificationForm.deadline" placeholder="例如：2026-04-15 10:30" />
        </el-form-item>
        <el-form-item label="整改说明">
          <el-input v-model="rectificationForm.reviewConclusion" type="textarea" :rows="3" placeholder="请输入整改要求" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rectificationDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRectification">确认派发</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import CoalQuickBar from '../../components/coal/CoalQuickBar.vue'
import { echarts } from '../../utils/echarts'
import { exportRowsToCsv, printRowsAsTable } from '../../utils/report-export'
import { listSafetyHealth, type SafetyHealthDto } from '../../api/coal-business'

const filterLevel = ref('')
const rows = ref<SafetyHealthDto[]>([])
const selectedRow = ref<SafetyHealthDto | null>(null)
const detailVisible = ref(false)
const currentPage = ref(1)
const pageSize = 8
const lastUpdatedText = ref('--')
const rectificationDialogVisible = ref(false)
const rectificationForm = ref({
  owner: '',
  deadline: '',
  reviewConclusion: '',
})
const chartEl = ref<HTMLElement | null>(null)
let chart: any = null
let refreshTimer = 0

const fallbackRows: SafetyHealthDto[] = [
  { area: '主洗车间', metricType: '粉尘浓度', level: '高风险', status: '超阈值', value: '6.4 mg/m3', risk: '连续 15 分钟高于阈值', owner: '赵强', rectificationNo: 'AQZG-20260415-001', deadline: '2026-04-15 10:00', closureStatus: '整改中', reviewConclusion: '通风恢复后复测待通过', updateTime: '2026-04-15 08:20' },
  { area: '精煤仓上', metricType: '人员定位', level: '中风险', status: '需复核', value: '2 人滞留', risk: '非作业时段停留超过 10 分钟', owner: '王建', rectificationNo: 'AQZG-20260415-002', deadline: '2026-04-15 09:30', closureStatus: '待复核', reviewConclusion: '需补充现场说明和轨迹截图', updateTime: '2026-04-15 08:15' },
  { area: '压滤车间', metricType: '噪声强度', level: '低风险', status: '已恢复', value: '79 dB', risk: '短时波动已回落', owner: '李燕', rectificationNo: 'AQZG-20260415-003', deadline: '2026-04-15 12:00', closureStatus: '已闭环', reviewConclusion: '复测连续 3 次达标', updateTime: '2026-04-15 08:08' },
  { area: '原煤仓下', metricType: '安全帽识别', level: '高风险', status: '处理中', value: '1 次未佩戴', risk: 'AI 识别到未佩戴防护装备', owner: '刘刚', rectificationNo: 'AQZG-20260415-004', deadline: '2026-04-15 09:00', closureStatus: '整改中', reviewConclusion: '已现场教育，待班组复核', updateTime: '2026-04-15 08:02' },
]

const stats = computed(() => [
  { label: '风险总数', value: `${rows.value.length} 条`, note: '当前筛选结果' },
  { label: '高风险', value: `${rows.value.filter((item) => item.level === '高风险').length} 条`, note: '优先派单处理' },
  { label: '处理中', value: `${rows.value.filter((item) => item.status === '处理中').length} 条`, note: '跟踪闭环进度' },
  { label: '已恢复', value: `${rows.value.filter((item) => item.status === '已恢复').length} 条`, note: '可纳入复盘样本' },
])

const exportColumns: Array<{ key: keyof SafetyHealthDto; label: string }> = [
  { key: 'area', label: '区域' },
  { key: 'metricType', label: '指标类型' },
  { key: 'level', label: '风险等级' },
  { key: 'status', label: '状态' },
  { key: 'value', label: '当前值' },
  { key: 'risk', label: '风险描述' },
  { key: 'owner', label: '责任人' },
  { key: 'rectificationNo', label: '整改单号' },
  { key: 'deadline', label: '完成时限' },
  { key: 'closureStatus', label: '闭环状态' },
  { key: 'reviewConclusion', label: '复盘结论' },
  { key: 'updateTime', label: '更新时间' },
]

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return rows.value.slice(start, start + pageSize)
})

async function loadRows(showToast = false) {
  try {
    const data = await listSafetyHealth({ level: filterLevel.value })
    rows.value = data.length ? data : fallbackRows
  } catch {
    rows.value = fallbackRows
  }
  currentPage.value = 1
  lastUpdatedText.value = new Date().toLocaleString('zh-CN', { hour12: false })
  await nextTick()
  renderChart()
  if (showToast) ElMessage.success('安全与健康数据已刷新')
}

function renderChart() {
  if (!chartEl.value) return
  chart?.dispose()
  chart = echarts.init(chartEl.value)
  const categories = ['高风险', '中风险', '低风险']
  const values = categories.map((key) => rows.value.filter((item) => item.level === key).length)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: categories, axisLabel: { color: '#9fb4c9' } },
    yAxis: { type: 'value', axisLabel: { color: '#9fb4c9' }, splitLine: { lineStyle: { color: 'rgba(120,160,200,0.12)' } } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    series: [{ type: 'bar', data: values, itemStyle: { color: '#ff8f4e', borderRadius: [6, 6, 0, 0] } }],
  })
}

const handleExport = () => {
  exportRowsToCsv(rows.value, exportColumns, `安全与健康清单_${new Date().toISOString().slice(0, 10)}`)
  ElMessage.success('安全与健康清单 CSV 已下载')
}

const handleQuery = () => loadRows(true)
const handleRefresh = () => loadRows(true)

const handlePrint = () => {
  const ok = printRowsAsTable('安全与健康清单', rows.value, exportColumns, {
    subtitle: '淖尔壕智能化选煤厂安全风险专项报表',
    meta: [
      { label: '筛选等级', value: filterLevel.value || '全部' },
      { label: '记录条数', value: `${rows.value.length}` },
    ],
    preparedBy: '安全员',
    reviewedBy: '安监科',
    approvedBy: '值班矿长',
  })
  if (!ok) {
    ElMessage.warning('浏览器拦截了打印窗口，请允许弹窗后重试')
    return
  }
  ElMessage.success('已打开打印预览')
}

const levelTagType = (level: string) => {
  if (level === '高风险') return 'danger'
  if (level === '中风险') return 'warning'
  return 'success'
}

const statusTagType = (status: string) => {
  if (status === '处理中' || status === '需复核') return 'warning'
  if (status === '超阈值') return 'danger'
  return 'success'
}

const openDetail = (row: SafetyHealthDto) => {
  selectedRow.value = row
  detailVisible.value = true
}

const updateRow = (target: SafetyHealthDto) => {
  rows.value = rows.value.map((item) => (item.rectificationNo === target.rectificationNo ? { ...target } : item))
  selectedRow.value = { ...target }
  nextTick(() => renderChart())
}

const openRectificationDialog = () => {
  if (!selectedRow.value) return
  rectificationForm.value = {
    owner: selectedRow.value.owner,
    deadline: selectedRow.value.deadline,
    reviewConclusion: selectedRow.value.reviewConclusion,
  }
  rectificationDialogVisible.value = true
}

const submitRectification = () => {
  if (!selectedRow.value) return
  const current = { ...selectedRow.value }
  current.owner = rectificationForm.value.owner || current.owner
  current.deadline = rectificationForm.value.deadline || current.deadline
  current.reviewConclusion = rectificationForm.value.reviewConclusion || current.reviewConclusion
  current.closureStatus = '整改中'
  current.status = '处理中'
  current.updateTime = new Date().toLocaleString('zh-CN', { hour12: false })
  updateRow(current)
  rectificationDialogVisible.value = false
  ElMessage.success('整改任务已派发')
}

const markForReview = () => {
  if (!selectedRow.value) return
  const current = { ...selectedRow.value }
  current.closureStatus = '待复核'
  current.status = '需复核'
  current.reviewConclusion = current.reviewConclusion || '整改已完成，等待复核'
  current.updateTime = new Date().toLocaleString('zh-CN', { hour12: false })
  updateRow(current)
  ElMessage.success('已标记为待复核')
}

const handleResize = () => chart?.resize()
onMounted(async () => {
  await loadRows()
  refreshTimer = window.setInterval(() => loadRows(), 30000)
  window.addEventListener('resize', handleResize)
})
onUnmounted(() => {
  clearInterval(refreshTimer)
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
.refresh-note{color:#8fb0c8;font-size:12px}
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
.pager-wrap{display:flex;justify-content:flex-end;margin-top:12px}
.drawer-actions{display:flex;gap:10px;margin-top:16px}
@media (max-width: 1200px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width: 768px){.stats-grid{grid-template-columns:1fr}}
</style>
