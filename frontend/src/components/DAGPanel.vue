<template>
  <div
    v-if="visible"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    @click.self="close"
  >
    <div class="bg-white rounded-lg shadow-2xl w-4/5 h-4/5 flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <div>
          <h3 class="text-lg font-bold text-gray-800">DAG 图谱: {{ nodeName }}</h3>
          <p class="text-sm text-gray-500 mt-1">显示节点及其所有相关路径</p>
        </div>
        <button
          @click="close"
          class="p-2 text-gray-400 hover:text-gray-600 transition rounded"
        >
          <i class="ph ph-x text-xl"></i>
        </button>
      </div>

      <!-- Graph Container -->
      <div class="flex-1 relative p-4 min-h-0">
        <div :id="containerId" class="w-full h-full border border-gray-200 rounded bg-white" style="min-height: 400px;"></div>
        
        <!-- Controls -->
        <div class="absolute bottom-6 right-6 flex gap-2">
          <button
            @click="fitGraph"
            class="bg-white p-2 rounded shadow text-gray-600 hover:text-blue-600 transition"
            title="自适应视图"
          >
            <i class="ph ph-corners-out"></i>
          </button>
          <button
            @click="resetView"
            class="bg-white p-2 rounded shadow text-gray-600 hover:text-blue-600 transition"
            title="重置视图"
          >
            <i class="ph ph-arrow-counter-clockwise"></i>
          </button>
        </div>
      </div>

      <!-- Legend -->
      <div class="p-4 border-t border-gray-200 bg-gray-50 flex flex-wrap gap-6 text-xs">
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 bg-blue-600 rounded-lg border-2 border-blue-700 shadow-sm"></div>
          <span class="font-medium text-gray-700">选中节点</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 bg-blue-100 rounded-lg border-2 border-blue-300 shadow-sm"></div>
          <span class="font-medium text-gray-700">相关节点（按章节颜色）</span>
        </div>
        <div class="flex items-center gap-2 ml-auto">
          <div class="w-6 h-0.5 bg-blue-500"></div>
          <span class="text-gray-500">主要连接</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-6 h-0.5 border-t-2 border-dashed border-gray-400"></div>
          <span class="text-gray-500">次要连接</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { DataSet, Network } from 'vis-network/standalone'
import axios from 'axios'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  nodeId: {
    type: String,
    default: null
  },
  nodeName: {
    type: String,
    default: ''
  },
  projectId: {
    type: String,
    default: null
  },
  projectData: {
    type: Object,
    default: () => ({ chapters: [], edges: [] })
  }
})

const emit = defineEmits(['close'])

let network = null
let nodesDataSet = null
let edgesDataSet = null

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

// 使用唯一的容器ID，避免多个实例冲突
const containerId = ref(`dag-network-container-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`)

const close = () => {
  emit('close')
}

// 获取所有节点及其章节信息
const getAllNodesWithChapter = () => {
  const nodes = []
  if (!props.projectData || !props.projectData.chapters) {
    return nodes
  }
  for (let chapterIndex = 0; chapterIndex < props.projectData.chapters.length; chapterIndex++) {
    const chapter = props.projectData.chapters[chapterIndex]
    if (!chapter.sections) continue
    for (let sectionIndex = 0; sectionIndex < chapter.sections.length; sectionIndex++) {
      const section = chapter.sections[sectionIndex]
      if (!section.nodes) continue
      for (const node of section.nodes) {
        nodes.push({
          id: node.id,
          name: node.name || node.id, // 确保有 name 属性
          label: node.name || node.id, // vis-network 使用 label
          chapterId: chapter.id,
          chapterIndex: chapterIndex,
          sectionIndex: sectionIndex,
          // 计算层级：chapter 作为主要层级，section 作为次要层级
          // 使用小数来区分同一 chapter 内的不同 section
          level: chapterIndex + sectionIndex * 0.1
        })
      }
    }
  }
  return nodes
}

// 获取与当前节点相关的所有节点ID（包括祖先、后代和当前节点）
const getRelatedNodeIds = (highlightIds) => {
  const relatedIds = new Set([props.nodeId])
  
  // 添加所有高亮节点（祖先和后代）
  highlightIds.forEach(id => relatedIds.add(id))
  
  // 使用广度优先搜索，找出所有与相关节点有连接的节点
  // 这样可以确保只显示与当前节点有路径连接的节点
  const edges = props.projectData.edges || []
  let changed = true
  
  while (changed) {
    changed = false
    edges.forEach(edge => {
      const source = edge.source || edge[0]
      const target = edge.target || edge[1]
      
      if (relatedIds.has(source) && !relatedIds.has(target)) {
        relatedIds.add(target)
        changed = true
      }
      if (relatedIds.has(target) && !relatedIds.has(source)) {
        relatedIds.add(source)
        changed = true
      }
    })
  }
  
  return Array.from(relatedIds)
}

const renderGraph = async () => {
  if (!props.nodeId || !props.projectId) {
    console.log('Missing nodeId or projectId:', { nodeId: props.nodeId, projectId: props.projectId })
    return
  }

  await nextTick()
  const container = document.getElementById(containerId.value)
  if (!container) {
    console.error('Container not found:', containerId.value)
    return
  }

  // 清理之前的网络实例
  if (network) {
    try {
      network.destroy()
    } catch (e) {
      console.warn('Error destroying network:', e)
    }
    network = null
  }

  try {
    // 获取图谱分析
    const res = await axios.get(
      `${API_URL}/projects/${props.projectId}/graph_analysis?focus_node=${props.nodeId}`
    )
    const highlightIds = res.data.highlight || []
    
    // 获取所有相关节点ID（只显示与当前节点有连接的节点）
    const relatedNodeIds = getRelatedNodeIds(highlightIds)

    // 章节颜色映射（Tailwind 风格）
    const chapterColors = [
      { bg: '#dbeafe', border: '#93c5fd', text: '#1e40af', icon: '#3b82f6' }, // blue
      { bg: '#fed7aa', border: '#fdba74', text: '#9a3412', icon: '#f97316' }, // orange
      { bg: '#bbf7d0', border: '#86efac', text: '#166534', icon: '#22c55e' }, // green
      { bg: '#e9d5ff', border: '#c084fc', text: '#6b21a8', icon: '#a855f7' }, // purple
      { bg: '#c7d2fe', border: '#a5b4fc', text: '#3730a3', icon: '#6366f1' }  // indigo
    ]

    // 创建节点（只包含相关节点）
    const allNodesWithChapter = getAllNodesWithChapter()
    const filteredNodes = allNodesWithChapter.filter(n => relatedNodeIds.includes(n.id))
    
    // 获取所有唯一的层级值，用于映射到连续的层级
    const uniqueLevels = [...new Set(filteredNodes.map(n => n.level))].sort((a, b) => a - b)
    const levelMap = new Map()
    uniqueLevels.forEach((level, index) => {
      levelMap.set(level, index)
    })
    
    const nodes = filteredNodes.map(n => {
      const chapterColor = chapterColors[n.chapterIndex % chapterColors.length]
      const isSelected = n.id === props.nodeId
      
      // 将原始层级映射到连续的整数层级（0, 1, 2, ...）
      const mappedLevel = levelMap.get(n.level) || 0
      
      return {
        id: n.id,
        label: n.name,
        level: mappedLevel, // 使用映射后的连续层级
        color: {
          background: isSelected ? '#3b82f6' : chapterColor.bg,
          border: isSelected ? '#1e40af' : chapterColor.border,
          highlight: {
            background: isSelected ? '#60a5fa' : chapterColor.bg,
            border: isSelected ? '#2563eb' : chapterColor.icon
          }
        },
        borderWidth: isSelected ? 3 : 2,
        font: {
          color: isSelected ? '#ffffff' : chapterColor.text,
          size: isSelected ? 16 : 14,
          face: 'Segoe UI',
          bold: isSelected
        },
        shadow: {
          enabled: true,
          color: 'rgba(0,0,0,0.15)',
          size: isSelected ? 8 : 5,
          x: 2,
          y: 2
        },
        shape: 'box',
        margin: isSelected ? 15 : 12
      }
    })

    // 创建边（只包含相关节点之间的边）
    const allEdges = props.projectData.edges || []
    const edges = allEdges
      .filter(e => {
        const source = e.source || e[0]
        const target = e.target || e[1]
        return relatedNodeIds.includes(source) && relatedNodeIds.includes(target)
      })
      .map(e => {
        const source = e.source || e[0]
        const target = e.target || e[1]
        const label = e.label || ''
        const isHighlighted = highlightIds.includes(source) && highlightIds.includes(target)
        
        return {
          from: source,
          to: target,
          label: label,
          arrows: {
            to: {
              enabled: true,
              scaleFactor: 0.7,
              type: 'arrow'
            }
          },
          color: {
            color: isHighlighted ? '#3b82f6' : '#94a3b8',
            highlight: isHighlighted ? '#60a5fa' : '#cbd5e1',
            opacity: isHighlighted ? 1 : 0.7
          },
          width: isHighlighted ? 2 : 1,
          dashes: !isHighlighted,
          font: {
            size: 11,
            align: 'middle',
            color: '#64748b'
          },
          smooth: {
            type: 'cubicBezier',
            forceDirection: 'vertical',
            roundness: 0.5
          }
        }
      })

    nodesDataSet = new DataSet(nodes)
    edgesDataSet = new DataSet(edges)
    const data = { nodes: nodesDataSet, edges: edgesDataSet }

    const options = {
      layout: {
        hierarchical: {
          enabled: true,
          direction: 'UD', // 从上到下
          sortMethod: 'directed',
          // 增加层级间距，使 chapter 之间更分明
          levelSeparation: 200,
          // 增加节点间距，使同一 section 内的节点更清晰
          nodeSpacing: 150,
          // 增加树间距，使不同分支更分明
          treeSpacing: 250,
          blockShifting: true,
          edgeMinimization: true,
          parentCentralization: true,
          // 使用自定义层级
          shakeTowards: 'leaves'
        }
      },
      nodes: {
        shape: 'box',
        margin: 12,
        font: { 
          face: 'Segoe UI',
          multi: false
        },
        shadow: {
          enabled: true,
          color: 'rgba(0,0,0,0.15)',
          size: 5,
          x: 2,
          y: 2
        },
        widthConstraint: { 
          maximum: 250,
          minimum: 120
        },
        heightConstraint: {
          minimum: 50
        },
        borderWidth: 2
      },
      edges: {
        smooth: { 
          type: 'cubicBezier', 
          forceDirection: 'vertical', 
          roundness: 0.5 
        },
        font: { 
          size: 11, 
          align: 'middle',
          color: '#64748b'
        },
        arrows: {
          to: {
            enabled: true,
            scaleFactor: 1.2,
            type: 'arrow'
          }
        },
        color: {
          inherit: false
        }
      },
      physics: false,
      interaction: {
        dragNodes: true,
        dragView: true,
        zoomView: true,
        hover: true,
        tooltipDelay: 200
      },
      configure: {
        enabled: false
      }
    }

    network = new Network(container, data, options)

    // 自动适应视图
    setTimeout(() => {
      if (network) {
        network.fit({ animation: { duration: 500 } })
      }
    }, 200)
  } catch (e) {
    console.error('Failed to render DAG:', e)
    alert('渲染DAG图失败: ' + (e.message || '未知错误'))
  }
}

const fitGraph = () => {
  if (network) {
    network.fit({ animation: true })
  }
}

const resetView = () => {
  if (network) {
    network.fit({ animation: true })
    network.moveTo({ position: { x: 0, y: 0 }, scale: 1, animation: true })
  }
}

let renderTimeout = null

watch([() => props.visible, () => props.nodeId, () => props.projectId], ([newVisible, newNodeId, newProjectId]) => {
  // 清理之前的定时器
  if (renderTimeout) {
    clearTimeout(renderTimeout)
    renderTimeout = null
  }
  
  if (newVisible && newNodeId && newProjectId) {
    // 延迟一下确保DOM已渲染，但减少延迟时间
    renderTimeout = setTimeout(() => {
      nextTick(() => {
        renderGraph()
        renderTimeout = null
      })
    }, 100)
  } else if (!newVisible && network) {
    // 关闭时清理
    try {
      network.destroy()
      network = null
      nodesDataSet = null
      edgesDataSet = null
    } catch (e) {
      console.warn('Error destroying network on close:', e)
    }
  }
}, { immediate: false })

onMounted(() => {
  if (props.visible && props.nodeId && props.projectId) {
    setTimeout(() => {
      renderGraph()
    }, 100)
  }
})

onUnmounted(() => {
  if (network) {
    try {
      network.destroy()
      network = null
    } catch (e) {
      console.warn('Error destroying network on unmount:', e)
    }
  }
})
</script>

