<template>
  <div class="data-page">
    <CoalQuickBar
      title="数据接入状态中心"
      subtitle="统一查看 IOT 数据源、点位台账、业务映射和实时质量，快速判断现场接入是否仍处于演示回退。"
    />

    <section class="status-band">
      <article class="provider-panel">
        <div>
          <span class="eyebrow">当前数据源</span>
          <h1>{{ providerName }}</h1>
          <p>{{ providerDescription }}</p>
        </div>
        <button class="refresh-btn" type="button" :disabled="loading" @click="loadStatus">
          {{ loading ? '刷新中' : '刷新' }}
        </button>
      </article>

      <article v-for="item in stats" :key="item.label" class="stat-card">
        <strong>{{ item.value }}</strong>
        <span>{{ item.label }}</span>
      </article>
    </section>

    <section class="grid-two">
      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>接入健康度</h2>
            <p>按点位启用状态、实时值时间和质量码计算，帮助现场先定位数据问题。</p>
          </div>
          <span :class="['status-pill', overallLevel]">{{ overallText }}</span>
        </div>
        <div class="health-list">
          <div v-for="item in healthItems" :key="item.label" class="health-row">
            <div>
              <strong>{{ item.label }}</strong>
              <span>{{ item.desc }}</span>
            </div>
            <em>{{ item.value }}</em>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>KEPServer 配置</h2>
            <p>展示当前后端首选采集源和回退策略，便于部署前核对。</p>
          </div>
        </div>
        <dl class="config-list">
          <div>
            <dt>首选 Provider</dt>
            <dd>{{ providerStatus?.configuredProvider || '-' }}</dd>
          </div>
          <div>
            <dt>实际 Provider</dt>
            <dd>{{ providerStatus?.actualProvider || '-' }}</dd>
          </div>
          <div>
            <dt>首选源可用</dt>
            <dd>{{ providerStatus?.preferredProviderAvailable ? '可用' : '不可用' }}</dd>
          </div>
          <div>
            <dt>允许演示回退</dt>
            <dd>{{ providerStatus?.fallbackToMock ? '允许' : '禁止' }}</dd>
          </div>
          <div>
            <dt>OPC UA 地址</dt>
            <dd>{{ providerStatus?.kepserver?.endpoint || '-' }}</dd>
          </div>
          <div>
            <dt>通道前缀</dt>
            <dd>{{ providerStatus?.kepserver?.channelPrefix || '-' }}</dd>
          </div>
        </dl>
      </article>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <h2>点位运行明细</h2>
          <p>优先展示启用点位，包含来源、设备、质量、最后更新时间和业务映射数。</p>
        </div>
        <input v-model="keyword" class="filter-input" placeholder="搜索点位 / 设备 / 业务" />
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>点位编码</th>
              <th>点位名称</th>
              <th>来源</th>
              <th>设备</th>
              <th>实时值</th>
              <th>质量</th>
              <th>最后更新</th>
              <th>业务映射</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filteredRows" :key="row.tagCode">
              <td>{{ row.tagCode }}</td>
              <td>{{ row.tagName }}</td>
              <td><span :class="['status-pill', row.sourceType === 'MOCK' ? 'warn' : 'good']">{{ row.sourceType }}</span></td>
              <td>{{ row.deviceName || row.deviceCode }}</td>
              <td>{{ row.valueText }}</td>
              <td><span :class="['status-pill', row.qualityLevel]">{{ row.qualityText }}</span></td>
              <td>{{ row.lastSeen }}</td>
              <td>{{ row.mappingCount }}</td>
            </tr>
            <tr v-if="!filteredRows.length">
              <td colspan="8" class="empty-cell">暂无匹配点位</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import CoalQuickBar from '../../components/coal/CoalQuickBar.vue'
import {
  getIotProviderStatus,
  getIotRealtimeSnapshot,
  getIotTagMappings,
  getIotTags,
  type IotProviderStatus,
  type IotRealtimeValue,
  type IotTagDefinition,
  type IotTagMapping,
} from '../../api/iot'

type DataAccessRow = IotTagDefinition & {
  valueText: string
  qualityText: string
  qualityLevel: 'good' | 'warn' | 'bad'
  lastSeen: string
  mappingCount: number
}

const loading = ref(false)
const keyword = ref('')
const providerStatus = ref<IotProviderStatus | null>(null)
const tags = ref<IotTagDefinition[]>([])
const mappings = ref<IotTagMapping[]>([])
const realtime = ref<Record<string, IotRealtimeValue>>({})

const loadStatus = async () => {
  loading.value = true
  try {
    const [providerRes, tagRes, mappingRes, realtimeRes] = await Promise.all([
      getIotProviderStatus(),
      getIotTags({ pageNum: 1, pageSize: 1000 }),
      getIotTagMappings(),
      getIotRealtimeSnapshot('data-access'),
    ])
    providerStatus.value = providerRes.data
    tags.value = tagRes.data.records || []
    mappings.value = mappingRes.data || []
    realtime.value = Object.fromEntries((realtimeRes.data.items || []).map((item) => [item.tagCode, item]))
  } finally {
    loading.value = false
  }
}

const enabledTags = computed(() => tags.value.filter((item) => item.enabled))
const mockTags = computed(() => tags.value.filter((item) => item.sourceType?.toUpperCase() === 'MOCK'))

const providerName = computed(() => {
  const actual = providerStatus.value?.actualProvider || 'unknown'
  return actual.toUpperCase()
})

const providerDescription = computed(() => {
  if (!providerStatus.value) return '正在读取后端数据接入状态'
  if (providerStatus.value.actualProvider === 'mock') {
    return providerStatus.value.fallbackToMock
      ? '当前使用演示数据源，首选采集源不可用或未启用，系统已回退到 mock。'
      : '当前使用演示数据源，生产部署前应切换到真实采集源。'
  }
  return '当前已使用真实采集 Provider，可继续核对点位质量、更新时间和业务映射。'
})

const rows = computed<DataAccessRow[]>(() => {
  const mappingCounter = mappings.value.reduce<Record<string, number>>((acc, item) => {
    acc[item.tagCode] = (acc[item.tagCode] || 0) + 1
    return acc
  }, {})

  return tags.value.map((tag) => {
    const item = realtime.value[tag.tagCode]
    const quality = item?.quality || 'NO_DATA'
    const qualityLevel = quality === 'GOOD' ? 'good' : item ? 'warn' : 'bad'
    return {
      ...tag,
      valueText: item ? `${item.valueText || item.value}${item.unit ? ` ${item.unit}` : ''}` : '-',
      qualityText: item ? quality : '无实时值',
      qualityLevel,
      lastSeen: item?.timestamp ? formatTime(item.timestamp) : '-',
      mappingCount: mappingCounter[tag.tagCode] || 0,
    }
  })
})

const filteredRows = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  const sorted = [...rows.value].sort((a, b) => Number(b.enabled) - Number(a.enabled))
  if (!text) return sorted
  return sorted.filter((item) => {
    return [item.tagCode, item.tagName, item.deviceCode, item.deviceName, item.sourceType]
      .some((value) => String(value || '').toLowerCase().includes(text))
  })
})

const onlineCount = computed(() => rows.value.filter((item) => item.qualityLevel === 'good').length)
const mappedCount = computed(() => new Set(mappings.value.map((item) => item.tagCode)).size)
const unmappedEnabledCount = computed(() => enabledTags.value.filter((item) => !mappings.value.some((mapping) => mapping.tagCode === item.tagCode)).length)

const stats = computed(() => [
  { label: '点位总数', value: String(tags.value.length) },
  { label: '启用点位', value: String(enabledTags.value.length) },
  { label: '实时正常', value: `${onlineRate.value}%` },
  { label: '演示点位', value: String(mockTags.value.length) },
])

const onlineRate = computed(() => {
  if (!enabledTags.value.length) return 0
  return Math.round((onlineCount.value / enabledTags.value.length) * 100)
})

const overallLevel = computed<'good' | 'warn' | 'bad'>(() => {
  if (providerStatus.value?.actualProvider === 'mock') return 'warn'
  if (onlineRate.value < 80 || unmappedEnabledCount.value > 0) return 'warn'
  return 'good'
})

const overallText = computed(() => {
  if (overallLevel.value === 'good') return '接入正常'
  if (providerStatus.value?.actualProvider === 'mock') return '演示回退'
  return '需要核对'
})

const healthItems = computed(() => [
  {
    label: '启用点位在线率',
    desc: '启用点位中实时质量为 GOOD 的占比',
    value: `${onlineRate.value}%`,
  },
  {
    label: '业务映射覆盖',
    desc: '已被业务页面或看板引用的点位数量',
    value: `${mappedCount.value}/${tags.value.length}`,
  },
  {
    label: '未映射启用点位',
    desc: '已启用但未绑定业务编码，容易造成页面无数据',
    value: String(unmappedEnabledCount.value),
  },
  {
    label: '演示回退风险',
    desc: 'Provider 为 mock 或点位来源为 MOCK 时需要现场替换',
    value: providerStatus.value?.actualProvider === 'mock' ? '高' : mockTags.value.length ? '中' : '低',
  },
])

const formatTime = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadStatus)
</script>

<style scoped>
.data-page {
  min-height: 100vh;
  padding: 0 20px 24px;
  background: #091019;
  color: #eef6ff;
}

.status-band,
.panel,
.grid-two {
  width: min(100%, 1680px);
  margin: 0 auto 16px;
}

.status-band {
  display: grid;
  grid-template-columns: minmax(320px, 2fr) repeat(4, minmax(140px, 1fr));
  gap: 14px;
}

.provider-panel,
.stat-card,
.panel {
  border: 1px solid rgba(96, 183, 255, 0.12);
  border-radius: 8px;
  background: rgba(8, 19, 30, 0.92);
}

.provider-panel {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 18px;
}

.eyebrow {
  color: #7ecfff;
  font-size: 12px;
  font-weight: 700;
}

.provider-panel h1 {
  margin: 8px 0;
  font-size: 28px;
}

.provider-panel p,
.panel-head p,
.health-row span {
  margin: 0;
  color: rgba(227, 239, 250, 0.68);
  line-height: 1.7;
}

.refresh-btn {
  flex: 0 0 auto;
  padding: 9px 16px;
  border: 1px solid rgba(126, 207, 255, 0.38);
  border-radius: 6px;
  background: rgba(45, 147, 255, 0.16);
  color: #eef6ff;
  cursor: pointer;
}

.refresh-btn:disabled {
  cursor: wait;
  opacity: 0.6;
}

.stat-card {
  padding: 18px;
}

.stat-card strong {
  display: block;
  color: #57d8ff;
  font-size: 30px;
}

.stat-card span {
  display: block;
  margin-top: 8px;
  color: rgba(227, 239, 250, 0.68);
}

.grid-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.panel {
  padding: 20px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.panel-head h2 {
  margin: 0 0 8px;
  font-size: 20px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 58px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.status-pill.good {
  background: rgba(33, 212, 164, 0.16);
  color: #21d4a4;
}

.status-pill.warn {
  background: rgba(255, 200, 87, 0.16);
  color: #ffc857;
}

.status-pill.bad {
  background: rgba(255, 123, 114, 0.16);
  color: #ff7b72;
}

.health-list {
  display: grid;
  gap: 10px;
}

.health-row,
.config-list div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(96, 183, 255, 0.08);
}

.health-row strong,
.health-row em {
  display: block;
  font-style: normal;
}

.health-row em {
  color: #57d8ff;
  font-size: 20px;
  font-weight: 800;
}

.config-list {
  margin: 0;
}

.config-list dt {
  color: rgba(227, 239, 250, 0.68);
}

.config-list dd {
  max-width: 60%;
  margin: 0;
  color: #eef6ff;
  text-align: right;
  word-break: break-all;
}

.filter-input {
  width: min(320px, 100%);
  height: 34px;
  padding: 0 12px;
  border: 1px solid rgba(126, 207, 255, 0.24);
  border-radius: 6px;
  outline: none;
  background: rgba(14, 27, 39, 0.75);
  color: #eef6ff;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 13px 12px;
  border-bottom: 1px solid rgba(96, 183, 255, 0.08);
  text-align: left;
  white-space: nowrap;
}

th {
  color: #7ecfff;
  font-size: 13px;
}

.empty-cell {
  color: rgba(227, 239, 250, 0.6);
  text-align: center;
}

@media (max-width: 1200px) {
  .status-band {
    grid-template-columns: repeat(2, 1fr);
  }

  .provider-panel {
    grid-column: 1 / -1;
  }

  .grid-two {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .status-band {
    grid-template-columns: 1fr;
  }

  .provider-panel,
  .panel-head {
    flex-direction: column;
  }
}
</style>
