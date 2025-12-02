import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
  getProjects: () => axios.get(`${API_URL}/projects`),
  createProject: (name) => axios.post(`${API_URL}/projects`, { name }),
  getProject: (id) => axios.get(`${API_URL}/projects/${id}`),
  addChapter: (projectId, chapterName) => 
    axios.post(`${API_URL}/projects/${projectId}/chapters`, { chapter_name: chapterName }),
  deleteChapter: (projectId, chapterId) => 
    axios.delete(`${API_URL}/projects/${projectId}/chapters/${chapterId}`),
  addSection: (projectId, chapterId, sectionName) => 
    axios.post(`${API_URL}/projects/${projectId}/sections`, { 
      chapter_id: chapterId, 
      section_name: sectionName 
    }),
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
  updateNodePosition: (projectId, nodeId, sectionId, x, y) =>
    axios.put(`${API_URL}/projects/${projectId}/nodes/position`, {
      node_id: nodeId,
      section_id: sectionId,
      x: x,
      y: y
    }),
  analyzeGraph: (projectId, focusNode) => 
    axios.get(`${API_URL}/projects/${projectId}/graph_analysis?focus_node=${focusNode}`)
}

