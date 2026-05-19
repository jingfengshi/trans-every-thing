<template>
  <div class="overlay" @keydown.esc="$emit('close')" tabindex="0" ref="overlayRef">
    <!-- Header -->
    <div class="viewer-header">
      <div class="header-labels">
        <span class="label">原文</span>
        <span class="label label-right">译文</span>
      </div>
      <div class="header-actions">
        <a :href="downloadUrl" download class="btn-dl">↓ 下载译文</a>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>
    </div>

    <!-- 分屏容器 -->
    <div class="panes">
      <!-- 左：原文 -->
      <div class="pane" ref="leftPane" @scroll="onLeftScroll">
        <div class="pages-wrap" ref="leftPages">
          <canvas
            v-for="n in pageCount"
            :key="'l'+n"
            :ref="el => setLeftCanvas(el, n-1)"
            class="pdf-page"
          />
        </div>
        <div v-if="leftLoading" class="loading">渲染中...</div>
      </div>

      <div class="divider" />

      <!-- 右：译文 -->
      <div class="pane" ref="rightPane" @scroll="onRightScroll">
        <div class="pages-wrap" ref="rightPages">
          <canvas
            v-for="n in pageCount"
            :key="'r'+n"
            :ref="el => setRightCanvas(el, n-1)"
            class="pdf-page"
          />
        </div>
        <div v-if="rightLoading" class="loading">渲染中...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { getDownloadUrl } from '../api.js'

const props = defineProps({
  taskId: String,
  originalFile: File,  // 原始上传的 File 对象
})
defineEmits(['close'])

const downloadUrl = getDownloadUrl(props.taskId)

const overlayRef = ref(null)
const leftPane = ref(null)
const rightPane = ref(null)
const pageCount = ref(0)
const leftLoading = ref(true)
const rightLoading = ref(true)

const leftCanvases = []
const rightCanvases = []

function setLeftCanvas(el, idx) { if (el) leftCanvases[idx] = el }
function setRightCanvas(el, idx) { if (el) rightCanvases[idx] = el }

// 同步滚动（防止递归）
let syncingLeft = false
let syncingRight = false

function onLeftScroll() {
  if (syncingRight) return
  syncingLeft = true
  rightPane.value.scrollTop = leftPane.value.scrollTop
  syncingLeft = false
}
function onRightScroll() {
  if (syncingLeft) return
  syncingRight = true
  leftPane.value.scrollTop = rightPane.value.scrollTop
  syncingRight = false
}

async function loadPdfs() {
  // 动态加载 PDF.js
  if (!window.pdfjsLib) {
    await loadScript('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js')
    window.pdfjsLib.GlobalWorkerOptions.workerSrc =
      'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'
  }

  const scale = window.devicePixelRatio || 1.5

  // 加载原文
  const origUrl = URL.createObjectURL(props.originalFile)
  const origPdf = await window.pdfjsLib.getDocument(origUrl).promise
  pageCount.value = origPdf.numPages

  // 加载译文
  const transResp = await fetch(downloadUrl)
  const transBlob = await transResp.blob()
  const transUrl = URL.createObjectURL(transBlob)
  const transPdf = await window.pdfjsLib.getDocument(transUrl).promise

  await nextTick()

  // 渲染两侧所有页
  const renderPage = async (pdf, canvases, idx) => {
    const page = await pdf.getPage(idx + 1)
    const viewport = page.getViewport({ scale: 1.5 })
    const canvas = canvases[idx]
    if (!canvas) return
    canvas.width = viewport.width
    canvas.height = viewport.height
    await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise
  }

  const leftJobs  = Array.from({ length: origPdf.numPages }, (_, i) => renderPage(origPdf, leftCanvases, i))
  const rightJobs = Array.from({ length: transPdf.numPages }, (_, i) => renderPage(transPdf, rightCanvases, i))

  await Promise.all(leftJobs)
  leftLoading.value = false

  await Promise.all(rightJobs)
  rightLoading.value = false

  URL.revokeObjectURL(origUrl)
  URL.revokeObjectURL(transUrl)
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = src
    s.onload = resolve
    s.onerror = reject
    document.head.appendChild(s)
  })
}

onMounted(() => {
  overlayRef.value?.focus()
  loadPdfs()
})
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: #0a0a1a;
  display: flex;
  flex-direction: column;
  outline: none;
}

.viewer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: rgba(255,255,255,0.04);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(12px);
  flex-shrink: 0;
}

.header-labels {
  display: flex;
  gap: 0;
  flex: 1;
}

.label {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255,255,255,0.5);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}
.label-right { text-align: right; padding-right: 12px; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-dl {
  padding: 7px 16px;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  transition: opacity 0.15s;
}
.btn-dl:hover { opacity: 0.85; }

.btn-close {
  width: 32px; height: 32px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: rgba(255,255,255,0.6);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex; align-items: center; justify-content: center;
}
.btn-close:hover { background: rgba(255,255,255,0.15); color: white; }

.panes {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.pane {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 20px;
  background: #111122;
  scroll-behavior: auto;
}
.pane::-webkit-scrollbar { width: 6px; }
.pane::-webkit-scrollbar-track { background: transparent; }
.pane::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }

.divider {
  width: 1px;
  background: rgba(255,255,255,0.08);
  flex-shrink: 0;
}

.pages-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.pdf-page {
  max-width: 100%;
  border-radius: 4px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
  display: block;
}

.loading {
  text-align: center;
  color: rgba(255,255,255,0.3);
  font-size: 13px;
  padding: 40px;
}
</style>
