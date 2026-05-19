<template>
  <div class="page">
    <!-- 背景光晕 -->
    <div class="glow glow-1" />
    <div class="glow glow-2" />
    <div class="glow glow-3" />

    <header class="header">
      <span class="brand">✦ Trans Every Thing</span>
    </header>

    <main class="main">
      <div class="hero" v-if="stage === 'upload'">
        <h1>PDF 智能翻译</h1>
        <p>保留原始排版，多引擎驱动，一键输出译文</p>
      </div>

      <UploadPanel v-if="stage === 'upload'" @submitted="onSubmitted" />
      <ProgressBar
        v-if="stage === 'progress'"
        :status="taskStatus.status"
        :progress="taskStatus.progress"
        :error="taskStatus.error"
      />
      <DownloadPanel v-if="stage === 'done'" :task-id="taskId" @reset="reset" @compare="showCompare = true" />

    <!-- 全屏对比预览 -->
    <CompareViewer
      v-if="showCompare && taskId && originalFile"
      :task-id="taskId"
      :original-file="originalFile"
      @close="showCompare = false"
    />
    </main>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import UploadPanel from './components/UploadPanel.vue'
import ProgressBar from './components/ProgressBar.vue'
import DownloadPanel from './components/DownloadPanel.vue'
import CompareViewer from './components/CompareViewer.vue'
import { getStatus } from './api.js'

const stage = ref('upload')
const taskId = ref(null)
const originalFile = ref(null)
const taskStatus = ref({ status: 'pending', progress: 0, error: null })
const showCompare = ref(false)
let pollTimer = null

async function onSubmitted({ taskId: id, file }) {
  taskId.value = id
  originalFile.value = file
  stage.value = 'progress'
  pollTimer = setInterval(async () => {
    try {
      const data = await getStatus(taskId.value)
      taskStatus.value = data
      if (data.status === 'done') {
        clearInterval(pollTimer)
        stage.value = 'done'
        // 只有 PDF 支持对比预览
        const isPdf = originalFile.value?.name?.toLowerCase().endsWith('.pdf')
        if (isPdf) showCompare.value = true
      }
      else if (data.status === 'failed') clearInterval(pollTimer)
    } catch (e) { console.error(e) }
  }, 2000)
}

function reset() {
  clearInterval(pollTimer)
  stage.value = 'upload'
  taskId.value = null
  originalFile.value = null
  taskStatus.value = { status: 'pending', progress: 0, error: null }
  showCompare.value = false
}

onUnmounted(() => clearInterval(pollTimer))
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
  background: #0a0a1a;
  color: #f0f0ff;
  min-height: 100vh;
  overflow-x: hidden;
}

.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 背景渐变 */
.page::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99, 60, 180, 0.45) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 80%, rgba(30, 80, 200, 0.35) 0%, transparent 60%),
    linear-gradient(160deg, #0d0d2b 0%, #080818 50%, #0a1020 100%);
  z-index: 0;
}

/* 光晕装饰 */
.glow {
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}
.glow-1 {
  width: 500px; height: 500px;
  top: -150px; left: -100px;
  background: rgba(120, 60, 220, 0.25);
}
.glow-2 {
  width: 400px; height: 400px;
  bottom: -100px; right: -80px;
  background: rgba(40, 100, 240, 0.2);
}
.glow-3 {
  width: 300px; height: 300px;
  top: 40%; left: 50%;
  transform: translateX(-50%);
  background: rgba(180, 80, 255, 0.1);
}

.header {
  position: relative;
  z-index: 10;
  padding: 20px 32px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  backdrop-filter: blur(12px);
  background: rgba(255,255,255,0.03);
}
.brand {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
  letter-spacing: 0.5px;
}

.main {
  position: relative;
  z-index: 10;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 56px 20px 80px;
  gap: 32px;
}

.hero { text-align: center; }
.hero h1 {
  font-size: 42px;
  font-weight: 700;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #fff 30%, #c4a8ff 70%, #82b0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
  line-height: 1.1;
}
.hero p {
  font-size: 16px;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.2px;
}

/* 玻璃卡片 —— 所有子组件共用 */
:deep(.glass) {
  width: 100%;
  max-width: 580px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 32px;
  box-shadow:
    0 8px 32px rgba(0,0,0,0.4),
    inset 0 1px 0 rgba(255,255,255,0.1);
}

/* 通用输入控件 */
:deep(label.field-label) {
  display: flex;
  flex-direction: column;
  gap: 7px;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.6px;
  text-transform: uppercase;
}

:deep(select), :deep(textarea) {
  padding: 11px 14px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  font-size: 14px;
  color: rgba(255,255,255,0.9);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
  width: 100%;
}
:deep(select):focus, :deep(textarea):focus {
  border-color: rgba(160, 110, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(140, 90, 255, 0.15);
}
:deep(select) option { background: #1a1a3a; color: #f0f0ff; }
:deep(textarea) { resize: vertical; }
</style>
