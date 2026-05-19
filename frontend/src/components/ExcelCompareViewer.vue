<template>
  <div class="overlay" @keydown.esc="$emit('close')" tabindex="0" ref="overlayRef">
    <!-- Header -->
    <div class="viewer-header">
      <div class="sheet-tabs">
        <button
          v-for="sheet in sheets"
          :key="sheet"
          class="tab"
          :class="{ active: activeSheet === sheet }"
          @click="activeSheet = sheet"
        >{{ sheet }}</button>
      </div>
      <div class="header-actions">
        <a :href="downloadUrl" download class="btn-dl">↓ 下载译文</a>
        <button class="btn-close" @click="$emit('close')">✕</button>
      </div>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-wrap">
      <div class="spinner" />
      <span>加载对比数据...</span>
    </div>

    <!-- 分屏表格 -->
    <div v-else class="panes">
      <!-- 左：原文 -->
      <div class="pane">
        <div class="pane-label">原文</div>
        <div class="table-wrap" ref="leftScroll" @scroll="onLeftScroll">
          <table v-if="origData[activeSheet]">
            <tbody>
              <tr v-for="(row, ri) in origData[activeSheet]" :key="ri">
                <td v-for="(cell, ci) in row" :key="ci" :class="{ changed: isCellChanged(ri, ci) }">
                  {{ cell }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="divider" />

      <!-- 右：译文 -->
      <div class="pane">
        <div class="pane-label pane-label-right">译文</div>
        <div class="table-wrap" ref="rightScroll" @scroll="onRightScroll">
          <table v-if="transData[activeSheet]">
            <tbody>
              <tr v-for="(row, ri) in transData[activeSheet]" :key="ri">
                <td v-for="(cell, ci) in row" :key="ci" :class="{ changed: isCellChanged(ri, ci), translated: isCellChanged(ri, ci) }">
                  {{ cell }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getDownloadUrl } from '../api.js'
import * as XLSX from 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/+esm'

const props = defineProps({
  taskId: String,
  originalFile: File,
})
defineEmits(['close'])

const downloadUrl = getDownloadUrl(props.taskId)
const overlayRef = ref(null)
const leftScroll = ref(null)
const rightScroll = ref(null)

const loading = ref(true)
const sheets = ref([])
const activeSheet = ref('')
const origData = ref({})   // { sheetName: [[cell,...], ...] }
const transData = ref({})

let syncingLeft = false
let syncingRight = false

function onLeftScroll() {
  if (syncingRight) return
  syncingLeft = true
  rightScroll.value.scrollTop = leftScroll.value.scrollTop
  rightScroll.value.scrollLeft = leftScroll.value.scrollLeft
  syncingLeft = false
}
function onRightScroll() {
  if (syncingLeft) return
  syncingRight = true
  leftScroll.value.scrollTop = rightScroll.value.scrollTop
  leftScroll.value.scrollLeft = rightScroll.value.scrollLeft
  syncingRight = false
}

function isCellChanged(ri, ci) {
  const o = origData.value[activeSheet.value]?.[ri]?.[ci]
  const t = transData.value[activeSheet.value]?.[ri]?.[ci]
  return o !== t && (o || t)
}

function parseWorkbook(wb) {
  const result = {}
  for (const name of wb.SheetNames) {
    const ws = wb.Sheets[name]
    const rows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' })
    result[name] = rows
  }
  return result
}

async function load() {
  loading.value = true
  try {
    // 读原文
    const origBuf = await props.originalFile.arrayBuffer()
    const origWb = XLSX.read(origBuf, { type: 'array' })
    origData.value = parseWorkbook(origWb)
    sheets.value = origWb.SheetNames
    activeSheet.value = sheets.value[0]

    // 读译文
    const transResp = await fetch(downloadUrl)
    const transBuf = await transResp.arrayBuffer()
    const transWb = XLSX.read(transBuf, { type: 'array' })
    transData.value = parseWorkbook(transWb)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  overlayRef.value?.focus()
  load()
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
  padding: 0 16px;
  height: 52px;
  background: rgba(255,255,255,0.04);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  flex-shrink: 0;
  gap: 12px;
}

.sheet-tabs { display: flex; gap: 4px; overflow-x: auto; }
.tab {
  padding: 6px 14px;
  background: none;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  color: rgba(255,255,255,0.45);
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.tab:hover { border-color: rgba(160,110,255,0.4); color: rgba(255,255,255,0.75); }
.tab.active { background: rgba(99,102,241,0.2); border-color: rgba(99,102,241,0.6); color: white; }

.header-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.btn-dl {
  padding: 6px 14px;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  color: white; text-decoration: none;
  border-radius: 7px; font-size: 13px; font-weight: 500;
  transition: opacity 0.15s;
}
.btn-dl:hover { opacity: 0.85; }
.btn-close {
  width: 30px; height: 30px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 7px; color: rgba(255,255,255,0.5);
  font-size: 13px; cursor: pointer; transition: all 0.15s;
  display: flex; align-items: center; justify-content: center;
}
.btn-close:hover { background: rgba(255,255,255,0.14); color: white; }

.loading-wrap {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 14px;
  color: rgba(255,255,255,0.4); font-size: 14px;
}
.spinner {
  width: 32px; height: 32px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #7c3aed;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.panes { display: flex; flex: 1; overflow: hidden; }

.pane {
  flex: 1; display: flex; flex-direction: column; overflow: hidden;
  background: #0e0e20;
}

.pane-label {
  padding: 8px 16px;
  font-size: 11px; font-weight: 600;
  color: rgba(255,255,255,0.3);
  letter-spacing: 0.8px; text-transform: uppercase;
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  flex-shrink: 0;
}
.pane-label-right { text-align: right; }

.table-wrap {
  flex: 1; overflow: auto;
  padding: 0;
}
.table-wrap::-webkit-scrollbar { width: 5px; height: 5px; }
.table-wrap::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }

table {
  border-collapse: collapse;
  width: max-content;
  min-width: 100%;
  font-size: 13px;
}

td {
  padding: 8px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  border-right: 1px solid rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.75);
  white-space: nowrap;
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
}

td.changed { background: rgba(99,60,180,0.12); }
td.translated { color: #c4b5fd; }

tr:hover td { background: rgba(255,255,255,0.03); }
tr:hover td.changed { background: rgba(99,60,180,0.2); }

.divider { width: 1px; background: rgba(255,255,255,0.07); flex-shrink: 0; }
</style>
