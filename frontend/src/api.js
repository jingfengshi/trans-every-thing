import axios from 'axios'

const BASE = '/api'

export async function submitTranslate(file, engine, targetLang, stylePrompt = '') {
  const form = new FormData()
  form.append('file', file)
  form.append('engine', engine)
  form.append('target_lang', targetLang)
  if (stylePrompt.trim()) form.append('style_prompt', stylePrompt.trim())
  const res = await axios.post(`${BASE}/translate`, form)
  return res.data
}

export async function getStatus(taskId) {
  const res = await axios.get(`${BASE}/status/${taskId}`)
  return res.data
}

export function getDownloadUrl(taskId) {
  return `${BASE}/download/${taskId}`
}
