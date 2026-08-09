import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 180_000, // 3 min — Ollama can be slow on first run
})

export default api
