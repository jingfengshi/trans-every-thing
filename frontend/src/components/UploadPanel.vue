<template>
  <div class="card">
    <div
      class="drop-zone"
      :class="{ dragover, 'has-file': file }"
      @dragover.prevent="dragover = true"
      @dragleave="dragover = false"
      @drop.prevent="onDrop"
      @click="$refs.fileInput.click()"
    >
      <input ref="fileInput" type="file" accept=".pdf" hidden @change="onFileChange" />
      <div class="drop-icon">{{ file ? '📄' : '☁️' }}</div>
      <div class="drop-text">
        <span v-if="!file">拖拽 PDF 到此处，或<em>点击选择</em></span>
        <span v-else class="file-name">{{ file.name }}</span>
      </div>
      <div v-if="file" class="file-size">{{ (file.size / 1024 / 1024).toFixed(2) }} MB</div>
    </div>

    <div class="row">
      <div class="field">
        <label>翻译引擎</label>
        <select v-model="engine">
          <option value="claude">Claude</option>
          <option value="openai">OpenAI</option>
          <option value="google">Google</option>
        </select>
      </div>
      <div class="field">
        <label>目标语言</label>
        <select v-model="targetLang">
          <option value="zh">中文</option>
          <option value="en">English</option>
          <option value="ja">日本語</option>
          <option value="ko">한국어</option>
          <option value="fr">Français</option>
          <option value="de">Deutsch</option>
          <option value="es">Español</option>
        </select>
      </div>
    </div>

    <div class="field">
      <label>翻译风格 <span class="optional">可选</span></label>
      <textarea
        v-model="stylePrompt"
        placeholder="例如：翻译成粤语、保留专业术语、使用口语化表达..."
        rows="3"
      />
    </div>

    <button class="btn-primary" :disabled="!file || loading" @click="submit">
      <span v-if="loading" class="spinner" />
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

function onFileChange(e) { file.value = e.target.files[0] || null }
function onDrop(e) { dragover.value = false; file.value = e.dataTransfer.files[0] || null }

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
.card { display: flex; flex-direction: column; gap: 20px; }

.drop-zone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: #6366f1;
  background: #f5f3ff;
}
.drop-zone.has-file {
  border-style: solid;
  border-color: #6366f1;
  background: #f5f3ff;
}
.drop-icon { font-size: 36px; margin-bottom: 10px; }
.drop-text { font-size: 15px; color: #6b7280; }
.drop-text em { color: #6366f1; font-style: normal; font-weight: 500; }
.file-name { color: #111827; font-weight: 500; word-break: break-all; }
.file-size { font-size: 12px; color: #9ca3af; margin-top: 4px; }

.row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.field { display: flex; flex-direction: column; gap: 6px; }
label { font-size: 13px; font-weight: 500; color: #374151; }
.optional { font-weight: 400; color: #9ca3af; margin-left: 4px; }

select, textarea {
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  color: #111827;
  background: white;
  transition: border-color 0.15s;
  outline: none;
  font-family: inherit;
}
select:focus, textarea:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.1); }
textarea { resize: vertical; }

.btn-primary {
  padding: 12px 24px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-primary:hover:not(:disabled) { background: #4f46e5; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
