<template>
  <div class="card progress-card">
    <div class="status-icon">{{ statusIcon }}</div>
    <div class="status-text">{{ statusText }}</div>

    <div class="bar-wrap">
      <div class="bar-track">
        <div
          class="bar-fill"
          :class="{ pulse: status === 'processing' }"
          :style="{ width: `${Math.round(progress * 100)}%` }"
        />
      </div>
      <span class="bar-pct">{{ Math.round(progress * 100) }}%</span>
    </div>

    <div v-if="error" class="error-box">
      <span>⚠️</span> {{ error }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ status: String, progress: Number, error: String })

const statusIcon = computed(() => ({
  pending: '⏳', processing: '⚙️', done: '✅', failed: '❌'
}[props.status] || '⏳'))

const statusText = computed(() => ({
  pending: '等待处理...',
  processing: `正在翻译中，请稍候`,
  done: '翻译完成！',
  failed: '翻译失败',
}[props.status] || props.status))
</script>

<style scoped>
.progress-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 48px 32px;
  text-align: center;
}
.status-icon { font-size: 48px; }
.status-text { font-size: 18px; font-weight: 500; color: #111827; }

.bar-wrap { width: 100%; display: flex; align-items: center; gap: 12px; }
.bar-track {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 99px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: #6366f1;
  border-radius: 99px;
  transition: width 0.4s ease;
}
.bar-fill.pulse {
  background: linear-gradient(90deg, #6366f1, #a78bfa, #6366f1);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
.bar-pct { font-size: 13px; font-weight: 500; color: #6b7280; width: 36px; text-align: right; }

.error-box {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 14px;
  color: #dc2626;
  width: 100%;
  text-align: left;
}
</style>
