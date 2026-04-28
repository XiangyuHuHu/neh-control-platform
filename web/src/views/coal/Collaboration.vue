<template>
  <div class="business-page">
    <section class="page-header">
      <div>
        <p class="page-tag">协同管理</p>
        <h1>待办协同与闭环跟踪</h1>
        <p class="page-desc">用于承接跨部门待办、工单流转、停送电协同、检维修配合和重要事项闭环。</p>
      </div>
      <div class="page-actions">
        <el-button @click="showShift = true">交接班事项</el-button>
        <el-button @click="showTicket = true">工单详情</el-button>
        <el-button type="primary">发起协同</el-button>
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
            <h2>待办中心</h2>
            <p>优先展示需要值班人员、机电、生产和调度联合处置的任务。</p>
          </div>
        </div>
        <div class="todo-list">
          <div v-for="item in todos" :key="item.title" class="todo-item">
            <div>
              <div class="todo-line">
                <strong>{{ item.title }}</strong>
                <span class="owner">{{ item.owner }}</span>
              </div>
              <p>{{ item.desc }}</p>
              <div class="todo-meta">
                <span>{{ item.category }}</span>
                <span>{{ item.deadline }}</span>
                <span>{{ item.status }}</span>
              </div>
            </div>
            <span :class="['priority-tag', item.level]">{{ item.levelText }}</span>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">
          <div>
            <h2>跨部门联动</h2>
            <p>展示当前需要生产、机修、电气、调度共同确认的事项。</p>
          </div>
        </div>
        <div class="link-grid">
          <div v-for="item in links" :key="item.title" class="link-card">
            <span>{{ item.title }}</span>
            <strong>{{ item.value }}</strong>
            <small>{{ item.note }}</small>
          </div>
        </div>
      </article>

      <article class="panel panel--wide">
        <div class="panel-head">
          <div>
            <h2>协同事项清单</h2>
            <p>用于现场值守时统一查看事项来源、责任人、当前阶段和闭环结果。</p>
          </div>
        </div>
        <el-table :data="taskRows" class="data-table">
          <el-table-column prop="taskNo" label="事项编号" width="140" />
          <el-table-column prop="title" label="事项名称" min-width="180" />
          <el-table-column prop="source" label="来源" width="120" />
          <el-table-column prop="departments" label="参与部门" min-width="180" />
          <el-table-column prop="owner" label="牵头人" width="120" />
          <el-table-column prop="progress" label="当前进度" width="120" />
          <el-table-column prop="deadline" label="截止时间" width="140" />
          <el-table-column prop="result" label="闭环结果" min-width="160" />
        </el-table>
      </article>
    </section>

    <el-dialog v-model="showShift" title="交接班协同重点" width="560px">
      <div class="dialog-grid">
        <div class="dialog-card">
          <span>当前重点</span>
          <strong>停送电确认 / 备件锁定 / 工艺切换</strong>
          <small>建议交接班记录和调度日志联动，避免事项断档。</small>
        </div>
        <div class="dialog-card">
          <span>建议字段</span>
          <strong>责任班组 / 协同部门 / 计划完成时间</strong>
          <small>后续可与待办、审批、短信或企业微信提醒联动。</small>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showTicket" title="工单协同详情" width="560px">
      <div class="dialog-grid">
        <div class="dialog-card">
          <span>当前工单</span>
          <strong>WO-20260425-017 离心机振动排查</strong>
          <small>已通知机修、电气、生产值班三方确认停机窗口。</small>
        </div>
        <div class="dialog-card">
          <span>下一动作</span>
          <strong>15 分钟内完成检修票确认</strong>
          <small>完成后同步更新调度日志和设备维修台账。</small>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showShift = ref(false)
const showTicket = ref(false)

const kpis = [
  { label: '待办事项', value: '18 项', note: '高优先级 4 项' },
  { label: '跨部门协同', value: '6 项', note: '生产、机修、电气联动' },
  { label: '今日闭环', value: '11 项', note: '闭环率 84.6%' },
  { label: '超时风险', value: '2 项', note: '均已提醒责任人' },
]

const todos = [
  { title: '311 离心机振动排查', owner: '机修班', desc: '需与生产值班确认停机窗口，并由电气确认隔离。', category: '检维修协同', deadline: '今日 23:00', status: '处理中', level: 'danger', levelText: '高优先级' },
  { title: '402 压滤机滤布领料审批', owner: '仓储+压滤岗位', desc: '备件库存不足，需同步采购计划和本班领用。', category: '备件协同', deadline: '今日 18:30', status: '待确认', level: 'warn', levelText: '需跟进' },
  { title: '中煤工艺切换准备', owner: '调度室', desc: '涉及生产、化验和加药岗位的参数切换。', category: '工艺协同', deadline: '明日 07:30', status: '待发布', level: 'info', levelText: '计划中' },
]

const links = [
  { title: '待确认停送电', value: '2 项', note: '均需调度+电气双签' },
  { title: '跨班交接事项', value: '5 项', note: '已纳入交接班重点' },
  { title: '工单协同中', value: '7 单', note: '其中 3 单关联设备预警' },
]

const taskRows = [
  { taskNo: 'XT-20260425-001', title: '311 离心机振动排查', source: '设备预警', departments: '机修、电气、生产', owner: '赵凯', progress: '检修票确认中', deadline: '2026-04-25 23:00', result: '待闭环' },
  { taskNo: 'XT-20260425-002', title: '402 滤布低库存补货', source: '备件预警', departments: '仓储、机修、采购', owner: '孙磊', progress: '待审批', deadline: '2026-04-25 18:30', result: '待闭环' },
  { taskNo: 'XT-20260425-003', title: '中煤工艺切换通知', source: '调度计划', departments: '调度、生产、化验', owner: '李静', progress: '已下发', deadline: '2026-04-26 07:30', result: '待执行' },
  { taskNo: 'XT-20260425-004', title: '夜班巡检异常复核', source: '巡检记录', departments: '巡检、生产、机修', owner: '王强', progress: '复核完成', deadline: '2026-04-25 16:00', result: '已闭环' },
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
.content-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:16px}
.panel{padding:24px}
.panel--wide{grid-column:1 / -1}
.panel-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:18px}
.todo-list,.dialog-grid{display:grid;gap:14px}
.todo-item{display:flex;justify-content:space-between;gap:16px;padding:16px;border-radius:14px;background:rgba(13,25,38,.82)}
.todo-item p{margin:8px 0 0;color:rgba(227,239,250,.64)}
.todo-line{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.owner{padding:3px 8px;border-radius:999px;background:rgba(69,203,255,.12);color:#7ad7ff;font-size:12px}
.todo-meta{display:flex;gap:12px;margin-top:10px;color:#74d9ff;font-size:13px;flex-wrap:wrap}
.priority-tag{height:fit-content;padding:5px 10px;border-radius:999px;font-size:12px;font-weight:600}
.priority-tag.danger{background:rgba(255,109,109,.14);color:#ff8181}
.priority-tag.warn{background:rgba(255,200,87,.16);color:#ffc857}
.priority-tag.info{background:rgba(69,203,255,.14);color:#71d5ff}
.link-grid{display:grid;gap:14px}
.link-card{padding:18px;border-radius:14px;background:rgba(13,25,38,.82)}
.link-card span{display:block;color:rgba(227,239,250,.66)}
.link-card strong{display:block;margin-top:10px;font-size:26px}
.link-card small{display:block;margin-top:8px;color:#74d9ff}
.dialog-card{padding:18px}
.dialog-card span{display:block;color:#91b6d0;font-size:13px}
.dialog-card strong{display:block;margin-top:10px;font-size:18px}
.dialog-card small{display:block;margin-top:10px;color:#6fcfff;line-height:1.7}
@media (max-width: 1200px){.kpi-grid,.content-grid{grid-template-columns:1fr}}
</style>
