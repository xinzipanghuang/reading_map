// frontend/src/stores/projectStore.js
import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { api } from '../api'

export const useProjectStore = defineStore('project', () => {
  // --- 状态 ---
  const currentProjectId = ref(null)
  const projectData = ref({ chapters: [], edges: [] })
  
  // 核心优化：节点位置缓存表 Map<nodeId, {x, y, w, h}>
  // 这是一个纯数据对象，连线层直接读它，不需要查 DOM
  const nodeLayoutMap = reactive(new Map())
  
  // 画布容器的视口信息
  const canvasRect = ref({ top: 0, left: 0 })
  const canvasScroll = ref({ x: 0, y: 0 })
  
  // 🟢 新增：行列模式下的布局缓存（用于自由模式加载）
  // 结构：{ chapterId: { x, y, width, height }, sectionId: { x, y, width, height }, nodeId: { x, y, width, height } }
  const rowColumnLayoutCache = reactive({
    chapters: new Map(), // Map<chapterId, {x, y, width, height}>
    sections: new Map(), // Map<sectionId, {x, y, width, height}>
    nodes: new Map()     // Map<nodeId, {x, y, width, height}>
  })

  // --- Actions ---
  
  // 加载项目
  const loadProject = async (id) => {
    if (!id) return
    try {
      const res = await api.getProject(id)
      // 保持引用更新
      projectData.value = res.data
      currentProjectId.value = id
    } catch (e) {
      console.error('Failed to load project:', e)
    }
  }

  // 更新节点在屏幕上的绝对位置 (由组件汇报)
  const updateNodeLayout = (nodeId, rect) => {
    // 简单防抖：只有数值变化超过 1px 才更新，避免浮点数抖动
    const current = nodeLayoutMap.get(nodeId)
    if (
      !current || 
      Math.abs(current.x - rect.x) > 1 || 
      Math.abs(current.y - rect.y) > 1 ||
      Math.abs(current.w - rect.width) > 1 ||
      Math.abs(current.h - rect.height) > 1
    ) {
      nodeLayoutMap.set(nodeId, {
        x: rect.x, // 视口绝对坐标 (getBoundingClientRect)
        y: rect.y,
        w: rect.width,
        h: rect.height
      })
    }
  }

  // 更新画布信息
  const updateCanvasState = (rect, scroll) => {
    canvasRect.value = rect
    canvasScroll.value = scroll
  }

  // 获取特定节点的“画布内相对坐标” (用于 SVG 连线计算)
  const getNodeRelativePosition = (nodeId) => {
    const layout = nodeLayoutMap.get(nodeId)
    if (!layout) return null
    
    // 计算公式：视口坐标 - 画布容器视口坐标 + 容器滚动偏移
    // 这样算出的是相对于 SVG 原点 (0,0) 的坐标
    return {
      x: layout.x - canvasRect.value.left + canvasScroll.value.x + layout.w / 2, // 中心点 X
      y: layout.y - canvasRect.value.top + canvasScroll.value.y + layout.h / 2,  // 中心点 Y
      w: layout.w,
      h: layout.h
    }
  }

  // 🟢 新增：保存行列模式下的布局到缓存
  const saveRowColumnLayout = (type, id, layout) => {
    if (type === 'chapter') {
      rowColumnLayoutCache.chapters.set(id, layout)
    } else if (type === 'section') {
      rowColumnLayoutCache.sections.set(id, layout)
    } else if (type === 'node') {
      rowColumnLayoutCache.nodes.set(id, layout)
    }
  }
  
  // 🟢 新增：从缓存获取布局
  const getRowColumnLayout = (type, id) => {
    if (type === 'chapter') {
      return rowColumnLayoutCache.chapters.get(id) || null
    } else if (type === 'section') {
      return rowColumnLayoutCache.sections.get(id) || null
    } else if (type === 'node') {
      return rowColumnLayoutCache.nodes.get(id) || null
    }
    return null
  }
  
  // 🟢 新增：清除布局缓存
  const clearRowColumnLayout = () => {
    rowColumnLayoutCache.chapters.clear()
    rowColumnLayoutCache.sections.clear()
    rowColumnLayoutCache.nodes.clear()
  }

  return {
    currentProjectId,
    projectData,
    nodeLayoutMap,
    rowColumnLayoutCache,
    loadProject,
    updateNodeLayout,
    updateCanvasState,
    getNodeRelativePosition,
    saveRowColumnLayout,
    getRowColumnLayout,
    clearRowColumnLayout
  }
})