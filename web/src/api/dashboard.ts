import { ElMessage } from 'element-plus'
import { buildJsonHeaders } from './http'

const request = async <T>(path: string): Promise<T> => {
  const response = await fetch(path, {
    headers: buildJsonHeaders({ Accept: 'application/json' }),
  })
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      ElMessage.error('未登录或权限不足，请重新登录（若已开启 API 认证）')
    } else {
      ElMessage.error(`大屏数据请求失败（${response.status}）`)
    }
    throw new Error(`Dashboard request failed: ${response.status}`)
  }
  return response.json()
}

export type DashboardOverview = {
  totalDevices: number
  runningDevices: number
  totalAlarms: number
  unhandledAlarms: number
  pendingWorkOrders: number
}

export const getDashboardOverview = () => request<DashboardOverview>('/api/dashboard/overview')

export const getDashboardProductionStats = () =>
  request<{ todayProduction: number; weekProduction: number; monthProduction: number }>('/api/dashboard/production-stats')

export const getDashboardEnergyStats = () =>
  request<{ todayEnergy: number; weekEnergy: number; monthEnergy: number }>('/api/dashboard/energy-stats')

export const getDashboardRealTimeData = () => request<{ deviceData: unknown[] }>('/api/dashboard/real-time-data')

export type PortalMetricItem = {
  label: string
  value: string
  note: string
}

export const getPortalMetrics = () =>
  request<{ metrics: PortalMetricItem[]; generatedAt: string }>('/api/dashboard/portal-metrics')
