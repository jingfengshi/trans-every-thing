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
      <input ref="fileInput" type="file" accept=".pdf,.xlsx,.xls" hidden @change="onFileChange" />
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
        <template v-if="!file">拖拽文件到此处<br><em>或点击选择</em></template>
        <template v-else>{{ file.name }}</template>
      </div>
      <div class="drop-secondary">
        {{ file ? ((file.size / 1024 / 1024).toFixed(2) + ' MB') : '支持 PDF / Excel 格式，最大 50MB' }}
      </div>
    </div>

    <!-- 引擎 + 语言 -->
    <div class="row">
      <div class="field">
        <span class="field-label">引擎</span>
        <div class="custom-select" :class="{ open: engineOpen }" @click.stop="engineOpen = !engineOpen" ref="engineRef">
          <div class="select-trigger">
            <span class="select-icon"><EngineIcon :engine="engine" /></span>
            <span class="select-value">{{ engineLabel }}</span>
            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </div>
          <div class="select-dropdown" v-if="engineOpen">
            <div
              v-for="opt in engineOptions"
              :key="opt.value"
              class="select-option"
              :class="{ active: engine === opt.value }"
              @click.stop="engine = opt.value; engineOpen = false"
            >
              <span class="opt-icon"><EngineIcon :engine="opt.value" /></span>
              <span>{{ opt.label }}</span>
              <svg v-if="engine === opt.value" class="check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M5 12l5 5L20 7" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div class="field">
        <span class="field-label">目标语言</span>
        <div class="custom-select" :class="{ open: langOpen }" @click.stop="langOpen = !langOpen" ref="langRef">
          <div class="select-trigger">
            <span class="select-icon">{{ langIcon }}</span>
            <span class="select-value">{{ langLabel }}</span>
            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </div>
          <div class="select-dropdown" v-if="langOpen">
            <div
              v-for="opt in langOptions"
              :key="opt.value"
              class="select-option"
              :class="{ active: targetLang === opt.value }"
              @click.stop="targetLang = opt.value; langOpen = false"
            >
              <span class="opt-icon">{{ opt.icon }}</span>
              <span>{{ opt.label }}</span>
              <svg v-if="targetLang === opt.value" class="check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M5 12l5 5L20 7" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 风格提示词 -->
    <div class="field">
      <span class="field-label">翻译风格 <span class="opt-tag">可选</span></span>
      <div class="textarea-wrap">
        <textarea
          v-model="stylePrompt"
          placeholder="例如：翻译成粤语、保留专业术语、使用口语化表达..."
          rows="3"
        />
      </div>
    </div>

    <!-- 提交 -->
    <button class="btn-submit" :disabled="!file || loading" @click="submit">
      <span v-if="loading" class="spinner" />
      <span v-else class="btn-arrow">→</span>
      {{ loading ? '处理中...' : '开始翻译' }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineComponent, h } from 'vue'
import { submitTranslate } from '../api.js'

// Inline brand SVG logos
const EngineIcon = defineComponent({
  props: { engine: String },
  setup(props) {
    return () => {
      if (props.engine === 'claude') {
        // Claude classic orange gradient circle icon
        return h('svg', { width: 18, height: 18, viewBox: '0 0 40 40', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
          h('defs', {}, [
            h('radialGradient', { id: 'claude-g', cx: '50%', cy: '35%', r: '65%' }, [
              h('stop', { offset: '0%', 'stop-color': '#F5A623' }),
              h('stop', { offset: '100%', 'stop-color': '#D4580A' }),
            ])
          ]),
          h('circle', { cx: '20', cy: '20', r: '20', fill: 'url(#claude-g)' }),
          h('path', {
            d: 'M22.8 11L17.2 27h3.2l1.2-3.4h5.6L28.4 27h3.2L26 11h-3.2zm-.4 9.8l2-5.8 2 5.8h-4zM11.6 11L6 27h3.2l1.2-3.4h5.6L17.2 27h3.2L14.8 11h-3.2zm-.4 9.8l2-5.8 2 5.8h-4z',
            fill: 'white'
          })
        ])
      }
      if (props.engine === 'openai') {
        // OpenAI logo
        return h('svg', { width: 18, height: 18, viewBox: '0 0 24 24', fill: 'none', xmlns: 'http://www.w3.org/2000/svg' }, [
          h('path', {
            d: 'M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.032.067L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0L4.01 14.48A4.501 4.501 0 0 1 2.34 7.896zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.816 2.78a4.496 4.496 0 0 1-.676 8.106v-5.678a.79.79 0 0 0-.393-.657zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .027-.067l4.817-2.776a4.5 4.5 0 0 1 6.679 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08-4.778 2.758a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.497v2.994l-2.597 1.5-2.607-1.497z',
            fill: 'white'
          })
        ])
      }
      if (props.engine === 'google') {
        // Google 'G' logo
        return h('svg', { width: 18, height: 18, viewBox: '0 0 24 24', xmlns: 'http://www.w3.org/2000/svg' }, [
          h('path', { d: 'M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z', fill: '#4285F4' }),
          h('path', { d: 'M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z', fill: '#34A853' }),
          h('path', { d: 'M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z', fill: '#FBBC05' }),
          h('path', { d: 'M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z', fill: '#EA4335' }),
        ])
      }
      return h('span', {}, '?')
    }
  }
})

const emit = defineEmits(['submitted'])

const file = ref(null)
const engine = ref('claude')
const targetLang = ref('zh')
const stylePrompt = ref('')
const dragover = ref(false)
const loading = ref(false)
const engineOpen = ref(false)
const langOpen = ref(false)
const engineRef = ref(null)
const langRef = ref(null)

const engineOptions = [
  { value: 'claude', label: 'Claude'  },
  { value: 'openai', label: 'OpenAI'  },
  { value: 'google', label: 'Google'  },
]

const langOptions = [
  { value: 'zh', label: '中文',     icon: '🇨🇳' },
  { value: 'en', label: 'English',  icon: '🇺🇸' },
  { value: 'ja', label: '日本語',   icon: '🇯🇵' },
  { value: 'ko', label: '한국어',   icon: '🇰🇷' },
  { value: 'fr', label: 'Français', icon: '🇫🇷' },
  { value: 'de', label: 'Deutsch',  icon: '🇩🇪' },
  { value: 'es', label: 'Español',  icon: '🇪🇸' },
]

const engineLabel = computed(() => engineOptions.find(o => o.value === engine.value)?.label)
const langLabel   = computed(() => langOptions.find(o => o.value === targetLang.value)?.label)
const langIcon    = computed(() => langOptions.find(o => o.value === targetLang.value)?.icon)

function onFileChange(e) { file.value = e.target.files[0] || null }
function onDrop(e) { dragover.value = false; file.value = e.dataTransfer.files[0] || null }

function onClickOutside(e) {
  if (engineRef.value && !engineRef.value.contains(e.target)) engineOpen.value = false
  if (langRef.value && !langRef.value.contains(e.target)) langOpen.value = false
}

onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))

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

/* drop zone */
.drop-zone {
  border: 1.5px dashed rgba(255,255,255,0.18);
  border-radius: 14px; padding: 36px 24px;
  text-align: center; cursor: pointer;
  transition: all 0.25s;
  background: rgba(255,255,255,0.03);
  display: flex; flex-direction: column; align-items: center; gap: 10px;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: rgba(160,110,255,0.7);
  background: rgba(130,80,255,0.08);
}
.drop-zone.has-file {
  border-style: solid; border-color: rgba(120,180,255,0.5);
  background: rgba(80,130,255,0.07);
}
.drop-icon { color: rgba(255,255,255,0.4); }
.drop-zone.dragover .drop-icon, .drop-zone.has-file .drop-icon { color: rgba(180,140,255,0.9); }
.drop-primary { font-size: 15px; color: rgba(255,255,255,0.75); line-height: 1.5; }
.drop-primary em { color: #a78bfa; font-style: normal; }
.drop-secondary { font-size: 12px; color: rgba(255,255,255,0.3); }

/* layout */
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 8px; }
.field-label {
  font-size: 11px; font-weight: 600;
  color: rgba(255,255,255,0.35);
  letter-spacing: 0.8px; text-transform: uppercase;
}
.opt-tag {
  font-weight: 400; color: rgba(255,255,255,0.2);
  text-transform: none; letter-spacing: 0; margin-left: 4px;
}

/* custom select */
.custom-select {
  position: relative; user-select: none;
}
.select-trigger {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.custom-select:hover .select-trigger,
.custom-select.open .select-trigger {
  border-color: rgba(160,110,255,0.5);
  background: rgba(255,255,255,0.09);
}
.select-icon { font-size: 15px; line-height: 1; }
.select-value { flex: 1; font-size: 14px; color: rgba(255,255,255,0.9); }
.chevron {
  color: rgba(255,255,255,0.3); flex-shrink: 0;
  transition: transform 0.2s;
}
.custom-select.open .chevron { transform: rotate(180deg); }

.select-dropdown {
  position: absolute; top: calc(100% + 6px); left: 0; right: 0;
  background: #1a1a35;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  overflow: hidden;
  z-index: 100;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
.select-option {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 14px; color: rgba(255,255,255,0.7);
  transition: background 0.15s;
}
.select-option:hover { background: rgba(255,255,255,0.07); }
.select-option.active { color: #c4b5fd; background: rgba(99,60,180,0.15); }
.opt-icon { font-size: 15px; flex-shrink: 0; }
.check { margin-left: auto; color: #a78bfa; flex-shrink: 0; }

/* textarea */
.textarea-wrap {
  position: relative;
}
.textarea-wrap textarea {
  width: 100%;
  padding: 12px 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  font-size: 14px; color: rgba(255,255,255,0.85);
  outline: none;
  resize: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
  line-height: 1.6;
}
.textarea-wrap textarea::placeholder { color: rgba(255,255,255,0.22); }
.textarea-wrap textarea:focus {
  border-color: rgba(160,110,255,0.5);
  box-shadow: 0 0 0 3px rgba(140,90,255,0.1);
  background: rgba(255,255,255,0.08);
}

/* submit */
.btn-submit {
  width: 100%; padding: 14px;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: white; border: none; border-radius: 12px;
  font-size: 15px; font-weight: 600; cursor: pointer;
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
  border-top-color: white; border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
