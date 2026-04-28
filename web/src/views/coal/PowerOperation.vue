<template>
  <div class="coal-page section-page">
    <CoalQuickBar
      title="停送电审批"
      subtitle="基础闭环页面：停电申请、停电审批、验电、检修开始/完成、送电申请、送电审批。"
    />

    <section class="page-shell">
      <section class="section-hero">
        <div>
          <p class="section-eyebrow">调度管理</p>
          <h1>停送电流程总览</h1>
          <p class="section-text">先覆盖基础审批与执行流程，支持实时查看状态、剩余挂牌和风险级别。</p>
        </div>
        <div class="hero-actions">
          <el-button @click="loadData">刷新</el-button>
          <el-button @click="handleExport">导出CSV</el-button>
          <el-button type="primary" @click="openApplyDialog">新建停电申请</el-button>
        </div>
      </section>

      <section class="stats-grid">
        <article class="stat-card stat-card--total">
          <span>工单总数</span>
          <strong>{{ rows.length }}</strong>
          <small>停送电全流程</small>
        </article>
        <article class="stat-card stat-card--pending-off">
          <span>待停电审批</span>
          <strong>{{ countByStatus('pending') }}</strong>
          <small>调度需处理</small>
        </article>
        <article class="stat-card stat-card--pending-on">
          <span>待送电审批</span>
          <strong>{{ countByStatus('power_on_applied') }}</strong>
          <small>送电确认</small>
        </article>
        <article class="stat-card stat-card--risk">
          <span>高风险工单</span>
          <strong>{{ highRiskCount }}</strong>
          <small>含挂牌阻断</small>
        </article>
      </section>

      <section class="section-panel filters">
        <el-select v-model="filterStatus" clearable placeholder="流程状态" style="width: 220px">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-input v-model="filterPowerRoom" placeholder="配电室" style="width: 180px" />
        <el-button type="primary" @click="loadData">查询</el-button>
        <el-tag type="info">{{ usingMockData ? '演示数据模式' : '实时接口模式' }}</el-tag>
      </section>

      <section class="section-panel">
        <div class="panel-head">
          <div>
            <h2>流程看板摘要</h2>
            <p>来自停送电数字孪生看板接口。</p>
          </div>
        </div>
        <div class="board-grid">
          <div class="board-card">
            <h3>状态统计</h3>
            <ul v-if="Object.keys(boardStatusOverview).length">
              <li v-for="(value, key) in boardStatusOverview" :key="key">{{ statusText(key) }}：{{ value }}</li>
            </ul>
            <div v-else class="board-skeleton">
              <span></span><span></span><span></span>
            </div>
          </div>
          <div class="board-card">
            <h3>配电室统计</h3>
            <ul v-if="Object.keys(boardPowerRoomOverview).length">
              <li v-for="(value, key) in boardPowerRoomOverview" :key="key">{{ key || '未分配' }}：{{ value }}</li>
            </ul>
            <div v-else class="board-skeleton">
              <span></span><span></span><span></span>
            </div>
          </div>
          <div class="board-card">
            <h3>高风险清单（前 5）</h3>
            <ul>
              <li v-for="item in highRiskTop5" :key="item.applicationNo">
                {{ item.applicationNo }} / {{ item.deviceName }} / 挂牌 {{ item.remainingTagCount || 0 }}
              </li>
              <li v-if="highRiskTop5.length === 0">暂无高风险工单</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="section-panel">
        <div class="panel-head">
          <div>
            <h2>停送电审批列表</h2>
            <p>按当前状态执行下一步动作。</p>
          </div>
        </div>
        <el-table :data="displayRows" class="records-table">
          <el-table-column prop="applicationNo" label="工单号" min-width="170" />
          <el-table-column prop="deviceName" label="设备" min-width="160" />
          <el-table-column prop="powerRoom" label="配电室" min-width="120" />
          <el-table-column prop="workflowStatus" label="状态" min-width="140">
            <template #default="{ row }">
              <el-tag :type="tagType(row.workflowStatus)">{{ statusText(row.workflowStatus) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="riskLevel" label="风险级别" min-width="110" />
          <el-table-column prop="remainingTagCount" label="剩余挂牌" min-width="100" />
          <el-table-column label="流程进度" min-width="240">
            <template #default="{ row }">
              <el-steps :active="stepIndex(row.workflowStatus)" finish-status="success" simple>
                <el-step title="申请" />
                <el-step title="停电审批" />
                <el-step title="检修" />
                <el-step title="送电" />
                <el-step title="完成" />
              </el-steps>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="原因" min-width="220" show-overflow-tooltip />
          <el-table-column label="操作" width="560" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="doApprovePowerOff(row, true)" :disabled="row.workflowStatus !== 'pending'">停电通过</el-button>
              <el-button size="small" type="danger" plain @click="doApprovePowerOff(row, false)" :disabled="row.workflowStatus !== 'pending'">
                停电驳回
              </el-button>
              <el-button size="small" @click="doVerify(row)" :disabled="row.workflowStatus !== 'approved'">验电</el-button>
              <el-button size="small" @click="doStartRepair(row)" :disabled="row.workflowStatus !== 'verified'">开始检修</el-button>
              <el-button size="small" @click="doCompleteRepair(row)" :disabled="row.workflowStatus !== 'repairing'">完成检修</el-button>
              <el-button size="small" @click="doApplyPowerOn(row)" :disabled="row.workflowStatus !== 'repair_completed'">送电申请</el-button>
              <el-button size="small" type="success" @click="doApprovePowerOn(row, true)" :disabled="row.workflowStatus !== 'power_on_applied'">
                送电通过
              </el-button>
              <el-button size="small" type="danger" plain @click="doApprovePowerOn(row, false)" :disabled="row.workflowStatus !== 'power_on_applied'">
                送电驳回
              </el-button>
              <el-button size="small" type="primary" link @click="openTimeline(row)">流程详情</el-button>
            </template>
          </el-table-column>
          <template #empty>
            <div class="table-empty">
              <div class="table-empty__icon">◌</div>
              <p>暂无停送电数据</p>
              <small>可先点击“新建停电申请”或切换筛选条件</small>
            </div>
          </template>
        </el-table>
      </section>
    </section>

    <el-dialog v-model="showApplyDialog" title="新建停电申请" width="700px">
      <el-form :model="applyForm" label-width="110px">
        <el-form-item label="设备ID"><el-input-number v-model="applyForm.deviceId" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="设备名称"><el-input v-model="applyForm.deviceName" /></el-form-item>
        <el-form-item label="配电室"><el-input v-model="applyForm.powerRoom" /></el-form-item>
        <el-form-item label="柜号"><el-input v-model="applyForm.cabinetNo" /></el-form-item>
        <el-form-item label="申请人"><el-input v-model="applyForm.requestedBy" /></el-form-item>
        <el-form-item label="停电原因"><el-input v-model="applyForm.reason" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApplyDialog = false">取消</el-button>
        <el-button type="primary" @click="submitApply">提交</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="showTimeline" title="停送电流程时间轴" size="520px">
      <div v-if="timelineTarget">
        <p class="timeline-title">{{ timelineTarget.applicationNo }} / {{ timelineTarget.deviceName }}</p>
        <el-timeline>
          <el-timeline-item
            v-for="item in buildTimeline(timelineTarget)"
            :key="item.label"
            :timestamp="item.time || '未发生'"
            :type="item.done ? 'success' : 'info'"
          >
            <strong>{{ item.label }}</strong>
            <p class="timeline-note">{{ item.note }}</p>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CoalQuickBar from '../../components/coal/CoalQuickBar.vue'
import { exportRowsToCsv } from '../../utils/report-export'
import {
  applyPowerOn,
  applyPowerOperation,
  approvePowerOff,
  approvePowerOn,
  completeRepairPowerOperation,
  getPowerDigitalTwinBoard,
  listPowerOperations,
  startRepairPowerOperation,
  verifyPowerOperation,
  type PowerApplyPayload,
  type PowerOperationDto,
} from '../../api/coal-business'

const filterStatus = ref('')
const filterPowerRoom = ref('')
const rows = ref<PowerOperationDto[]>([])
const usingMockData = ref(false)
const boardStatusOverview = ref<Record<string, number>>({})
const boardPowerRoomOverview = ref<Record<string, number>>({})
const showTimeline = ref(false)
const timelineTarget = ref<PowerOperationDto | null>(null)

const showApplyDialog = ref(false)
const applyForm = ref<PowerApplyPayload>({
  deviceId: 1,
  deviceName: '',
  powerRoom: '',
  cabinetNo: '',
  reason: '',
  requestedBy: '调度员',
})

const statusOptions = [
  { label: '待审批', value: 'pending' },
  { label: '停电已审批', value: 'approved' },
  { label: '已验电', value: 'verified' },
  { label: '检修中', value: 'repairing' },
  { label: '检修完成', value: 'repair_completed' },
  { label: '待送电审批', value: 'power_on_applied' },
  { label: '已完成', value: 'completed' },
]

const mockRows: PowerOperationDto[] = [
  {
    id: 9001,
    applicationNo: 'PO-20260427-0001',
    deviceId: 101,
    deviceName: '主洗一段泵',
    powerRoom: '主配电室A',
    cabinetNo: 'A-12',
    workflowStatus: 'pending',
    operationType: 'power_off',
    riskLevel: 'medium',
    reason: '计划检修，更换轴承',
    requestedBy: '张伟',
    remainingTagCount: 0,
    createdAt: new Date().toISOString(),
  },
  {
    id: 9002,
    applicationNo: 'PO-20260427-0002',
    deviceId: 102,
    deviceName: '重介旋流器泵',
    powerRoom: '主配电室B',
    cabinetNo: 'B-08',
    workflowStatus: 'repair_completed',
    operationType: 'power_off',
    riskLevel: 'high',
    reason: '振动偏大，计划检修',
    requestedBy: '李超',
    approvedBy: '调度员',
    verifiedBy: '电工甲',
    repairedBy: '电工甲',
    remainingTagCount: 1,
    approvedAt: new Date(Date.now() - 1000 * 60 * 80).toISOString(),
    verifiedAt: new Date(Date.now() - 1000 * 60 * 70).toISOString(),
    repairStartedAt: new Date(Date.now() - 1000 * 60 * 65).toISOString(),
    repairCompletedAt: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
  },
  {
    id: 9003,
    applicationNo: 'PO-20260427-0003',
    deviceId: 103,
    deviceName: '压滤机给料泵',
    powerRoom: '主配电室A',
    cabinetNo: 'A-18',
    workflowStatus: 'power_on_applied',
    operationType: 'power_off',
    riskLevel: 'low',
    reason: '电机温升异常处理',
    requestedBy: '王敏',
    approvedBy: '调度员',
    verifiedBy: '电工乙',
    repairedBy: '电工乙',
    remainingTagCount: 0,
    approvedAt: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    verifiedAt: new Date(Date.now() - 1000 * 60 * 110).toISOString(),
    repairStartedAt: new Date(Date.now() - 1000 * 60 * 100).toISOString(),
    repairCompletedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    powerOnAppliedAt: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    createdAt: new Date(Date.now() - 1000 * 60 * 130).toISOString(),
  },
]

const highRiskCount = computed(() =>
  rows.value.filter((item) => item.riskLevel === 'high' || Number(item.remainingTagCount || 0) > 0).length,
)
const highRiskTop5 = computed(() =>
  rows.value
    .filter((item) => item.riskLevel === 'high' || Number(item.remainingTagCount || 0) > 0)
    .slice(0, 5),
)

const exportColumns: Array<{ key: keyof PowerOperationDto; label: string }> = [
  { key: 'applicationNo', label: '工单号' },
  { key: 'deviceName', label: '设备名称' },
  { key: 'powerRoom', label: '配电室' },
  { key: 'workflowStatus', label: '流程状态' },
  { key: 'riskLevel', label: '风险级别' },
  { key: 'remainingTagCount', label: '剩余挂牌' },
  { key: 'requestedBy', label: '申请人' },
  { key: 'approvedBy', label: '审批人' },
  { key: 'reason', label: '停电原因' },
  { key: 'createdAt', label: '申请时间' },
]
const displayRows = computed(() =>
  rows.value.filter((item) => {
    const statusMatch = !filterStatus.value || item.workflowStatus === filterStatus.value
    const roomMatch = !filterPowerRoom.value || (item.powerRoom || '').includes(filterPowerRoom.value)
    return statusMatch && roomMatch
  }),
)

function countByStatus(status: string) {
  return rows.value.filter((item) => item.workflowStatus === status).length
}

function statusText(status?: string) {
  const map: Record<string, string> = {
    pending: '待停电审批',
    approved: '停电已审批',
    rejected: '停电已驳回',
    verified: '已验电',
    repairing: '检修中',
    repair_completed: '检修完成',
    power_on_applied: '待送电审批',
    power_on_rejected: '送电已驳回',
    completed: '流程完成',
  }
  return status ? map[status] || status : '-'
}

function tagType(status?: string) {
  if (status === 'completed') return 'success'
  if (status === 'pending' || status === 'power_on_applied') return 'warning'
  if (status === 'rejected' || status === 'power_on_rejected') return 'danger'
  return 'info'
}

function stepIndex(status?: string) {
  if (!status) return 0
  if (status === 'pending') return 1
  if (status === 'approved' || status === 'verified') return 2
  if (status === 'repairing' || status === 'repair_completed') return 3
  if (status === 'power_on_applied' || status === 'power_on_rejected') return 4
  if (status === 'completed') return 5
  if (status === 'rejected') return 1
  return 1
}

function handleExport() {
  const filename = `停送电审批_${new Date().toISOString().slice(0, 10)}`
  exportRowsToCsv(displayRows.value, exportColumns, filename)
  ElMessage.success('停送电审批数据 CSV 已导出')
}

async function loadData() {
  try {
    rows.value = await listPowerOperations({ status: filterStatus.value, powerRoom: filterPowerRoom.value })
    usingMockData.value = false
  } catch {
    rows.value = structuredClone(mockRows)
    usingMockData.value = true
    ElMessage.warning('停送电接口未就绪，已切换演示数据模式')
  }

  try {
    const board = await getPowerDigitalTwinBoard({ powerRoom: filterPowerRoom.value })
    boardStatusOverview.value = board.statusOverview || {}
    boardPowerRoomOverview.value = board.powerRoomOverview || {}
  } catch {
    boardStatusOverview.value = buildOverview(rows.value)
    boardPowerRoomOverview.value = buildPowerRoomOverview(rows.value)
  }
}

function openApplyDialog() {
  applyForm.value = {
    deviceId: 1,
    deviceName: '',
    powerRoom: '',
    cabinetNo: '',
    reason: '',
    requestedBy: '调度员',
  }
  showApplyDialog.value = true
}

async function submitApply() {
  try {
    await applyPowerOperation(applyForm.value)
    ElMessage.success('停电申请已提交')
    showApplyDialog.value = false
    await loadData()
  } catch {
    const now = new Date().toISOString()
    rows.value.unshift({
      id: Date.now(),
      applicationNo: `PO-${now.slice(0, 10).replaceAll('-', '')}-${String(rows.value.length + 1).padStart(4, '0')}`,
      workflowStatus: 'pending',
      operationType: 'power_off',
      riskLevel: 'medium',
      remainingTagCount: 0,
      createdAt: now,
      ...applyForm.value,
    })
    showApplyDialog.value = false
    ElMessage.success('已在演示模式下创建停电申请')
  }
}

async function doApprovePowerOff(row: PowerOperationDto, approved: boolean) {
  let comment = approved ? '同意停电' : ''
  try {
    if (approved) {
      await ElMessageBox.confirm(`确认通过工单 ${row.applicationNo} 的停电审批吗？`, '停电审批确认', { type: 'warning' })
    } else {
      const result = await ElMessageBox.prompt(`请输入工单 ${row.applicationNo} 的驳回意见`, '停电审批驳回', {
        confirmButtonText: '确认驳回',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入驳回原因',
        inputValidator: (value) => (value.trim() ? true : '驳回意见不能为空'),
      })
      comment = result.value.trim()
    }
  } catch {
    return
  }

  try {
    await approvePowerOff({ applicationId: row.id!, operator: '调度员', approved, comment })
    ElMessage.success(approved ? '停电审批已通过' : '停电审批已驳回')
    await loadData()
  } catch (error: any) {
    applyLocalTransition(row, approved ? 'approved' : 'rejected', { approvedBy: '调度员', approvedAt: new Date().toISOString(), dispatchDecision: comment })
    ElMessage.warning(error?.message || '接口不可用，已在演示模式执行')
  }
}

async function doVerify(row: PowerOperationDto) {
  try {
    await verifyPowerOperation({ applicationId: row.id!, operator: '电工', comment: '验电完成' })
    ElMessage.success('验电完成')
    await loadData()
  } catch (error: any) {
    applyLocalTransition(row, 'verified', {
      verifiedBy: '电工',
      verifiedAt: new Date().toISOString(),
      remainingTagCount: 1,
      riskLevel: 'high',
    })
    ElMessage.warning(error?.message || '接口不可用，已在演示模式执行')
  }
}

async function doStartRepair(row: PowerOperationDto) {
  try {
    await startRepairPowerOperation({ applicationId: row.id!, operator: '电工', comment: '开始检修' })
    ElMessage.success('已开始检修')
    await loadData()
  } catch (error: any) {
    applyLocalTransition(row, 'repairing', { repairedBy: '电工', repairStartedAt: new Date().toISOString() })
    ElMessage.warning(error?.message || '接口不可用，已在演示模式执行')
  }
}

async function doCompleteRepair(row: PowerOperationDto) {
  try {
    await completeRepairPowerOperation({ applicationId: row.id!, operator: '电工', comment: '检修完成' })
    ElMessage.success('检修完成')
    await loadData()
  } catch (error: any) {
    applyLocalTransition(row, 'repair_completed', { repairCompletedAt: new Date().toISOString() })
    ElMessage.warning(error?.message || '接口不可用，已在演示模式执行')
  }
}

async function doApplyPowerOn(row: PowerOperationDto) {
  try {
    await applyPowerOn({ applicationId: row.id!, operator: '电工', comment: '申请送电' })
    ElMessage.success('送电申请已提交')
    await loadData()
  } catch (error: any) {
    const remain = Number(row.remainingTagCount || 0)
    if (remain > 0) {
      ElMessage.warning('演示模式：仍有挂牌，禁止送电申请')
      return
    }
    applyLocalTransition(row, 'power_on_applied', { powerOnAppliedAt: new Date().toISOString() })
    ElMessage.warning(error?.message || '接口不可用，已在演示模式执行')
  }
}

async function doApprovePowerOn(row: PowerOperationDto, approved: boolean) {
  let comment = approved ? '同意送电' : ''
  try {
    if (approved) {
      await ElMessageBox.confirm(`确认通过工单 ${row.applicationNo} 的送电审批吗？`, '送电审批确认', { type: 'warning' })
    } else {
      const result = await ElMessageBox.prompt(`请输入工单 ${row.applicationNo} 的送电驳回意见`, '送电审批驳回', {
        confirmButtonText: '确认驳回',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入驳回原因',
        inputValidator: (value) => (value.trim() ? true : '驳回意见不能为空'),
      })
      comment = result.value.trim()
    }
  } catch {
    return
  }

  try {
    await approvePowerOn({ applicationId: row.id!, operator: '调度员', approved, comment })
    ElMessage.success(approved ? '送电审批已通过' : '送电审批已驳回')
    await loadData()
  } catch (error: any) {
    applyLocalTransition(row, approved ? 'completed' : 'power_on_rejected', { powerOnApprovedAt: new Date().toISOString(), dispatchDecision: comment })
    ElMessage.warning(error?.message || '接口不可用，已在演示模式执行')
  }
}

function openTimeline(row: PowerOperationDto) {
  timelineTarget.value = row
  showTimeline.value = true
}

function buildTimeline(row: PowerOperationDto) {
  return [
    { label: '停电申请', time: row.createdAt, done: true, note: `申请人：${row.requestedBy || '-'}` },
    { label: '停电审批', time: row.approvedAt, done: !!row.approvedAt, note: `审批人：${row.approvedBy || '-'}` },
    { label: '验电确认', time: row.verifiedAt, done: !!row.verifiedAt, note: `电工：${row.verifiedBy || '-'}` },
    { label: '开始检修', time: row.repairStartedAt, done: !!row.repairStartedAt, note: `执行人：${row.repairedBy || '-'}` },
    { label: '完成检修', time: row.repairCompletedAt, done: !!row.repairCompletedAt, note: '检修结果已回填' },
    { label: '送电申请', time: row.powerOnAppliedAt, done: !!row.powerOnAppliedAt, note: `剩余挂牌：${row.remainingTagCount || 0}` },
    { label: '送电审批', time: row.powerOnApprovedAt, done: !!row.powerOnApprovedAt, note: `决策：${statusText(row.workflowStatus)}` },
  ]
}

function applyLocalTransition(row: PowerOperationDto, nextStatus: string, patch: Partial<PowerOperationDto> = {}) {
  const idx = rows.value.findIndex((item) => item.id === row.id)
  if (idx < 0) return
  rows.value[idx] = { ...rows.value[idx], ...patch, workflowStatus: nextStatus, updatedAt: new Date().toISOString() }
  boardStatusOverview.value = buildOverview(rows.value)
  boardPowerRoomOverview.value = buildPowerRoomOverview(rows.value)
}

function buildOverview(data: PowerOperationDto[]) {
  return data.reduce<Record<string, number>>((acc, item) => {
    const key = item.workflowStatus || 'unknown'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
}

function buildPowerRoomOverview(data: PowerOperationDto[]) {
  return data.reduce<Record<string, number>>((acc, item) => {
    const key = item.powerRoom || '未分配'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
}

onMounted(async () => {
  await loadData()
})
</script>

<style scoped>
.section-page{min-height:100vh;padding:0 20px 24px;background:#091019;color:#eef6ff}
.page-shell{width:min(100%,1680px);margin:0 auto}
.section-hero{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;margin-bottom:20px}
.section-eyebrow{margin:0 0 10px;color:#72d8ff;font-size:12px;letter-spacing:.2em;text-transform:uppercase}
.section-hero h1{margin:0;font-size:38px}
.section-text{max-width:820px;margin:12px 0 0;color:#96aabc;line-height:1.7}
.hero-actions{display:flex;gap:12px}
.section-panel{padding:22px;border-radius:20px;border:1px solid rgba(122,190,255,.12);background:rgba(12,20,31,.88);box-shadow:0 18px 40px rgba(0,0,0,.16);margin-bottom:20px}
.filters{display:flex;gap:12px;align-items:center;flex-wrap:wrap;background:rgba(24,45,66,.34);border:1px solid rgba(122,190,255,.16)}
.filters :deep(.el-input__wrapper),.filters :deep(.el-select__wrapper){min-height:36px}
.filters :deep(.el-button--primary){box-shadow:0 0 14px rgba(80,193,255,.35)}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}
.stat-card{padding:18px;border-radius:18px;border:1px solid rgba(122,190,255,.2);background:linear-gradient(145deg,rgba(18,34,51,.95),rgba(10,21,33,.95))}
.stat-card span{display:block;color:#97aabc}
.stat-card strong{display:block;margin-top:10px;font-size:44px;line-height:1;color:#dff6ff;letter-spacing:.02em;text-shadow:0 0 14px rgba(74,212,255,.2)}
.stat-card small{display:block;margin-top:10px;color:#6ec8ff}
.stat-card--total strong{color:#45d2ff}
.stat-card--pending-off strong{color:#ffb257}
.stat-card--pending-on strong{color:#7edbff}
.stat-card--risk strong{color:#ff6f6f}
.panel-head{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin-bottom:16px}
.panel-head h2{margin:0;font-size:24px}
.panel-head p{margin:8px 0 0;color:#8fa8bc}
.board-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.board-card{padding:16px;border:1px solid rgba(122,190,255,.18);border-radius:14px;background:linear-gradient(180deg,rgba(14,29,45,.9),rgba(10,20,31,.92));position:relative;overflow:hidden}
.board-card::after{content:'';position:absolute;inset:auto -20% 0;height:1px;background:linear-gradient(90deg,transparent,rgba(84,213,255,.32),transparent)}
.board-card h3{margin:0 0 12px;font-size:16px}
.board-card ul{margin:0;padding-left:16px;display:grid;gap:8px;color:#9db0c2}
.board-skeleton{display:grid;gap:10px}
.board-skeleton span{display:block;height:12px;border-radius:999px;background:linear-gradient(90deg,rgba(61,89,114,.35),rgba(107,150,184,.45),rgba(61,89,114,.35))}
.board-skeleton span:nth-child(2){width:82%}
.board-skeleton span:nth-child(3){width:68%}
.records-table :deep(.el-table th.el-table__cell){background:rgba(39,71,98,.34);color:#9ed8ff}
.records-table :deep(.el-table td.el-table__cell){border-bottom:1px dashed rgba(111,166,205,.25)}
.records-table :deep(.el-table .cell){line-height:1.8}
.table-empty{padding:18px 0 24px;text-align:center;color:#97b8d5}
.table-empty__icon{margin:0 auto 8px;width:52px;height:52px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:1px solid rgba(111,204,255,.3);color:#7fd9ff;font-size:26px;box-shadow:0 0 20px rgba(111,204,255,.2)}
.table-empty p{margin:0 0 6px;font-size:15px;color:#c8e9ff}
.table-empty small{color:#88a9c4}
.timeline-title{margin:0 0 16px;font-size:16px;color:#d8ebff}
.timeline-note{margin:6px 0 0;color:#90a5bc;font-size:13px}
@media (max-width: 1200px){.stats-grid{grid-template-columns:repeat(2,1fr)}.board-grid{grid-template-columns:1fr}}
@media (max-width: 768px){.stats-grid{grid-template-columns:1fr}}
</style>
