export type JsonRecord = Record<string, unknown>

export const parseNumberArray = (text: string, label: string): number[] => {
  const parsed: unknown = JSON.parse(text)
  if (!Array.isArray(parsed)) {
    throw new Error(`${label} 必须是数组`)
  }
  return parsed.map((value, index) => {
    const numericValue = Number(value)
    if (!Number.isFinite(numericValue)) {
      throw new Error(`${label} 第 ${index + 1} 项不是有效数字`)
    }
    return numericValue
  })
}

export const parseJsonObject = (text: string): JsonRecord => {
  const parsed: unknown = JSON.parse(text)
  if (!parsed || Array.isArray(parsed) || typeof parsed !== 'object') {
    throw new Error('参数对象必须是 JSON 对象')
  }
  return parsed as JsonRecord
}

export const toErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof Error && error.message) {
    return error.message
  }
  return fallback
}
