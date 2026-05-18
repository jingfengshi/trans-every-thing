<template>
  <div class="glass progress-wrap">
    <div class="orbit">
      <svg class="ring" viewBox="0 0 80 80">
        <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="5"/>
        <circle
          cx="40" cy="40" r="34"
          fill="none"
          stroke="url(#grad)"
          stroke-width="5"
          stroke-linecap="round"
          :stroke-dasharray="`${213.6 * progress} 213.6`"
          transform="rotate(-90 40 40)"
          style="transition: stroke-dasharray 0.5s ease"
        />
        <defs>
          <linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#a78bfa"/>
            <stop offset="100%" stop-color="#60a5fa"/>
          </linearGradient>
        </defs>
      </svg>
      <div class="pct">{{ Math.round(progress * 100) }}<span>%</span></div>
    </div>

    <div class="status-title">{{ statusText }}</div>
    <div class="status-sub" v-if="status === 'processing'">正在调用翻译引擎，请稍候...</div>

    <div class="bar-row">
      <div class="bar-track">
        <div class="bar-fill" :style="{ width: `${progress * 100}%` }" />
      </div>
    </div>

    <div v-if="error" class="error-box">⚠ {{ error }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ status: String, progress: Number, error: String })

const statusText = computed(() => ({
  pending: '正在排队...',
  processing: '翻译中',
  done: '翻译完成 🎉',
  failed: '翻译失败',
}[props.status] || props.status))
</script>

<style scoped>
.progress-wrap {
  display: flex; flex-direction: column; align-items: center;
  gap: 20px; padding: 48px 32px; text-align: center;
}

.orbit { position: relative; width: 100px; height: 100px; }
.ring { width: 100%; height: 100%; }
.pct {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 700; color: rgba(255,255,255,0.9);
}
.pct span { font-size: 13px; font-weight: 400; color: rgba(255,255,255,0.4); margin-top: 4px; }

.status-title { font-size: 20px; font-weight: 600; color: rgba(255,255,255,0.9); }
.status-sub { font-size: 13px; color: rgba(255,255,255,0.35); margin-top: -12px; }

.bar-row { width: 100%; }
.bar-track {
  height: 4px; background: rgba(255,255,255,0.08); border-radius: 99px; overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed, #60a5fa);
  border-radius: 99px;
  transition: width 0.5s ease;
}

.error-box {
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.3);
  border-radius: 10px;
  padding: 10px 16px;
  font-size: 13px;
  color: #fca5a5;
  width: 100%; text-align: left;
}
</style>
