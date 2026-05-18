<template>
  <div class="download-panel">
    <p>翻译完成，点击下载：</p>
    <a :href="downloadUrl" download>
      <button class="primary">下载翻译 PDF</button>
    </a>
    <button class="secondary" @click="$emit('reset')">翻译新文件</button>
  </div>
</template>

<script setup>
import { getDownloadUrl } from '../api.js'

const props = defineProps({ taskId: String })
defineEmits(['reset'])

const downloadUrl = getDownloadUrl(props.taskId)
</script>

<style scoped>
.download-panel { display: flex; flex-direction: column; gap: 12px; align-items: flex-start; }
button { padding: 10px 24px; font-size: 16px; cursor: pointer; border: none; border-radius: 6px; }
.primary { background: #4f8ef7; color: white; }
.secondary { background: #eee; color: #333; }
</style>
