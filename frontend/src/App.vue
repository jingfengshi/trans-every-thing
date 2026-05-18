<template>
  <div class="app">
    <h1>Trans Every Thing</h1>

    <UploadPanel v-if="stage === 'upload'" @submitted="onSubmitted" />

    <ProgressBar
      v-if="stage === 'progress'"
      :status="taskStatus.status"
      :progress="taskStatus.progress"
      :error="taskStatus.error"
    />

    <DownloadPanel
      v-if="stage === 'done'"
      :task-id="taskId"
      @reset="reset"
    />
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
  startPolling()
}

function startPolling() {
  pollTimer = setInterval(async () => {
    try {
      const data = await getStatus(taskId.value)
      taskStatus.value = data
      if (data.status === 'done') {
        clearInterval(pollTimer)
        stage.value = 'done'
      } else if (data.status === 'failed') {
        clearInterval(pollTimer)
      }
    } catch (e) {
      console.error('Poll error:', e)
    }
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
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; color: #333; }
h1 { margin-bottom: 32px; font-size: 28px; }
</style>
