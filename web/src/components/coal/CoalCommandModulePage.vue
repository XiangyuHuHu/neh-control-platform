<template>
  <div class="module-page command-page">
    <header class="hero-shell">
      <div>
        <p class="eyebrow">{{ config.badge }}</p>
        <h1>{{ config.title }}</h1>
        <p class="subtitle">{{ config.subtitle }}</p>
      </div>
      <div class="hero-actions">
        <button type="button" class="ghost-btn" @click="notify(`已生成${config.title}分析报告`)">导出报告</button>
        <button type="button" class="primary-btn" @click="notify(`已打开${config.title}执行面板`)">进入执行</button>
      </div>
    </header>

    <section class="metric-grid">
      <article
        v-for="item in config.metrics"
        :key="item.label"
        class="metric-card"
        :class="metricLevelClass(item)"
      >
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}<em v-if="item.unit">{{ item.unit }}</em></strong>
        <small>{{ item.note }}</small>
        <p v-if="item.trend" class="metric-trend">趋势 {{ metricTrendText(item.trend) }}</p>
        <p v-if="item.refreshRate || config.refreshRate" class="metric-refresh">刷新频率 {{ item.refreshRate || config.refreshRate }}s</p>
      </article>
    </section>

    <section class="main-grid">
      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>功能总览</h2>
            <p>{{ config.scenario }}</p>
          </div>
        </div>
        <div class="chip-list">
          <span v-for="item in config.highlights" :key="item" class="chip">{{ item }}</span>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>{{ config.chartTitle }}</h2>
            <p>按当前模块关键过程进行可视化展示</p>
          </div>
        </div>
        <div class="bar-list">
          <div v-for="item in config.chartSeries" :key="item.label" class="bar-row">
            <div class="bar-meta">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}%</strong>
            </div>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: `${item.value}%`, background: item.color }"></div>
            </div>
          </div>
        </div>
      </article>
    </section>

    <section class="panel table-panel">
      <div class="panel-head">
        <div>
          <h2>{{ config.tableTitle }}</h2>
          <p>当前使用演示数据占位，后续可直接切换正式数据源。</p>
        </div>
        <div class="table-actions">
          <button type="button" class="text-btn" @click="notify(`已刷新${config.tableTitle}`)">刷新</button>
          <button type="button" class="text-btn" @click="notify(`已派发${config.tableTitle}任务`)">派发</button>
        </div>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="col in config.columns" :key="col.key">{{ col.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in config.rows" :key="index">
            <td v-for="col in config.columns" :key="col.key">{{ row[col.key] }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import type { ModuleConfig, ModuleMetric } from '../../views/coal/moduleConfigs'

defineProps<{
  config: ModuleConfig
}>()

const notify = (message: string) => ElMessage.success(message)

const extractNumber = (value: string | number) => {
  if (typeof value === 'number') return value
  const matched = value.match(/-?\d+(\.\d+)?/)
  return matched ? Number(matched[0]) : Number.NaN
}

const metricTrendText = (trend: NonNullable<ModuleMetric['trend']>) => {
  if (trend === 'up') return '上升'
  if (trend === 'down') return '下降'
  return '持平'
}

const metricLevelClass = (metric: ModuleMetric) => {
  if (metric.status === 'danger') return 'metric-card--critical'
  if (metric.status === 'warning') return 'metric-card--warning'
  if (!metric.threshold) return ''
  const numeric = extractNumber(metric.value)
  if (Number.isNaN(numeric)) return ''
  const { warning, critical, direction = 'higher' } = metric.threshold
  if (direction === 'higher') {
    if (critical !== undefined && numeric >= critical) return 'metric-card--critical'
    if (warning !== undefined && numeric >= warning) return 'metric-card--warning'
    return ''
  }
  if (critical !== undefined && numeric <= critical) return 'metric-card--critical'
  if (warning !== undefined && numeric <= warning) return 'metric-card--warning'
  return ''
}
</script>

<style scoped>
.command-page {
  min-height: 100%;
  width: min(100%, 1680px);
  margin: 0 auto;
  --cc-gap: var(--control-gap, 16px);
  --cc-padding: var(--control-padding, 16px);
  --cc-radius: var(--control-radius, 16px);
  padding: 16px;
  background:
    radial-gradient(circle at top right, rgba(55, 174, 255, 0.16), transparent 22%),
    radial-gradient(circle at left top, rgba(26, 241, 180, 0.08), transparent 20%),
    #07111b;
  color: #ecf7ff;
}

.hero-shell,
.metric-card,
.panel {
  border: 1px solid rgba(106, 188, 255, 0.14);
  border-radius: calc(var(--cc-radius) + 8px);
  background: rgba(8, 19, 30, 0.9);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.24);
}

.hero-shell {
  display: flex;
  justify-content: space-between;
  gap: var(--cc-gap);
  align-items: center;
  padding: calc(var(--cc-padding) + 4px);
}

.eyebrow {
  margin: 0 0 10px;
  color: #7bc8ff;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.hero-shell h1,
.panel-head h2 {
  margin: 0;
}

.hero-shell h1 {
  font-size: 32px;
}

.subtitle,
.panel-head p {
  margin: 12px 0 0;
  color: rgba(227, 239, 250, 0.72);
  line-height: 1.8;
}

.hero-actions,
.table-actions {
  display: flex;
  gap: 12px;
}

.primary-btn,
.ghost-btn,
.text-btn {
  border: 0;
  cursor: pointer;
}

.primary-btn,
.ghost-btn {
  padding: 14px 20px;
  border-radius: 14px;
}

.primary-btn {
  background: linear-gradient(135deg, #2cd1ff, #21b7ff);
  color: #082338;
}

.ghost-btn {
  background: rgba(24, 37, 52, 0.94);
  color: #7fdaff;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--cc-gap);
  margin-top: var(--cc-gap);
}

.metric-card {
  padding: calc(var(--cc-padding) + 4px);
}

.metric-card span,
.bar-meta span {
  color: rgba(220, 235, 251, 0.62);
  font-size: 13px;
}

.metric-card strong {
  display: block;
  margin-top: 12px;
  font-size: 36px;
}

.metric-card strong em {
  margin-left: 6px;
  font-size: 16px;
  font-style: normal;
  color: rgba(227, 239, 250, 0.76);
}

.metric-card small {
  display: block;
  margin-top: 8px;
  color: #1ce7ba;
}

.metric-refresh {
  margin: 8px 0 0;
  font-size: 12px;
  color: rgba(163, 196, 225, 0.88);
}

.metric-trend {
  margin: 8px 0 0;
  font-size: 12px;
  color: rgba(154, 208, 255, 0.92);
}

.metric-card--warning {
  border-color: rgba(255, 181, 71, 0.5);
  box-shadow: 0 16px 36px rgba(255, 181, 71, 0.12);
}

.metric-card--warning small {
  color: #ffb547;
}

.metric-card--critical {
  border-color: rgba(255, 107, 107, 0.5);
  box-shadow: 0 16px 36px rgba(255, 107, 107, 0.12);
}

.metric-card--critical small {
  color: #ff8f8f;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--cc-gap);
  margin-top: var(--cc-gap);
}

.panel {
  padding: calc(var(--cc-padding) + 4px);
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: var(--cc-gap);
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.chip {
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(16, 35, 53, 0.9);
  color: #8fdfff;
  font-size: 13px;
}

.bar-list {
  display: grid;
  gap: 16px;
}

.bar-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.bar-track {
  height: 10px;
  border-radius: 999px;
  background: rgba(197, 214, 236, 0.12);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: inherit;
}

.table-panel {
  margin-top: var(--cc-gap);
}

.text-btn {
  padding: 0;
  background: transparent;
  color: #7fdaff;
  font-weight: 700;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 14px 12px;
  border-bottom: 1px solid rgba(116, 152, 188, 0.12);
  text-align: left;
}

.data-table th {
  color: #8fb7dc;
  font-weight: 600;
}

@media (max-width: 1000px) {
  .hero-shell,
  .metric-grid,
  .main-grid {
    grid-template-columns: 1fr;
    flex-direction: column;
  }
}
</style>
