<template>
  <div class="upload-panel">
    <div
      class="drop-zone"
      :class="{ dragover }"
      @dragover.prevent="dragover = true"
      @dragleave="dragover = false"
      @drop.prevent="onDrop"
      @click="$refs.fileInput.click()"
    >
      <span v-if="!file">拖拽 PDF 到此处，或点击选择文件</span>
      <span v-else>已选择：{{ file.name }}</span>
      <input ref="fileInput" type="file" accept=".pdf" hidden @change="onFileChange" />
    </div>

    <div class="options">
      <label>
        翻译引擎：
        <select v-model="engine">
          <option value="claude">Claude</option>
          <option value="openai">OpenAI</option>
          <option value="google">Google</option>
        </select>
      </label>

      <label>
        目标语言：
        <select v-model="targetLang">
          <option value="zh">中文</option>
          <option value="en">English</option>
          <option value="ja">日本語</option>
          <option value="ko">한국어</option>
          <option value="fr">Français</option>
          <option value="de">Deutsch</option>
          <option value="es">Español</option>
        </select>
      </label>
    </div>

    <label class="style-label">
      翻译风格（可选）：
      <textarea
        v-model="stylePrompt"
        placeholder="例如：翻译成粤语、保留专业术语、使用口语化表达..."
        rows="3"
      />
    </label>

    <button :disabled="!file || loading" @click="submit">
      {{ loading ? '提交中...' : '开始翻译' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { submitTranslate } from '../api.js'

const emit = defineEmits(['submitted'])

const file = ref(null)
const engine = ref('claude')
const targetLang = ref('zh')
const stylePrompt = ref('')
const dragover = ref(false)
const loading = ref(false)

function onFileChange(e) {
  file.value = e.target.files[0] || null
}

function onDrop(e) {
  dragover.value = false
  file.value = e.dataTransfer.files[0] || null
}

async function submit() {
  if (!file.value) return
  loading.value = true
  try {
    const data = await submitTranslate(file.value, engine.value, targetLang.value, stylePrompt.value)
    emit('submitted', data.task_id)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.upload-panel { display: flex; flex-direction: column; gap: 16px; }
.drop-zone {
  border: 2px dashed #aaa; border-radius: 8px; padding: 40px;
  text-align: center; cursor: pointer; transition: border-color 0.2s;
}
.drop-zone.dragover { border-color: #4f8ef7; background: #f0f5ff; }
.options { display: flex; gap: 24px; flex-wrap: wrap; }
.style-label { display: flex; flex-direction: column; gap: 6px; }
.style-label textarea { resize: vertical; padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px; }
button { padding: 10px 24px; font-size: 16px; cursor: pointer; border: none; background: #4f8ef7; color: white; border-radius: 6px; }
button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
