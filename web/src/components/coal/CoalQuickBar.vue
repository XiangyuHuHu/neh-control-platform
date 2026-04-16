<template>
  <section class="quick-bar">
    <div class="quick-bar__copy">
      <p class="quick-bar__eyebrow">模块入口</p>
      <h2>{{ title }}</h2>
      <p v-if="subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="status" class="quick-bar__status" :class="`quick-bar__status--${status.type}`">
      <i class="quick-bar__status-dot"></i>
      <span>{{ status.text }}</span>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  status?: {
    text: string
    type: 'running' | 'idle' | 'stopped'
  }
}>()
</script>

<style scoped>
.quick-bar {
  width: min(100%, 1680px);
  margin: 0 auto 16px;
  padding: 20px 22px;
  border: 1px solid rgba(96, 183, 255, 0.12);
  border-radius: 20px;
  background: rgba(9, 19, 29, 0.84);
  box-shadow: inset 0 1px 0 rgba(136, 211, 255, 0.06);
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.quick-bar__eyebrow {
  margin: 0 0 6px;
  color: #7ecfff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.quick-bar h2 {
  margin: 0;
  font-size: 22px;
  line-height: 1.1;
  color: #f3faff;
}

.quick-bar__copy p:last-child {
  margin: 8px 0 0;
  color: rgba(224, 239, 251, 0.64);
  line-height: 1.6;
}

.quick-bar__status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  font-size: 12px;
  color: #e8f5ff;
  white-space: nowrap;
}

.quick-bar__status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 0 0 currentColor;
  animation: pulse 1.6s infinite;
}

.quick-bar__status--running {
  color: var(--status-running, #00d8a6);
}

.quick-bar__status--idle {
  color: var(--status-idle, #ffb547);
}

.quick-bar__status--stopped {
  color: var(--status-stopped, #ff6b6b);
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 currentColor; }
  70% { box-shadow: 0 0 0 6px transparent; }
  100% { box-shadow: 0 0 0 0 transparent; }
}
</style>
