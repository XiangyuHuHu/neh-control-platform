<template>
  <div class="energy-screen">
    <section class="screen-header">
      <div class="header-left">
        <span>{{ weather.city }}</span>
        <span>{{ weather.time }}</span>
        <strong>{{ weather.temp }}</strong>
        <span>{{ weather.text }}</span>
      </div>
      <div class="header-title">
        <h1>消耗大屏</h1>
      </div>
      <div class="header-right">
        <button type="button" @click="openDialog('electricity')">电耗查询</button>
        <button type="button" @click="openDialog('water')">历史水耗</button>
        <button type="button" @click="openDialog('medium')">介耗查询</button>
      </div>
    </section>

    <section class="summary-strip">
      <article class="summary-card">
        <span>年介耗</span>
        <strong>0.58 <small>kg/t</small></strong>
      </article>
      <article class="summary-card">
        <span>年药耗</span>
        <strong>28.33 <small>kg/t</small></strong>
      </article>
      <article class="summary-card">
        <span>年电耗</span>
        <strong>2.73 <small>kWh/t</small></strong>
      </article>
    </section>

    <section class="screen-grid">
      <article class="panel">
        <div class="panel-title">实时风耗</div>
        <div ref="airGaugeRef" class="chart gauge-chart"></div>
      </article>

      <article class="panel panel--center">
        <div class="center-orbit">
          <div class="orbit-line orbit-line--1"></div>
          <div class="orbit-line orbit-line--2"></div>
          <div class="planet planet--1">
            <strong>0.58</strong>
            <span>月介耗 kg/t</span>
          </div>
          <div class="planet planet--2">
            <strong>2.73</strong>
            <span>月耗电 kWh/t</span>
          </div>
          <div class="planet planet--3">
            <strong>0.40</strong>
            <span>低风流量 m³/t</span>
          </div>
          <div class="planet planet--4">
            <strong>0.04</strong>
            <span>高风流量 m³/t</span>
          </div>
          <div class="planet planet--5">
            <strong>0.00</strong>
            <span>3251补水 m³/t</span>
          </div>
          <div class="planet planet--6">
            <strong>0.00</strong>
            <span>后勤补水 m³/t</span>
          </div>
          <div class="planet planet--7">
            <strong>28.33</strong>
            <span>月药耗 kg/t</span>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-title">实时水耗</div>
        <div ref="waterGaugeRef" class="chart gauge-chart"></div>
      </article>

      <article class="panel">
        <div class="panel-title panel-title--action">
          <span>介耗</span>
          <button type="button" class="link-btn" @click="openDialog('medium')">查看明细</button>
        </div>
        <div ref="mediumTrendRef" class="chart line-chart"></div>
      </article>

      <article class="panel">
        <div class="panel-title panel-title--action">
          <span>耗电量</span>
          <button type="button" class="link-btn" @click="openDialog('electricity')">查询电耗</button>
        </div>
        <div ref="electricityBarRef" class="chart bar-chart"></div>
      </article>

      <article class="panel">
        <div class="panel-title panel-title--action">
          <span>药耗</span>
          <button type="button" class="link-btn" @click="openDialog('water')">水耗联查</button>
        </div>
        <div ref="medicineTrendRef" class="chart line-chart"></div>
      </article>
    </section>

    <el-dialog v-model="dialogVisible.electricity" title="电耗查询" width="88%" class="blue-dialog">
      <div class="query-dialog">
        <div class="query-toolbar">
          <div class="query-filters">
            <el-select v-model="electricityQuery.granularity" size="large" style="width: 110px">
              <el-option label="按天" value="day" />
              <el-option label="按月" value="month" />
            </el-select>
            <el-date-picker v-model="electricityQuery.start" type="date" size="large" value-format="YYYY-MM-DD" />
            <el-date-picker v-model="electricityQuery.end" type="date" size="large" value-format="YYYY-MM-DD" />
            <el-button type="primary" size="large">查询</el-button>
          </div>
          <div class="display-switch">
            <button type="button" :class="{ active: electricityView === 'chart' }" @click="electricityView = 'chart'">图表展示</button>
            <button type="button" :class="{ active: electricityView === 'table' }" @click="electricityView = 'table'">列表展示</button>
          </div>
        </div>

        <div v-show="electricityView === 'chart'" ref="electricityDialogChartRef" class="dialog-chart"></div>

        <el-table v-show="electricityView === 'table'" :data="electricityRows" class="dialog-table">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="usage" label="用电量(kWh)" width="160" />
          <el-table-column prop="unitConsumption" label="电耗(kWh/t)" width="160" />
          <el-table-column prop="shift" label="班次" width="120" />
          <el-table-column prop="remark" label="说明" min-width="240" />
        </el-table>
      </div>
    </el-dialog>

    <el-dialog v-model="dialogVisible.water" title="历史水耗" width="88%" class="blue-dialog">
      <div class="query-dialog">
        <div class="query-toolbar">
          <div class="query-filters">
            <el-date-picker
              v-model="waterQuery.range"
              type="daterange"
              size="large"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
            <el-select v-model="waterQuery.type" size="large" style="width: 140px">
              <el-option label="全部" value="all" />
              <el-option label="后勤补水" value="后勤补水" />
              <el-option label="3251补水" value="3251补水" />
            </el-select>
          </div>
          <div class="display-switch">
            <button type="button" :class="{ active: waterView === 'chart' }" @click="waterView = 'chart'">图表展示</button>
            <button type="button" :class="{ active: waterView === 'table' }" @click="waterView = 'table'">列表展示</button>
          </div>
        </div>

        <div v-show="waterView === 'chart'" ref="waterDialogChartRef" class="dialog-chart"></div>

        <el-table v-show="waterView === 'table'" :data="waterRows" class="dialog-table">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="office" label="后勤补水(m³)" width="180" />
          <el-table-column prop="workshop" label="3251补水(m³)" width="180" />
          <el-table-column prop="remark" label="说明" min-width="260" />
        </el-table>
      </div>
    </el-dialog>

    <el-dialog v-model="dialogVisible.medium" title="介耗查询" width="88%" class="blue-dialog">
      <div class="query-dialog">
        <div class="query-toolbar">
          <div class="query-filters">
            <el-select v-model="mediumQuery.granularity" size="large" style="width: 110px">
              <el-option label="按天" value="day" />
              <el-option label="按月" value="month" />
            </el-select>
            <el-date-picker v-model="mediumQuery.start" type="date" size="large" value-format="YYYY-MM-DD" />
            <el-date-picker v-model="mediumQuery.end" type="date" size="large" value-format="YYYY-MM-DD" />
            <el-select v-model="mediumQuery.category" size="large" style="width: 120px">
              <el-option label="全部" value="all" />
              <el-option label="重介" value="heavy" />
              <el-option label="磁选" value="magnetic" />
            </el-select>
            <el-button type="primary" size="large">查询</el-button>
          </div>
          <div class="display-switch">
            <button type="button" :class="{ active: mediumView === 'chart' }" @click="mediumView = 'chart'">图表展示</button>
            <button type="button" :class="{ active: mediumView === 'table' }" @click="mediumView = 'table'">列表展示</button>
          </div>
        </div>

        <div v-show="mediumView === 'chart'" ref="mediumDialogChartRef" class="dialog-chart"></div>

        <el-table v-show="mediumView === 'table'" :data="mediumRows" class="dialog-table">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="value" label="介耗(kg/t)" width="140" />
          <el-table-column prop="category" label="类别" width="120" />
          <el-table-column prop="operator" label="记录人" width="120" />
          <el-table-column prop="remark" label="说明" min-width="260" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { echarts } from '../../utils/echarts'

const weather = {
  city: '鄂尔多斯市',
  time: '2025-01-13 11:28',
  temp: '-7°',
  text: '晴',
}

const dialogVisible = reactive({
  electricity: false,
  water: false,
  medium: false,
})

const electricityView = ref<'chart' | 'table'>('chart')
const waterView = ref<'chart' | 'table'>('chart')
const mediumView = ref<'chart' | 'table'>('chart')

const electricityQuery = reactive({
  granularity: 'day',
  start: '2025-01-03',
  end: '2025-01-13',
})

const waterQuery = reactive({
  range: ['2024-12-29', '2025-01-13'],
  type: 'all',
})

const mediumQuery = reactive({
  granularity: 'day',
  start: '2025-01-03',
  end: '2025-01-13',
  category: 'all',
})

const electricityRows = [
  { date: '01-03', usage: 81493.16, unitConsumption: 3.0, shift: '早班', remark: '入洗负荷偏低' },
  { date: '01-05', usage: 82850.24, unitConsumption: 3.08, shift: '中班', remark: '系统运行稳定' },
  { date: '01-06', usage: 83627.52, unitConsumption: 3.12, shift: '夜班', remark: '主洗系统提升' },
  { date: '01-07', usage: 86124.52, unitConsumption: 3.18, shift: '早班', remark: '分选密度调整后稳定' },
  { date: '01-08', usage: 85758.68, unitConsumption: 3.22, shift: '中班', remark: '矸石带负荷提高' },
  { date: '01-09', usage: 76725.08, unitConsumption: 3.5, shift: '夜班', remark: '压滤系统检修' },
  { date: '01-10', usage: 86022.84, unitConsumption: 3.28, shift: '早班', remark: '恢复正常' },
  { date: '01-11', usage: 90301.0, unitConsumption: 3.32, shift: '中班', remark: '高负荷满产' },
  { date: '01-12', usage: 75410.44, unitConsumption: 3.26, shift: '夜班', remark: '计划降负荷' },
]

const waterRows = [
  { date: '2025-01-13', office: 0.02, workshop: 0.06, remark: '补水正常' },
  { date: '2025-01-12', office: 0.03, workshop: 0.07, remark: '后勤区补水增加' },
  { date: '2025-01-11', office: 0.02, workshop: 0.06, remark: '主系统冲洗' },
  { date: '2025-01-10', office: 0.04, workshop: 0.08, remark: '洗选高负荷运行' },
  { date: '2025-01-09', office: 0.03, workshop: 0.07, remark: '系统补水调整' },
  { date: '2025-01-08', office: 0.02, workshop: 0.05, remark: '低位水池补水' },
  { date: '2025-01-07', office: 0.05, workshop: 0.06, remark: '冲洗作业' },
  { date: '2025-01-05', office: 0.04, workshop: 0.06, remark: '系统调水' },
  { date: '2025-01-03', office: 0.03, workshop: 0.06, remark: '全厂高负荷' },
  { date: '2025-01-01', office: 0.01, workshop: 0.02, remark: '节假日低负荷' },
]

const mediumRows = [
  { date: '01-04', value: 0.38, category: '重介', operator: '张伟', remark: '介耗稳定' },
  { date: '01-05', value: 0.39, category: '重介', operator: '李超', remark: '系统运行稳定' },
  { date: '01-06', value: 0.4, category: '磁选', operator: '王敏', remark: '介质密度正常' },
  { date: '01-07', value: 0.41, category: '重介', operator: '周洋', remark: '运行效率平稳' },
  { date: '01-08', value: 0.4, category: '重介', operator: '赵凯', remark: '原煤波动' },
  { date: '01-09', value: 0.39, category: '磁选', operator: '孙博', remark: '补介及时' },
  { date: '01-10', value: 0.4, category: '重介', operator: '刘勇', remark: '运行平稳' },
  { date: '01-11', value: 0.36, category: '磁选', operator: '陈峰', remark: '清洗后下降' },
  { date: '01-12', value: 0.42, category: '重介', operator: '高磊', remark: '块煤系统波动' },
  { date: '01-13', value: 0.4, category: '重介', operator: '马强', remark: '维持当前水平' },
]

const airGaugeRef = ref<HTMLElement | null>(null)
const waterGaugeRef = ref<HTMLElement | null>(null)
const mediumTrendRef = ref<HTMLElement | null>(null)
const electricityBarRef = ref<HTMLElement | null>(null)
const medicineTrendRef = ref<HTMLElement | null>(null)
const electricityDialogChartRef = ref<HTMLElement | null>(null)
const waterDialogChartRef = ref<HTMLElement | null>(null)
const mediumDialogChartRef = ref<HTMLElement | null>(null)

let airGaugeChart: any = null
let waterGaugeChart: any = null
let mediumTrendChart: any = null
let electricityBarChart: any = null
let medicineTrendChart: any = null
let electricityDialogChart: any = null
let waterDialogChart: any = null
let mediumDialogChart: any = null

const openDialog = async (type: 'electricity' | 'water' | 'medium') => {
  dialogVisible[type] = true
  await nextTick()
  renderDialogCharts()
}

const syncScreenCopy = () => {
  const setHtml = (selector: string, html: string) => {
    const el = document.querySelector(selector)
    if (el) el.innerHTML = html
  }

  const setText = (selector: string, text: string) => {
    const el = document.querySelector(selector)
    if (el) el.textContent = text
  }

  setText('.energy-screen .header-title h1', '消耗大屏')
  setText('.energy-screen .summary-card:nth-child(1) span', '介耗')
  setHtml('.energy-screen .summary-card:nth-child(1) strong', '0.4 <small>kg/t</small>')
  setText('.energy-screen .summary-card:nth-child(2) span', '药耗')
  setHtml('.energy-screen .summary-card:nth-child(2) strong', '26.3 <small>g/t</small>')
  setText('.energy-screen .summary-card:nth-child(3) span', '电耗')
  setHtml('.energy-screen .summary-card:nth-child(3) strong', '3.2 <small>kWh/t</small>')
  setText('.energy-screen .screen-grid > .panel:nth-child(1) .panel-title', '风流量')
  setText('.energy-screen .planet--1 strong', '0.4')
  setText('.energy-screen .planet--1 span', '介耗 kg/t')
  setText('.energy-screen .planet--2 strong', '2.6000')
  setText('.energy-screen .planet--2 span', '耗电量 3.0-3.5')
  setText('.energy-screen .planet--3 strong', '0.5')
  setText('.energy-screen .planet--3 span', '风流量 m³/t')
  setText('.energy-screen .planet--5 strong', '0.06')
  setText('.energy-screen .planet--5 span', '水耗 m³/t')
  setText('.energy-screen .planet--7 strong', '26.3')
  setText('.energy-screen .planet--7 span', '药耗 g/t')
  setText('.energy-screen .screen-grid > .panel:nth-child(3) .panel-title', '水耗')
  setText('.energy-screen .screen-grid > .panel:nth-child(4) .panel-title span', '介耗')
  setText('.energy-screen .screen-grid > .panel:nth-child(5) .panel-title span', '耗电量')
  setText('.energy-screen .screen-grid > .panel:nth-child(6) .panel-title span', '药耗')
  setText('.energy-screen .screen-grid > .panel:nth-child(6) .link-btn', '查询药耗')

  const planet4 = document.querySelector('.energy-screen .planet--4') as HTMLElement | null
  if (planet4) planet4.style.display = 'none'
  const planet6 = document.querySelector('.energy-screen .planet--6') as HTMLElement | null
  if (planet6) planet6.style.display = 'none'
}

const renderCharts = () => {
  if (airGaugeRef.value) {
    airGaugeChart ??= echarts.init(airGaugeRef.value)
    airGaugeChart.setOption({
      series: [
        {
          type: 'pie',
          radius: ['56%', '78%'],
          center: ['50%', '48%'],
          data: [
            { value: 0.5, name: '风流量', itemStyle: { color: '#6d84db' } },
          ],
          label: {
            color: '#eaf6ff',
            formatter: ({ name, value }: { name: string; value: number }) => `${name}\n${value.toFixed(2)}m³/t`,
            fontSize: 16,
          },
        },
      ],
    })
  }

  if (waterGaugeRef.value) {
    waterGaugeChart ??= echarts.init(waterGaugeRef.value)
    waterGaugeChart.setOption({
      series: [
        {
          type: 'pie',
          radius: ['56%', '78%'],
          center: ['50%', '48%'],
          data: [
            { value: 0.06, name: '水耗', itemStyle: { color: '#16dfff' } },
          ],
          label: {
            color: '#eaf6ff',
            formatter: ({ name, value }: { name: string; value: number }) => `${name}\n${value.toFixed(2)}m³/t`,
            fontSize: 16,
          },
        },
      ],
    })
  }

  if (mediumTrendRef.value) {
    mediumTrendChart ??= echarts.init(mediumTrendRef.value)
    mediumTrendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 24, left: 48, right: 20, bottom: 32 },
      xAxis: {
        type: 'category',
        data: mediumRows.map((item) => item.date),
        axisLabel: { color: '#dbe7ff' },
        axisLine: { lineStyle: { color: '#37516d' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#dbe7ff' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series: [
        {
          type: 'line',
          smooth: true,
          data: mediumRows.map((item) => item.value),
          itemStyle: { color: '#31b4ff' },
          lineStyle: { width: 3, color: '#31b4ff' },
          label: { show: true, color: '#ffe164' },
        },
      ],
    })
  }

  if (electricityBarRef.value) {
    electricityBarChart ??= echarts.init(electricityBarRef.value)
    electricityBarChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 24, left: 56, right: 20, bottom: 32 },
      xAxis: {
        type: 'category',
        data: electricityRows.map((item) => item.date),
        axisLabel: { color: '#dbe7ff' },
        axisLine: { lineStyle: { color: '#37516d' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#dbe7ff' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series: [
        {
          type: 'bar',
          barWidth: 38,
          data: electricityRows.map((item) => item.usage),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#8fcfff' },
              { offset: 1, color: '#198cf3' },
            ]),
            borderRadius: [8, 8, 0, 0],
          },
          label: {
            show: true,
            position: 'top',
            color: '#ffe164',
            formatter: ({ value }: { value: number }) => `${value.toFixed(2)}`,
          },
        },
      ],
    })
  }

  if (medicineTrendRef.value) {
    medicineTrendChart ??= echarts.init(medicineTrendRef.value)
    medicineTrendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 24, left: 48, right: 20, bottom: 32 },
      xAxis: {
        type: 'category',
        data: ['01-04', '01-05', '01-06', '01-07', '01-08', '01-09', '01-10', '01-11', '01-12', '01-13'],
        axisLabel: { color: '#dbe7ff' },
        axisLine: { lineStyle: { color: '#37516d' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#dbe7ff' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series: [
        {
          type: 'line',
          smooth: true,
          data: [27.49, 27.29, 27.42, 27.9, 27.6, 28.21, 26.15, 24.71, 25.76, 18.25],
          itemStyle: { color: '#3aa4ff' },
          lineStyle: { width: 3, color: '#3aa4ff' },
          label: { show: true, color: '#ffe164' },
        },
      ],
    })
  }
}

const renderDialogCharts = () => {
  if (electricityDialogChartRef.value) {
    electricityDialogChart ??= echarts.init(electricityDialogChartRef.value)
    electricityDialogChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#dbe7ff' } },
      grid: { top: 40, left: 56, right: 24, bottom: 40 },
      xAxis: {
        type: 'category',
        data: electricityRows.map((item) => item.date),
        axisLabel: { color: '#dbe7ff' },
        axisLine: { lineStyle: { color: '#37516d' } },
      },
      yAxis: [
        {
          type: 'value',
          axisLabel: { color: '#dbe7ff' },
          splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
        },
        {
          type: 'value',
          axisLabel: { color: '#dbe7ff' },
          splitLine: { show: false },
        },
      ],
      series: [
        {
          name: '用电量',
          type: 'bar',
          barWidth: 42,
          data: electricityRows.map((item) => item.usage),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#9ed6ff' },
              { offset: 1, color: '#2c90e8' },
            ]),
            borderRadius: [8, 8, 0, 0],
          },
          label: {
            show: true,
            position: 'top',
            color: '#ffe164',
            formatter: ({ value }: { value: number }) => `${value.toFixed(2)} kWh`,
          },
        },
        {
          name: '电耗',
          type: 'line',
          yAxisIndex: 1,
          smooth: true,
          data: electricityRows.map((item) => item.unitConsumption),
          itemStyle: { color: '#ffffff' },
          lineStyle: { width: 2, color: '#ffffff' },
        },
      ],
    })
  }

  if (waterDialogChartRef.value) {
    waterDialogChart ??= echarts.init(waterDialogChartRef.value)
    waterDialogChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { textStyle: { color: '#dbe7ff' } },
      grid: { top: 40, left: 56, right: 24, bottom: 40 },
      xAxis: {
        type: 'category',
        data: waterRows.map((item) => item.date),
        axisLabel: { color: '#dbe7ff' },
        axisLine: { lineStyle: { color: '#37516d' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#dbe7ff' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series: [
        {
          name: '后勤补水',
          type: 'line',
          smooth: true,
          data: waterRows.map((item) => item.office),
          itemStyle: { color: '#31a0ff' },
          lineStyle: { width: 3, color: '#31a0ff' },
          label: { show: true, color: '#ffe164' },
        },
        {
          name: '3251补水',
          type: 'line',
          smooth: true,
          data: waterRows.map((item) => item.workshop),
          itemStyle: { color: '#35ff8f' },
          lineStyle: { width: 3, color: '#35ff8f' },
          label: { show: true, color: '#ffe164' },
        },
      ],
    })
  }

  if (mediumDialogChartRef.value) {
    mediumDialogChart ??= echarts.init(mediumDialogChartRef.value)
    mediumDialogChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 40, left: 56, right: 24, bottom: 40 },
      xAxis: {
        type: 'category',
        data: mediumRows.map((item) => item.date),
        axisLabel: { color: '#dbe7ff' },
        axisLine: { lineStyle: { color: '#37516d' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#dbe7ff' },
        splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      },
      series: [
        {
          type: 'line',
          smooth: true,
          data: mediumRows.map((item) => item.value),
          itemStyle: { color: '#31b4ff' },
          lineStyle: { width: 3, color: '#31b4ff' },
          label: { show: true, color: '#ffe164' },
        },
      ],
    })
  }
}

watch(
  () => [dialogVisible.electricity, dialogVisible.water, dialogVisible.medium],
  async () => {
    await nextTick()
    renderDialogCharts()
  },
)

onMounted(async () => {
  await nextTick()
  syncScreenCopy()
  renderCharts()
  window.addEventListener('resize', renderCharts)
  window.addEventListener('resize', renderDialogCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderCharts)
  window.removeEventListener('resize', renderDialogCharts)
  airGaugeChart?.dispose()
  waterGaugeChart?.dispose()
  mediumTrendChart?.dispose()
  electricityBarChart?.dispose()
  medicineTrendChart?.dispose()
  electricityDialogChart?.dispose()
  waterDialogChart?.dispose()
  mediumDialogChart?.dispose()
})
</script>

<style scoped>
.energy-screen {
  min-height: 100vh;
  padding: 24px 0 32px;
  background:
    radial-gradient(circle at center, rgba(38, 166, 255, 0.12), transparent 28%),
    #040914;
  color: #eaf6ff;
}

.screen-header,
.summary-strip,
.screen-grid {
  width: min(100%, 1920px);
  margin: 0 auto;
}

.screen-header {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  align-items: center;
  margin-bottom: 18px;
}

.header-left,
.header-right {
  display: flex;
  gap: 14px;
  align-items: center;
  color: rgba(234, 246, 255, 0.88);
}

.header-right {
  justify-content: flex-end;
}

.header-right button,
.center-actions button,
.display-switch button,
.link-btn {
  border: 1px solid rgba(74, 215, 255, 0.36);
  background: rgba(8, 28, 50, 0.88);
  color: #8fe9ff;
  cursor: pointer;
}

.header-right button {
  height: 42px;
  padding: 0 18px;
}

.header-title {
  text-align: center;
}

.header-title h1 {
  margin: 0;
  font-size: 54px;
  color: #14dfff;
  text-shadow: 0 0 24px rgba(20, 223, 255, 0.35);
}

.summary-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}

.summary-card {
  padding: 24px 28px;
  border: 1px solid rgba(40, 184, 255, 0.58);
  background: linear-gradient(180deg, rgba(8, 18, 41, 0.94), rgba(3, 8, 20, 0.92));
  text-align: center;
}

.summary-card span {
  display: block;
  color: #14dfff;
  font-size: 18px;
}

.summary-card strong {
  display: block;
  margin-top: 16px;
  font-size: 58px;
  color: #ffd15d;
}

.summary-card small {
  font-size: 28px;
  color: #29e0ff;
}

.screen-grid {
  display: grid;
  grid-template-columns: 0.72fr 1.44fr 0.72fr;
  grid-template-rows: 370px 340px;
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

.panel-title--action {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.link-btn {
  height: 34px;
  padding: 0 12px;
}

.chart {
  width: 100%;
}

.gauge-chart {
  height: calc(100% - 48px);
}

.line-chart,
.bar-chart {
  height: 270px;
}

.panel--center {
  position: relative;
  padding: 26px;
  overflow: hidden;
}

.center-orbit {
  position: relative;
  width: 100%;
  height: 100%;
}

.orbit-line {
  position: absolute;
  inset: 60px 100px;
  border: 1px solid rgba(47, 223, 255, 0.18);
  border-radius: 50%;
}

.orbit-line--2 {
  inset: 92px 180px;
}

.planet {
  position: absolute;
  width: 148px;
  height: 148px;
  border-radius: 50%;
  display: grid;
  place-content: center;
  text-align: center;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.26), rgba(21, 89, 165, 0.82));
  box-shadow: 0 0 26px rgba(58, 240, 255, 0.22);
}

.planet strong {
  font-size: 34px;
}

.planet span {
  margin-top: 8px;
  color: #d8faff;
  line-height: 1.4;
}

.planet--1 { left: 6%; top: 2%; }
.planet--2 { left: 30%; top: 12%; }
.planet--3 { right: 18%; top: 2%; }
.planet--4 { right: 4%; top: 28%; }
.planet--5 { left: 45%; top: 44%; }
.planet--6 { left: 22%; top: 54%; }
.planet--7 { left: 2%; top: 38%; }

.blue-dialog :deep(.el-dialog) {
  background: rgba(6, 20, 52, 0.96);
  border: 3px solid rgba(60, 243, 255, 0.8);
  box-shadow: 0 0 30px rgba(60, 243, 255, 0.18);
}

.blue-dialog :deep(.el-dialog__title),
.blue-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #fff;
}

.query-dialog {
  min-height: 620px;
}

.query-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 18px;
}

.query-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.display-switch {
  display: flex;
}

.display-switch button {
  width: 110px;
  height: 44px;
}

.display-switch button.active {
  background: rgba(32, 120, 196, 0.92);
  color: #fff;
}

.dialog-chart {
  height: 620px;
}

.dialog-table :deep(.el-table),
.dialog-table :deep(.el-table__inner-wrapper),
.dialog-table :deep(.el-table tr),
.dialog-table :deep(.el-table th.el-table__cell),
.dialog-table :deep(.el-table td.el-table__cell) {
  background: transparent;
  color: #eef6ff;
}

.dialog-table :deep(.el-table__header th.el-table__cell) {
  color: #7ecfff;
}

@media (max-width: 1600px) {
  .screen-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }

  .summary-strip {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .screen-header,
  .query-toolbar {
    grid-template-columns: 1fr;
    display: grid;
  }

  .header-right,
  .header-left {
    flex-wrap: wrap;
  }
}
</style>
