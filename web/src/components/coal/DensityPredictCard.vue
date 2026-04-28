<template>
  <article class="density-card">
    <header>
      <h3>{{ title }}</h3>
      <span class="indicator" :class="levelClass"></span>
    </header>
    <div class="gauge-wrap">
      <div class="gauge" :style="gaugeStyle">
        <div class="gauge-inner">
          <div class="value">{{ predictText }}</div>
          <small>预测值</small>
        </div>
      </div>
      <div class="meta">
        <p><label>设定值</label><strong>{{ setpointText }}</strong></p>
        <p><label>偏差</label><strong :class="levelClass">{{ deltaText }}</strong></p>
      </div>
    </div>
    <footer>
      <slot />
    </footer>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  predict: number
  setpoint: number
}>()

const delta = computed(() => props.predict - props.setpoint)
const ratio = computed(() => Math.min(1, Math.abs(delta.value) / 0.12))
const levelClass = computed(() => {
  const abs = Math.abs(delta.value)
  if (abs >= 0.08) return 'warn'
  if (abs >= 0.04) return 'attention'
  return 'good'
})

const gaugeStyle = computed(() => {
  const degree = Math.round(ratio.value * 260)
  return {
    background: `conic-gradient(from 220deg, rgba(0, 242, 241, 0.85) ${degree}deg, rgba(255,255,255,0.08) ${degree}deg 360deg)`,
  }
})

const predictText = computed(() => props.predict.toFixed(3))
const setpointText = computed(() => props.setpoint.toFixed(3))
const deltaText = computed(() => `${delta.value >= 0 ? '+' : ''}${delta.value.toFixed(3)}`)
</script>

<style scoped>
.density-card {
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(126, 175, 220, 0.28);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(8px);
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
h3 {
  margin: 0;
  font-size: 14px;
  color: #d8e8f7;
}
.indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.indicator.good {
  background: #3dd598;
  box-shadow: 0 0 8px rgba(61, 213, 152, 0.55);
}
.indicator.attention {
  background: #fdb731;
  box-shadow: 0 0 8px rgba(253, 183, 49, 0.55);
}
.indicator.warn {
  background: #ff6b6b;
  box-shadow: 0 0 8px rgba(255, 107, 107, 0.55);
}
.gauge-wrap {
  margin: 10px 0;
  display: flex;
  gap: 10px;
  align-items: center;
}
.gauge {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  display: grid;
  place-items: center;
}
.gauge-inner {
  width: 66px;
  height: 66px;
  border-radius: 50%;
  background: rgba(10, 18, 32, 0.95);
  display: grid;
  place-items: center;
  text-align: center;
}
.value {
  font-size: 16px;
  font-weight: 700;
  color: #eaf4ff;
}
.gauge-inner small {
  color: rgba(226, 238, 248, 0.65);
  font-size: 10px;
}
.meta {
  display: grid;
  gap: 6px;
}
.meta p {
  margin: 0;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}
.meta label {
  color: rgba(216, 232, 247, 0.7);
}
.meta strong {
  color: #f0f7ff;
}
.meta .good {
  color: #3dd598;
}
.meta .attention {
  color: #fdb731;
}
.meta .warn {
  color: #ff6b6b;
}
footer {
  display: flex;
  gap: 8px;
}
</style>
