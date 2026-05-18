<template>
  <div class="progress-wrap">
    <p>{{ statusText }}</p>
    <div class="bar-bg">
      <div class="bar-fill" :style="{ width: `${Math.round(progress * 100)}%` }" />
    </div>
    <p v-if="error" class="error">错误：{{ error }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: String,
  progress: Number,
  error: String,
})

const statusText = computed(() => ({
  pending: '等待处理...',
  processing: `翻译中 ${Math.round(props.progress * 100)}%`,
  done: '翻译完成！',
  failed: '翻译失败',
}[props.status] || props.status))
</script>

<style scoped>
.progress-wrap { display: flex; flex-direction: column; gap: 12px; }
.bar-bg { background: #eee; border-radius: 4px; height: 10px; overflow: hidden; }
.bar-fill { background: #4f8ef7; height: 100%; transition: width 0.3s ease; }
.error { color: #e53e3e; }
</style>
