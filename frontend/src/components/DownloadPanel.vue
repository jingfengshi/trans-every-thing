<template>
  <div class="glass download-wrap">
    <div class="checkmark">
      <svg viewBox="0 0 64 64" fill="none">
        <circle cx="32" cy="32" r="30" stroke="url(#cg)" stroke-width="2.5"/>
        <path d="M20 32l9 9 15-16" stroke="url(#cg)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        <defs>
          <linearGradient id="cg" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
            <stop stop-color="#a78bfa"/>
            <stop offset="1" stop-color="#60a5fa"/>
          </linearGradient>
        </defs>
      </svg>
    </div>

    <div class="title">翻译完成</div>
    <div class="subtitle">PDF 已保留原始排版，可立即下载</div>

    <a :href="downloadUrl" download class="btn-download">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <path d="M12 4v12M12 16l-4-4M12 16l4-4" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M4 20h16" stroke-linecap="round"/>
      </svg>
      下载翻译 PDF
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
.download-wrap {
  display: flex; flex-direction: column; align-items: center;
  gap: 16px; padding: 52px 32px; text-align: center;
}

.checkmark { width: 80px; height: 80px; margin-bottom: 8px; }

.title { font-size: 24px; font-weight: 700; color: rgba(255,255,255,0.95); }
.subtitle { font-size: 14px; color: rgba(255,255,255,0.35); margin-top: -4px; }

.btn-download {
  margin-top: 12px;
  display: inline-flex; align-items: center; gap: 8px;
  padding: 14px 36px;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: white;
  text-decoration: none;
  border-radius: 12px;
  font-size: 15px; font-weight: 600;
  box-shadow: 0 4px 20px rgba(120,60,220,0.45);
  transition: all 0.2s;
  letter-spacing: 0.3px;
}
.btn-download:hover {
  background: linear-gradient(135deg, #6d28d9, #4338ca);
  box-shadow: 0 6px 28px rgba(120,60,220,0.6);
  transform: translateY(-1px);
}

.btn-reset {
  padding: 10px 24px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  font-size: 13px;
  color: rgba(255,255,255,0.4);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-reset:hover {
  background: rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.7);
}
</style>
