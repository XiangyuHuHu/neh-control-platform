import { ElMessage } from 'element-plus'
import { buildJsonHeaders } from './http'

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface IotTagDefinition {
  tagCode: string
  tagName: string
  sourceType: string
  sourcePath: string
  deviceCode: string
  deviceName: string
  areaCode: string
  dataType: string
  unit: string
  scanRate: number
  deadband: number
  qualityRule: string
  enabled: boolean
  remark: string
}

export interface IotRealtimeValue {
  tagCode: string
  value: number
  valueText: string
  dataType: string
  unit: string
  quality: string
  timestamp: string
  sourceTime: string
  deviceCode: string
  areaCode: string
  sourceType: string
}

export interface IotAlarmEvent {
  alarmId: string
  tagCode: string
  alarmCode: string
  alarmName: string
  alarmLevel: string
  alarmStatus: string
  currentValue: number | null
  thresholdValue: number | null
  unit: string
  deviceCode: string
  startTime: string
  ackTime: string | null
  recoverTime: string | null
  ackBy: string | null
  remark: string
}

export interface IotTagMapping {
  mappingId: string
  tagCode: string
  businessCode: string
  businessName: string
  sourcePath: string
  transformRule: string
  enabled: boolean
  remark: string
}

export interface IotTagMappingUpsertPayload {
  mappingId?: string
  tagCode: string
  businessCode: string
  businessName: string
  sourcePath: string
  transformRule?: string
  enabled?: boolean
  remark?: string
}

export interface IotTagUpsertPayload {
  tagCode?: string
  tagName: string
  sourceType: string
  sourcePath: string
  deviceCode: string
  deviceName: string
  areaCode: string
  dataType: string
  unit: string
  scanRate: number
  deadband: number
  qualityRule: string
  enabled?: boolean
  remark?: string
}

const buildQuery = (params: Record<string, string | number | boolean | undefined | null>) => {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, String(value))
    }
  })
  const queryString = query.toString()
  return queryString ? `?${queryString}` : ''
}

const request = async <T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> => {
  const headerExtra: Record<string, string> = {}
  const h = init?.headers
  if (h instanceof Headers) {
    h.forEach((v, k) => {
      headerExtra[k] = v
    })
  } else if (h && typeof h === 'object') {
    Object.assign(headerExtra, h as Record<string, string>)
  }

  const response = await fetch(`/api/iot${path}`, {
    ...init,
    headers: buildJsonHeaders(headerExtra),
  })

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      ElMessage.error('未登录或权限不足，请重新登录（若已开启 API 认证）')
    } else {
      ElMessage.error(`IOT 请求失败（${response.status}）`)
    }
    throw new Error(`IOT request failed: ${response.status}`)
  }

  return response.json()
}

export const getIotTags = (params: {
  keyword?: string
  deviceCode?: string
  areaCode?: string
  enabled?: boolean
  sourceType?: string
  pageNum?: number
  pageSize?: number
} = {}) => request<{ total: number; records: IotTagDefinition[] }>(`/tags${buildQuery(params)}`)

export const getIotTagDetail = (tagCode: string) => request<IotTagDefinition | null>(`/tags/${encodeURIComponent(tagCode)}`)

export const getDeviceIotTags = (deviceCode: string) => request<IotTagDefinition[]>(`/devices/${encodeURIComponent(deviceCode)}/tags`)

export const createIotTag = (payload: IotTagUpsertPayload) =>
  request<IotTagDefinition>('/tags', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const updateIotTag = (tagCode: string, payload: IotTagUpsertPayload) =>
  request<IotTagDefinition>(`/tags/${encodeURIComponent(tagCode)}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })

export const enableIotTag = (tagCode: string) =>
  request<IotTagDefinition>(`/tags/${encodeURIComponent(tagCode)}/enable`, {
    method: 'POST',
  })

export const disableIotTag = (tagCode: string) =>
  request<IotTagDefinition>(`/tags/${encodeURIComponent(tagCode)}/disable`, {
    method: 'POST',
  })

export const deleteIotTag = (tagCode: string) =>
  request<{ tagCode: string; deleted: boolean }>(`/tags/${encodeURIComponent(tagCode)}`, {
    method: 'DELETE',
  })

export const getIotRealtime = (params: {
  tagCodes?: string
  deviceCode?: string
  areaCode?: string
} = {}) => request<IotRealtimeValue[]>(`/realtime${buildQuery(params)}`)

export const getIotRealtimeSnapshot = (pageKey?: string) =>
  request<{ pageKey: string; generatedAt: string; items: IotRealtimeValue[] }>(`/realtime/snapshot${buildQuery({ pageKey })}`)

export const getIotHistory = (params: {
  tagCode: string
  startTime?: string
  endTime?: string
  interval?: string
  aggregate?: string
}) => request(`/history${buildQuery(params)}`)

export const getIotAlarms = (params: {
  alarmLevel?: string
  alarmStatus?: string
  deviceCode?: string
} = {}) => request<IotAlarmEvent[]>(`/alarms${buildQuery(params)}`)

export const ackIotAlarm = (payload: { alarmId: string; operator?: string; remark?: string }) =>
  request<IotAlarmEvent>('/alarms/ack', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const closeIotAlarm = (payload: { alarmId: string; operator?: string; remark?: string }) =>
  request<IotAlarmEvent>('/alarms/close', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const getIotTagMappings = () => request<IotTagMapping[]>('/tag-mappings')

export const createIotTagMapping = (payload: IotTagMappingUpsertPayload) =>
  request<IotTagMapping>('/tag-mappings', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const updateIotTagMapping = (mappingId: string, payload: IotTagMappingUpsertPayload) =>
  request<IotTagMapping>(`/tag-mappings/${encodeURIComponent(mappingId)}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })

export const enableIotTagMapping = (mappingId: string) =>
  request<IotTagMapping>(`/tag-mappings/${encodeURIComponent(mappingId)}/enable`, {
    method: 'POST',
  })

export const disableIotTagMapping = (mappingId: string) =>
  request<IotTagMapping>(`/tag-mappings/${encodeURIComponent(mappingId)}/disable`, {
    method: 'POST',
  })

export const deleteIotTagMapping = (mappingId: string) =>
  request<{ mappingId: string; deleted: boolean }>(`/tag-mappings/${encodeURIComponent(mappingId)}`, {
    method: 'DELETE',
  })
