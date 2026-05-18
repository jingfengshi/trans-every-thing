<template>
  <div class="card download-card">
    <div class="success-icon">✅</div>
    <div class="title">翻译完成</div>
    <div class="subtitle">你的 PDF 已准备好下载</div>

    <a :href="downloadUrl" download class="btn-download">
      ↓ 下载翻译 PDF
    </a>

    <button class="btn-reset" @click="$emit('reset')">
      翻译新文件
    </button>
  </div>
</template>

<script setup>
import { getDownloadUrl } from '../api.js'
const props = defineProps({ taskId: String })
defineEmits(['reset'])
const downloadUrl = getDownloadUrl(props.taskId)
</script>

<style scoped>
.download-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 48px 32px;
  text-align: center;
}
.success-icon { font-size: 56px; }
.title { font-size: 22px; font-weight: 600; color: #111827; }
.subtitle { font-size: 14px; color: #6b7280; margin-top: -8px; }

.btn-download {
  margin-top: 8px;
  display: inline-block;
  padding: 12px 32px;
  background: #6366f1;
  color: white;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.15s;
}
.btn-download:hover { background: #4f46e5; }

.btn-reset {
  padding: 10px 24px;
  background: none;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-reset:hover { border-color: #d1d5db; color: #374151; background: #f9fafb; }
</style>
