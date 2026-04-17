import { onBeforeUnmount } from 'vue'
import { storeToRefs } from 'pinia'
import { useIotStore } from '../stores/iot'

type SubscribeOptions = {
  pageKey: string
  intervalMs?: number
}

type SubscriberState = {
  intervalMs: number
  refCount: number
}

const subscribers = new Map<string, SubscriberState>()
let pollingTimer: number | null = null
let inflightPromise: Promise<void> | null = null
let lastSnapshotAt = 0
let activePageKey = 'global'
const DEFAULT_INTERVAL = 5000

const buildPageKey = () => {
  if (!subscribers.size) return 'global'
  return Array.from(subscribers.keys()).sort().join(',')
}

const resolveInterval = () => {
  const intervals = Array.from(subscribers.values()).map((item) => item.intervalMs)
  if (!intervals.length) return DEFAULT_INTERVAL
  return Math.max(1000, Math.min(...intervals))
}

const useIotHubState = () => {
  const iotStore = useIotStore()
  const { realtimeMap, generatedAt, loading, lastError } = storeToRefs(iotStore)
  return {
    iotStore,
    realtimeMap,
    generatedAt,
    loading,
    lastError,
  }
}

const runSnapshot = async (force = false) => {
  const { iotStore } = useIotHubState()
  const nextPageKey = buildPageKey()
  if (!force && nextPageKey === activePageKey && inflightPromise) return inflightPromise
  activePageKey = nextPageKey
  if (inflightPromise) return inflightPromise
  inflightPromise = iotStore
    .fetchSnapshot(activePageKey)
    .then(() => {
      lastSnapshotAt = Date.now()
    })
    .finally(() => {
      inflightPromise = null
    })
  return inflightPromise
}

const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

const startPolling = () => {
  stopPolling()
  const interval = resolveInterval()
  pollingTimer = window.setInterval(() => {
    void runSnapshot()
  }, interval)
}

const refreshPollingIfNeeded = () => {
  if (!subscribers.size) {
    stopPolling()
    return
  }
  startPolling()
}

const subscribe = (options: SubscribeOptions) => {
  const intervalMs = options.intervalMs || DEFAULT_INTERVAL
  const current = subscribers.get(options.pageKey)
  if (current) {
    current.refCount += 1
    current.intervalMs = Math.min(current.intervalMs, intervalMs)
  } else {
    subscribers.set(options.pageKey, { intervalMs, refCount: 1 })
  }
  refreshPollingIfNeeded()
}

const unsubscribe = (pageKey: string) => {
  const current = subscribers.get(pageKey)
  if (!current) return
  current.refCount -= 1
  if (current.refCount <= 0) subscribers.delete(pageKey)
  refreshPollingIfNeeded()
}

const ensureFresh = async (pageKey: string, ttlMs = 3000) => {
  const now = Date.now()
  const activeKeys = activePageKey.split(',').filter(Boolean)
  const isFresh = activeKeys.includes(pageKey) && now - lastSnapshotAt <= ttlMs
  if (isFresh) return
  await runSnapshot(true)
}

export const useIotHub = () => {
  const state = useIotHubState()
  const subscribePage = (options: SubscribeOptions) => {
    void subscribe(options)
    void ensureFresh(options.pageKey)
    onBeforeUnmount(() => {
      unsubscribe(options.pageKey)
    })
  }

  return {
    realtimeMap: state.realtimeMap,
    generatedAt: state.generatedAt,
    loading: state.loading,
    lastError: state.lastError,
    getTagValue: state.iotStore.getTagValue,
    subscribe: subscribePage,
    unsubscribe,
    ensureFresh,
  }
}
