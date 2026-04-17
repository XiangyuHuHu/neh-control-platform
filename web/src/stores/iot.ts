import { ref } from 'vue'
import { defineStore } from 'pinia'
import { getIotRealtimeSnapshot, type IotRealtimeValue } from '../api/iot'

export const useIotStore = defineStore('iot', () => {
  const realtimeMap = ref<Record<string, IotRealtimeValue>>({})
  const generatedAt = ref('')
  const loading = ref(false)
  const lastError = ref('')

  async function fetchSnapshot(pageKey = 'global') {
    loading.value = true
    try {
      const response = await getIotRealtimeSnapshot(pageKey)
      generatedAt.value = response.data.generatedAt
      lastError.value = ''
      const next: Record<string, IotRealtimeValue> = { ...realtimeMap.value }
      response.data.items.forEach((item) => {
        next[item.tagCode] = item
      })
      realtimeMap.value = next
    } catch (error) {
      lastError.value = error instanceof Error ? error.message : 'IOT snapshot failed'
    } finally {
      loading.value = false
    }
  }

  function getTagValue(tagCode: string) {
    return realtimeMap.value[tagCode]
  }

  return {
    realtimeMap,
    generatedAt,
    loading,
    lastError,
    fetchSnapshot,
    getTagValue,
  }
})
