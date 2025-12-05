import axios from 'axios'

// 自动检测 API URL：如果设置了环境变量则使用，否则根据当前页面 hostname 自动构建
const getApiUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // 在开发环境中，使用当前页面的 hostname 和端口 8000
  if (import.meta.env.DEV) {
    const hostname = window.location.hostname
    return `http://${hostname}:8000`
  }
  
  // 生产环境使用当前页面的 origin
  return window.location.origin.replace(/:\d+$/, ':8000')
}

const API_URL = getApiUrl()

export const api = {
  getProjects: () => axios.get(`${API_URL}/projects`),
  createProject: (name) => axios.post(`${API_URL}/projects`, { name }),
  updateProject: (projectId, name) => axios.put(`${API_URL}/projects/${projectId}`, { name }),
  deleteProject: (projectId) => axios.delete(`${API_URL}/projects/${projectId}`),
  getProject: (id) => axios.get(`${API_URL}/projects/${id}`),
  addChapter: (projectId, chapterName) => 
    axios.post(`${API_URL}/projects/${projectId}/chapters`, { chapter_name: chapterName }),
  updateChapter: (projectId, chapterId, data) =>
    axios.put(`${API_URL}/projects/${projectId}/chapters/${chapterId}`, data),
  deleteChapter: (projectId, chapterId) => 
    axios.delete(`${API_URL}/projects/${projectId}/chapters/${chapterId}`),
  addSection: (projectId, chapterId, sectionName) => 
    axios.post(`${API_URL}/projects/${projectId}/sections`, { 
      chapter_id: chapterId, 
      section_name: sectionName 
    }),
  updateSection: (projectId, sectionId, name) =>
    axios.put(`${API_URL}/projects/${projectId}/sections/${sectionId}`, { name }),
  deleteSection: (projectId, sectionId) => 
    axios.delete(`${API_URL}/projects/${projectId}/sections/${sectionId}`),
  addNode: (projectId, chapterId, sectionId, nodeName, nodeContent = '') => 
    axios.post(`${API_URL}/projects/${projectId}/nodes`, {
      chapter_id: chapterId,
      section_id: sectionId,
      node_name: nodeName,
      node_content: nodeContent
    }),
  addEdge: (projectId, source, target, label = '') => 
    axios.post(`${API_URL}/projects/${projectId}/edges`, { source, target, label }),
  deleteEdge: (projectId, source, target) =>
    axios.delete(`${API_URL}/projects/${projectId}/edges`, { data: { source, target } }),
  updateEdge: (projectId, source, target, label) =>
    axios.put(`${API_URL}/projects/${projectId}/edges`, { source, target, label }),
  reorderNodes: (projectId, sectionId, nodeIds) =>
    axios.post(`${API_URL}/projects/${projectId}/nodes/reorder`, {
      section_id: sectionId,
      node_ids: nodeIds
    }),
  reorderSections: (projectId, chapterId, sectionIds) =>
    axios.post(`${API_URL}/projects/${projectId}/sections/reorder`, {
      chapter_id: chapterId,
      section_ids: sectionIds
    }),
  reorderChapters: (projectId, chapterIds) =>
    axios.post(`${API_URL}/projects/${projectId}/chapters/reorder`, {
      chapter_ids: chapterIds
    }),
  updateNodePosition: (projectId, nodeId, sectionId, x, y) =>
    axios.put(`${API_URL}/projects/${projectId}/nodes/position`, {
      node_id: nodeId,
      section_id: sectionId,
      x: x,
      y: y
    }),
  analyzeGraph: (projectId, focusNode) => 
    axios.get(`${API_URL}/projects/${projectId}/graph_analysis?focus_node=${focusNode}`),
  exportProject: (projectId) =>
    axios.get(`${API_URL}/projects/${projectId}/export`, {
      responseType: 'blob'
    }),
  importProject: (file, projectName) => {
    const formData = new FormData()
    formData.append('file', file)
    if (projectName) {
      formData.append('project_name', projectName)
    }
    return axios.post(`${API_URL}/projects/import`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

