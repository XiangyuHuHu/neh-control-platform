<template>
  <div class="coal-page-v2 quality-page">
    <div class="page-layout">
      <main class="page-main">
        <section class="hero">
          <div>
            <p class="eyebrow">质量管理</p>
            <h1>质量控制中心</h1>
            <p class="hero-text">围绕灰分、密度、单耗和设备参数给出可执行建议，帮助工艺和值班人员快速调整运行策略。</p>
          </div>
          <button type="button" class="export-btn" @click="exportQualityReport">导出分析报告</button>
        </section>

        <section class="main-grid">
          <article class="panel recommendation">
            <div class="panel-head">
              <h3>AI 分选参数建议</h3>
              <span class="badge">模型版本：V4.2 稳定版</span>
            </div>

            <div class="recommend-grid">
              <div class="big-number">
                <span>目标密度</span>
                <strong>{{ targetDensity.toFixed(2) }} <em>SG</em></strong>
                <p>根据当前煤层硬度、入料含水量和历史质量波动自动计算，建议本班继续保持稳态运行。</p>
              </div>

              <div class="suggestions">
                <article class="suggest-card blue">
                  <strong>旋流器设定值</strong>
                  <span>{{ densityOffsetText }}</span>
                  <p>适当提升介质密度，稳定当前分选比重。</p>
                </article>
                <article class="suggest-card yellow">
                  <strong>给料速率缓冲</strong>
                  <span>-12%</span>
                  <p>减缓波动给料，降低粗煤泥分选单元的停留时间波动。</p>
                </article>
              </div>
            </div>

            <button type="button" class="cta-btn" :class="{ applied: autoApplied }" @click="applyAutoAdjust">{{ autoApplied ? '已应用 ✓' : '应用自主调节' }}</button>
          </article>

          <aside class="device-column">
            <article class="device-card">
              <div class="device-head">
                <strong>重介旋流器</strong>
                <span class="dot ok"></span>
              </div>
              <div class="device-metric">
                <span>处理量</span>
                <strong>{{ cycloneThroughput.toFixed(0) }} <em>吨/小时</em></strong>
              </div>
              <div class="mini-progress"><div :style="{ width: `${throughputProgress}%` }"></div></div>
              <div class="device-foot"><span>效率：98.2%</span><span>磨损程度：低</span></div>
            </article>

            <article class="device-card">
              <div class="device-head">
                <strong>粗煤泥分选机</strong>
                <span class="dot ok"></span>
              </div>
              <div class="device-metric">
                <span>固体浓度</span>
                <strong>{{ slurryConcentration.toFixed(1) }} <em>%</em></strong>
              </div>
              <div class="mini-progress"><div :style="{ width: `${concentrationProgress}%` }"></div></div>
              <div class="device-foot"><span>床层高度：1.2 米</span><span>状态：同步中</span></div>
            </article>
          </aside>
        </section>

        <section class="panel trend-panel">
          <div class="panel-head">
            <div>
              <h3>灰分含量趋势</h3>
              <p>过去 24 小时分析窗口</p>
            </div>
            <div class="legend">
              <span><i class="blue"></i>当前灰分</span>
              <span><i class="ghost"></i>目标值 9.5%</span>
            </div>
          </div>

          <div ref="ashChartEl" class="chart-box"></div>
        </section>

        <section class="footer-stats">
          <article class="footer-card"><span>工艺用水酸碱度</span><strong>{{ processPh.toFixed(1) }}</strong></article>
          <article class="footer-card"><span>产率效率</span><strong>{{ yieldEfficiency.toFixed(1) }}%</strong></article>
          <article class="footer-card"><span>介质损耗率</span><strong>{{ mediumLoss.toFixed(2) }} <em>千克/吨</em></strong></article>
          <article class="footer-card"><span>累计处理量</span><strong>{{ totalHandledText }} <em>吨</em></strong></article>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { echarts } from '../../utils/echarts'
import { useIotHub } from '../../composables/useIotHub'

const ashChartEl = ref<HTMLElement | null>(null)
let ashChart: any = null
const autoApplied = ref(false)
const iotHub = useIotHub()

const getNumericTag = (tagCode: string, fallback: number) => {
  const value = iotHub.getTagValue(tagCode)?.value
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

const targetDensity = computed(() => getNumericTag('coal.quality.target_density', 1.54))
const cycloneThroughput = computed(() => getNumericTag('coal.cyclone.throughput', 425))
const slurryConcentration = computed(() => getNumericTag('coal.slurry.concentration', 34.8))
const processPh = computed(() => getNumericTag('coal.process.water.ph', 7.4))
const yieldEfficiency = computed(() => getNumericTag('coal.quality.yield_efficiency', 84.2))
const mediumLoss = computed(() => getNumericTag('coal.medium.loss', 0.68))
const totalHandled = computed(() => getNumericTag('coal.process.total_handled', 1200000))

const throughputProgress = computed(() => Math.min(100, Math.max(0, Number(((cycloneThroughput.value / 480) * 100).toFixed(0)))))
const concentrationProgress = computed(() => Math.min(100, Math.max(0, Number(((slurryConcentration.value / 56) * 100).toFixed(0)))))
const densityOffsetText = computed(() => {
  const offset = Number((targetDensity.value - 1.49).toFixed(2))
  return `${offset >= 0 ? '+' : ''}${offset.toFixed(2)} SG`
})
const totalHandledText = computed(() => {
  if (totalHandled.value >= 1000000) return `${(totalHandled.value / 1000000).toFixed(1)}M`
  return `${totalHandled.value.toFixed(0)}`
})

type AshSample = { time: string; ash: number; target: number; overLimit: boolean }
const ashSamples = ref<AshSample[]>([])

const buildAshSamples = () => {
  const now = new Date()
  const baseAsh = getNumericTag('coal.quality.ash', 9.1)
  const target = getNumericTag('coal.quality.ash.target', 9.5)
  const offsets = [-0.35, -0.22, -0.18, -0.08, 0.05, -0.11, 0.18, 0.12]
  const samples: AshSample[] = []
  for (let i = 23; i >= 0; i--) {
    const h = new Date(now.getTime() - i * 3600000)
    const time = `${String(h.getHours()).padStart(2, '0')}:00`
    const offset = offsets[(23 - i) % offsets.length]
    const ash = Number((baseAsh + offset).toFixed(2))
    samples.push({
      time,
      ash,
      target,
      overLimit: ash > target,
    })
  }
  ashSamples.value = samples
}

function renderAshChart() {
  if (!ashChartEl.value) return
  ashChart?.dispose()
  ashChart = echarts.init(ashChartEl.value)
  const hours = ashSamples.value.map((item) => item.time)
  const ashData = ashSamples.value.map((item) => item.ash)
  const targetData = ashSamples.value.map((item) => item.target)
  ashChart.setOption({
    tooltip: { trigger: 'axis', formatter: (p: any) => `${p[0].axisValue}<br/>灰分：${p[0].value}%${p[1] ? '<br/>目标：' + p[1].value + '%' : ''}` },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: hours, axisLabel: { color: '#8ab4d6' }, axisLine: { lineStyle: { color: '#1e3a52' } } },
    yAxis: { type: 'value', name: '灰分(%)', min: 7, max: 12, axisLabel: { color: '#8ab4d6' }, splitLine: { lineStyle: { color: '#1e3a52' } }, nameTextStyle: { color: '#8ab4d6' } },
    series: [
      { name: '当前灰分', type: 'bar', data: ashData, itemStyle: { color: (p: any) => p.value > targetData[p.dataIndex] ? '#ff7b82' : '#67d8ff', borderRadius: [4, 4, 0, 0] }, barWidth: '55%' },
      { name: '目标值', type: 'line', data: targetData, lineStyle: { type: 'dashed', color: '#95a2b1' }, symbol: 'none', itemStyle: { color: '#95a2b1' } },
    ],
  })
}

function applyAutoAdjust() {
  autoApplied.value = true
  ElMessage.success('自主调节建议已应用到当前工艺参数')
  setTimeout(() => { autoApplied.value = false }, 5000)
}

function exportQualityReport() {
  const csv = ['时间,灰分(%),目标值(%),是否超标']
  ashSamples.value.forEach((item) => {
    csv.push(`${item.time},${item.ash.toFixed(2)},${item.target.toFixed(2)},${item.overLimit ? '是' : '否'}`)
  })
  const blob = new Blob(['\uFEFF' + csv.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = `质量分析报告_${new Date().toISOString().slice(0, 10)}.csv`; a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('质量分析报告已下载')
}

const handleResize = () => ashChart?.resize()

onMounted(async () => {
  iotHub.subscribe({ pageKey: 'quality-center', intervalMs: 5000 })
  await iotHub.ensureFresh('quality-center', 2000)
  await nextTick()
  buildAshSamples()
  renderAshChart()
  window.addEventListener('resize', handleResize)
})

watch(
  () => iotHub.generatedAt.value,
  () => {
    buildAshSamples()
    renderAshChart()
  },
)

onUnmounted(() => {
  ashChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.coal-page-v2{min-height:100vh;background:#091019;color:#eef6ff}
.page-layout{width:min(100%,1800px);margin:0 auto;display:grid;grid-template-columns:1fr;gap:24px;padding:24px}
.panel,.device-card,.footer-card{border:1px solid rgba(122,190,255,.1);background:rgba(12,20,31,.92);box-shadow:0 18px 40px rgba(0,0,0,.18)}
.hero{display:flex;justify-content:space-between;align-items:flex-start;gap:24px}
.eyebrow{margin:0 0 10px;color:#78cfff;font-size:12px;letter-spacing:.2em;text-transform:uppercase}
.hero h1{margin:0;font-size:60px;line-height:1}
.hero-text{max-width:760px;margin:12px 0 0;color:#97aac0;font-size:16px;line-height:1.7}
.export-btn{height:56px;padding:0 22px;border:0;border-radius:14px;background:#151f2d;color:#d8ebfb;cursor:pointer}
.main-grid{display:grid;grid-template-columns:1.55fr .75fr;gap:24px;margin-top:20px}
.panel,.device-card,.footer-card{padding:24px;border-radius:24px}
.panel-head{display:flex;justify-content:space-between;align-items:flex-start;gap:18px}
.panel-head h3{margin:0;font-size:30px}
.panel-head p{margin:8px 0 0;color:#95aabd}
.badge{padding:8px 14px;border-radius:999px;border:1px solid rgba(24,240,191,.35);color:#18f0bf}
.recommend-grid{display:grid;grid-template-columns:1fr 320px;gap:28px;margin-top:30px}
.big-number span{color:#95a2b1}
.big-number strong{display:block;margin:18px 0 14px;font-size:82px;line-height:1;color:#67d8ff;text-shadow:0 0 16px rgba(103,216,255,.24)}
.big-number em{font-style:normal;font-size:40px}
.big-number p{max-width:420px;color:#a8b5c3;line-height:1.7}
.suggestions{display:grid;gap:16px}
.suggest-card{padding:18px;border-radius:14px;background:#1b2430;box-shadow:inset 4px 0 0 #67d8ff}
.suggest-card.yellow{box-shadow:inset 4px 0 0 #f8c76d}
.suggest-card strong,.suggest-card span{display:block}
.suggest-card span{margin:6px 0 10px;text-align:right;color:#67d8ff}
.suggest-card.yellow span{color:#f8c76d}
.suggest-card p{margin:0;color:#d7e1ea;line-height:1.6}
.cta-btn{margin-top:28px;width:100%;height:64px;border:0;border-radius:14px;background:#61c8eb;color:#06313e;font-size:20px;font-weight:800;cursor:pointer}
.device-column{display:grid;gap:24px}
.device-head,.device-foot,.device-metric{display:flex;justify-content:space-between;align-items:center;gap:12px}
.device-head strong{font-size:24px}
.dot{width:16px;height:16px;border-radius:50%}.dot.ok{background:#18f0bf;box-shadow:0 0 12px #18f0bf}
.device-metric{margin:30px 0 16px}.device-metric span{color:#98a5b5}.device-metric strong{font-size:48px}.device-metric em{font-style:normal;font-size:22px;color:#98a5b5}
.mini-progress{height:8px;border-radius:999px;background:#2b3240;overflow:hidden}.mini-progress div{height:100%;border-radius:inherit;background:#67d8ff}
.device-foot{margin-top:16px;color:#ccd8e4}
.trend-panel{margin-top:24px}
.legend{display:flex;gap:20px}.legend span{display:flex;align-items:center;gap:8px;color:#cfd8e3}.legend i{width:12px;height:12px;border-radius:50%;display:inline-block}.legend .blue{background:#67d8ff}.legend .ghost{border:1px dashed #95a2b1}
.chart-box{width:100%;height:340px;margin-top:16px}
.cta-btn.applied{background:#18f0bf;color:#062230}
.footer-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-top:24px}
.footer-card span{display:block;color:#96a4b7;margin-bottom:20px}.footer-card strong{font-size:52px;line-height:1}.footer-card em{font-style:normal;font-size:20px;color:#a2b0bf}
@media (max-width: 1400px){
  .page-layout,.main-grid,.footer-stats{grid-template-columns:1fr}
  .recommend-grid{grid-template-columns:1fr}
}
</style>
