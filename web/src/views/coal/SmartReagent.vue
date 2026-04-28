<template>
  <div class="coal-page section-page">
    <CoalQuickBar
      title="智能加药"
      subtitle="保留卓朗2算法中的泵频预测、备用泵建议和阀门输出结构，先在扩展功能里形成统一入口。"
      :status="{ text: result?.mode || '演示回退', type: result?.mode === '模型服务' ? 'running' : 'idle' }"
    />

    <section class="page-shell">
      <section class="stats-grid">
        <article class="stat-card">
          <span>预测泵频</span>
          <strong>{{ result?.predPump ?? '--' }}</strong>
          <small>模型输出主泵建议</small>
        </article>
        <article class="stat-card">
          <span>备用泵建议</span>
          <strong>{{ result?.predBackupPump ?? '--' }}</strong>
          <small>0 表示无需切换</small>
        </article>
        <article class="stat-card">
          <span>阀门建议</span>
          <strong>{{ result?.valveMN ?? '--' }}</strong>
          <small>模型输出阀门开度</small>
        </article>
        <article class="stat-card">
          <span>当前状态</span>
          <strong>{{ result?.stateName ?? '--' }}</strong>
          <small>主泵与加药控制状态</small>
        </article>
      </section>

      <section class="panel-grid">
        <section class="section-panel">
          <div class="panel-head">
            <div>
              <h2>模型调用参数</h2>
              <p>保留加药算法原始入参结构，可直接替换为现场实时点位。</p>
            </div>
            <div class="panel-actions">
              <el-select v-model="selectedUnit" style="width: 160px" @change="applyTemplate">
                <el-option v-for="unit in reagentUnits" :key="unit.value" :label="unit.label" :value="unit.value" />
              </el-select>
              <el-button @click="applyTemplate">载入模板</el-button>
              <el-button type="primary" :loading="loading" @click="runPredict">调用模型</el-button>
            </div>
          </div>

          <div class="form-grid">
            <label class="field">
              <span>长周期数据数组</span>
              <el-input v-model="dataLongText" type="textarea" :rows="7" />
            </label>
            <label class="field">
              <span>短周期数据数组</span>
              <el-input v-model="dataShortText" type="textarea" :rows="7" />
            </label>
            <label class="field field--full">
              <span>参数对象</span>
              <el-input v-model="paramsText" type="textarea" :rows="8" />
            </label>
          </div>
        </section>

        <section class="section-panel">
          <div class="panel-head">
            <div>
              <h2>加药单元概览</h2>
              <p>展示四个加药单元的当前状态、泵频和备用泵信息。</p>
            </div>
            <el-button @click="loadOverview">刷新概览</el-button>
          </div>
          <el-table :data="overviewRows">
            <el-table-column prop="unit" label="单元" width="90" />
            <el-table-column prop="area" label="区域" min-width="140" />
            <el-table-column prop="status" label="状态" width="110" />
            <el-table-column prop="pump" label="泵频" width="100" />
            <el-table-column prop="backupPump" label="备用泵" width="100" />
            <el-table-column prop="valve" label="阀门" width="100" />
            <el-table-column prop="mode" label="模式" width="110" />
          </el-table>
        </section>
      </section>

      <section class="section-panel">
        <div class="panel-head">
          <div>
            <h2>加药结果可视化</h2>
            <p>对泵频、阀门和备用泵输出做统一展示，便于和现场 PLC 回写值对比。</p>
          </div>
        </div>
        <div ref="chartEl" class="chart-box"></div>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import CoalQuickBar from '../../components/coal/CoalQuickBar.vue'
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
    series: [
      {
        type: 'bar',
        data: [result.value.predPump, result.value.predBackupPump, result.value.valveMN],
        itemStyle: {
          color: (params: any) => [INDUSTRIAL_CHART_COLORS.primary, INDUSTRIAL_CHART_COLORS.warning, INDUSTRIAL_CHART_COLORS.secondary][params.dataIndex],
          borderRadius: [8, 8, 0, 0],
        },
      },
    ],
  }, true)
}

const handleResize = () => chart?.resize()

onMounted(async () => {
  applyTemplate()
  await loadOverview()
  await runPredict()
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
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}
.stat-card,.section-panel{padding:22px;border-radius:20px;border:1px solid rgba(122,190,255,.12);background:rgba(12,20,31,.92);box-shadow:0 18px 40px rgba(0,0,0,.16)}
.stat-card span{display:block;color:#97aabc}
.stat-card strong{display:block;margin-top:14px;font-size:32px}
.stat-card small{display:block;margin-top:10px;color:#6ec8ff}
.panel-grid{display:grid;grid-template-columns:1.2fr .9fr;gap:20px;margin-bottom:20px}
.panel-head{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin-bottom:16px}
.panel-head h2{margin:0;font-size:24px}
.panel-head p{margin:8px 0 0;color:#8fa8bc}
.panel-actions{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.field{display:grid;gap:8px}
.field span{color:#9bc2df;font-size:13px}
.field--full{grid-column:1 / -1}
.chart-box{height:320px}
@media (max-width: 1200px){.stats-grid,.panel-grid,.form-grid{grid-template-columns:1fr}}
</style>
