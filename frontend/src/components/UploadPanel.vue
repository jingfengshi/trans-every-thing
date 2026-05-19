<template>
  <div class="glass">
    <!-- 拖拽区 -->
    <div
      class="drop-zone"
      :class="{ dragover, 'has-file': file }"
      @dragover.prevent="dragover = true"
      @dragleave="dragover = false"
      @drop.prevent="onDrop"
      @click="$refs.fileInput.click()"
    >
      <input ref="fileInput" type="file" accept=".pdf" hidden @change="onFileChange" />
      <div class="drop-icon">
        <svg v-if="!file" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 16V4M12 4l-4 4M12 4l4 4" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M3 16v2a2 2 0 002 2h14a2 2 0 002-2v-2" stroke-linecap="round"/>
        </svg>
        <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <path d="M14 2v6h6M9 13h6M9 17h4" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="drop-primary">
        <template v-if="!file">拖拽 PDF 到此处<br><em>或点击选择文件</em></template>
        <template v-else>{{ file.name }}</template>
      </div>
      <div class="drop-secondary">
        {{ file ? ((file.size / 1024 / 1024).toFixed(2) + ' MB') : '支持 PDF 格式，最大 50MB' }}
      </div>
    </div>

    <!-- 引擎 + 语言 -->
    <div class="row">
      <label class="field-label">
        引擎
        <select v-model="engine">
          <option value="claude">Claude</option>
          <option value="openai">OpenAI</option>
          <option value="google">Google</option>
        </select>
      </label>
      <label class="field-label">
        目标语言
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

    <!-- 风格提示词 -->
    <label class="field-label">
      翻译风格 <span class="opt">可选</span>
      <textarea
        v-model="stylePrompt"
        placeholder="例如：翻译成粤语、保留专业术语、使用口语化表达..."
        rows="3"
      />
    </label>

    <!-- 提交 -->
    <button class="btn-submit" :disabled="!file || loading" @click="submit">
      <span v-if="loading" class="spinner" />
      <span v-else class="btn-arrow">→</span>
      {{ loading ? '处理中...' : '开始翻译' }}
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
    emit('submitted', { taskId: data.task_id, file: file.value })
  } finally { loading.value = false }
}
</script>

<style scoped>
.glass { display: flex; flex-direction: column; gap: 20px; }

.drop-zone {
  border: 1.5px dashed rgba(255,255,255,0.18);
  border-radius: 14px;
  padding: 36px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s;
  background: rgba(255,255,255,0.03);
  display: flex; flex-direction: column; align-items: center; gap: 10px;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: rgba(160,110,255,0.7);
  background: rgba(130,80,255,0.08);
  box-shadow: 0 0 24px rgba(130,80,255,0.12) inset;
}
.drop-zone.has-file {
  border-style: solid;
  border-color: rgba(120,180,255,0.5);
  background: rgba(80,130,255,0.07);
}

.drop-icon { color: rgba(255,255,255,0.4); }
.drop-zone.dragover .drop-icon, .drop-zone.has-file .drop-icon { color: rgba(180,140,255,0.9); }

.drop-primary {
  font-size: 15px;
  color: rgba(255,255,255,0.75);
  line-height: 1.5;
}
.drop-primary em { color: #a78bfa; font-style: normal; }
.drop-secondary { font-size: 12px; color: rgba(255,255,255,0.3); }

.row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.field-label { display: flex; flex-direction: column; gap: 7px; font-size: 12px; font-weight: 500; color: rgba(255,255,255,0.4); letter-spacing: 0.6px; text-transform: uppercase; }
.opt { font-weight: 400; color: rgba(255,255,255,0.2); text-transform: none; letter-spacing: 0; margin-left: 4px; }

.btn-submit {
  margin-top: 4px;
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: all 0.2s;
  box-shadow: 0 4px 20px rgba(120,60,220,0.4);
  letter-spacing: 0.3px;
}
.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, #6d28d9, #4338ca);
  box-shadow: 0 6px 28px rgba(120,60,220,0.55);
  transform: translateY(-1px);
}
.btn-submit:active:not(:disabled) { transform: translateY(0); }
.btn-submit:disabled { opacity: 0.4; cursor: not-allowed; box-shadow: none; }

.btn-arrow { font-size: 18px; }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
