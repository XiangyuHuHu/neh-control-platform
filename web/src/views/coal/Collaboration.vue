<template>
  <div class="closure-page">
    <section class="page-header">
      <div>
        <p class="page-tag">协同闭环</p>
        <h1>报警处置闭环看板</h1>
        <p class="page-desc">把报警、工单、停送电和调度协同放在同一张表里，方便值班人员判断每条异常是否有人接、是否执行、是否归档。</p>
      </div>
      <div class="page-actions">
        <el-button @click="loadData">刷新</el-button>
        <el-button type="primary" @click="openCreateDialog">报警转工单</el-button>
      </div>
    </section>

    <section class="kpi-grid">
      <article v-for="item in kpis" :key="item.label" class="kpi-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.note }}</small>
      </article>
    </section>

    <section class="content-grid">
      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>闭环漏斗</h2>
            <p>从异常发现到执行归档，逐层查看当前卡点。</p>
          </div>
        </div>
        <div class="funnel">
          <div v-for="item in funnelItems" :key="item.label" class="funnel-row">
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
            <h2>高优先级事项</h2>
            <p>优先展示未完成、超时风险高或涉及停送电的协同事项。</p>
          </div>
        </div>
        <div class="todo-list">
          <div v-for="item in priorityItems" :key="item.id" class="todo-item">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.summary }}</p>
              <span>{{ item.owner }} / {{ item.deadline }}</span>
            </div>
            <b :class="['level-tag', item.level]">{{ item.levelText }}</b>
          </div>
        </div>
      </article>

      <article class="panel panel--wide">
        <div class="panel-head">
          <div>
            <h2>闭环事项清单</h2>
            <p>按报警来源聚合工单、停送电和处置状态，接口不可用时自动展示演示闭环数据。</p>
          </div>
          <div class="filter-tools">
            <el-select v-model="statusFilter" clearable placeholder="闭环状态" style="width: 150px">
              <el-option label="未派工" value="unassigned" />
              <el-option label="处置中" value="processing" />
              <el-option label="待送电" value="power_on" />
              <el-option label="已闭环" value="closed" />
            </el-select>
            <el-input v-model="keyword" placeholder="搜索报警 / 设备 / 工单" style="width: 220px" />
          </div>
        </div>

        <el-table :data="filteredRows" class="data-table">
          <el-table-column prop="alarmId" label="报警编号" width="150" />
          <el-table-column prop="title" label="事项" min-width="220" show-overflow-tooltip />
          <el-table-column prop="deviceName" label="设备" min-width="150" />
          <el-table-column label="等级" width="100">
            <template #default="{ row }">
              <el-tag :type="levelTag(row.level)" effect="dark">{{ levelText(row.level) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="workOrderNo" label="关联工单" width="150" />
          <el-table-column prop="powerNo" label="停送电单" width="160" />
          <el-table-column prop="owner" label="责任人" width="110" />
          <el-table-column label="闭环进度" min-width="260">
            <template #default="{ row }">
              <el-steps :active="row.step" finish-status="success" simple>
                <el-step title="报警" />
                <el-step title="派工" />
                <el-step title="执行" />
                <el-step title="归档" />
              </el-steps>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="statusTag(row.status)">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </article>
    </section>

    <el-dialog v-model="showCreateDialog" title="报警转工单" width="640px">
      <el-form :model="form" label-width="96px">
        <el-form-item label="报警来源">
          <el-select v-model="form.alarmId" style="width: 100%">
            <el-option v-for="alarm in alarms" :key="alarm.alarmId" :label="`${alarm.alarmId} / ${alarm.alarmName || alarm.alarmCode}`" :value="alarm.alarmId" />
          </el-select>
        </el-form-item>
        <el-form-item label="工单标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority" style="width: 100%">
            <el-option label="高" value="HIGH" />
            <el-option label="中" value="MEDIUM" />
            <el-option label="低" value="LOW" />
          </el-select>
        </el-form-item>
        <el-form-item label="处置说明"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitWorkOrder">创建工单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getIotAlarms, type IotAlarmEvent } from '../../api/iot'
import {
  createWorkOrder,
  listPowerOperations,
  listWorkOrders,
  type PowerOperationDto,
  type WorkOrderDto,
} from '../../api/coal-business'

type ClosureStatus = 'unassigned' | 'processing' | 'power_on' | 'closed'
type ClosureRow = {
  id: string
  alarmId: string
  title: string
  deviceName: string
  level: string
  workOrderNo: string
  powerNo: string
  owner: string
  deadline: string
  status: ClosureStatus
  step: number
  summary: string
}

const loading = ref(false)
const showCreateDialog = ref(false)
const keyword = ref('')
const statusFilter = ref<ClosureStatus | ''>('')
const alarms = ref<IotAlarmEvent[]>([])
const workOrders = ref<WorkOrderDto[]>([])
const powerOrders = ref<PowerOperationDto[]>([])
const usingMock = ref(false)

const form = ref({
  alarmId: '',
  title: '',
  priority: 'HIGH',
  description: '',
})

const mockRows: ClosureRow[] = [
  {
    id: 'mock-1',
    alarmId: 'ALM-20260430-001',
    title: '311中煤卧式离心机振动超限',
    deviceName: '311中煤卧式离心机',
    level: 'HIGH',
    workOrderNo: 'WO-20260430-011',
    powerNo: 'PO-20260430-0003',
    owner: '机修班',
    deadline: '今日 18:00',
    status: 'processing',
    step: 3,
    summary: '已派维修工单，停电审批完成，正在执行检修。',
  },
  {
    id: 'mock-2',
    alarmId: 'ALM-20260430-002',
    title: '325矸石脱介筛筛板破损趋势',
    deviceName: '325矸石脱介筛',
    level: 'MEDIUM',
    workOrderNo: 'WO-20260430-012',
    powerNo: '-',
    owner: '生产三班',
    deadline: '明日 10:00',
    status: 'processing',
    step: 2,
    summary: '已生成巡检工单，等待备件确认。',
  },
  {
    id: 'mock-3',
    alarmId: 'ALM-20260430-003',
    title: '101原煤皮带机电流波动',
    deviceName: '101原煤皮带机',
    level: 'LOW',
    workOrderNo: '-',
    powerNo: '-',
    owner: '调度室',
    deadline: '今日 22:00',
    status: 'unassigned',
    step: 1,
    summary: '已报警但未派工，需要值班人员确认是否转工单。',
  },
  {
    id: 'mock-4',
    alarmId: 'ALM-20260429-009',
    title: '压滤机给料泵温升异常',
    deviceName: '压滤机给料泵',
    level: 'HIGH',
    workOrderNo: 'WO-20260429-018',
    powerNo: 'PO-20260429-0006',
    owner: '电气班',
    deadline: '已完成',
    status: 'closed',
    step: 4,
    summary: '已完成检修并归档，复盘结论为电机接线端子松动。',
  },
]

const loadData = async () => {
  loading.value = true
  try {
    const [alarmRes, workOrderRes, powerRes] = await Promise.all([
      getIotAlarms(),
      listWorkOrders(),
      listPowerOperations(),
    ])
    alarms.value = alarmRes.data || []
    workOrders.value = workOrderRes || []
    powerOrders.value = powerRes || []
    usingMock.value = false
  } catch {
    alarms.value = []
    workOrders.value = []
    powerOrders.value = []
    usingMock.value = true
  } finally {
    loading.value = false
  }
}

const rows = computed<ClosureRow[]>(() => {
  if (usingMock.value || (!alarms.value.length && !workOrders.value.length)) return mockRows

  const powerByDevice = new Map(powerOrders.value.map((item) => [String(item.deviceId), item]))
  return alarms.value.map((alarm, index) => {
    const deviceId = alarm.deviceCode || alarm.deviceCode === '' ? alarm.deviceCode : alarm.tagCode
    const order = workOrders.value.find((item) =>
      String(item.deviceId || '') === String(deviceId || '') ||
      (item.title || '').includes(alarm.alarmName || alarm.alarmCode || alarm.tagCode),
    )
    const power = order?.deviceId ? powerByDevice.get(String(order.deviceId)) : undefined
    const status = resolveStatus(alarm, order, power)
    return {
      id: alarm.alarmId || `alarm-${index}`,
      alarmId: alarm.alarmId || '-',
      title: alarm.alarmName || alarm.alarmCode || alarm.tagCode,
      deviceName: alarm.deviceCode || '-',
      level: alarm.alarmLevel || 'MEDIUM',
      workOrderNo: order?.orderNo || '-',
      powerNo: power?.applicationNo || '-',
      owner: order?.assigneeId ? `用户${order.assigneeId}` : alarm.ackBy || '-',
      deadline: order?.plannedEndTime ? formatTime(order.plannedEndTime) : '-',
      status,
      step: status === 'closed' ? 4 : order ? power ? 3 : 2 : 1,
      summary: order?.description || alarm.remark || '等待确认处置方案',
    }
  })
})

const filteredRows = computed(() => {
  const text = keyword.value.trim().toLowerCase()
  return rows.value.filter((item) => {
    const matchStatus = !statusFilter.value || item.status === statusFilter.value
    const matchText = !text || [item.alarmId, item.title, item.deviceName, item.workOrderNo, item.powerNo]
      .some((value) => String(value || '').toLowerCase().includes(text))
    return matchStatus && matchText
  })
})

const kpis = computed(() => {
  const total = rows.value.length
  const closed = rows.value.filter((item) => item.status === 'closed').length
  const unassigned = rows.value.filter((item) => item.status === 'unassigned').length
  const power = rows.value.filter((item) => item.powerNo !== '-').length
  return [
    { label: '闭环事项', value: `${total} 项`, note: usingMock.value ? '演示闭环数据' : '来自接口汇总' },
    { label: '未派工', value: `${unassigned} 项`, note: '需要值班确认' },
    { label: '涉及停送电', value: `${power} 项`, note: '需调度与电气协同' },
    { label: '闭环率', value: `${total ? Math.round((closed / total) * 100) : 0}%`, note: `${closed}/${total} 已归档` },
  ]
})

const funnelItems = computed(() => [
  { label: '报警发现', desc: '采集、规则或模型触发的异常', value: rows.value.length },
  { label: '已派工单', desc: '已形成维修、巡检或调度任务', value: rows.value.filter((item) => item.workOrderNo !== '-').length },
  { label: '执行处置', desc: '处于执行中或进入停送电流程', value: rows.value.filter((item) => ['processing', 'power_on'].includes(item.status)).length },
  { label: '复盘归档', desc: '完成处置并有结果记录', value: rows.value.filter((item) => item.status === 'closed').length },
])

const priorityItems = computed(() =>
  rows.value
    .filter((item) => item.status !== 'closed')
    .sort((a, b) => levelRank(b.level) - levelRank(a.level))
    .slice(0, 4)
    .map((item) => ({
      ...item,
      levelText: levelText(item.level),
      level: levelClass(item.level),
    })),
)

const openCreateDialog = () => {
  const first = alarms.value[0]
  form.value = {
    alarmId: first?.alarmId || '',
    title: first ? `${first.alarmName || first.alarmCode}处置工单` : '',
    priority: first?.alarmLevel || 'HIGH',
    description: first?.remark || '',
  }
  showCreateDialog.value = true
}

const submitWorkOrder = async () => {
  if (!form.value.title.trim()) {
    ElMessage.warning('请填写工单标题')
    return
  }
  const alarm = alarms.value.find((item) => item.alarmId === form.value.alarmId)
  try {
    await createWorkOrder({
      orderNo: `WO-${new Date().toISOString().slice(0, 10).replaceAll('-', '')}-${Date.now().toString().slice(-4)}`,
      title: form.value.title,
      description: form.value.description || alarm?.remark || '',
      type: 'ALARM',
      priority: form.value.priority,
      status: '待处理',
      deviceId: Number(alarm?.deviceCode) || undefined,
      creatorId: 1,
    })
    ElMessage.success('已创建报警处置工单')
    showCreateDialog.value = false
    await loadData()
  } catch {
    ElMessage.warning('接口不可用，当前仅保留闭环看板演示')
    showCreateDialog.value = false
  }
}

const resolveStatus = (alarm: IotAlarmEvent, order?: WorkOrderDto, power?: PowerOperationDto): ClosureStatus => {
  if (alarm.alarmStatus === 'CLOSED' || order?.status?.includes('完成') || order?.status?.includes('关闭')) return 'closed'
  if (power?.workflowStatus === 'power_on_applied') return 'power_on'
  if (order) return 'processing'
  return 'unassigned'
}

const levelRank = (level: string) => ({ HIGH: 3, CRITICAL: 3, MEDIUM: 2, LOW: 1 }[level?.toUpperCase()] || 1)
const levelClass = (level: string) => levelRank(level) >= 3 ? 'danger' : levelRank(level) === 2 ? 'warn' : 'info'
const levelText = (level: string) => levelRank(level) >= 3 ? '高' : levelRank(level) === 2 ? '中' : '低'
const levelTag = (level: string) => levelRank(level) >= 3 ? 'danger' : levelRank(level) === 2 ? 'warning' : 'info'
const statusText = (status: ClosureStatus) => ({ unassigned: '未派工', processing: '处置中', power_on: '待送电', closed: '已闭环' }[status])
const statusTag = (status: ClosureStatus) => ({ unassigned: 'warning', processing: 'primary', power_on: 'danger', closed: 'success' }[status] as 'warning' | 'primary' | 'danger' | 'success')

const formatTime = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadData)
</script>

<style scoped>
.closure-page{min-height:100vh;padding:24px 20px 28px;background:#091019;color:#eef6ff}
.page-header,.kpi-grid,.content-grid{width:min(100%,1680px);margin:0 auto 16px}
.page-header{display:flex;justify-content:space-between;gap:24px;padding:26px 28px;border:1px solid rgba(96,183,255,.12);border-radius:8px;background:rgba(8,19,30,.92)}
.page-tag{margin:0 0 10px;color:#7ecfff;font-size:12px;font-weight:700}
.page-header h1,.panel-head h2{margin:0}
.page-desc,.panel-head p{margin:10px 0 0;color:rgba(227,239,250,.68);line-height:1.7}
.page-actions,.filter-tools{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.kpi-card,.panel{border:1px solid rgba(96,183,255,.12);border-radius:8px;background:rgba(8,19,30,.92)}
.kpi-card{padding:20px}
.kpi-card span{display:block;color:rgba(227,239,250,.62);font-size:13px}
.kpi-card strong{display:block;margin-top:12px;font-size:32px;color:#f3faff}
.kpi-card small{display:block;margin-top:10px;color:#67d8ff}
.content-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.panel{padding:22px}
.panel--wide{grid-column:1 / -1}
.panel-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:18px}
.funnel,.todo-list{display:grid;gap:12px}
.funnel-row,.todo-item{display:flex;justify-content:space-between;gap:16px;padding:15px;border-radius:8px;background:rgba(13,25,38,.82)}
.funnel-row strong,.todo-item strong{display:block}
.funnel-row span,.todo-item p,.todo-item span{display:block;margin-top:8px;color:rgba(227,239,250,.66);line-height:1.6}
.funnel-row em{font-style:normal;color:#57d8ff;font-size:26px;font-weight:800}
.level-tag{height:fit-content;padding:5px 10px;border-radius:999px;font-size:12px;white-space:nowrap}
.level-tag.danger{background:rgba(255,109,109,.14);color:#ff8181}
.level-tag.warn{background:rgba(255,200,87,.16);color:#ffc857}
.level-tag.info{background:rgba(69,203,255,.14);color:#71d5ff}
.data-table :deep(.el-table),.data-table :deep(.el-table__inner-wrapper),.data-table :deep(.el-table tr),.data-table :deep(.el-table th.el-table__cell),.data-table :deep(.el-table td.el-table__cell){background:transparent;color:#eef6ff}
.data-table :deep(.el-table__header th.el-table__cell){color:#7ecfff}
@media (max-width:1200px){.kpi-grid,.content-grid{grid-template-columns:1fr}.page-header,.panel-head{flex-direction:column}}
</style>
