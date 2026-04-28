import { createRouter, createWebHistory } from 'vue-router'

const extensionRoutes = [
  { path: '/coal/process-check', name: 'CoalProcessCheck', moduleKey: 'process-check' },
  { path: '/coal/material-tracking', name: 'CoalMaterialTracking', moduleKey: 'material-tracking' },
  { path: '/coal/medium', name: 'CoalMedium', moduleKey: 'medium' },
  { path: '/coal/reagent', name: 'CoalReagent', moduleKey: 'reagent' },
  { path: '/coal/water', name: 'CoalWater', moduleKey: 'water' },
  { path: '/coal/power', name: 'CoalPower', moduleKey: 'power' },
  { path: '/coal/grease', name: 'CoalGrease', moduleKey: 'grease' },
  { path: '/coal/air', name: 'CoalAir', moduleKey: 'air' },
]

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/coal',
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue'),
      children: [
        { path: 'user', name: 'User', component: () => import('../views/User.vue') },
        { path: 'device', name: 'Device', component: () => import('../views/Device.vue') },
        { path: 'monitor', name: 'Monitor', component: () => import('../views/Monitor.vue') },
        { path: 'alarm', name: 'Alarm', component: () => import('../views/Alarm.vue') },
        { path: 'report', name: 'Report', component: () => import('../views/Report.vue') },
        { path: 'workorder', name: 'WorkOrder', component: () => import('../views/WorkOrder.vue') },
      ],
    },
    {
      path: '/coal',
      name: 'CoalHome',
      component: () => import('../views/coal/Home.vue'),
    },
    {
      path: '/coal/dashboard',
      name: 'CoalDashboard',
      component: () => import('../views/coal/Dashboard.vue'),
    },
    {
      path: '/coal/dashboard-screen',
      name: 'CoalDashboardScreen',
      component: () => import('../views/coal/DashboardScreen.vue'),
    },
    {
      path: '/coal/production',
      name: 'CoalProduction',
      component: () => import('../views/coal/Production.vue'),
    },
    {
      path: '/coal/production-operation',
      name: 'CoalProductionOperation',
      component: () => import('../views/coal/ProductionOperation.vue'),
    },
    {
      path: '/coal/process-flow',
      name: 'CoalProcessFlow',
      component: () => import('../views/coal/ProcessFlow.vue'),
    },
    {
      path: '/coal/safety-health',
      name: 'CoalSafetyHealth',
      component: () => import('../views/coal/SafetyHealth.vue'),
    },
    {
      path: '/coal/planning',
      name: 'CoalPlanning',
      component: () => import('../views/coal/Planning.vue'),
    },
    {
      path: '/coal/equipment',
      name: 'CoalEquipment',
      component: () => import('../views/coal/Equipment.vue'),
    },
    {
      path: '/coal/equipment-screen',
      name: 'CoalEquipmentScreen',
      component: () => import('../views/coal/EquipmentScreen.vue'),
    },
    {
      path: '/coal/quality',
      name: 'CoalQuality',
      component: () => import('../views/coal/Quality.vue'),
    },
    {
      path: '/coal/quality-entry',
      name: 'CoalQualityEntry',
      component: () => import('../views/coal/QualityEntry.vue'),
    },
    {
      path: '/coal/storage',
      name: 'CoalStorage',
      component: () => import('../views/coal/Storage.vue'),
    },
    {
      path: '/coal/energy',
      name: 'CoalEnergy',
      component: () => import('../views/coal/Energy.vue'),
    },
    {
      path: '/coal/spare-parts',
      name: 'CoalSpareParts',
      component: () => import('../views/coal/SpareParts.vue'),
    },
    {
      path: '/coal/collaboration',
      name: 'CoalCollaboration',
      component: () => import('../views/coal/Collaboration.vue'),
    },
    {
      path: '/coal/energy-screen',
      name: 'CoalEnergyScreen',
      redirect: '/coal/energy',
    },
    {
      path: '/coal/report',
      name: 'CoalReport',
      component: () => import('../views/coal/Report.vue'),
    },
    {
      path: '/coal/settings',
      name: 'CoalSettings',
      component: () => import('../views/coal/Settings.vue'),
    },
    {
      path: '/coal/dispatch',
      name: 'CoalDispatch',
      component: () => import('../views/coal/Dispatch.vue'),
    },
    {
      path: '/coal/dispatch-log',
      name: 'CoalDispatchLog',
      component: () => import('../views/coal/DispatchLog.vue'),
    },
    {
      path: '/coal/power-operation',
      name: 'CoalPowerOperation',
      component: () => import('../views/coal/PowerOperation.vue'),
    },
    {
      path: '/coal/decision',
      name: 'CoalDecision',
      component: () => import('../views/coal/Decision.vue'),
    },
    {
      path: '/coal/model-analysis',
      name: 'CoalModelAnalysis',
      component: () => import('../views/coal/ModelAnalysis.vue'),
    },
    {
      path: '/coal/monitor',
      name: 'CoalMonitor',
      component: () => import('../views/coal/Monitor.vue'),
    },
    {
      path: '/coal/data-governance',
      name: 'CoalDataGovernance',
      component: () => import('../views/coal/DataGovernance.vue'),
    },
    {
      path: '/coal/data-integration',
      name: 'CoalDataIntegration',
      component: () => import('../views/coal/DataIntegration.vue'),
    },
    {
      path: '/coal/data-access',
      name: 'CoalDataAccess',
      component: () => import('../views/coal/DataAccess.vue'),
    },
    {
      path: '/coal/sales',
      name: 'CoalSales',
      component: () => import('../views/coal/Sales.vue'),
    },
    {
      path: '/coal/quality-report',
      name: 'CoalQualityReport',
      component: () => import('../views/coal/QualityReportCenter.vue'),
    },
    {
      path: '/coal/mechanical',
      name: 'CoalMechanical',
      component: () => import('../views/coal/Mechanical.vue'),
    },
    {
      path: '/coal/smart-density',
      name: 'CoalSmartDensity',
      component: () => import('../views/coal/SmartDensity.vue'),
    },
    {
      path: '/coal/smart-reagent',
      name: 'CoalSmartReagent',
      component: () => import('../views/coal/SmartReagent.vue'),
    },
    {
      path: '/coal/shift-schedule',
      name: 'CoalShiftSchedule',
      component: () => import('../views/coal/ShiftSchedule.vue'),
    },
    ...extensionRoutes.map((item) => ({
      path: item.path,
      name: item.name,
      component: () => import('../views/coal/ExtensionModulePage.vue'),
      meta: { moduleKey: item.moduleKey },
    })),
  ],
})

export default router
