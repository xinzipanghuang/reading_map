<template>
  <div
    :class="[
      'relative p-3 rounded-2xl border-2 transition',
      isHexColor(chapterColor.border) ? '' : chapterColor.border,
      isHexColor(chapterColor.bg) ? '' : chapterColor.bg
    ]"
    :style="{
      borderColor: isHexColor(chapterColor.border) ? chapterColor.border : undefined,
      backgroundColor: isHexColor(chapterColor.bg) ? `${chapterColor.bg}30` : undefined
    }"
    :data-chapter-id="chapter.id"
  >
    <!-- Chapter Badge -->
    <div
      :class="[
        'absolute -left-3 top-6 px-2 py-1 text-xs font-bold rounded shadow-sm',
        isHexColor(chapterColor.badgeBg) ? '' : chapterColor.badgeBg,
        isHexColor(chapterColor.badgeText) ? '' : chapterColor.badgeText
      ]"
      :style="{
        backgroundColor: isHexColor(chapterColor.badgeBg) ? chapterColor.badgeBg : undefined,
        color: isHexColor(chapterColor.badgeText) ? chapterColor.badgeText : undefined
      }"
    >
      {{ chapterIndex }}
    </div>

    <!-- Chapter Header -->
    <div 
      :class="['flex items-center justify-between mb-2', isHexColor(chapterColor.chapterText || chapterColor.text) ? '' : (chapterColor.chapterText || chapterColor.text)]"
      :style="{
        color: isHexColor(chapterColor.chapterText || chapterColor.text) ? (chapterColor.chapterText || chapterColor.text) : undefined
      }"
    >
      <h2 class="text-lg font-bold flex items-center gap-2">
        <i :class="[chapterIcon, 'text-lg']"></i>
        {{ chapter.name }}
      </h2>
      <div class="flex gap-2">
        <button
          @click="showAddSectionModal = true"
          class="p-1.5 text-gray-400 hover:text-blue-600 transition rounded"
          title="添加部分"
        >
          <i class="ph ph-plus-circle"></i>
        </button>
        <button
          @click="handleDeleteChapter"
          class="p-1.5 text-gray-400 hover:text-red-600 transition rounded"
          title="删除章节"
        >
          <i class="ph ph-trash"></i>
        </button>
      </div>
    </div>

    <!-- Sections -->
    <div class="space-y-3">
      <div
        v-for="section in chapter.sections"
        :key="section.id"
        class="bg-white p-2 rounded-lg border border-gray-200 shadow-sm"
      >
        <!-- Section Header -->
        <div 
          class="flex items-center justify-between mb-2"
          :class="isHexColor(chapterColor.text) ? '' : chapterColor.text"
          :style="{
            color: isHexColor(chapterColor.text) ? chapterColor.text : undefined
          }"
        >
          <h3 class="font-medium text-sm">{{ section.name }}</h3>
          <div class="flex gap-2">
            <button
              @click="showAddNodeModal(section.id)"
              class="p-1 text-gray-400 hover:text-blue-600 transition text-xs"
              title="添加节点"
            >
              <i class="ph ph-plus"></i>
            </button>
            <button
              @click="handleDeleteSection(section.id)"
              class="p-1 text-gray-400 hover:text-red-600 transition text-xs"
              title="删除部分"
            >
              <i class="ph ph-trash"></i>
            </button>
          </div>
        </div>

        <!-- Nodes Container -->
        <div 
          class="relative" 
          :style="getSectionContainerStyle(section)"
          :ref="el => setSectionContainerRef(section.id, el)"
          :key="`container-${section.id}-${containerStyleKey}`"
        >
          <!-- Nodes -->
          <div
            v-for="(node, idx) in section.nodes"
            :key="node.id"
            :ref="el => setNodeRef(node.id, el, idx, section.id)"
            :data-node-id="node.id"
            :class="[
              'absolute z-10',
              draggingNodeId === node.id 
                ? 'opacity-50 scale-95 cursor-grabbing' 
                : 'cursor-grab transition-all duration-200 ease-out hover:shadow-lg'
            ]"
            :style="getNodeStyle(node, section.id)"
            @mousedown="(e) => handleMouseDown(e, node.id, idx, section.id)"
          >
            <KnowledgeCard
              :title="node.name"
              :subtitle="node.content || ''"
              :color="getColorForChapter(chapterIndex - 1)"
              :icon="getIconForChapter(chapterIndex - 1)"
              :text-color="isHexColor(chapterColor.text) ? chapterColor.text : undefined"
              :text-color-class="!isHexColor(chapterColor.text) ? chapterColor.text : undefined"
              :is-selected="isNodeSelected(node.id) || isNodeInLink(node.id)"
              :class="getLinkStatusClass(node.id)"
              @click="(e) => handleNodeClick(node.id, e)"
              @dblclick="() => handleNodeDoubleClick(node.id)"
              @edit="handleEditNode(node)"
              @delete="handleDeleteNode(node.id)"
            />
          </div>
          <button
            v-if="section.nodes.length === 0"
            @click="showAddNodeModal(section.id)"
            class="p-2 rounded-lg border-2 border-dashed border-gray-300 text-gray-400 hover:border-blue-400 hover:text-blue-600 transition text-sm min-w-[180px] h-[70px] flex items-center justify-center gap-2 flex-shrink-0"
          >
            <i class="ph ph-plus"></i>
            添加知识点
          </button>
        </div>
      </div>

      <!-- Add Section Button -->
      <button
        v-if="chapter.sections.length === 0"
        @click="showAddSectionModal = true"
        class="w-full p-4 rounded-lg border-2 border-dashed border-gray-300 text-gray-400 hover:border-blue-400 hover:text-blue-600 transition text-sm flex items-center justify-center gap-2"
      >
        <i class="ph ph-plus-circle"></i>
        添加第一个部分
      </button>
    </div>

    <!-- Add Section Modal -->
    <div
      v-if="showAddSectionModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showAddSectionModal = false"
    >
      <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4">添加部分</h3>
        <input
          v-model="newSectionName"
          @keyup.enter="addSection"
          class="w-full border p-2 rounded mb-4 focus:outline-none focus:border-blue-500"
          placeholder="部分名称 (如: 1.1 基本概念)"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="showAddSectionModal = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition"
          >
            取消
          </button>
          <button
            @click="addSection"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            创建
          </button>
        </div>
      </div>
    </div>

    <!-- Add Node Modal -->
    <div
      v-if="showAddNodeModalForSection"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showAddNodeModalForSection = null"
    >
      <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4">添加知识点</h3>
        <input
          v-model="newNodeName"
          @keyup.enter="addNode"
          class="w-full border p-2 rounded mb-2 focus:outline-none focus:border-blue-500"
          :placeholder="`知识点名称，留空则使用默认名称`"
        />
        <textarea
          v-model="newNodeContent"
          class="w-full border p-2 rounded mb-4 focus:outline-none focus:border-blue-500"
          placeholder="备注/内容 (可选)"
          rows="3"
        ></textarea>
        <div class="flex justify-end gap-2">
          <button
            @click="showAddNodeModalForSection = null"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition"
          >
            取消
          </button>
          <button
            @click="addNode"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            创建
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import KnowledgeCard from './KnowledgeCard.vue'

const props = defineProps({
  chapter: {
    type: Object,
    required: true
  },
  chapterIndex: {
    type: Number,
    required: true
  },
  isLast: {
    type: Boolean,
    default: false
  },
  selectedNodeId: {
    type: String,
    default: null
  },
  linkSource: {
    type: String,
    default: null
  },
  linkTarget: {
    type: String,
    default: null
  },
  nodePositions: {
    type: Object,
    default: () => ({})
  },
  projectId: {
    type: String,
    required: true
  },
  colorScheme: {
    type: String,
    default: 'seaborn-set2',
    validator: (value) => [
      'default', 'seaborn-set1', 'seaborn-set2', 'seaborn-set3',
      'seaborn-pastel1', 'seaborn-pastel2', 'seaborn-dark2',
      'seaborn-accent', 'seaborn-paired', 'seaborn-spectral'
    ].includes(value)
  }
})

const emit = defineEmits([
  'add-section',
  'delete-chapter',
  'delete-section',
  'add-node',
  'edit-node',
  'delete-node',
  'node-click',
  'node-dblclick',
  'update-node-positions',
  'node-dragging',
  'node-drag-end'
])

const showAddSectionModal = ref(false)
const showAddNodeModalForSection = ref(null)
const newSectionName = ref('')
const newNodeName = ref('')
const newNodeContent = ref('')
const nodeRefs = ref({})
const nodePositions = ref({})
const sectionContainerRefs = ref({})

// 拖拽相关状态
const draggingNodeId = ref(null)
const dragStartIndex = ref(null)
const dragStartSectionId = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragAnimationFrame = ref(null)

// 当前颜色方案（保留作为备选）
const chapterColorsDefault = [
  {
    border: 'border-blue-200',
    bg: 'bg-blue-50',
    text: 'text-gray-700', // 用于 section 和 node 标题，使用柔和的灰色
    chapterText: 'text-gray-700', // 用于章节标题，使用柔和的灰色
    badgeBg: 'bg-blue-100',
    badgeText: 'text-blue-700'
  },
  {
    border: 'border-orange-200',
    bg: 'bg-orange-50',
    text: 'text-gray-700',
    chapterText: 'text-gray-700',
    badgeBg: 'bg-orange-100',
    badgeText: 'text-orange-700'
  },
  {
    border: 'border-green-200',
    bg: 'bg-green-50',
    text: 'text-gray-700',
    chapterText: 'text-gray-700',
    badgeBg: 'bg-green-100',
    badgeText: 'text-green-700'
  },
  {
    border: 'border-purple-200',
    bg: 'bg-purple-50',
    text: 'text-gray-700',
    chapterText: 'text-gray-700',
    badgeBg: 'bg-purple-100',
    badgeText: 'text-purple-700'
  },
  {
    border: 'border-indigo-200',
    bg: 'bg-indigo-50',
    text: 'text-gray-700',
    chapterText: 'text-gray-700',
    badgeBg: 'bg-indigo-100',
    badgeText: 'text-indigo-700'
  }
]

// 辅助函数：从十六进制颜色生成颜色配置
const createColorConfig = (hexColors) => {
  return hexColors.map(hex => {
    // 计算对比色（深色文字或白色文字）
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    const brightness = (r * 299 + g * 587 + b * 114) / 1000
    
    // 由于章节背景色只有 30% 透明度，即使是深色也会变得很浅
    // 所以章节标题也始终使用深色文字，确保在任何情况下都能看清楚
    const chapterTextColor = '#1a1a1a' // 始终使用深色
    
    // section 和 node 标题始终使用深色（因为它们在白色背景上）
    const sectionNodeTextColor = '#1a1a1a' // 始终使用深色，确保在白色背景上可读
    
    // badge 文字可以使用对比色，因为 badge 背景是实色（100% 不透明）
    const badgeTextColor = brightness > 128 ? '#1a1a1a' : '#ffffff'
    
    return {
      border: hex,
      bg: hex,
      text: sectionNodeTextColor, // 用于 section 和 node 标题（白色背景），始终使用深色
      chapterText: chapterTextColor, // 用于章节标题（章节背景），始终使用深色
      badgeBg: hex,
      badgeText: badgeTextColor // badge 文字使用对比色（因为背景是实色）
    }
  })
}

// Seaborn Set1 颜色方案（9种颜色）
const chapterColorsSeabornSet1 = createColorConfig([
  '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
  '#ffff33', '#a65628', '#f781bf', '#999999'
])

// Seaborn Set2 颜色方案（8种颜色）
const chapterColorsSeabornSet2 = createColorConfig([
  '#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854',
  '#ffd92f', '#e5c494', '#b3b3b3'
])

// Seaborn Set3 颜色方案（12种颜色）
const chapterColorsSeabornSet3 = createColorConfig([
  '#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3',
  '#fdb462', '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd',
  '#ccebc5', '#ffed6f'
])

// Seaborn Pastel1 颜色方案（9种颜色）
const chapterColorsSeabornPastel1 = createColorConfig([
  '#fbb4ae', '#b3cde3', '#ccebc5', '#decbe4', '#fed9a6',
  '#ffffcc', '#e5d8bd', '#fddaec', '#f2f2f2'
])

// Seaborn Pastel2 颜色方案（8种颜色）
const chapterColorsSeabornPastel2 = createColorConfig([
  '#b3e2cd', '#fdcdac', '#cbd5e8', '#f4cae4', '#e6f5c9',
  '#fff2ae', '#f1e2cc', '#cccccc'
])

// Seaborn Dark2 颜色方案（8种颜色）
const chapterColorsSeabornDark2 = createColorConfig([
  '#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e',
  '#e6ab02', '#a6761d', '#666666'
])

// Seaborn Accent 颜色方案（8种颜色）
const chapterColorsSeabornAccent = createColorConfig([
  '#7fc97f', '#beaed4', '#fdc086', '#ffff99', '#386cb0',
  '#f0027f', '#bf5b17', '#666666'
])

// Seaborn Paired 颜色方案（12种颜色）
const chapterColorsSeabornPaired = createColorConfig([
  '#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
  '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
  '#ffff99', '#b15928'
])

// Seaborn Spectral 颜色方案（11种颜色，发散色）
const chapterColorsSeabornSpectral = createColorConfig([
  '#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b',
  '#ffffbf', '#e6f598', '#abdda4', '#66c2a5', '#3288bd',
  '#5e4fa2'
])

const chapterIcons = ['ph-brain', 'ph-calculator', 'ph-sparkle', 'ph-sigma', 'ph-sparkle']

// 判断是否为十六进制颜色值
const isHexColor = (color) => {
  return typeof color === 'string' && color.startsWith('#')
}

// 根据颜色方案选择颜色数组
const chapterColors = computed(() => {
  const schemeMap = {
    'default': chapterColorsDefault,
    'seaborn-set1': chapterColorsSeabornSet1,
    'seaborn-set2': chapterColorsSeabornSet2,
    'seaborn-set3': chapterColorsSeabornSet3,
    'seaborn-pastel1': chapterColorsSeabornPastel1,
    'seaborn-pastel2': chapterColorsSeabornPastel2,
    'seaborn-dark2': chapterColorsSeabornDark2,
    'seaborn-accent': chapterColorsSeabornAccent,
    'seaborn-paired': chapterColorsSeabornPaired,
    'seaborn-spectral': chapterColorsSeabornSpectral
  }
  return schemeMap[props.colorScheme] || chapterColorsDefault
})

const chapterColor = computed(() => {
  const index = (props.chapterIndex - 1) % chapterColors.value.length
  return chapterColors.value[index]
})

const chapterIcon = computed(() => {
  const index = (props.chapterIndex - 1) % chapterIcons.length
  return chapterIcons[index]
})

const getColorForChapter = (index) => {
  const colors = ['blue', 'orange', 'green', 'purple', 'indigo']
  return colors[index % colors.length]
}

const getIconForChapter = (index) => {
  const icons = ['ph-book-open', 'ph-calculator', 'ph-book-open', 'ph-sigma', 'ph-sparkle']
  return icons[index % icons.length]
}

const isNodeSelected = (nodeId) => {
  return props.selectedNodeId === nodeId
}

const isNodeInLink = (nodeId) => {
  const isSource = props.linkSource === nodeId
  const isTarget = props.linkTarget === nodeId
  return isSource || isTarget
}

// 获取连接状态样式
const getLinkStatusClass = (nodeId) => {
  const isSource = props.linkSource === nodeId
  const isTarget = props.linkTarget === nodeId
  
  if (isSource) {
    return 'ring-2 ring-green-400 border-green-500 bg-green-50'
  } else if (isTarget) {
    return 'ring-2 ring-purple-400 border-purple-500 bg-purple-50'
  }
  return ''
}

const addSection = () => {
  if (!newSectionName.value.trim()) return
  emit('add-section', {
    chapterId: props.chapter.id,
    sectionName: newSectionName.value
  })
  newSectionName.value = ''
  showAddSectionModal.value = false
}

const handleDeleteChapter = async () => {
  try {
    await ElMessageBox.confirm(
      `确定删除章节 "${props.chapter.name}" 吗？所有相关的部分和节点将被删除。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    emit('delete-chapter', props.chapter.id)
  } catch {
    // 用户取消删除
  }
}

const handleDeleteSection = async (sectionId) => {
  try {
    await ElMessageBox.confirm(
      '确定删除此部分吗？所有相关的节点将被删除。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    emit('delete-section', sectionId)
  } catch {
    // 用户取消删除
  }
}

const showAddNodeModal = (sectionId) => {
  showAddNodeModalForSection.value = sectionId
  newNodeName.value = ''
  newNodeContent.value = ''
}

const addNode = () => {
  if (!showAddNodeModalForSection.value) return
  
  // 允许空名称，后端会生成默认名称
  emit('add-node', {
    chapterId: props.chapter.id,
    sectionId: showAddNodeModalForSection.value,
    nodeName: newNodeName.value.trim(),
    nodeContent: newNodeContent.value
  })
  newNodeName.value = ''
  newNodeContent.value = ''
  showAddNodeModalForSection.value = null
}

const handleNodeClick = (nodeId, event) => {
  // 阻止双击事件触发单击
  if (event && event.detail === 2) {
    return
  }
  
  // 如果按住 Ctrl 键，才传递点击事件（用于连接功能）
  // 普通左键点击不传递，避免与拖拽冲突
  if (event && (event.ctrlKey || event.metaKey)) {
    // 使用 nextTick 确保事件正确传递
    emit('node-click', nodeId, event)
  }
}

const handleNodeDoubleClick = (nodeId) => {
  console.log('Double click on node:', nodeId)
  emit('node-dblclick', nodeId)
}

const handleEditNode = (node) => {
  emit('edit-node', node)
}

const handleDeleteNode = (nodeId) => {
  // 直接 emit 事件，由父组件处理确认和删除
  emit('delete-node', nodeId)
}

// 设置section容器引用
const setSectionContainerRef = (sectionId, el) => {
  if (el) {
    sectionContainerRefs.value[sectionId] = el
  }
}

// 获取 section 容器样式（确保高度足够容纳所有节点）
const getSectionContainerStyle = (section) => {
  // 使用 containerStyleKey 来触发重新计算
  const _ = containerStyleKey.value
  
  let minHeight = '80px'
  
  // 计算所有节点的最大 y 坐标，确保容器高度足够（支持自动换行，高度不限制）
  if (section.nodes && section.nodes.length > 0) {
    const nodeMaxWidth = 300 // 节点最大宽度（与 KnowledgeCard 的 max-w-[300px] 一致）
    const nodeHeight = 70 // 节点默认高度
    const horizontalSpacing = 100 // 水平间距（大于100px）
    const verticalSpacing = 20 // 垂直间距
    
    // 获取容器宽度（如果容器还没准备好，使用默认值）
    const container = sectionContainerRefs.value[section.id]
    const containerWidth = container ? container.clientWidth : 800 // 默认800px
    const availableWidth = containerWidth - 40 // 减去左右padding
    
    // 计算每行可以放多少个节点（使用最大宽度作为计算基准）
    const nodesPerRow = Math.floor((availableWidth + horizontalSpacing) / (nodeMaxWidth + horizontalSpacing))
    const actualNodesPerRow = Math.max(1, nodesPerRow) // 至少1个
    
    // 使用 position 字段排序
    const sortedNodes = [...section.nodes].sort((a, b) => {
      const posA = a.position != null ? a.position : section.nodes.findIndex(n => n.id === a.id)
      const posB = b.position != null ? b.position : section.nodes.findIndex(n => n.id === b.id)
      return posA - posB
    })
    
    let maxY = 0
    
    sortedNodes.forEach((node, index) => {
      // 尝试获取节点的实际高度（如果节点已经渲染）
      let actualNodeHeight = nodeHeight // 默认高度
      const nodeElement = nodeRefs.value[`${section.id}-${node.id}`]
      if (nodeElement) {
        const rect = nodeElement.getBoundingClientRect()
        actualNodeHeight = Math.max(rect.height || nodeHeight, 70) // 至少70px
      } else {
        // 如果节点还没渲染，使用估算值（考虑内容可能换行）
        actualNodeHeight = 100 // 估算节点可能的最大高度（考虑内容换行）
      }
      
      if (node.x != null && node.y != null) {
        // 使用保存的位置，加上实际节点高度
        maxY = Math.max(maxY, node.y + actualNodeHeight)
      } else {
        // 使用默认位置计算（自动换行）
        const row = Math.floor(index / actualNodesPerRow)
        const defaultY = row * (nodeHeight + verticalSpacing)
        maxY = Math.max(maxY, defaultY + actualNodeHeight)
      }
    })
    
    // 使用 minHeight 允许容器根据内容自动扩展，确保包含所有节点
    minHeight = `${Math.max(maxY + 40, 80)}px` // 至少 80px，加上足够的边距（40px）
  }
  
  return {
    minHeight: minHeight,
    position: 'relative',
    width: '100%',
    overflow: 'visible', // 确保节点不会被裁剪
    // 不设置 maxHeight，允许容器根据内容无限扩展
  }
}

// 获取节点样式（绝对定位）
const getNodeStyle = (node, sectionId) => {
  // 如果节点有保存的位置（x 和 y 都不为空），使用保存的位置
  if (node.x != null && node.y != null) {
    return {
      left: `${node.x}px`,
      top: `${node.y}px`
    }
  }
  
  // 否则使用默认位置（按 position 排序，自动换行，间隔大于100px）
  const section = props.chapter.sections.find(s => s.id === sectionId)
  if (!section) {
    return { left: '0px', top: '0px' }
  }
  
  // 使用 position 字段排序，如果没有则使用索引
  const sortedNodes = [...section.nodes].sort((a, b) => {
    const posA = a.position != null ? a.position : section.nodes.findIndex(n => n.id === a.id)
    const posB = b.position != null ? b.position : section.nodes.findIndex(n => n.id === b.id)
    return posA - posB
  })
  
  const nodeIndex = sortedNodes.findIndex(n => n.id === node.id)
  const nodeMaxWidth = 300 // 节点最大宽度（与 KnowledgeCard 的 max-w-[300px] 一致）
  const nodeMinWidth = 180 // 节点最小宽度（与 KnowledgeCard 的 min-w-[180px] 一致）
  const nodeHeight = 70 // 节点默认高度
  const horizontalSpacing = 100 // 水平间距（大于100px）
  const verticalSpacing = 20 // 垂直间距
  
  // 获取容器宽度（如果容器还没准备好，使用默认值）
  const container = sectionContainerRefs.value[sectionId]
  const containerWidth = container ? container.clientWidth : 800 // 默认800px
  const availableWidth = containerWidth - 40 // 减去左右padding
  
  // 计算每行可以放多少个节点（使用最大宽度作为计算基准，确保有足够空间）
  const nodesPerRow = Math.floor((availableWidth + horizontalSpacing) / (nodeMaxWidth + horizontalSpacing))
  const actualNodesPerRow = Math.max(1, nodesPerRow) // 至少1个
  
  // 计算节点所在的行和列
  const row = Math.floor(nodeIndex / actualNodesPerRow)
  const col = nodeIndex % actualNodesPerRow
  
  // 计算默认位置：自动换行（使用最大宽度作为间距基准）
  const defaultX = col * (nodeMaxWidth + horizontalSpacing)
  const defaultY = row * (nodeHeight + verticalSpacing)
  
  return {
    left: `${defaultX}px`,
    top: `${defaultY}px`
  }
}

// 拖曳性能优化：缓存容器和节点尺寸
const dragCache = {
  containerRect: null,
  nodeWidth: null,
  nodeHeight: null,
  containerWidth: null,
  containerHeight: null
}

// 鼠标拖拽处理
const handleMouseDown = (event, nodeId, index, sectionId) => {
  // 如果按住 Ctrl 键，不触发拖拽（用于连接功能）
  if (event.ctrlKey || event.metaKey) {
    return
  }
  
  // 如果点击的是按钮，不触发拖拽
  if (event.target.closest('button') || event.target.closest('i')) {
    return
  }
  
  event.preventDefault()
  
  const node = props.chapter.sections.find(s => s.id === sectionId)?.nodes.find(n => n.id === nodeId)
  if (!node) return
  
  const container = sectionContainerRefs.value[sectionId]
  if (!container) return
  
  const nodeElement = nodeRefs.value[`${sectionId}-${nodeId}`]
  if (!nodeElement) return
  
  // 缓存容器和节点尺寸（只在开始时计算一次）
  const containerRect = container.getBoundingClientRect()
  const nodeRect = nodeElement.getBoundingClientRect()
  
  dragCache.containerRect = containerRect
  dragCache.nodeWidth = nodeRect.width
  dragCache.nodeHeight = nodeRect.height
  dragCache.containerWidth = containerRect.width
  dragCache.containerHeight = containerRect.height
  
  // 计算鼠标相对于节点的偏移
  dragOffset.value = {
    x: event.clientX - nodeRect.left,
    y: event.clientY - nodeRect.top
  }
  
  draggingNodeId.value = nodeId
  dragStartIndex.value = index
  dragStartSectionId.value = sectionId
  isDragging.value = true
  
  // 添加全局事件监听（使用 passive 优化）
  document.addEventListener('mousemove', handleMouseMove, { passive: true })
  document.addEventListener('mouseup', handleMouseUp)
  
  // 防止文本选择
  event.preventDefault()
}

// 节流连接线更新（使用时间戳，每 50ms 更新一次）
let lastConnectionUpdateTime = 0
const CONNECTION_UPDATE_INTERVAL = 50 // 50ms

const handleMouseMove = (event) => {
  if (!isDragging.value || !draggingNodeId.value) return
  
  // 直接更新，不使用 requestAnimationFrame（mousemove 本身已经很快）
  const sectionId = dragStartSectionId.value
  
  // 使用缓存的容器尺寸，避免频繁调用 getBoundingClientRect
  if (!dragCache.containerRect) return
  
  const containerRect = dragCache.containerRect
  
  // 计算新位置（相对于容器）
  const newX = event.clientX - containerRect.left - dragOffset.value.x
  const newY = event.clientY - containerRect.top - dragOffset.value.y
  
  // 限制在容器内（使用缓存的节点尺寸）
  const nodeWidth = dragCache.nodeWidth
  const nodeHeight = dragCache.nodeHeight
  
  const minX = 0
  const minY = 0
  const maxX = dragCache.containerWidth - nodeWidth
  const maxY = dragCache.containerHeight - nodeHeight
  
  const clampedX = Math.max(minX, Math.min(maxX, newX))
  const clampedY = Math.max(minY, Math.min(maxY, newY))
  
  // 更新节点位置（立即更新UI）
  const node = props.chapter.sections.find(s => s.id === sectionId)?.nodes.find(n => n.id === draggingNodeId.value)
  if (node) {
    node.x = clampedX
    node.y = clampedY
    
    // 节流连接线更新：使用时间戳，每 50ms 更新一次
    const now = Date.now()
    if (now - lastConnectionUpdateTime >= CONNECTION_UPDATE_INTERVAL) {
      lastConnectionUpdateTime = now
      emit('node-dragging', { nodeId: draggingNodeId.value, x: clampedX, y: clampedY })
    }
  }
}

const handleMouseUp = async (event) => {
  if (!isDragging.value || !draggingNodeId.value) return
  
  const sectionId = dragStartSectionId.value
  const node = props.chapter.sections.find(s => s.id === sectionId)?.nodes.find(n => n.id === draggingNodeId.value)
  
  if (node && node.x !== null && node.x !== undefined && node.y !== null && node.y !== undefined) {
    // 保存位置到后端
    try {
      const { api } = await import('../api.js')
      await api.updateNodePosition(
        props.projectId,
        draggingNodeId.value,
        sectionId,
        node.x,
        node.y
      )
    } catch (error) {
      console.error('Failed to update node position:', error)
    }
  }
  
  // 通知父组件拖拽结束，更新连接线（最终更新）
  emit('node-drag-end', { nodeId: draggingNodeId.value })
  
  // 清理
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  
  // 清理动画帧（如果存在）
  if (dragAnimationFrame.value) {
    cancelAnimationFrame(dragAnimationFrame.value)
    dragAnimationFrame.value = null
  }
  
  // 清理缓存和重置时间戳
  dragCache.containerRect = null
  dragCache.nodeWidth = null
  dragCache.nodeHeight = null
  dragCache.containerWidth = null
  dragCache.containerHeight = null
  lastConnectionUpdateTime = 0
  
  draggingNodeId.value = null
  dragStartIndex.value = null
  dragStartSectionId.value = null
  isDragging.value = false
  dragOffset.value = { x: 0, y: 0 }
}

// 旧的拖拽处理函数（保留用于兼容，但不再使用）
const handleDragStart = (event, nodeId, index, sectionId) => {
  draggingNodeId.value = nodeId
  dragStartIndex.value = index
  dragStartSectionId.value = sectionId
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', nodeId)
  // 添加拖拽样式
  if (event.target) {
    event.target.style.cursor = 'grabbing'
  }
}

const handleDragEnter = (event, index, sectionId) => {
  if (draggingNodeId.value && dragStartSectionId.value === sectionId) {
    dragOverIndex.value = index
  }
}

const handleDragOver = (event, index, sectionId) => {
  if (draggingNodeId.value && dragStartSectionId.value === sectionId) {
    event.preventDefault()
    dragOverIndex.value = index
  }
}

const handleDragLeave = () => {
  // 延迟清除，避免快速移动时闪烁
  setTimeout(() => {
    if (dragOverIndex.value !== null) {
      dragOverIndex.value = null
    }
  }, 50)
}

const handleDrop = async (event, targetNodeId, targetIndex, sectionId) => {
  event.preventDefault()
  
  if (!draggingNodeId.value || dragStartSectionId.value !== sectionId) {
    return
  }
  
  const section = props.chapter.sections.find(s => s.id === sectionId)
  if (!section) return
  
  const sourceIndex = dragStartIndex.value
  const targetIdx = targetIndex
  
  if (sourceIndex === targetIdx) {
    handleDragEnd()
    return
  }
  
  // 创建新的节点顺序
  const newNodes = [...section.nodes]
  const [removed] = newNodes.splice(sourceIndex, 1)
  newNodes.splice(targetIdx, 0, removed)
  
  // 更新本地状态（立即更新，提供即时反馈）
  section.nodes = newNodes
  
  // 调用 API 保存新顺序
  try {
    const { api } = await import('../api.js')
    await api.reorderNodes(
      props.projectId,
      sectionId,
      newNodes.map(n => n.id)
    )
  } catch (error) {
    console.error('Failed to reorder nodes:', error)
    // 如果失败，恢复原顺序（需要重新加载数据）
    emit('reorder-failed', { sectionId, originalNodes: section.nodes })
  }
  
  handleDragEnd()
}

const handleDragEnd = () => {
  draggingNodeId.value = null
  dragOverIndex.value = null
  dragStartIndex.value = null
  dragStartSectionId.value = null
}

// 使用防抖优化节点位置更新
const nodePositionUpdateTimers = new Map()
const MAX_TIMERS = 100 // 限制定时器数量

const setNodeRef = (nodeId, el, index, sectionId) => {
  if (el) {
    const key = `${sectionId}-${nodeId}`
    nodeRefs.value[key] = el
    
    // 防抖更新位置
    const timerKey = key
    if (nodePositionUpdateTimers.has(timerKey)) {
      clearTimeout(nodePositionUpdateTimers.get(timerKey))
    }
    
    // 限制定时器数量，防止内存泄漏
    if (nodePositionUpdateTimers.size > MAX_TIMERS) {
      // 清理最旧的定时器
      const firstKey = nodePositionUpdateTimers.keys().next().value
      clearTimeout(nodePositionUpdateTimers.get(firstKey))
      nodePositionUpdateTimers.delete(firstKey)
    }
    
    nodePositionUpdateTimers.set(timerKey, setTimeout(() => {
      nextTick(() => {
        updateNodePosition(nodeId, sectionId)
        // 更新完成后删除定时器引用
        nodePositionUpdateTimers.delete(timerKey)
      })
    }, 50))
  }
}

// 添加一个响应式变量来强制更新容器样式
const containerStyleKey = ref(0)

// 监听节点变化，更新位置和容器高度
watch(() => props.chapter.sections, (sections) => {
  nextTick(() => {
    sections.forEach(section => {
      section.nodes.forEach(node => {
        const key = `${section.id}-${node.id}`
        const el = nodeRefs.value[key]
        if (el) {
          updateNodePosition(node.id, section.id)
        }
      })
    })
    // 触发容器高度重新计算
    containerStyleKey.value++
  })
}, { deep: true, immediate: true })

// 监听节点内容变化，更新容器高度
watch(() => {
  // 监听所有节点的内容变化
  return props.chapter.sections.flatMap(s => s.nodes.map(n => ({
    id: n.id,
    name: n.name,
    content: n.content,
    x: n.x,
    y: n.y
  })))
}, () => {
  // 节点内容变化后，等待 DOM 更新，然后触发容器高度重新计算
  nextTick(() => {
    containerStyleKey.value++
  })
}, { deep: true })


// 组件卸载时清理所有定时器
onUnmounted(() => {
  nodePositionUpdateTimers.forEach(timer => clearTimeout(timer))
  nodePositionUpdateTimers.clear()
  nodeRefs.value = {}
  nodePositions.value = {}
})

const updateNodePosition = (nodeId, sectionId) => {
  const key = `${sectionId}-${nodeId}`
  const el = nodeRefs.value[key]
  if (!el) return
  
  // 在 Vue 3 中，ref 可能是组件实例，需要获取 $el 或直接使用 DOM 元素
  // 对于组件，尝试获取 $el 属性（Vue 2 风格）或直接使用（Vue 3 中组件实例没有 $el）
  let domElement = el
  if (el && typeof el === 'object' && '$el' in el) {
    domElement = el.$el
  }
  
  // 确保是 DOM 元素
  if (!domElement || typeof domElement.getBoundingClientRect !== 'function') {
    // 如果还不是 DOM 元素，尝试查找根元素
    if (domElement && typeof domElement === 'object' && 'querySelector' in domElement) {
      // 可能是组件实例，尝试查找根元素
      return
    }
    console.warn('Element is not a DOM element:', domElement)
    return
  }
  
  try {
    const rect = domElement.getBoundingClientRect()
    const container = domElement.closest('.relative')
    if (container && typeof container.getBoundingClientRect === 'function') {
      const containerRect = container.getBoundingClientRect()
      // 使用响应式更新
      nodePositions.value = {
        ...nodePositions.value,
        [key]: {
          x: rect.left - containerRect.left + rect.width / 2,
          y: rect.top - containerRect.top + rect.height / 2,
          width: rect.width,
          height: rect.height
        }
      }
    }
  } catch (e) {
    console.warn('Error updating node position:', e)
  }
}

// 获取节点中心位置
const getNodeCenter = (nodeId, section) => {
  const key = `${section.id}-${nodeId}`
  const pos = nodePositions.value[key]
  if (pos) {
    return { x: pos.x, y: pos.y, width: pos.width || 180, height: pos.height || 70 }
  }
  
  // 如果位置未计算，返回估算值
  const nodeIndex = section.nodes.findIndex(n => n.id === nodeId)
  if (nodeIndex >= 0) {
    return { x: 100 + nodeIndex * 200, y: 60, width: 180, height: 70 }
  }
  return { x: 0, y: 0, width: 180, height: 70 }
}

// 计算节点边缘的连接点
const getNodeEdgePoint = (nodeId, section, targetNodeId, targetSection) => {
  const source = getNodeCenter(nodeId, section)
  const target = getNodeCenter(targetNodeId, targetSection)
  
  // 计算方向向量
  const dx = target.x - source.x
  const dy = target.y - source.y
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  if (distance === 0) {
    return { x: source.x, y: source.y }
  }
  
  // 归一化方向向量
  const nx = dx / distance
  const ny = dy / distance
  
  // 计算边缘点（从中心点向目标方向延伸，到达节点边缘）
  // 使用节点的半宽和半高来计算边缘点
  const halfWidth = source.width / 2
  const halfHeight = source.height / 2
  
  // 计算在节点矩形上的交点
  // 使用更精确的矩形边界计算
  let edgeX, edgeY
  
  // 计算斜率
  if (Math.abs(dx) > Math.abs(dy)) {
    // 水平方向为主，从左右边缘出发
    const slope = dy / dx
    const signX = dx > 0 ? 1 : -1
    edgeX = source.x + signX * halfWidth
    edgeY = source.y + slope * (edgeX - source.x)
    
    // 检查是否超出上下边界
    if (Math.abs(edgeY - source.y) > halfHeight) {
      const signY = dy > 0 ? 1 : -1
      edgeY = source.y + signY * halfHeight
      edgeX = source.x + (edgeY - source.y) / slope
    }
  } else {
    // 垂直方向为主，从上下边缘出发
    const slope = dx / dy
    const signY = dy > 0 ? 1 : -1
    edgeY = source.y + signY * halfHeight
    edgeX = source.x + slope * (edgeY - source.y)
    
    // 检查是否超出左右边界
    if (Math.abs(edgeX - source.x) > halfWidth) {
      const signX = dx > 0 ? 1 : -1
      edgeX = source.x + signX * halfWidth
      edgeY = source.y + (edgeX - source.x) / slope
    }
  }
  
  return { x: edgeX, y: edgeY }
}

const getNodeX = (nodeId, section) => {
  return getNodeCenter(nodeId, section).x
}

const getNodeY = (nodeId, section) => {
  return getNodeCenter(nodeId, section).y
}
</script>

