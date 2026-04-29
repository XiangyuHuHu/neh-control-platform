<template>
  <div class="coal-page section-page">
    <CoalQuickBar
      title="智能密控"
      subtitle="接入卓朗2中的密控模型接口，当前页面先放在扩展功能中，支持演示回退和真实模型代理两种模式。"
      :status="{ text: result?.mode || '演示回退', type: result?.mode === '模型服务' ? 'running' : 'idle' }"
    />

    <section class="page-shell">
      <section class="stats-grid">
        <article class="stat-card">
          <span>当前分流建议</span>
          <strong>{{ result?.predDiverter ?? '--' }}</strong>
          <small>预测分流阀开度</small>
        </article>
        <article class="stat-card">
          <span>当前补水建议</span>
          <strong>{{ result?.predWater ?? '--' }}</strong>
          <small>预测补水阀开度</small>
        </article>
        <article class="stat-card">
          <span>预测密度</span>
          <strong>{{ result?.predDensity ?? '--' }}</strong>
          <small>模型输出密度值</small>
        </article>
        <article class="stat-card">
          <span>设定密度建议</span>
          <strong>{{ setpointText }}</strong>
          <small>中煤 / 精煤密度设定</small>
        </article>
      </section>

      <section class="panel-grid">
        <section class="section-panel">
          <div class="panel-head">
            <div>
              <h2>模型调用参数</h2>
              <p>按照卓朗2算法接口保留 `dataLong`、`dataShort`、`params` 结构。</p>
            </div>
            <div class="panel-actions">
              <el-select v-model="selectedUnit" style="width: 140px" @change="applyTemplate">
                <el-option v-for="unit in densityUnits" :key="unit.value" :label="unit.label" :value="unit.value" />
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
              <h2>密控单元概览</h2>
              <p>展示 3207、3208、316 当前密控状态和调用模式。</p>
            </div>
            <el-button @click="loadOverview">刷新概览</el-button>
          </div>
          <el-table :data="overviewRows">
            <el-table-column prop="unit" label="单元" width="90" />
            <el-table-column prop="area" label="区域" min-width="140" />
            <el-table-column prop="status" label="状态" width="110" />
            <el-table-column prop="density" label="密度" width="110" />
            <el-table-column prop="diverter" label="分流阀" width="110" />
            <el-table-column prop="water" label="补水阀" width="110" />
            <el-table-column prop="mode" label="模式" width="110" />
          </el-table>
        </section>
      </section>

      <section class="section-panel">
        <div class="panel-head">
          <div>
            <h2>结果可视化</h2>
            <p>对比密度、分流和补水三个关键输出，用于现场联调时快速核对算法返回。</p>
          </div>
        </div>
        <div ref="chartEl" class="chart-box"></div>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import CoalQuickBar from '../../components/coal/CoalQuickBar.vue'
import { echarts, INDUSTRIAL_CHART_COLORS } from '../../utils/echarts'
import { parseJsonObject, parseNumberArray, toErrorMessage, type JsonRecord } from './smartModelPayload'
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

const setpointText = computed(() => {
  if (!setpoint.value) return '--'
  return `${setpoint.value.predMiddlingDensity} / ${setpoint.value.predCleanDensity}`
})

function applyTemplate() {
  const template = templates[selectedUnit.value]
  dataLongText.value = JSON.stringify(template.dataLong, null, 2)
  dataShortText.value = JSON.stringify(template.dataShort, null, 2)
  paramsText.value = JSON.stringify(template.params, null, 2)
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
      dataLong: parseNumberArray(dataLongText.value, '长周期数据'),
      dataShort: parseNumberArray(dataShortText.value, '短周期数据'),
      params: parseJsonObject(paramsText.value),
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
  } catch (error: unknown) {
    ElMessage.error(toErrorMessage(error, '智能密控调用失败'))
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
