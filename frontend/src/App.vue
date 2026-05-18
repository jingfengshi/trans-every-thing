<template>
  <div class="page">
    <header class="header">
      <span class="logo">📄</span>
      <span class="brand">Trans Every Thing</span>
    </header>

    <main class="main">
      <div class="hero" v-if="stage === 'upload'">
        <h1>PDF 智能翻译</h1>
        <p>上传 PDF，保留原始排版，输出翻译版本</p>
      </div>

      <UploadPanel v-if="stage === 'upload'" @submitted="onSubmitted" />
      <ProgressBar
        v-if="stage === 'progress'"
        :status="taskStatus.status"
        :progress="taskStatus.progress"
        :error="taskStatus.error"
      />
      <DownloadPanel v-if="stage === 'done'" :task-id="taskId" @reset="reset" />
    </main>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import UploadPanel from './components/UploadPanel.vue'
import ProgressBar from './components/ProgressBar.vue'
import DownloadPanel from './components/DownloadPanel.vue'
import { getStatus } from './api.js'

const stage = ref('upload')
const taskId = ref(null)
const taskStatus = ref({ status: 'pending', progress: 0, error: null })
let pollTimer = null

async function onSubmitted(id) {
  taskId.value = id
  stage.value = 'progress'
  pollTimer = setInterval(async () => {
    try {
      const data = await getStatus(taskId.value)
      taskStatus.value = data
      if (data.status === 'done') { clearInterval(pollTimer); stage.value = 'done' }
      else if (data.status === 'failed') clearInterval(pollTimer)
    } catch (e) { console.error('Poll error:', e) }
  }, 2000)
}

function reset() {
  clearInterval(pollTimer)
  stage.value = 'upload'
  taskId.value = null
  taskStatus.value = { status: 'pending', progress: 0, error: null }
}

onUnmounted(() => clearInterval(pollTimer))
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
  background: #f3f4f6;
  color: #111827;
  min-height: 100vh;
}

.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo { font-size: 22px; }
.brand { font-size: 16px; font-weight: 600; color: #111827; letter-spacing: -0.3px; }

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 20px 80px;
  gap: 28px;
}

.hero { text-align: center; }
.hero h1 { font-size: 32px; font-weight: 700; letter-spacing: -0.5px; color: #111827; margin-bottom: 8px; }
.hero p { font-size: 15px; color: #6b7280; }

/* card 共用样式（UploadPanel / ProgressBar / DownloadPanel 都用） */
:deep(.card) {
  width: 100%;
  max-width: 560px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.05);
  padding: 28px;
}
</style>
