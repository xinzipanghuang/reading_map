<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden">
    <!-- Left Sidebar: Projects -->
    <ProjectSidebar
      :projects="projects"
      :current-project-id="currentProjectId"
      @project-selected="handleProjectSelected"
      @project-created="handleProjectCreated"
    />

    <!-- Right Canvas: Knowledge Map -->
    <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Header -->
      <header class="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center shadow-sm">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">
            {{ currentProject?.name || '知识图谱构建器' }}
          </h1>
          <p v-if="currentProject" class="text-sm text-gray-600 mt-1">
            从直觉到综合：构建你的知识路径
          </p>
      </div>
      <div class="flex items-center gap-4">
          <!-- Link Mode Status -->
          <div
            v-if="linkMode.source"
            class="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200 flex items-center gap-3 text-sm"
          >
            <span class="font-bold text-blue-600">{{ getNodeName(linkMode.source) }}</span>
            <i class="ph ph-arrow-right text-gray-400"></i>
            <span v-if="!linkMode.target" class="text-gray-400">选择终点...</span>
            <span v-else class="font-bold text-green-600">{{ getNodeName(linkMode.target) }}</span>
        <button 
              v-if="linkMode.target"
              @click="createEdge"
              class="ml-2 bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition text-xs"
        >
              连接
            </button>
            <button @click="resetLinkMode" class="text-gray-400 hover:text-gray-600">
              <i class="ph ph-x"></i>
        </button>
          </div>
          <div v-else class="text-sm text-gray-500">
            点击节点选择起点，再点击另一个节点创建连接 | 双击节点查看 DAG
          </div>
      </div>
    </header>

      <!-- Canvas Area -->
      <div class="flex-1 overflow-y-auto p-4 relative" v-if="currentProjectId" ref="canvasContainer">
        <!-- Connection Lines SVG Overlay (统一处理所有连接) -->
        <svg
          v-if="crossChapterEdges.length > 0"
          class="absolute inset-0 pointer-events-none z-10"
          style="overflow: visible;"
          :width="canvasWidth"
          :height="canvasHeight"
        >
          <defs>
            <marker
              id="cross-chapter-arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#cbd5e1" class="transition-colors duration-200" />
            </marker>
            <marker
              id="cross-chapter-arrowhead-hover"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#3b82f6" />
            </marker>
            <!-- 阴影滤镜，用于 hover 时的立体效果 -->
            <filter id="cross-chapter-glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          <!-- 非 hover 状态的边缘（先渲染，在底层） -->
          <g
            v-for="edge in crossChapterEdges.filter(e => !hoveredCrossEdge || hoveredCrossEdge.source !== e.source || hoveredCrossEdge.target !== e.target)"
            :key="`${edge.source}-${edge.target}`"
            @click.stop="showEdgeContextMenu($event, edge)"
            @contextmenu.prevent="showEdgeContextMenu($event, edge)"
            @mouseenter="hoveredCrossEdge = { source: edge.source, target: edge.target }"
            @mouseleave="hoveredCrossEdge = null"
            class="cursor-pointer transition-all"
            style="pointer-events: all;"
          >
            <!-- 背景线（用于增加 hover 区域） -->
            <path
              :d="getEdgePath(edge)"
              stroke="transparent"
              stroke-width="16"
              fill="none"
              class="transition-all duration-200"
            />
            <!-- 实际连接线 -->
            <path
              :d="getEdgePath(edge)"
              stroke="#cbd5e1"
              stroke-width="2.5"
              stroke-dasharray="4 4"
              marker-end="url(#cross-chapter-arrowhead)"
              fill="none"
              class="transition-all duration-200 ease-in-out opacity-50"
            />
            <!-- 标签背景 -->
            <rect
              v-if="edge.label"
              :x="getEdgeLabelX(edge) - 40"
              :y="getEdgeLabelY(edge) - 12"
              :width="edge.label ? 80 : 70"
              :height="(edge.label ? edge.label.split('\n').length : 1) * 16 + 12"
              fill="white"
              fill-opacity="0.9"
              stroke="#cbd5e1"
              stroke-width="1.5"
              rx="8"
              class="cursor-pointer transition-all duration-200 shadow-sm hover:fill-opacity-100"
              style="pointer-events: all;"
              @click.stop="showEdgeContextMenu($event, edge)"
              @contextmenu.prevent="showEdgeContextMenu($event, edge)"
            />
            <!-- 标签文字 -->
            <text
              v-if="edge.label"
              :x="getEdgeLabelX(edge)"
              :y="getEdgeLabelY(edge)"
              class="text-xs cursor-pointer transition-all duration-200 fill-gray-500 font-medium"
              style="pointer-events: all;"
              text-anchor="middle"
              dominant-baseline="middle"
              @click.stop="showEdgeContextMenu($event, edge)"
              @contextmenu.prevent="showEdgeContextMenu($event, edge)"
            >
              <tspan
                v-for="(line, i) in edge.label.split('\n')"
                :key="i"
                :x="getEdgeLabelX(edge)"
                :dy="i === 0 ? 0 : 16"
              >
                {{ line }}
              </tspan>
            </text>
          </g>
          <!-- hover 状态的背景线（用于鼠标事件，保留在原 SVG 中） -->
          <g
            v-for="edge in crossChapterEdges.filter(e => hoveredCrossEdge && hoveredCrossEdge.source === e.source && hoveredCrossEdge.target === e.target)"
            :key="`hover-bg-${edge.source}-${edge.target}`"
            @click.stop="showEdgeContextMenu($event, edge)"
            @contextmenu.prevent="showEdgeContextMenu($event, edge)"
            @mouseenter="hoveredCrossEdge = { source: edge.source, target: edge.target }"
            @mouseleave="hoveredCrossEdge = null"
            class="cursor-pointer transition-all"
            style="pointer-events: all;"
          >
            <!-- 背景线（用于增加 hover 区域） -->
            <path
              :d="getEdgePath(edge)"
              stroke="transparent"
              stroke-width="20"
              fill="none"
              class="transition-all duration-200"
            />
          </g>
        </svg>
        <!-- Hover 状态的连接线和标签层（单独的 SVG，更高的 z-index） -->
        <svg
          v-if="crossChapterEdges.some(e => hoveredCrossEdge && hoveredCrossEdge.source === e.source && hoveredCrossEdge.target === e.target)"
          class="absolute inset-0 pointer-events-none z-20"
          style="overflow: visible;"
          :width="canvasWidth"
          :height="canvasHeight"
        >
          <defs>
            <marker
              id="cross-chapter-arrowhead-hover-top"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="#3b82f6" />
            </marker>
            <!-- 阴影滤镜，用于 hover 时的立体效果 -->
            <filter id="cross-chapter-glow-top" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          <g
            v-for="edge in crossChapterEdges.filter(e => hoveredCrossEdge && hoveredCrossEdge.source === e.source && hoveredCrossEdge.target === e.target)"
            :key="`hover-top-${edge.source}-${edge.target}`"
          >
            <!-- 阴影线（hover 时的发光效果） -->
            <path
              :d="getEdgePath(edge)"
              stroke="#3b82f6"
              stroke-width="6"
              stroke-opacity="0.25"
              fill="none"
              filter="url(#cross-chapter-glow-top)"
              class="transition-all duration-200"
            />
            <!-- 实际连接线（hover 状态，置顶） -->
            <path
              :d="getEdgePath(edge)"
              stroke="#3b82f6"
              stroke-width="3"
              stroke-dasharray="4 4"
              marker-end="url(#cross-chapter-arrowhead-hover-top)"
              fill="none"
              class="transition-all duration-200 ease-in-out opacity-100 drop-shadow-sm"
            />
            <!-- 标签背景（hover 状态，置顶） -->
            <rect
              v-if="edge.label"
              :x="getEdgeLabelX(edge) - 40"
              :y="getEdgeLabelY(edge) - 12"
              :width="edge.label ? 80 : 70"
              :height="(edge.label ? edge.label.split('\n').length : 1) * 16 + 12"
              fill="#dbeafe"
              fill-opacity="0.98"
              stroke="#3b82f6"
              stroke-width="2"
              rx="8"
              class="cursor-pointer transition-all duration-200 shadow-md"
              style="pointer-events: all;"
              @click.stop="showEdgeContextMenu($event, edge)"
              @contextmenu.prevent="showEdgeContextMenu($event, edge)"
            />
            <!-- 标签文字（hover 状态，置顶） -->
            <text
              v-if="edge.label"
              :x="getEdgeLabelX(edge)"
              :y="getEdgeLabelY(edge)"
              class="text-xs cursor-pointer transition-all duration-200 fill-blue-700 font-bold"
              style="pointer-events: all;"
              text-anchor="middle"
              dominant-baseline="middle"
              @click.stop="showEdgeContextMenu($event, edge)"
              @contextmenu.prevent="showEdgeContextMenu($event, edge)"
            >
              <tspan
                v-for="(line, i) in edge.label.split('\n')"
                :key="i"
                :x="getEdgeLabelX(edge)"
                :dy="i === 0 ? 0 : 16"
              >
                {{ line }}
              </tspan>
            </text>
          </g>
        </svg>
        <!-- Empty State -->
        <div v-if="projectData.chapters.length === 0" class="text-center py-20">
          <i class="ph ph-graph text-6xl text-gray-300 mb-4"></i>
          <p class="text-gray-500 mb-6">还没有章节，开始添加第一个章节吧</p>
          <div class="flex gap-2 justify-center">
            <input
              v-model="newChapterName"
              @keyup.enter="addChapter"
              type="text"
              placeholder="输入新章节名称 (如: 第一章)"
              class="border border-gray-300 rounded px-4 py-2 focus:outline-none focus:border-blue-500"
            />
              <button 
              @click="addChapter"
              class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
            >
              添加章节
              </button>
          </div>
        </div>

        <!-- Chapters -->
        <div v-if="projectData.chapters && projectData.chapters.length > 0" class="max-w-7xl mx-auto space-y-6 px-2">
          <ChapterSection
            v-for="(chapter, index) in projectData.chapters"
            :key="chapter.id"
            :chapter="chapter"
            :chapter-index="index + 1"
            :is-last="index === projectData.chapters.length - 1"
            :selected-node-id="linkMode.source || linkMode.target"
            :link-source="linkMode.source"
            :link-target="linkMode.target"
            :edges="projectData.edges"
            :node-positions="nodePositions"
            :project-id="currentProjectId"
            @update-node-positions="(positions) => Object.assign(nodePositions, positions)"
            @add-section="handleAddSection"
            @delete-chapter="handleDeleteChapter"
            @delete-section="handleDeleteSection"
            @add-node="handleAddNode"
            @edit-node="handleEditNode"
            @delete-node="handleDeleteNode"
            @node-click="(nodeId, event) => handleNodeClick(nodeId, event)"
            @node-dblclick="showDAGForNode"
            @node-dragging="handleNodeDragging"
            @node-drag-end="handleNodeDragEnd"
          />

          <!-- Add Chapter Button -->
          <div v-if="projectData.chapters.length > 0" class="flex justify-center">
            <button 
              @click="showAddChapterModal = true"
              class="px-6 py-3 rounded-lg border-2 border-dashed border-gray-300 text-gray-400 hover:border-blue-400 hover:text-blue-600 transition flex items-center gap-2"
            >
              <i class="ph ph-plus-circle"></i>
              添加新章节
            </button>
          </div>
        </div>
        </div>

      <!-- Empty Project State -->
    <div v-if="!currentProjectId" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <i class="ph ph-graph text-6xl text-gray-300 mb-4"></i>
          <p class="text-gray-500">请从左侧选择一个项目或创建新项目</p>
        </div>
      </div>
    </div>

    <!-- Add Chapter Modal -->
    <div 
      v-if="showAddChapterModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" 
      @click.self="showAddChapterModal = false"
    >
      <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4">添加章节</h3>
        <input 
          v-model="newChapterName"
          @keyup.enter="addChapter"
          class="w-full border p-2 rounded mb-4 focus:outline-none focus:border-blue-500" 
          placeholder="章节名称 (如: 第一章：基础概念)"
        />
        <div class="flex justify-end gap-2">
          <button 
            @click="showAddChapterModal = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition"
          >
            取消
          </button>
          <button 
            @click="addChapter"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            创建
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Node Modal -->
    <div 
      v-if="editingNode"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" 
      @click.self="editingNode = null"
    >
      <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4">编辑节点</h3>
        <input 
          v-model="editNodeName"
          class="w-full border p-2 rounded mb-2 focus:outline-none focus:border-blue-500"
          placeholder="节点名称"
        />
        <textarea
          v-model="editNodeContent"
          class="w-full border p-2 rounded mb-4 focus:outline-none focus:border-blue-500" 
          placeholder="备注/内容"
          rows="3"
        ></textarea>
        <div class="flex justify-end gap-2">
          <button 
            @click="editingNode = null"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition"
          >
            取消
          </button>
          <button 
            @click="saveNodeEdit"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            保存
          </button>
        </div>
      </div>
    </div>

    <!-- DAG Panel -->
    <DAGPanel
      :visible="showDAGPanel"
      :node-id="selectedNodeForDAG"
      :node-name="selectedNodeNameForDAG"
      :project-id="currentProjectId"
      :project-data="projectData"
      @close="showDAGPanel = false"
    />
    
    <!-- 连接线菜单（点击或右键显示） -->
    <div
      v-if="edgeContextMenu.show"
      class="fixed bg-white border border-gray-200 rounded-lg shadow-xl py-2 z-50 min-w-[140px]"
      :style="{
        left: edgeContextMenu.x + 'px',
        top: edgeContextMenu.y + 'px',
        transform: 'translate(-50%, -100%)',
        marginTop: '-8px'
      }"
      @click.stop
    >
      <div class="px-2 py-1.5 text-xs text-gray-500 border-b border-gray-100 mb-1">
        连接操作
      </div>
      <button
        @click="editEdge(edgeContextMenu.edge)"
        class="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition flex items-center gap-2 rounded"
      >
        <i class="ph ph-pencil text-base"></i>
        <span>编辑标签</span>
      </button>
      <button
        @click="deleteEdge(edgeContextMenu.edge)"
        class="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition flex items-center gap-2 rounded"
      >
        <i class="ph ph-trash text-base"></i>
        <span>删除连接</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import axios from 'axios'
import ProjectSidebar from './components/ProjectSidebar.vue'
import ChapterSection from './components/ChapterSection.vue'
import DAGPanel from './components/DAGPanel.vue'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const projects = ref([])
const currentProjectId = ref(null)
const projectData = reactive({ chapters: [], edges: [] })
const newChapterName = ref('')
const showAddChapterModal = ref(false)
const linkMode = reactive({ source: null, target: null })
const editingNode = ref(null)
const editNodeName = ref('')
const editNodeContent = ref('')
const showDAGPanel = ref(false)
const selectedNodeForDAG = ref(null)
const selectedNodeNameForDAG = ref('')
const canvasContainer = ref(null)
const canvasWidth = ref(window.innerWidth)
const canvasHeight = ref(window.innerHeight)
const editingEdge = ref(null)
const editEdgeLabel = ref('')
const nodePositions = ref({})
const hoveredCrossEdge = ref(null)
const edgeContextMenu = ref({ show: false, x: 0, y: 0, edge: null })
const edgeUpdateTrigger = ref(0)

const currentProject = computed(() => {
  return projects.value.find(p => p.id === currentProjectId.value)
})

// --- API Calls ---

const fetchProjects = async () => {
  try {
    const res = await axios.get(`${API_URL}/projects`)
    projects.value = res.data
    
    // 如果有项目但没有选中项目，自动选中第一个项目（优先选择 demo）
    if (projects.value.length > 0 && !currentProjectId.value) {
      const demoProject = projects.value.find(p => p.id === 'demo')
      if (demoProject) {
        currentProjectId.value = demoProject.id
        loadProject()
      } else {
      currentProjectId.value = projects.value[0].id
      loadProject()
      }
    }
  } catch (e) {
    console.error('Failed to fetch projects:', e)
  }
}

const loadProject = async () => {
  if (!currentProjectId.value) return
  try {
    const res = await axios.get(`${API_URL}/projects/${currentProjectId.value}`)
    console.log('Loaded project response:', res.data)
    
    // 确保 edges 是数组格式
    const data = res.data
    if (!data) {
      console.error('No data in response')
      return
    }
    
    // 确保 chapters 是数组
    if (!data.chapters) {
      data.chapters = []
    }
    if (!Array.isArray(data.chapters)) {
      console.warn('Chapters is not an array:', data.chapters)
      data.chapters = []
    }
    
    // 确保 edges 是数组格式
    if (!data.edges) {
      data.edges = []
    }
    if (data.edges && Array.isArray(data.edges)) {
      // 确保边的格式正确
      data.edges = data.edges.map(edge => {
        if (typeof edge === 'object' && 'source' in edge && 'target' in edge) {
          return edge // 已经是新格式
        } else if (Array.isArray(edge) && edge.length === 2) {
          // 旧格式，转换为新格式
          return { source: edge[0], target: edge[1], label: '' }
        }
        return edge
      })
    } else if (!Array.isArray(data.edges)) {
      console.warn('Edges is not an array:', data.edges)
      data.edges = []
    }
    
    // 确保节点按 position 排序
    if (data.chapters) {
      data.chapters.forEach(chapter => {
        chapter.sections?.forEach(section => {
          if (section.nodes && Array.isArray(section.nodes)) {
            // 按 position 排序，如果 position 为 null 则放在最后
            section.nodes.sort((a, b) => {
              const posA = a.position !== null && a.position !== undefined ? a.position : Infinity
              const posB = b.position !== null && b.position !== undefined ? b.position : Infinity
              return posA - posB
            })
          }
        })
      })
    }
    
    console.log('Processed project data:', { 
      chapters: data.chapters?.length, 
      edges: data.edges?.length,
      chaptersData: data.chapters 
    })
    
    // 清空缓存
    nodeLocationCache.clear()
    
    // 使用 Object.assign 更新响应式对象
    Object.assign(projectData, {
      chapters: data.chapters || [],
      edges: data.edges || []
    })
    
    console.log('Project data after assignment:', {
      chapters: projectData.chapters?.length,
      edges: projectData.edges?.length,
      hasChapters: !!projectData.chapters
    })
    
    resetLinkMode()
  } catch (e) {
    console.error('Failed to load project:', e)
    ElMessage.error('加载项目失败: ' + (e.response?.data?.detail || e.message))
  }
}

const handleProjectSelected = (projectId) => {
  currentProjectId.value = projectId
  loadProject()
}

const handleProjectCreated = (project) => {
  projects.value.push(project)
  currentProjectId.value = project.id
  loadProject()
}

const addChapter = async () => {
  if (!currentProjectId.value) return
  
  // 允许空名称，后端会生成默认名称
  try {
    await axios.post(`${API_URL}/projects/${currentProjectId.value}/chapters`, { 
      chapter_name: newChapterName.value.trim()
    })
    newChapterName.value = ''
    showAddChapterModal.value = false
    loadProject()
    ElMessage.success('章节添加成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '添加章节失败')
  }
}

const handleDeleteChapter = async (chapterId) => {
  try {
    await axios.delete(`${API_URL}/projects/${currentProjectId.value}/chapters/${chapterId}`)
    loadProject()
  } catch (e) {
    alert(e.response?.data?.detail || '删除章节失败')
  }
}

const handleAddSection = async ({ chapterId, sectionName }) => {
  try {
    await axios.post(`${API_URL}/projects/${currentProjectId.value}/sections`, {
      chapter_id: chapterId,
      section_name: sectionName
    })
    loadProject()
    ElMessage.success('部分添加成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '添加部分失败')
  }
}

const handleDeleteSection = async (sectionId) => {
  try {
    await axios.delete(`${API_URL}/projects/${currentProjectId.value}/sections/${sectionId}`)
    loadProject()
    ElMessage.success('部分删除成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除部分失败')
  }
}

const handleAddNode = async ({ chapterId, sectionId, nodeName, nodeContent }) => {
  try {
    await axios.post(`${API_URL}/projects/${currentProjectId.value}/nodes`, {
      chapter_id: chapterId,
      section_id: sectionId,
      node_name: nodeName,
      node_content: nodeContent || ''
    })
    loadProject()
    ElMessage.success('节点添加成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '添加节点失败')
  }
}

const handleEditNode = (node) => {
  editingNode.value = node
  editNodeName.value = node.name
  editNodeContent.value = node.content || ''
}

const saveNodeEdit = async () => {
  if (!editingNode.value) return
  
  // 如果没有输入名称，使用默认名称
  const nodeName = editNodeName.value.trim() || editingNode.value.name || '未命名节点'
  
  try {
    await axios.put(
      `${API_URL}/projects/${currentProjectId.value}/nodes/${editingNode.value.id}`,
      {
        name: nodeName,
        content: editNodeContent.value
      }
    )
    editingNode.value = null
    editNodeName.value = ''
    editNodeContent.value = ''
    loadProject()
    ElMessage.success('节点更新成功')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '更新节点失败')
  }
}

const handleDeleteNode = async (nodeId) => {
  try {
    // 查找节点名称用于确认对话框
    const node = projectData.value?.chapters
      ?.flatMap(ch => ch.sections || [])
      .flatMap(sec => sec.nodes || [])
      .find(n => n.id === nodeId)
    const nodeName = node?.name || '此节点'
    
    await ElMessageBox.confirm(
      `确定删除节点 "${nodeName}" 吗？所有相关的连接将被删除。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await axios.delete(`${API_URL}/projects/${currentProjectId.value}/nodes/${nodeId}`)
    console.log('Delete node response:', response)
    
    // 重新加载项目数据
    await loadProject()
    ElMessage.success('节点删除成功')
  } catch (e) {
    // 如果是用户取消，不显示错误
    if (e === 'cancel' || e === 'close') {
      return
    }
    console.error('Delete node error:', e)
    ElMessage.error(e.response?.data?.detail || e.message || '删除节点失败')
  }
}

const handleNodeClick = (nodeId, event) => {
  console.log('handleNodeClick called:', { nodeId, event, linkMode: { ...linkMode } })
  
  // 如果按住 Ctrl 或 Cmd，显示 DAG
  if (event?.ctrlKey || event?.metaKey) {
    showDAGForNode(nodeId)
    return
  }

  // 阻止事件冒泡
  if (event) {
    event.stopPropagation()
  }

  // 处理连接逻辑
  if (!linkMode.source) {
    // 选择起点
    linkMode.source = nodeId
    linkMode.target = null
    console.log('Set source:', nodeId)
  } else if (linkMode.source === nodeId) {
    // 如果点击的是已选中的起点，取消选择
    resetLinkMode()
    console.log('Reset link mode')
  } else if (linkMode.target === nodeId) {
    // 如果点击的是已选中的终点，取消选择终点
    linkMode.target = null
    console.log('Reset target')
  } else {
    // 选择终点
    linkMode.target = nodeId
    console.log('Set target:', nodeId)
  }
}

const showDAGForNode = (nodeId) => {
  console.log('showDAGForNode called with:', nodeId)
  const node = findNodeById(nodeId)
  if (node) {
    selectedNodeForDAG.value = nodeId
    selectedNodeNameForDAG.value = node.name
    showDAGPanel.value = true
    console.log('DAG Panel opened for node:', node.name)
  } else {
    console.error('Node not found:', nodeId)
  }
}

const findNodeById = (nodeId) => {
  for (const chapter of projectData.chapters) {
    for (const section of chapter.sections) {
      for (const node of section.nodes) {
        if (node.id === nodeId) return node
      }
    }
  }
  return null
}

const createEdge = async () => {
  if (!linkMode.source || !linkMode.target) {
    console.warn('Cannot create edge: missing source or target', { source: linkMode.source, target: linkMode.target })
    ElMessage.warning('请先选择起点和终点节点')
    return
  }
  
  if (linkMode.source === linkMode.target) {
    ElMessage.warning('起点和终点不能是同一个节点')
    return
  }
  
  console.log('Creating edge:', { source: linkMode.source, target: linkMode.target })
  
  // 弹出输入框让用户输入边的标签
  try {
    const { value: label } = await ElMessageBox.prompt(
      '请输入连接线的标签（可选）',
      '创建连接',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPlaceholder: '连接标签，留空则无标签'
      }
    )
    
    console.log('Sending edge creation request:', {
      projectId: currentProjectId.value,
      source: linkMode.source,
      target: linkMode.target,
      label: label || ''
    })
    
    const response = await axios.post(`${API_URL}/projects/${currentProjectId.value}/edges`, {
      source: linkMode.source,
      target: linkMode.target,
      label: label || ''
    })
    
    console.log('Edge created successfully:', response.data)
    loadProject()
    resetLinkMode()
    ElMessage.success('连接创建成功')
  } catch (e) {
    console.error('Failed to create edge:', e)
    if (e === 'cancel') {
      // 用户取消输入
      return
    }
    const errorMsg = e.response?.data?.detail || e.message || '未知错误'
    ElMessage.error('无法创建连接: ' + errorMsg)
  }
}

const resetLinkMode = () => {
  linkMode.source = null
  linkMode.target = null
}

const getNodeName = (nodeId) => {
  for (const chapter of projectData.chapters) {
    for (const section of chapter.sections) {
      for (const node of section.nodes) {
        if (node.id === nodeId) return node.name
      }
    }
  }
  return nodeId
}


// 缓存节点位置查找结果
const nodeLocationCache = new Map()

// 限制缓存大小，防止内存泄漏
const MAX_CACHE_SIZE = 1000
const cleanupNodeLocationCache = () => {
  if (nodeLocationCache.size > MAX_CACHE_SIZE) {
    // 删除最旧的 50% 缓存项
    const keysToDelete = Array.from(nodeLocationCache.keys()).slice(0, Math.floor(MAX_CACHE_SIZE / 2))
    keysToDelete.forEach(key => nodeLocationCache.delete(key))
  }
}

// 缓存跨章节边计算结果
let cachedCrossEdges = []
let cachedEdgesHash = ''

// 拖拽状态
const isDraggingNode = ref(false)
const draggingNodeId = ref(null)

// 计算所有连接线（统一处理，不再区分部分内外）
const crossChapterEdges = computed(() => {
  // 使用 edgeUpdateTrigger 来触发重新计算位置（滚动时更新）
  edgeUpdateTrigger.value
  
  if (!projectData.edges || !projectData.chapters || !Array.isArray(projectData.edges) || projectData.edges.length === 0) {
    cachedCrossEdges = []
    cachedEdgesHash = ''
    return []
  }
  
  // 计算数据哈希，如果没变化则返回缓存（拖拽时禁用缓存）
  const edgesHash = JSON.stringify(projectData.edges) + JSON.stringify(projectData.chapters.map(ch => ch.id))
  if (!isDraggingNode.value && edgesHash === cachedEdgesHash && cachedCrossEdges.length > 0) {
    return cachedCrossEdges
  }
  
  // 处理所有连接（不再区分是否跨章节）
  const allEdges = projectData.edges.filter(edge => {
    // 支持新的 Edge 格式 {source, target, label} 和旧的格式 [source, target]
    const source = edge.source || edge[0]
    const target = edge.target || edge[1]
    
    if (!source || !target) return false
    
    // 拖拽时清除相关节点的缓存，强制重新计算
    if (isDraggingNode.value && (source === draggingNodeId.value || target === draggingNodeId.value)) {
      nodeLocationCache.delete(source)
      nodeLocationCache.delete(target)
    }
    
    // 使用缓存查找节点位置
    let sourceLocation = nodeLocationCache.get(source)
    if (!sourceLocation) {
      sourceLocation = findNodeLocation(source)
      if (sourceLocation) {
        nodeLocationCache.set(source, sourceLocation)
        cleanupNodeLocationCache() // 定期清理缓存
      }
    }
    
    let targetLocation = nodeLocationCache.get(target)
    if (!targetLocation) {
      targetLocation = findNodeLocation(target)
      if (targetLocation) {
        nodeLocationCache.set(target, targetLocation)
        cleanupNodeLocationCache() // 定期清理缓存
      }
    }
    
    // 只要两个节点都存在就显示连接
    return sourceLocation && targetLocation
  }).map(edge => ({
    source: edge.source || edge[0],
    target: edge.target || edge[1],
    label: edge.label || ''
  }))
  
  // 更新缓存（拖拽时不更新缓存）
  if (!isDraggingNode.value) {
    cachedCrossEdges = allEdges
    cachedEdgesHash = edgesHash
  }
  
  return allEdges
})

// 查找节点位置
const findNodeLocation = (nodeId) => {
  if (!projectData.chapters) return null
  for (const chapter of projectData.chapters) {
    if (!chapter.sections) continue
    for (const section of chapter.sections) {
      if (!section.nodes) continue
      for (const node of section.nodes) {
        if (node.id === nodeId) {
          return {
            chapterId: chapter.id,
            sectionId: section.id,
            node
          }
        }
      }
    }
  }
  return null
}

// 获取节点在画布上的绝对位置（考虑滚动）
const getNodeAbsolutePosition = (nodeId) => {
  // 查找节点所在的章节和部分
  const location = findNodeLocation(nodeId)
  if (!location) {
    return null
  }
  
  // 查找对应的 DOM 元素，使用更宽松的选择器
  let chapterElement = document.querySelector(`[data-chapter-id="${location.chapterId}"]`)
  
  // 如果找不到，尝试等待一下再查找（可能是 DOM 还没渲染完成）
  if (!chapterElement) {
    // 尝试查找所有章节元素
    const allChapters = document.querySelectorAll('[data-chapter-id]')
    for (const ch of allChapters) {
      if (ch.getAttribute('data-chapter-id') === location.chapterId) {
        chapterElement = ch
        break
      }
    }
  }
  
  if (!chapterElement) {
    return null
  }
  
  const nodeElement = chapterElement.querySelector(`[data-node-id="${nodeId}"]`)
  if (!nodeElement) {
    return null
  }
  
  // 确保是 DOM 元素
  if (typeof nodeElement.getBoundingClientRect !== 'function') {
    return null
  }
  
  const canvasContainerEl = canvasContainer.value
  if (!canvasContainerEl) {
    return null
  }
  
  const canvasRect = canvasContainerEl.getBoundingClientRect()
  if (!canvasRect) {
    return null
  }
  
  try {
    const nodeRect = nodeElement.getBoundingClientRect()
    // 计算相对于画布容器的位置，考虑滚动偏移
    const scrollLeft = canvasContainerEl.scrollLeft || 0
    const scrollTop = canvasContainerEl.scrollTop || 0
    
    // 返回节点的中心点坐标和尺寸（用于计算边缘点）
    return {
      x: nodeRect.left - canvasRect.left + scrollLeft + nodeRect.width / 2,
      y: nodeRect.top - canvasRect.top + scrollTop + nodeRect.height / 2,
      width: nodeRect.width,
      height: nodeRect.height,
      left: nodeRect.left - canvasRect.left + scrollLeft,
      top: nodeRect.top - canvasRect.top + scrollTop,
      right: nodeRect.left - canvasRect.left + scrollLeft + nodeRect.width,
      bottom: nodeRect.top - canvasRect.top + scrollTop + nodeRect.height
    }
  } catch (e) {
    return null
  }
}

// 计算节点边缘的连接点（跨章节）
const getNodeEdgePointCrossChapter = (sourcePos, targetPos) => {
  if (!sourcePos || !targetPos) return null
  
  // 使用节点的实际边界（left, top, right, bottom）来计算边缘点
  const sourceLeft = sourcePos.left !== undefined ? sourcePos.left : (sourcePos.x - (sourcePos.width || 180) / 2)
  const sourceTop = sourcePos.top !== undefined ? sourcePos.top : (sourcePos.y - (sourcePos.height || 70) / 2)
  const sourceRight = sourcePos.right !== undefined ? sourcePos.right : (sourcePos.x + (sourcePos.width || 180) / 2)
  const sourceBottom = sourcePos.bottom !== undefined ? sourcePos.bottom : (sourcePos.y + (sourcePos.height || 70) / 2)
  
  const sourceCenterX = sourcePos.x
  const sourceCenterY = sourcePos.y
  
  // 计算方向向量（从源节点中心指向目标节点中心）
  const dx = targetPos.x - sourceCenterX
  const dy = targetPos.y - sourceCenterY
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  if (distance === 0) {
    return { x: sourceCenterX, y: sourceCenterY }
  }
  
  // 归一化方向向量
  const nx = dx / distance
  const ny = dy / distance
  
  // 计算节点矩形的半宽和半高
  const halfWidth = (sourceRight - sourceLeft) / 2
  const halfHeight = (sourceBottom - sourceTop) / 2
  
  // 计算边缘点：从中心点沿方向向量延伸到矩形边界
  let edgeX, edgeY
  
  // 使用参数方程：从中心点出发，沿方向向量延伸
  // 找到与矩形边界的交点
  if (Math.abs(nx) > Math.abs(ny)) {
    // 水平方向为主
    const t = halfWidth / Math.abs(nx)
    edgeX = sourceCenterX + nx * halfWidth
    edgeY = sourceCenterY + ny * t * Math.abs(nx)
    
    // 检查是否超出上下边界
    if (edgeY < sourceTop || edgeY > sourceBottom) {
      const tY = dy > 0 ? (sourceBottom - sourceCenterY) / Math.abs(dy) : (sourceCenterY - sourceTop) / Math.abs(dy)
      edgeY = sourceCenterY + dy * tY
      edgeX = sourceCenterX + dx * tY
    }
  } else {
    // 垂直方向为主
    const t = halfHeight / Math.abs(ny)
    edgeY = sourceCenterY + ny * halfHeight
    edgeX = sourceCenterX + nx * t * Math.abs(ny)
    
    // 检查是否超出左右边界
    if (edgeX < sourceLeft || edgeX > sourceRight) {
      const tX = dx > 0 ? (sourceRight - sourceCenterX) / Math.abs(dx) : (sourceCenterX - sourceLeft) / Math.abs(dx)
      edgeX = sourceCenterX + dx * tX
      edgeY = sourceCenterY + dy * tX
    }
  }
  
  return { x: edgeX, y: edgeY }
}

// 边的路径缓存
let edgePathCache = new Map()
let edgePathUpdateTimer = null

// 获取边的路径（使用贝塞尔曲线，从节点边缘开始）
// 使用缓存和防抖优化性能
const getEdgePath = (edge) => {
  const edgeKey = `${edge.source}-${edge.target}`
  
  // 拖拽时实时更新，不使用缓存
  if (isDraggingNode.value && (edge.source === draggingNodeId.value || edge.target === draggingNodeId.value)) {
    return calculateEdgePath(edge)
  }
  
  // 非拖拽时使用缓存
  if (edgePathCache.has(edgeKey)) {
    return edgePathCache.get(edgeKey)
  }
  
  const path = calculateEdgePath(edge)
  edgePathCache.set(edgeKey, path)
  
  // 限制缓存大小
  if (edgePathCache.size > 500) {
    const firstKey = edgePathCache.keys().next().value
    edgePathCache.delete(firstKey)
  }
  
  return path
}

const calculateEdgePath = (edge) => {
  const sourcePos = getNodeAbsolutePosition(edge.source)
  const targetPos = getNodeAbsolutePosition(edge.target)
  
  if (!sourcePos || !targetPos) {
    return ''
  }
  
  // 获取源节点和目标节点的边缘点
  const sourceEdge = getNodeEdgePointCrossChapter(sourcePos, targetPos)
  const targetEdge = getNodeEdgePointCrossChapter(targetPos, sourcePos)
  
  if (!sourceEdge || !targetEdge) {
    return ''
  }
  
  const dx = targetEdge.x - sourceEdge.x
  const dy = targetEdge.y - sourceEdge.y
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  // 如果距离为0，返回空路径
  if (distance === 0) return ''
  
  // 使用二次贝塞尔曲线，根据距离调整弧度
  const controlX = sourceEdge.x + dx / 2
  // 弧度大小根据水平距离和总距离调整，形成优雅的曲线
  const curveAmount = Math.min(Math.abs(dx) * 0.4, distance * 0.35)
  const controlY = sourceEdge.y + dy / 2 - curveAmount
  
  return `M ${sourceEdge.x} ${sourceEdge.y} Q ${controlX} ${controlY} ${targetEdge.x} ${targetEdge.y}`
}

// 获取边标签的位置
const getEdgeLabelX = (edge) => {
  const sourcePos = getNodeAbsolutePosition(edge.source)
  const targetPos = getNodeAbsolutePosition(edge.target)
  
  if (!sourcePos || !targetPos) return 0
  
  return (sourcePos.x + targetPos.x) / 2
}

const getEdgeLabelY = (edge) => {
  const sourcePos = getNodeAbsolutePosition(edge.source)
  const targetPos = getNodeAbsolutePosition(edge.target)
  
  if (!sourcePos || !targetPos) return 0
  
  const dy = targetPos.y - sourcePos.y
  const dx = targetPos.x - sourcePos.x
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  // 标签位置在曲线中间，根据弧度调整偏移
  const curveAmount = Math.min(Math.abs(dx) * 0.4, distance * 0.35)
  let labelY = (sourcePos.y + targetPos.y) / 2 - curveAmount - 8
  
  // 标签尺寸
  const labelHeight = 24
  const labelWidth = 80
  const labelX = (sourcePos.x + targetPos.x) / 2
  
  // 检测标签是否与节点重叠
  const labelTop = labelY - labelHeight / 2
  const labelBottom = labelY + labelHeight / 2
  const labelLeft = labelX - labelWidth / 2
  const labelRight = labelX + labelWidth / 2
  
  // 获取节点尺寸（从 DOM 元素）
  const sourceLocation = findNodeLocation(edge.source)
  const targetLocation = findNodeLocation(edge.target)
  
  if (sourceLocation) {
    let chapterElement = document.querySelector(`[data-chapter-id="${sourceLocation.chapterId}"]`)
    if (!chapterElement) {
      const allChapters = document.querySelectorAll('[data-chapter-id]')
      for (const ch of allChapters) {
        if (ch.getAttribute('data-chapter-id') === sourceLocation.chapterId) {
          chapterElement = ch
          break
        }
      }
    }
    
    if (chapterElement) {
      const sourceNodeElement = chapterElement.querySelector(`[data-node-id="${edge.source}"]`)
      if (sourceNodeElement && typeof sourceNodeElement.getBoundingClientRect === 'function') {
        const sourceNodeRect = sourceNodeElement.getBoundingClientRect()
        const canvasContainerEl = canvasContainer.value
        if (canvasContainerEl) {
          const canvasRect = canvasContainerEl.getBoundingClientRect()
          const scrollLeft = canvasContainerEl.scrollLeft || 0
          const scrollTop = canvasContainerEl.scrollTop || 0
          
          const sourceNodeTop = sourceNodeRect.top - canvasRect.top + scrollTop
          const sourceNodeBottom = sourceNodeTop + sourceNodeRect.height
          const sourceNodeLeft = sourceNodeRect.left - canvasRect.left + scrollLeft
          const sourceNodeRight = sourceNodeLeft + sourceNodeRect.width
          
          const nodePadding = 10
          const sourceTop = sourceNodeTop - nodePadding
          const sourceBottom = sourceNodeBottom + nodePadding
          const sourceLeft = sourceNodeLeft - nodePadding
          const sourceRight = sourceNodeRight + nodePadding
          
          // 检测重叠
          const overlapsSource = !(
            labelRight < sourceLeft ||
            labelLeft > sourceRight ||
            labelBottom < sourceTop ||
            labelTop > sourceBottom
          )
          
          if (overlapsSource) {
            // 尝试向上移动
            let adjustedY = labelY - 30
            const adjustedTop = adjustedY - labelHeight / 2
            const adjustedBottom = adjustedY + labelHeight / 2
            
            const stillOverlapsSource = !(
              labelRight < sourceLeft ||
              labelLeft > sourceRight ||
              adjustedBottom < sourceTop ||
              adjustedTop > sourceBottom
            )
            
            if (!stillOverlapsSource) {
              labelY = adjustedY
    } else {
              // 如果向上移动还是重叠，尝试向下移动
              adjustedY = labelY + 30
              const adjustedTop2 = adjustedY - labelHeight / 2
              const adjustedBottom2 = adjustedY + labelHeight / 2
              
              const stillOverlapsSource2 = !(
                labelRight < sourceLeft ||
                labelLeft > sourceRight ||
                adjustedBottom2 < sourceTop ||
                adjustedTop2 > sourceBottom
              )
              
              if (!stillOverlapsSource2) {
                labelY = adjustedY
              } else {
                // 如果上下都不行，尝试更远的距离
                labelY = labelY - 50
              }
            }
          }
        }
      }
    }
  }
  
  // 检查目标节点
  if (targetLocation) {
    let chapterElement = document.querySelector(`[data-chapter-id="${targetLocation.chapterId}"]`)
    if (!chapterElement) {
      const allChapters = document.querySelectorAll('[data-chapter-id]')
      for (const ch of allChapters) {
        if (ch.getAttribute('data-chapter-id') === targetLocation.chapterId) {
          chapterElement = ch
          break
        }
      }
    }
    
    if (chapterElement) {
      const targetNodeElement = chapterElement.querySelector(`[data-node-id="${edge.target}"]`)
      if (targetNodeElement && typeof targetNodeElement.getBoundingClientRect === 'function') {
        const targetNodeRect = targetNodeElement.getBoundingClientRect()
        const canvasContainerEl = canvasContainer.value
        if (canvasContainerEl) {
          const canvasRect = canvasContainerEl.getBoundingClientRect()
          const scrollLeft = canvasContainerEl.scrollLeft || 0
          const scrollTop = canvasContainerEl.scrollTop || 0
          
          const targetNodeTop = targetNodeRect.top - canvasRect.top + scrollTop
          const targetNodeBottom = targetNodeTop + targetNodeRect.height
          const targetNodeLeft = targetNodeRect.left - canvasRect.left + scrollLeft
          const targetNodeRight = targetNodeLeft + targetNodeRect.width
          
          const nodePadding = 10
          const targetTop = targetNodeTop - nodePadding
          const targetBottom = targetNodeBottom + nodePadding
          const targetLeft = targetNodeLeft - nodePadding
          const targetRight = targetNodeRight + nodePadding
          
          // 检测重叠
          const overlapsTarget = !(
            labelRight < targetLeft ||
            labelLeft > targetRight ||
            labelBottom < targetTop ||
            labelTop > targetBottom
          )
          
          if (overlapsTarget) {
            // 尝试向上移动
            let adjustedY = labelY - 30
            const adjustedTop = adjustedY - labelHeight / 2
            const adjustedBottom = adjustedY + labelHeight / 2
            
            const stillOverlapsTarget = !(
              labelRight < targetLeft ||
              labelLeft > targetRight ||
              adjustedBottom < targetTop ||
              adjustedTop > targetBottom
            )
            
            if (!stillOverlapsTarget) {
              labelY = adjustedY
            } else {
              // 如果向上移动还是重叠，尝试向下移动
              adjustedY = labelY + 30
              const adjustedTop2 = adjustedY - labelHeight / 2
              const adjustedBottom2 = adjustedY + labelHeight / 2
              
              const stillOverlapsTarget2 = !(
                labelRight < targetLeft ||
                labelLeft > targetRight ||
                adjustedBottom2 < targetTop ||
                adjustedTop2 > targetBottom
              )
              
              if (!stillOverlapsTarget2) {
                labelY = adjustedY
              } else {
                // 如果上下都不行，尝试更远的距离
                labelY = labelY - 50
              }
            }
          }
        }
      }
    }
  }
  
  return labelY
}

// 拖拽状态
const isDraggingNode = ref(false)
const draggingNodeId = ref(null)
let edgePathCache = new Map()
let edgePathUpdateTimer = null

// 处理节点拖拽事件
const handleNodeDragging = ({ nodeId, x, y }) => {
  isDraggingNode.value = true
  draggingNodeId.value = nodeId
  
  // 清除相关节点的缓存，强制重新计算位置
  nodeLocationCache.delete(nodeId)
  // 清除相关边的路径缓存
  for (const [key, _] of edgePathCache.entries()) {
    if (key.includes(nodeId)) {
      edgePathCache.delete(key)
    }
  }
  
  // 触发连接线更新（使用 requestAnimationFrame 优化，约 60fps）
  if (edgePathUpdateTimer) {
    cancelAnimationFrame(edgePathUpdateTimer)
  }
  edgePathUpdateTimer = requestAnimationFrame(() => {
    edgeUpdateTrigger.value++
  })
}

// 处理节点拖拽结束事件
const handleNodeDragEnd = ({ nodeId }) => {
  isDraggingNode.value = false
  draggingNodeId.value = null
  
  // 清除所有缓存，强制重新计算
  nodeLocationCache.clear()
  edgePathCache.clear()
  
  // 触发连接线更新
  if (edgePathUpdateTimer) {
    cancelAnimationFrame(edgePathUpdateTimer)
    edgePathUpdateTimer = null
  }
  
  // 延迟更新，确保 DOM 已更新
  requestAnimationFrame(() => {
    edgeUpdateTrigger.value++
  })
}


// 显示连接线菜单（点击或右键）
const showEdgeContextMenu = (event, edge) => {
  // 如果是右键，阻止默认行为
  if (event.type === 'contextmenu') {
    event.preventDefault()
  }
  
  edgeContextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    edge: edge
  }
}

// 关闭右键菜单
const closeEdgeContextMenu = () => {
  edgeContextMenu.value.show = false
}

// 编辑连接线
const editEdge = async (edge) => {
  closeEdgeContextMenu()
  try {
    const { value: label } = await ElMessageBox.prompt(
      '编辑连接线标签',
      '编辑连接',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: edge.label || '',
        inputPlaceholder: '连接标签，留空则无标签'
      }
    )
    
    await axios.put(`${API_URL}/projects/${currentProjectId.value}/edges`, {
      source: edge.source,
      target: edge.target,
      label: label || ''
    })
    loadProject()
    ElMessage.success('连接标签更新成功')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('更新连接标签失败: ' + (e.response?.data?.detail || '未知错误'))
    }
  }
}

// 删除连接线
const deleteEdge = async (edge) => {
  closeEdgeContextMenu()
  try {
    await ElMessageBox.confirm(
      '确定删除此连接线吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await axios.delete(`${API_URL}/projects/${currentProjectId.value}/edges`, {
      data: {
        source: edge.source,
        target: edge.target
      }
    })
  loadProject()
    ElMessage.success('连接线删除成功')
  } catch (e) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error('删除连接线失败: ' + (e.response?.data?.detail || '未知错误'))
    }
  }
}

// 更新画布尺寸
const updateCanvasSize = () => {
  if (!canvasContainer.value) {
    return
  }
  try {
    canvasWidth.value = canvasContainer.value.scrollWidth || window.innerWidth
    canvasHeight.value = canvasContainer.value.scrollHeight || window.innerHeight
  } catch (e) {
    // 静默处理错误，避免控制台噪音
  }
}

// 使用防抖优化画布尺寸更新
let canvasSizeUpdateTimer = null
const debouncedUpdateCanvasSize = () => {
  if (canvasSizeUpdateTimer) {
    clearTimeout(canvasSizeUpdateTimer)
  }
  canvasSizeUpdateTimer = setTimeout(() => {
    if (canvasContainer.value) {
      updateCanvasSize()
    }
  }, 100)
}

let resizeHandler = null
let mutationObserver = null

// 点击外部关闭右键菜单
const handleClickOutside = (event) => {
  if (edgeContextMenu.value.show) {
    closeEdgeContextMenu()
  }
}

// 滚动处理函数（使用防抖优化性能）
let scrollTimer = null
const handleScroll = () => {
  // 清除之前的定时器
  if (scrollTimer) {
    clearTimeout(scrollTimer)
  }
  // 防抖：延迟更新，避免频繁计算
  scrollTimer = setTimeout(() => {
    // 触发响应式更新，强制重新计算连接线位置
    edgeUpdateTrigger.value++
  }, 50)
}

onMounted(() => {
  fetchProjects()
  // 监听窗口大小变化和滚动，更新画布尺寸
  resizeHandler = () => debouncedUpdateCanvasSize()
  window.addEventListener('resize', resizeHandler)
  // 监听点击外部关闭右键菜单
  document.addEventListener('click', handleClickOutside)
  // 监听画布容器的滚动事件
  if (canvasContainer.value) {
    canvasContainer.value.addEventListener('scroll', handleScroll, { passive: true })
  }
  
  // 使用 nextTick 确保 DOM 已渲染
  nextTick(() => {
    if (canvasContainer.value) {
      mutationObserver = new MutationObserver(debouncedUpdateCanvasSize)
      mutationObserver.observe(canvasContainer.value, { childList: true, subtree: true })
      // 初始更新
      updateCanvasSize()
      // 监听滚动事件
      canvasContainer.value.addEventListener('scroll', handleScroll, { passive: true })
    }
  })
})

onUnmounted(() => {
  // 清理事件监听器
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
    resizeHandler = null
  }
  // 清理右键菜单监听器
  document.removeEventListener('click', handleClickOutside)
  // 清理滚动监听器
  if (canvasContainer.value) {
    canvasContainer.value.removeEventListener('scroll', handleScroll)
  }
  // 清理滚动定时器
  if (scrollTimer) {
    clearTimeout(scrollTimer)
    scrollTimer = null
  }
  
  // 清理 MutationObserver
  if (mutationObserver) {
    mutationObserver.disconnect()
    mutationObserver = null
  }
  
  // 清理防抖定时器
  if (canvasSizeUpdateTimer) {
    clearTimeout(canvasSizeUpdateTimer)
    canvasSizeUpdateTimer = null
  }
  
  // 清理缓存
  nodeLocationCache.clear()
})

// 使用 shallow watch 减少深度监听的开销，只监听长度变化
watch(() => projectData.chapters?.length, () => {
  nextTick(() => {
    if (canvasContainer.value) {
      debouncedUpdateCanvasSize()
    }
  })
})

watch(() => projectData.edges?.length, () => {
  // 当边数据更新时，重新计算画布尺寸
  nextTick(() => {
    if (canvasContainer.value) {
      debouncedUpdateCanvasSize()
    }
  })
})
</script>

