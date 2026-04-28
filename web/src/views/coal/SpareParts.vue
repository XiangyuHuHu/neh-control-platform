<template>
  <div class="business-page">
    <section class="page-header">
      <div>
        <p class="page-tag">备品备件管理</p>
        <h1>备件台账与库存协同</h1>
        <p class="page-desc">用于管理关键备件台账、库存预警、领用记录和更换计划，支撑机电管理与检维修闭环。</p>
      </div>
      <div class="page-actions">
        <el-button @click="selectedStatus = '全部'">查看全部</el-button>
        <el-button @click="showInbound = true">入库登记</el-button>
        <el-button type="primary" @click="showIssue = true">领用登记</el-button>
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
            <h2>关键预警</h2>
            <p>聚焦低库存、待更换和高价值备件，便于现场优先协调。</p>
          </div>
          <el-radio-group v-model="selectedStatus" size="small">
            <el-radio-button label="全部" />
            <el-radio-button label="库存不足" />
            <el-radio-button label="待更换" />
          </el-radio-group>
        </div>
        <div class="warning-list">
          <div v-for="item in filteredWarnings" :key="item.title" class="warning-item">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.desc }}</p>
            </div>
            <span :class="['warning-tag', item.level]">{{ item.tag }}</span>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>本班领用动态</h2>
            <p>查看当前班次的领用、退库和待确认事项。</p>
          </div>
        </div>
        <div class="flow-list">
          <div v-for="item in issueFlows" :key="item.partNo + item.time" class="flow-item">
            <strong>{{ item.partName }}</strong>
            <p>{{ item.partNo }} · {{ item.department }}</p>
            <div class="flow-meta">
              <span>{{ item.action }}</span>
              <span>{{ item.quantity }}</span>
              <span>{{ item.time }}</span>
            </div>
          </div>
        </div>
      </article>

      <article class="panel panel--wide">
        <div class="panel-head">
          <div>
            <h2>备件库存台账</h2>
            <p>覆盖编码、规格、所属设备、库存、安全库存和状态。</p>
          </div>
        </div>
        <el-table :data="ledgerRows" class="data-table">
          <el-table-column prop="partNo" label="备件编号" width="140" />
          <el-table-column prop="partName" label="备件名称" min-width="180" />
          <el-table-column prop="specification" label="规格型号" min-width="160" />
          <el-table-column prop="deviceName" label="所属设备" min-width="180" />
          <el-table-column prop="stock" label="库存" width="90" />
          <el-table-column prop="safety" label="安全库存" width="110" />
          <el-table-column prop="location" label="库位" width="120" />
          <el-table-column prop="nextReplaceDate" label="下次更换" width="120" />
          <el-table-column prop="status" label="状态" width="110" />
        </el-table>
      </article>
    </section>

    <el-dialog v-model="showInbound" title="备件入库登记" width="560px">
      <div class="dialog-grid">
        <div class="dialog-card">
          <span>建议字段</span>
          <strong>备件编号 / 名称 / 规格 / 数量</strong>
          <small>入库前建议同步设备归属、供应商与库位。</small>
        </div>
        <div class="dialog-card">
          <span>现场确认</span>
          <strong>批次 / 单价 / 到货日期</strong>
          <small>如果要做成本分析，建议把入库单号也一起补齐。</small>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showIssue" title="备件领用登记" width="560px">
      <div class="dialog-grid">
        <div class="dialog-card">
          <span>建议字段</span>
          <strong>领用部门 / 设备 / 数量 / 工单号</strong>
          <small>现场联调时建议把工单号和维修记录关联起来。</small>
        </div>
        <div class="dialog-card">
          <span>闭环要求</span>
          <strong>领用人 / 审核人 / 退库状态</strong>
          <small>后续可和协同管理联动形成待办流程。</small>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const showInbound = ref(false)
const showIssue = ref(false)
const selectedStatus = ref('全部')

const kpis = [
  { label: '备件总数', value: '326 项', note: '关键备件 48 项' },
  { label: '库存不足', value: '7 项', note: '其中 3 项需本周补货' },
  { label: '本班领用', value: '12 单', note: '机修班 7 单，生产班 5 单' },
  { label: '待更换件', value: '5 项', note: '已关联设备寿命计划' },
]

const warnings = [
  { title: '压滤机滤布库存不足', desc: 'PF-402 关键滤布当前库存 2 件，低于安全库存 5 件。', level: 'danger', tag: '库存不足', status: '库存不足' },
  { title: '离心机轴承待更换', desc: 'LC-311 轴承预计 3 天内到期，建议提前领料锁定。', level: 'warn', tag: '待更换', status: '待更换' },
  { title: '高价值备件待确认', desc: '进口密封组件单价较高，建议入库后双人复核。', level: 'info', tag: '重点关注', status: '全部' },
]

const filteredWarnings = computed(() =>
  selectedStatus.value === '全部'
    ? warnings
    : warnings.filter((item) => item.status === selectedStatus.value),
)

const issueFlows = [
  { partName: '离心机主轴轴承', partNo: 'SP-311-002', department: '机修班', action: '领用', quantity: '2 套', time: '08:20' },
  { partName: '压滤机滤布', partNo: 'SP-402-015', department: '压滤岗位', action: '待审核', quantity: '4 件', time: '09:05' },
  { partName: '皮带托辊', partNo: 'SP-101-008', department: '生产一班', action: '退库', quantity: '6 件', time: '10:12' },
]

const ledgerRows = [
  { partNo: 'SP-311-002', partName: '离心机主轴轴承', specification: 'SKF-23122', deviceName: '311 中煤卧式离心机', stock: 4, safety: 3, location: 'A-03', nextReplaceDate: '2026-05-03', status: '正常' },
  { partNo: 'SP-402-015', partName: '压滤机滤布', specification: 'PF-1200', deviceName: '402 精煤压滤机', stock: 2, safety: 5, location: 'B-11', nextReplaceDate: '2026-04-29', status: '库存不足' },
  { partNo: 'SP-101-008', partName: '皮带托辊', specification: 'TD75-108', deviceName: '101 原煤皮带机', stock: 36, safety: 20, location: 'C-05', nextReplaceDate: '2026-06-10', status: '正常' },
  { partNo: 'SP-203-006', partName: '加药泵密封组件', specification: 'P203-MF', deviceName: 'P-203 絮凝剂泵', stock: 1, safety: 2, location: 'A-09', nextReplaceDate: '2026-05-15', status: '重点关注' },
]
</script>

<style scoped>
.business-page{min-height:100vh;padding:24px 20px 28px;background:#091019;color:#eef6ff}
.page-header,.kpi-grid,.content-grid{width:min(100%,1680px);margin:0 auto 16px}
.page-header{display:flex;justify-content:space-between;gap:24px;padding:28px 30px;border:1px solid rgba(96,183,255,.12);border-radius:20px;background:rgba(8,19,30,.92)}
.page-tag{margin:0 0 10px;color:#7ecfff;font-size:12px;letter-spacing:.12em}
.page-header h1,.panel-head h2{margin:0}
.page-desc,.panel-head p{margin:10px 0 0;color:rgba(227,239,250,.68);line-height:1.7}
.page-actions{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.kpi-card,.panel,.dialog-card{border:1px solid rgba(96,183,255,.12);border-radius:18px;background:rgba(8,19,30,.92)}
.kpi-card{padding:20px}
.kpi-card span{display:block;color:rgba(227,239,250,.62);font-size:13px}
.kpi-card strong{display:block;margin-top:14px;font-size:34px;color:#f3faff}
.kpi-card small{display:block;margin-top:10px;color:#67d8ff}
.content-grid{display:grid;grid-template-columns:1fr .9fr;gap:16px}
.panel{padding:24px}
.panel--wide{grid-column:1 / -1}
.panel-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:18px}
.warning-list,.flow-list{display:grid;gap:14px}
.warning-item,.flow-item{display:flex;justify-content:space-between;gap:16px;padding:16px;border-radius:14px;background:rgba(13,25,38,.82)}
.warning-item p,.flow-item p{margin:8px 0 0;color:rgba(227,239,250,.64)}
.warning-tag{height:fit-content;padding:5px 10px;border-radius:999px;font-size:12px;font-weight:600}
.warning-tag.danger{background:rgba(255,109,109,.14);color:#ff8181}
.warning-tag.warn{background:rgba(255,200,87,.16);color:#ffc857}
.warning-tag.info{background:rgba(69,203,255,.14);color:#71d5ff}
.flow-meta{display:flex;gap:12px;margin-top:10px;color:#74d9ff;font-size:13px;flex-wrap:wrap}
.dialog-grid{display:grid;gap:16px}
.dialog-card{padding:18px}
.dialog-card span{display:block;color:#91b6d0;font-size:13px}
.dialog-card strong{display:block;margin-top:10px;font-size:18px}
.dialog-card small{display:block;margin-top:10px;color:#6fcfff;line-height:1.7}
@media (max-width: 1200px){.kpi-grid,.content-grid{grid-template-columns:1fr}}
</style>
