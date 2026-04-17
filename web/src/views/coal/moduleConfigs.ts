export type ModuleMetric = {
  label: string
  value: string | number
  note: string
  unit?: string
  status?: 'normal' | 'warning' | 'danger'
  trend?: 'up' | 'down' | 'flat'
  tagId?: string
  threshold?: {
    warning?: number
    critical?: number
    direction?: 'higher' | 'lower'
  }
  refreshRate?: number
}

export type ModuleRow = Record<string, string>

export type ModuleConfig = {
  key: string
  title: string
  subtitle: string
  badge: string
  scenario: string
  metrics: ModuleMetric[]
  highlights: string[]
  chartTitle: string
  chartSeries: { label: string; value: number; color: string }[]
  tableTitle: string
  columns: { key: string; label: string }[]
  rows: ModuleRow[]
  refreshRate?: number
}

export const moduleConfigs: Record<string, ModuleConfig> = {
  'process-check': {
    key: 'process-check',
    title: '生产技术检查',
    subtitle: '覆盖生产记录、实验记录、工艺管理和材料消耗跟踪，形成值班检查与技术稽核闭环。',
    badge: '生产技术检查',
    scenario: '班组技术检查 / 工艺稽核 / 实验记录联动',
    metrics: [
      { label: '当日检查项', value: 28, unit: '项', note: '已完成 23 项', status: 'normal', trend: 'flat', tagId: 'coal.process.check.daily_count' },
      { label: '异常整改', value: 5, unit: '条', note: '2 条待复核', status: 'warning', trend: 'up', tagId: 'coal.process.check.rectify_pending', threshold: { warning: 4, critical: 8, direction: 'higher' }, refreshRate: 30 },
      { label: '工艺偏差', value: 1.8, unit: '%', note: '较昨日下降', status: 'normal', trend: 'down', tagId: 'coal.process.deviation.rate', threshold: { warning: 2.5, critical: 3.5, direction: 'higher' }, refreshRate: 30 },
    ],
    highlights: ['生产记录检查', '实验记录归档', '工艺制度执行', '材料消耗复核'],
    chartTitle: '检查项完成率',
    chartSeries: [
      { label: '记录类', value: 86, color: '#44b6ff' },
      { label: '工艺类', value: 72, color: '#11d6a4' },
      { label: '材料类', value: 68, color: '#ffc857' },
      { label: '整改类', value: 58, color: '#ff7b72' },
    ],
    tableTitle: '检查任务台账',
    columns: [
      { key: 'name', label: '检查项' },
      { key: 'owner', label: '责任人' },
      { key: 'status', label: '状态' },
      { key: 'deadline', label: '完成时限' },
    ],
    rows: [
      { name: '重介密度校验', owner: '工艺工程师', status: '进行中', deadline: '今日 18:00' },
      { name: '浮选药剂用量复核', owner: '技术员', status: '待复核', deadline: '今日 20:00' },
      { name: '班组实验记录抽查', owner: '质检员', status: '已完成', deadline: '已归档' },
    ],
    refreshRate: 30,
  },
  'material-tracking': {
    key: 'material-tracking',
    title: '原材料跟踪',
    subtitle: '建立原材料入库、领用、消耗与库存的全过程追踪台账，支持入出库协同。',
    badge: '原材料跟踪',
    scenario: '原材料追踪 / 库存流转 / 消耗闭环',
    metrics: [
      { label: '库存批次', value: '14 批', note: '可追溯率 100%' },
      { label: '当班领用', value: '38 单', note: '自动归集' },
      { label: '异常库存', value: '2 批', note: '待复盘' },
    ],
    highlights: ['入库记录', '领料登记', '出库追踪', '库存异常提示'],
    chartTitle: '材料流转占比',
    chartSeries: [
      { label: '入库', value: 32, color: '#44b6ff' },
      { label: '领用', value: 24, color: '#11d6a4' },
      { label: '库存', value: 28, color: '#ffc857' },
      { label: '待复盘', value: 16, color: '#ff7b72' },
    ],
    tableTitle: '原材料追踪台账',
    columns: [
      { key: 'batch', label: '批次号' },
      { key: 'material', label: '物料名称' },
      { key: 'stage', label: '当前环节' },
      { key: 'owner', label: '责任岗位' },
    ],
    rows: [
      { batch: 'RM-240801', material: '絮凝剂', stage: '已领用', owner: '浮选岗位' },
      { batch: 'RM-240802', material: '捕收剂', stage: '在库', owner: '材料仓库' },
      { batch: 'RM-240803', material: '润滑脂', stage: '异常复盘', owner: '机修班' },
    ],
  },
  'quality-report': {
    key: 'quality-report',
    title: '产品质量报表',
    subtitle: '围绕日报、周报、月报输出质量结果与趋势，为质量稳定分析和考核提供依据。',
    badge: '质量报表',
    scenario: '日报 / 周报 / 月报生成',
    metrics: [
      { label: '日报生成', value: '1 次', note: '自动出表' },
      { label: '周报草稿', value: '2 份', note: '待审核' },
      { label: '月报指标', value: '96.8%', note: '质量达标率' },
    ],
    highlights: ['日报模板', '周报汇总', '月报指标', '质量异常追踪'],
    chartTitle: '报表指标覆盖率',
    chartSeries: [
      { label: '灰分', value: 94, color: '#44b6ff' },
      { label: '水分', value: 90, color: '#11d6a4' },
      { label: '硫分', value: 82, color: '#ffc857' },
      { label: '热值', value: 88, color: '#ff7b72' },
    ],
    tableTitle: '质量报表任务',
    columns: [
      { key: 'report', label: '报表类型' },
      { key: 'cycle', label: '周期' },
      { key: 'status', label: '状态' },
      { key: 'owner', label: '负责人' },
    ],
    rows: [
      { report: '商品煤日报', cycle: '日', status: '已生成', owner: '质量科' },
      { report: '灰分周报', cycle: '周', status: '待审核', owner: '质检主任' },
      { report: '月度质量汇总', cycle: '月', status: '编制中', owner: '技术部' },
    ],
  },
  medium: {
    key: 'medium',
    title: '介质消耗管理',
    subtitle: '统计介质消耗与历史变化，支持班报月报生成、异常提醒和定制化统计。',
    badge: '介质消耗',
    scenario: '介质台账 / 异常提醒 / 消耗统计',
    metrics: [
      { label: '当班介耗', value: '0.82 kg/t', note: '低于目标 3%' },
      { label: '月累计', value: '18.4 t', note: '自动归档' },
      { label: '异常提醒', value: '1 条', note: '待确认' },
    ],
    highlights: ['介质班报', '介质月报', '异常提醒', '历史对比'],
    chartTitle: '介质消耗对比',
    chartSeries: [
      { label: '班报', value: 76, color: '#44b6ff' },
      { label: '月报', value: 62, color: '#11d6a4' },
      { label: '异常', value: 18, color: '#ff7b72' },
    ],
    tableTitle: '介质消耗记录',
    columns: [
      { key: 'shift', label: '班次' },
      { key: 'dosage', label: '介耗' },
      { key: 'compare', label: '对标情况' },
      { key: 'remark', label: '备注' },
    ],
    rows: [
      { shift: '白班', dosage: '0.79 kg/t', compare: '优于目标', remark: '稳定' },
      { shift: '夜班', dosage: '0.84 kg/t', compare: '轻微波动', remark: '复核中' },
      { shift: '检修班', dosage: '0.91 kg/t', compare: '异常', remark: '需分析' },
    ],
  },
  reagent: {
    key: 'reagent',
    title: '药剂消耗管理',
    subtitle: '实时监控药剂用量和单耗，支持异常推送、时段对比与统计报表输出。',
    badge: '药剂消耗',
    scenario: '药剂监控 / 单耗统计 / 推送提醒',
    metrics: [
      { label: '实时药剂量', value: '186 kg', note: '在线监控' },
      { label: '单耗水平', value: '0.42 kg/t', note: '较上周下降' },
      { label: '异常波动', value: '2 次', note: '已通知巡检' },
    ],
    highlights: ['单耗监测', '时段对比', '异常推送', '统计报表'],
    chartTitle: '药剂单耗趋势',
    chartSeries: [
      { label: '上午', value: 64, color: '#44b6ff' },
      { label: '下午', value: 71, color: '#11d6a4' },
      { label: '夜班', value: 59, color: '#ffc857' },
    ],
    tableTitle: '药剂用量记录',
    columns: [
      { key: 'agent', label: '药剂名称' },
      { key: 'usage', label: '用量' },
      { key: 'unitCost', label: '单耗' },
      { key: 'status', label: '状态' },
    ],
    rows: [
      { agent: '捕收剂', usage: '72 kg', unitCost: '0.18 kg/t', status: '正常' },
      { agent: '起泡剂', usage: '54 kg', unitCost: '0.13 kg/t', status: '正常' },
      { agent: '絮凝剂', usage: '60 kg', unitCost: '0.11 kg/t', status: '偏高' },
    ],
  },
  water: {
    key: 'water',
    title: '水消耗管理',
    subtitle: '对生产、生活用水进行在线采集、实时汇总、异常提示和历史统计。',
    badge: '水消耗',
    scenario: '在线采集 / 实时汇总 / 异常提示',
    metrics: [
      { label: '当日补水量', value: '1,260 m3', note: '自动汇总' },
      { label: '回用率', value: '78%', note: '较昨日提升' },
      { label: '异常点位', value: '1 个', note: '等待处理' },
    ],
    highlights: ['补水汇总', '历史统计', '异常提示', '定制报表'],
    chartTitle: '用水结构',
    chartSeries: [
      { label: '生产用水', value: 74, color: '#44b6ff' },
      { label: '生活用水', value: 18, color: '#11d6a4' },
      { label: '回收循环', value: 66, color: '#ffc857' },
    ],
    tableTitle: '用水监测记录',
    columns: [
      { key: 'zone', label: '区域' },
      { key: 'flow', label: '流量' },
      { key: 'status', label: '状态' },
      { key: 'remark', label: '备注' },
    ],
    rows: [
      { zone: '主洗车间', flow: '680 m3', status: '正常', remark: '循环稳定' },
      { zone: '压滤区', flow: '420 m3', status: '关注', remark: '波动偏大' },
      { zone: '生活区', flow: '160 m3', status: '正常', remark: '平稳' },
    ],
  },
  power: {
    key: 'power',
    title: '电力消耗管理',
    subtitle: '查看供配电系统状态、电耗历史和异常告警，输出台账与月报。',
    badge: '电力消耗',
    scenario: '供电状态 / 电耗统计 / 异常报警',
    metrics: [
      { label: '实时负荷', value: '8.4 MW', note: '当前厂区总负荷' },
      { label: '月累计电耗', value: '164 万kWh', note: '已生成月报' },
      { label: '异常告警', value: '2 条', note: '待派发' },
    ],
    highlights: ['配电状态', '历史电耗', '自动报警', '月报台账'],
    chartTitle: '电耗结构',
    chartSeries: [
      { label: '破碎系统', value: 82, color: '#44b6ff' },
      { label: '洗选系统', value: 74, color: '#11d6a4' },
      { label: '脱水系统', value: 58, color: '#ffc857' },
      { label: '辅助系统', value: 36, color: '#ff7b72' },
    ],
    tableTitle: '电耗监控记录',
    columns: [
      { key: 'system', label: '系统' },
      { key: 'load', label: '负荷' },
      { key: 'energy', label: '电耗' },
      { key: 'status', label: '状态' },
    ],
    rows: [
      { system: '破碎系统', load: '2.3 MW', energy: '42,000 kWh', status: '正常' },
      { system: '洗选系统', load: '3.1 MW', energy: '66,000 kWh', status: '正常' },
      { system: '高压配电', load: '0.8 MW', energy: '14,000 kWh', status: '告警' },
    ],
  },
  grease: {
    key: 'grease',
    title: '油脂消耗管理',
    subtitle: '统计润滑油脂消耗，支持班报月报、异常提醒与领用对比。',
    badge: '油脂消耗',
    scenario: '润滑管理 / 领用统计 / 异常提醒',
    metrics: [
      { label: '本周领用', value: '420 L', note: '机修班主导' },
      { label: '异常设备', value: '1 台', note: '润滑偏高' },
      { label: '月报进度', value: '87%', note: '待补录' },
    ],
    highlights: ['班报输出', '领用对比', '异常提醒', '库存联动'],
    chartTitle: '油脂领用分布',
    chartSeries: [
      { label: '破碎机', value: 68, color: '#44b6ff' },
      { label: '离心机', value: 51, color: '#11d6a4' },
      { label: '输送带', value: 39, color: '#ffc857' },
    ],
    tableTitle: '油脂领用记录',
    columns: [
      { key: 'device', label: '设备' },
      { key: 'type', label: '油脂类型' },
      { key: 'amount', label: '领用量' },
      { key: 'status', label: '状态' },
    ],
    rows: [
      { device: 'CR-01 破碎机', type: '锂基脂', amount: '120 L', status: '正常' },
      { device: '402 离心机', type: '齿轮油', amount: '88 L', status: '关注' },
      { device: '101 输送机', type: '润滑脂', amount: '64 L', status: '正常' },
    ],
  },
  air: {
    key: 'air',
    title: '用风量管理',
    subtitle: '采集压风机流量数据，统计用风情况并结合循环次数计算单耗。',
    badge: '用风量',
    scenario: '流量采集 / 单耗分析 / 考核依据',
    metrics: [
      { label: '实时风量', value: '12,400 m3/h', note: '稳定输出' },
      { label: '单耗水平', value: '0.38 m3/t', note: '接近最优' },
      { label: '考核偏差', value: '-1.6%', note: '优于基准' },
    ],
    highlights: ['风量统计', '班报输出', '单耗测算', '考核支撑'],
    chartTitle: '用风负荷分布',
    chartSeries: [
      { label: '主压风机', value: 88, color: '#44b6ff' },
      { label: '浮选系统', value: 62, color: '#11d6a4' },
      { label: '辅助风路', value: 34, color: '#ffc857' },
    ],
    tableTitle: '风量记录',
    columns: [
      { key: 'line', label: '风路' },
      { key: 'flow', label: '风量' },
      { key: 'consumption', label: '单耗' },
      { key: 'remark', label: '备注' },
    ],
    rows: [
      { line: '主风路 A', flow: '6,400 m3/h', consumption: '0.16 m3/t', remark: '稳定' },
      { line: '浮选风路 B', flow: '4,800 m3/h', consumption: '0.14 m3/t', remark: '正常' },
      { line: '辅助风路 C', flow: '1,200 m3/h', consumption: '0.08 m3/t', remark: '低负荷' },
    ],
  },
  planning: {
    key: 'planning',
    title: '生产计划统计',
    subtitle: '围绕原煤入选量、精煤量、矸石量及主要报表，完成计划统计展示。',
    badge: '生产计划统计',
    scenario: '计划统计 / 指标汇总 / 报表输出',
    metrics: [
      { label: '原煤入选量', value: '12,580 吨', note: '完成率 87.5%' },
      { label: '精煤量', value: '7,240 吨', note: '稳定输出' },
      { label: '主要报表', value: '3 张', note: '日报 / 月报 / 库存报表' },
    ],
    highlights: ['计划指标', '日报统计', '月报统计', '库存报表'],
    chartTitle: '计划执行进度',
    chartSeries: [
      { label: '原煤', value: 88, color: '#44b6ff' },
      { label: '精煤', value: 82, color: '#11d6a4' },
      { label: '矸石', value: 74, color: '#ffc857' },
      { label: '药剂', value: 66, color: '#ff7b72' },
    ],
    tableTitle: '计划执行记录',
    columns: [
      { key: 'item', label: '指标项' },
      { key: 'plan', label: '计划值' },
      { key: 'actual', label: '实际值' },
      { key: 'rate', label: '完成率' },
    ],
    rows: [
      { item: '原煤入选', plan: '14,000 吨', actual: '12,580 吨', rate: '89.8%' },
      { item: '精煤产量', plan: '8,600 吨', actual: '7,240 吨', rate: '84.2%' },
      { item: '药剂消耗', plan: '520 kg', actual: '486 kg', rate: '93.5%' },
    ],
  },
  mechanical: {
    key: 'mechanical',
    title: '机电设备管理',
    subtitle: '建立设备运行档案、动态数据、问题发现与处置闭环，支撑机电管理。',
    badge: '机电设备管理',
    scenario: '设备档案 / 动态数据 / 问题闭环',
    metrics: [
      { label: '设备档案', value: '1,284 份', note: '全生命周期管理' },
      { label: '动态点位', value: '426 个', note: '持续采集' },
      { label: '待处理问题', value: '6 条', note: '3 条高优先级' },
    ],
    highlights: ['运行档案', '动态数据', '问题发现', '处置闭环'],
    chartTitle: '机电状态分布',
    chartSeries: [
      { label: '正常', value: 86, color: '#11d6a4' },
      { label: '检修', value: 22, color: '#ffc857' },
      { label: '告警', value: 10, color: '#ff7b72' },
    ],
    tableTitle: '机电问题清单',
    columns: [
      { key: 'device', label: '设备' },
      { key: 'issue', label: '问题描述' },
      { key: 'priority', label: '优先级' },
      { key: 'owner', label: '责任人' },
    ],
    rows: [
      { device: 'CR-01 破碎机', issue: '振动偏高', priority: '高', owner: '机修班' },
      { device: '402 离心机', issue: '滤网寿命接近阈值', priority: '中', owner: '点检员' },
      { device: '101 输送机', issue: '润滑补给待执行', priority: '低', owner: '运维组' },
    ],
  },
}

export const extensionModules = [
  { key: 'process-check', title: '生产技术检查' },
  { key: 'material-tracking', title: '原材料跟踪' },
  { key: 'quality-report', title: '质量报表' },
  { key: 'medium', title: '介质消耗' },
  { key: 'reagent', title: '药剂消耗' },
  { key: 'water', title: '水消耗' },
  { key: 'power', title: '电力消耗' },
  { key: 'grease', title: '油脂消耗' },
  { key: 'air', title: '用风量' },
  { key: 'planning', title: '生产计划统计' },
  { key: 'mechanical', title: '机电设备管理' },
]
