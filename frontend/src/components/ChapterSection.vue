<template>
  <div
    ref="chapterRef"
    :class="[
      'relative p-4 rounded-lg border border-gray-200 bg-white shadow-sm transition',
      // 核心修复：自由模式下章节不允许拖动，移除 cursor-move
      chapterLayout === 'free' ? 'cursor-default' : 'cursor-move',
      isHexColor(chapterColor.border) ? '' : chapterColor.border,
      isHexColor(chapterColor.bg) ? '' : chapterColor.bg
    ]"
    :style="getChapterContainerStyle()"
    :data-chapter-id="chapter.id"
    @mousedown="(e) => handleChapterMouseDown(e, chapter.id)"
  >
    <!-- Chapter Badge -->
    <div
      :class="[
        'absolute -left-3 top-6 px-2.5 py-1 text-xs font-semibold rounded-lg shadow-sm border border-gray-200',
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
      <h2 
        class="text-lg font-bold flex items-center gap-2 px-2 py-1 rounded"
      >
        <i :class="[chapterIcon, 'text-lg']"></i>
        {{ chapter.name }}
      </h2>
      <div class="flex gap-2">
        <button
          @click.stop="emit('edit-item', { type: 'chapter', id: chapter.id, chapterId: chapter.id })"
          class="p-1.5 text-gray-400 hover:text-blue-600 transition rounded"
          title="编辑章节属性"
        >
          <i class="ph ph-pencil"></i>
        </button>
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
    <div 
      ref="sectionsContainerRef"
      :class="[
        'flex',
        chapterLayout === 'row' ? 'flex-col' : chapterLayout === 'column' ? 'flex-row flex-wrap items-start' : 'relative'
      ]"
      :style="{
        gap: chapterLayout === 'free' ? '0' : `${props.sectionSpacing}px`,
        //  行列模式下移除 minHeight，防止父级撑大
        minHeight: chapterLayout === 'free' ? '400px' : 'auto'
      }"
    >
      <div
        v-for="(section, index) in chapter.sections"
        :key="section.id"
        :data-section-id="section.id"
        :class="[
          'bg-white p-3 rounded-lg border border-gray-200 shadow-sm cursor-move transition',
          chapterLayout === 'free' ? 'absolute' : '',
          chapterLayout === 'row' ? 'w-full' : '',
          chapterLayout === 'column' ? 'flex-1 min-w-[300px]' : '',
          draggingSectionId === section.id ? 'opacity-50 scale-95' : 'hover:shadow-md hover:border-gray-300'
        ]"
        :style="getSectionStyle(section, index)"
        @mousedown="(e) => handleSectionMouseDown(e, section.id, index)"
      >
        <!-- Resize Handles -->
        <template v-if="true">
          <!-- Edges - 更宽的手柄，更容易点击 -->
          <div
            class="absolute inset-y-0 left-0 w-3 cursor-ew-resize z-20 hover:bg-blue-200 hover:bg-opacity-30 transition-colors"
            @mousedown.stop.prevent="(e) => startSectionResize(e, section, 'w')"
            title="拉伸宽度"
          ></div>
          <div
            class="absolute inset-y-0 right-0 w-3 cursor-ew-resize z-20 hover:bg-blue-200 hover:bg-opacity-30 transition-colors"
            @mousedown.stop.prevent="(e) => startSectionResize(e, section, 'e')"
            title="拉伸宽度"
          ></div>
          <div
            class="absolute inset-x-0 top-0 h-3 cursor-ns-resize z-20 hover:bg-blue-200 hover:bg-opacity-30 transition-colors"
            @mousedown.stop.prevent="(e) => startSectionResize(e, section, 'n')"
            title="拉伸高度"
          ></div>
          <div
            class="absolute inset-x-0 bottom-0 h-3 cursor-ns-resize z-20 hover:bg-blue-200 hover:bg-opacity-30 transition-colors"
            @mousedown.stop.prevent="(e) => startSectionResize(e, section, 's')"
            title="拉伸高度"
          ></div>
          <!-- Corners - 更大的角落手柄 -->
          <div
            class="absolute top-0 left-0 w-4 h-4 -mt-2 -ml-2 rounded-sm bg-blue-400 bg-opacity-0 hover:bg-opacity-30 cursor-nwse-resize z-30 transition-all"
            @mousedown.stop.prevent="(e) => startSectionResize(e, section, 'nw')"
            title="拉伸宽度和高度"
          ></div>
          <div
            class="absolute top-0 right-0 w-4 h-4 -mt-2 -mr-2 rounded-sm bg-blue-400 bg-opacity-0 hover:bg-opacity-30 cursor-nesw-resize z-30 transition-all"
            @mousedown.stop.prevent="(e) => startSectionResize(e, section, 'ne')"
            title="拉伸宽度和高度"
          ></div>
          <div
            class="absolute bottom-0 left-0 w-4 h-4 -mb-2 -ml-2 rounded-sm bg-blue-400 bg-opacity-0 hover:bg-opacity-30 cursor-nesw-resize z-30 transition-all"
            @mousedown.stop.prevent="(e) => startSectionResize(e, section, 'sw')"
            title="拉伸宽度和高度"
          ></div>
          <div
            class="absolute bottom-0 right-0 w-4 h-4 -mb-2 -mr-2 rounded-sm bg-blue-400 bg-opacity-0 hover:bg-opacity-30 cursor-nwse-resize z-30 transition-all"
            @mousedown.stop.prevent="(e) => startSectionResize(e, section, 'se')"
            title="拉伸宽度和高度"
          ></div>
        </template>
        <!-- Section Header -->
        <div 
          class="flex items-center justify-between mb-2"
          :class="isHexColor(chapterColor.text) ? '' : chapterColor.text"
          :style="{
            color: isHexColor(chapterColor.text) ? chapterColor.text : undefined
          }"
        >
          <h3 
            class="font-medium text-sm px-2 py-1 rounded"
          >
            {{ section.name }}
          </h3>
          <div class="flex gap-2">
            <button
              @click.stop="emit('edit-item', { type: 'section', id: section.id, sectionId: section.id, chapterId: chapter.id })"
              class="p-1 text-gray-400 hover:text-blue-600 transition text-xs"
              title="编辑部分属性"
            >
              <i class="ph ph-pencil"></i>
            </button>
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
            :ref="(el) => registerNodeRef(node.id, el, section.id)"
            :data-node-id="node.id"
            :class="[
              //  只有在真正的自由模式下，或者是正在拖拽时，才加 absolute
              ((nodeLayout === 'free' || chapterLayout === 'free') || draggingNodeId === node.id) ? 'absolute' : '',
              draggingNodeId === node.id 
                ? 'opacity-90 z-50' 
                : ''
            ]"
            :style="{
              //  核心修复：拖拽时优先使用 dragStartNodeStyle
              // 这解决了行列模式下，初始拖拽没有坐标导致跳变/无法移动的问题
              ...(draggingNodeId === node.id 
                  ? dragStartNodeStyle 
                  : getNodeStyle(node, section.id)
              ),
              
              // 核心修复：拖拽时必须禁用 transition，否则会跟手不灵敏
              transition: draggingNodeId === node.id ? 'none' : 'box-shadow 0.2s, transform 0.1s, left 0.2s, top 0.2s',
              
              //  position 逻辑：拖拽时强制 absolute
              position: (
                draggingNodeId === node.id || 
                ((nodeLayout === 'free' || chapterLayout === 'free') && node.x != null)
              ) ? 'absolute' : undefined,
              
              // z-index
              zIndex: draggingNodeId === node.id ? 100 : ((nodeLayout === 'free' || chapterLayout === 'free') ? 15 : undefined)
            }"
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
                :border-color="node.borderColor || undefined"
                :background-color="node.backgroundColor || node.fillColor || undefined"
              :class="getLinkStatusClass(node.id)"
              :style="{ maxWidth: `${props.nodeWidth}px`, minWidth: `${Math.min(props.nodeWidth * 0.6, 180)}px` }"
              @click="(e) => { handleNodeClick(node.id, e); }"
              @dblclick="() => handleNodeDoubleClick(node.id)"
              @edit="emit('edit-item', { type: 'node', id: node.id, nodeId: node.id, sectionId: section.id, chapterId: chapter.id })"
              @delete="handleDeleteNode(node.id)"
            />
          </div>
          <button
            v-if="section.nodes.length === 0"
            @click="showAddNodeModal(section.id)"
            class="p-3 rounded-lg border border-dashed border-gray-300 text-gray-400 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition text-sm min-w-[180px] h-[70px] flex items-center justify-center gap-2 flex-shrink-0"
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
        class="w-full p-4 rounded-lg border border-dashed border-gray-300 text-gray-400 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition text-sm flex items-center justify-center gap-2"
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
      <div class="bg-white p-6 rounded-lg w-96 shadow-lg border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">添加部分</h3>
        <input
          v-model="newSectionName"
          @keyup.enter="addSection"
          class="w-full border border-gray-300 px-3 py-2 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="部分名称 (如: 1.1 基本概念)"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="showAddSectionModal = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            取消
          </button>
          <button
            @click="addSection"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition shadow-sm"
          >
            创建
          </button>
        </div>
      </div>
    </div>

    <!-- Rename Chapter Modal -->
    <div
      v-if="showRenameChapterModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showRenameChapterModal = false"
    >
      <div class="bg-white p-6 rounded-lg w-96 shadow-lg border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">重命名章节</h3>
        <input
          v-model="renameChapterName"
          @keyup.enter="renameChapter"
          class="w-full border border-gray-300 px-3 py-2 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="章节名称"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="showRenameChapterModal = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            取消
          </button>
          <button
            @click="renameChapter"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition shadow-sm"
          >
            保存
          </button>
        </div>
      </div>
    </div>

    <!-- Rename Section Modal -->
    <div
      v-if="showRenameSectionModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showRenameSectionModal = false"
    >
      <div class="bg-white p-6 rounded-lg w-96 shadow-lg border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">重命名部分</h3>
        <input
          v-model="renameSectionName"
          @keyup.enter="renameSection"
          class="w-full border border-gray-300 px-3 py-2 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="部分名称"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="showRenameSectionModal = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            取消
          </button>
          <button
            @click="renameSection"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition shadow-sm"
          >
            保存
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
      <div class="bg-white p-6 rounded-lg w-96 shadow-lg border border-gray-200">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">添加知识点</h3>
        <input
          v-model="newNodeName"
          @keyup.enter="addNode"
          class="w-full border border-gray-300 px-3 py-2 rounded-lg mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          :placeholder="`知识点名称，留空则使用默认名称`"
        />
        <textarea
          v-model="newNodeContent"
          class="w-full border border-gray-300 px-3 py-2 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          placeholder="备注/内容 (可选)"
          rows="3"
        ></textarea>
        <div class="flex justify-end gap-2">
          <button
            @click="showAddNodeModalForSection = null"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            取消
          </button>
          <button
            @click="addNode"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition shadow-sm"
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
import { useProjectStore } from '../stores/projectStore'
// 删除 useElementBounding 引入，避免为每个节点创建 ResizeObserver 导致性能问题

const projectStore = useProjectStore()

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
  },
  globalLayout: {
    type: String,
    default: 'row',
    validator: (value) => ['row', 'column'].includes(value)
  },
  globalChapterLayout: {
    type: String,
    default: 'column',
    validator: (value) => ['row', 'column', 'free'].includes(value)
  },
  globalNodeLayout: {
    type: String,
    default: 'wrap',
    validator: (value) => ['row', 'column', 'wrap'].includes(value)
  },
  globalNodeAlignment: {
    type: String,
    default: 'flex-start',
    validator: (value) => ['flex-start', 'center', 'flex-end', 'space-between', 'space-around', 'space-evenly'].includes(value)
  },
  nodeWidth: {
    type: Number,
    default: 300
  },
  nodeHeight: {
    type: Number,
    default: 70
  },
  horizontalSpacing: {
    type: Number,
    default: 100
  },
  verticalSpacing: {
    type: Number,
    default: 20
  },
  chapterWidth: {
    type: Number,
    default: null
  },
  chapterHeight: {
    type: Number,
    default: null
  },
  sectionWidth: {
    type: Number,
    default: null
  },
  sectionHeight: {
    type: Number,
    default: null
  },
  sectionSpacing: {
    type: Number,
    default: 12
  },
  nodeAlignment: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'center', 'right', 'justify-between', 'space-evenly', 'space-around'].includes(value)
  }
})

const emit = defineEmits([
  'chapter-selected',
  'add-section',
  'delete-chapter',
  'delete-section',
  'add-node',
  'edit-node',
  'delete-node',
  'node-click',
  'node-dblclick',
  'update-node-positions',
  'update-node-position', //  新增：用于通知父组件更新单个节点位置
  'edit-item',
  'node-dragging',
  'node-drag-end',
  'section-reorder',
  'chapter-reorder',
  'section-position-updated',
  'section-dragging',
  'section-drag-end',
  'section-size-updated',
  'chapter-layout-change',
  'chapter-updated',
  'chapter-selected',
  'section-updated'
])

const showAddSectionModal = ref(false)
const showAddNodeModalForSection = ref(null)
const newSectionName = ref('')
const newNodeName = ref('')
const newNodeContent = ref('')
const showRenameChapterModal = ref(false)
const renameChapterName = ref('')
const showRenameSectionModal = ref(false)
const renameSectionName = ref('')
const renamingSectionId = ref(null)
const nodeRefs = ref({})
const nodePositions = ref({})
const sectionContainerRefs = ref({})
const chapterRef = ref(null)
const sectionsContainerRef = ref(null)

// 拖拽相关状态
const draggingNodeId = ref(null)
const draggingSectionId = ref(null)
const draggingChapterId = ref(null)

// 节点拖拽独立变量
const isDraggingNode = ref(false)
const nodeDragOffset = ref({ x: 0, y: 0 })
const nodeDragStartIndex = ref(null)
const nodeDragStartSectionId = ref(null)

// Section 拖拽独立变量
const isDraggingSection = ref(false)
const sectionDragOffset = ref({ x: 0, y: 0 })
// Section 拖拽时的原始状态
const originalSectionState = ref({
  width: null,
  height: null,
  x: null,
  y: null
})
// Delta 算法拖拽状态变量
const dragStartData = ref({ mouseX: 0, mouseY: 0, initialLeft: 0, initialTop: 0 })
const nodeDragStartData = ref({ mouseX: 0, mouseY: 0, initialLeft: 0, initialTop: 0 })

// Chapter 拖拽时的原始状态
const originalChapterState = ref({
  width: null,
  height: null,
  x: null,
  y: null
})

// 节点拖拽时的原始状态（用于保持尺寸和位置）
const originalNodeState = ref({
  width: null,
  height: null,
  x: null,
  y: null
})

// 用于存储拖动开始瞬间节点的样式，防止在行列模式下拖动时跳变
const dragStartNodeStyle = ref({})

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
  const schemeColor = chapterColors.value[index]
  const customBorder = props.chapter.borderColor
  const customBg = props.chapter.backgroundColor

  return {
    ...schemeColor,
    border: customBorder || schemeColor.border,
    bg: customBg || schemeColor.bg
  }
})

const chapterIcon = computed(() => {
  const index = (props.chapterIndex - 1) % chapterIcons.length
  return chapterIcons[index]
})

// 章节布局 - 使用全局布局控制
//  核心修复：全局设置拥有最高优先级，忽略数据中的坐标
const chapterLayout = computed(() => {
  // 1. 核心修复：如果全局明确指定了 'row' 或 'column'，必须无条件服从
  // 此时忽略数据中已有的 x/y 坐标
  if (props.globalChapterLayout === 'row' || props.globalChapterLayout === 'column') {
    return props.globalChapterLayout
  }

  // 2. 只有在全局设置为 'free' 或者未定义时，才根据是否有坐标来智能判断
  if (props.globalChapterLayout === 'free') {
    return 'free'
  }
  
  // 3. 智能回退：如果没指定布局，但发现用户拖拽过(有坐标)，则显示为 free
  const hasPositionedSections = props.chapter.sections.some(s => s.x != null || s.y != null)
  if (hasPositionedSections) {
    return 'free'
  }
  
  // 4. 默认兜底
  return 'column'
})

// 修复 initializeSectionPositions
const initializeSectionPositions = () => {
  const isFreeMode = chapterLayout.value === 'free'
  
  nextTick(() => {
    // 1. 如果不是自由模式，清除可能的脏样式，让 Flex 接管
    if (!isFreeMode) {
      adjustParentContainers()
      emit('chapter-updated')
      return 
    }

    // 2. 自由模式逻辑：如果是初次进入自由模式（数据里没有 x/y），则抓取当前 DOM 位置
    // 核心修复：获取中间容器作为参考系
    const containerEl = sectionsContainerRef.value
    if (!containerEl) return
    
    let hasUpdates = false
    
    props.chapter.sections.forEach((section) => {
      const el = document.querySelector(`[data-section-id="${section.id}"]`)
      if (el) {
        // 只有当 x,y 为 null 或 undefined 时才初始化，防止覆盖已保存的位置
        if (section.x == null || section.y == null) {
            // 核心修复：使用 getBoundingClientRect 计算相对位置
            // 防止 offsetParent 不一致导致的巨大偏移
            const containerRect = containerEl.getBoundingClientRect()
            const elRect = el.getBoundingClientRect()

            // 获取容器边框宽度
            const containerStyle = window.getComputedStyle(containerEl)
            const borderLeft = parseFloat(containerStyle.borderLeftWidth) || 0
            const borderTop = parseFloat(containerStyle.borderTopWidth) || 0

            // 相对坐标 = 元素屏幕坐标 - 容器屏幕坐标 - 容器边框
            section.x = elRect.left - containerRect.left - borderLeft
            section.y = elRect.top - containerRect.top - borderTop
            
            // 锁定尺寸
            section.width = el.offsetWidth
            section.height = el.offsetHeight
            
            hasUpdates = true
        }
        
        // 同样处理 Nodes
        section.nodes.forEach(node => {
            const nodeEl = nodeRefs.value[`${section.id}-${node.id}`]
            // 兼容 Vue ref
            const domNode = (nodeEl && nodeEl.$el) ? nodeEl.$el : nodeEl
            
            if (domNode && (node.x == null || node.y == null)) {
                node.x = domNode.offsetLeft
                node.y = domNode.offsetTop
                hasUpdates = true
            }
        })
      }
    })

    if (hasUpdates) {
        // 如果我们初始化了位置，保存一下，或者至少触发视图更新
        emit('chapter-updated')
    }
  })
}

//  辅助函数：调整父容器大小，确保包含所有子元素 (自适应高度核心)
const adjustParentContainers = () => {
  //  修复：行列模式下，清除所有强制的高度样式，让 Flexbox/CSS 决定高度
  // 自由模式下才需要精确计算高度
  
  // 1. 调整每个 Section 的大小
  props.chapter.sections.forEach((section) => {
    const sectionEl = document.querySelector(`[data-section-id="${section.id}"]`)
    if (!sectionEl) return
    
    //  核心修改：行列模式下，清除所有强制的高度样式，让 Flexbox/CSS 决定高度
    if (chapterLayout.value !== 'free') {
      sectionEl.style.minHeight = '' // 清除内联样式
      sectionEl.style.height = ''    // 清除内联样式
      return
    }
    
    //  自由模式：需要精确计算高度
    if (!section.nodes || section.nodes.length === 0) {
      sectionEl.style.minHeight = `${props.sectionHeight || 100}px`
      sectionEl.style.height = 'auto'
      return
    }
    
    let maxBottom = 0
    let isFreeLayout = false
    
    // 计算所有节点的底部位置
    section.nodes.forEach((node) => {
      //  优先从 Pinia 缓存获取位置（用于模式切换时的准确性）
      const cached = projectStore.getRowColumnLayout('node', node.id)
      if (cached) {
        isFreeLayout = true
        maxBottom = Math.max(maxBottom, cached.y + cached.height)
      }
      // 方式 A: 自由布局 (有坐标)
      else if (node.x != null && node.y != null) {
        isFreeLayout = true
        const nodeH = node.height || 70
        maxBottom = Math.max(maxBottom, node.y + nodeH)
      } 
      // 方式 B: 文档流布局 (无坐标)
      else {
        const nodeEl = nodeRefs.value[`${section.id}-${node.id}`]
        if (nodeEl) {
          const nodeRect = nodeEl.getBoundingClientRect()
          const sectionRect = sectionEl.getBoundingClientRect()
          const nodeRelativeBottom = (nodeRect.top - sectionRect.top) + nodeRect.height
          maxBottom = Math.max(maxBottom, nodeRelativeBottom)
        }
      }
    })
    
    if (maxBottom > 0 || section.nodes.length === 0) {
      let requiredHeight = maxBottom
      
      if (isFreeLayout) {
         const sectionHeader = sectionEl.querySelector('div.flex.items-center.justify-between.mb-2')
         const headerHeight = sectionHeader ? sectionHeader.offsetHeight + 8 : 50
         requiredHeight += headerHeight
      }
      
      const PADDING_BOTTOM_SECTION = 40
      requiredHeight += PADDING_BOTTOM_SECTION
      
      const minPropsHeight = props.sectionHeight || 0
      const finalHeight = Math.max(requiredHeight, minPropsHeight)
      
      sectionEl.style.minHeight = `${finalHeight}px`
      sectionEl.style.height = 'auto'
      
      if (section.height < finalHeight) {
         section.height = finalHeight
      }
    }
  })
  
  // 2. 调整 Chapter 的大小
  const chapterEl = chapterRef.value
  if (!chapterEl) return
  
  //  核心修改：行列模式下，清除 Chapter 的高度限制
  if (chapterLayout.value !== 'free') {
    chapterEl.style.minHeight = '' 
    chapterEl.style.height = ''
    return
  }
  
  //  自由模式：需要精确计算高度
  let maxChapterBottom = 0
  
  props.chapter.sections.forEach((section) => {
    if (section.x != null && section.y != null) {
      const sectionH = section.height || 200
      maxChapterBottom = Math.max(maxChapterBottom, section.y + sectionH)
    } else {
      const sectionEl = document.querySelector(`[data-section-id="${section.id}"]`)
      if (sectionEl) {
        const sectionRect = sectionEl.getBoundingClientRect()
        const chapterRect = chapterEl.getBoundingClientRect()
        const sectionRelativeBottom = (sectionRect.top - chapterRect.top) + sectionRect.height
        maxChapterBottom = Math.max(maxChapterBottom, sectionRelativeBottom)
      }
    }
  })
  
  const PADDING_BOTTOM_CHAPTER = 80
  const calculatedHeight = maxChapterBottom + PADDING_BOTTOM_CHAPTER
  const minPropsChapterHeight = props.chapterHeight || 400
  const finalChapterHeight = Math.max(calculatedHeight, minPropsChapterHeight)
  
  chapterEl.style.minHeight = `${finalChapterHeight}px`
  chapterEl.style.height = 'auto'
}

// 监听布局变化，重新初始化位置
watch(
  [() => props.globalChapterLayout, () => props.chapter.sections.length],
  ([newLayout], [oldLayout] = []) => {
    // 当从行/列切换到自由时，先冻结当前 DOM 位置，再进入自由模式
    if (oldLayout && oldLayout !== 'free' && newLayout === 'free' && chapterRef.value) {
      freezeEverything()

      // 将冻结后的行/列布局坐标持久化给父组件（从而存到后端）
      props.chapter.sections.forEach((section) => {
        // Section 坐标
        emit('section-position-updated', {
          sectionId: section.id,
          chapterId: props.chapter.id,
          x: section.x ?? 0,
          y: section.y ?? 0,
          width: section.width,
          height: section.height
        })

        // Node 坐标
        section.nodes.forEach((node) => {
          if (node.x != null && node.y != null) {
            emit('update-node-position', {
              nodeId: node.id,
              sectionId: section.id,
              chapterId: props.chapter.id,
              position: {
                x: node.x,
                y: node.y,
                width: node.width,
                height: node.height
              }
            })
          }
        })
      })
    }
    initializeSectionPositions()
  },
  { immediate: true, flush: 'pre' }
)

// 组件挂载时初始化
onMounted(() => {
  initializeSectionPositions()
  adjustParentContainers()
  saveRowColumnPositions()
  
  //  新增：双重保险，确保挂载后再次检查高度
  // 解决因字体加载、子组件渲染延迟导致的计算偏差
  setTimeout(() => {
    adjustParentContainers()
    containerStyleKey.value++ // 强制触发一次样式重算
    //  新增：行列模式下，渲染完成后保存位置到后端
    if (chapterLayout.value !== 'free') {
      saveRowColumnPositions()
    }
  }, 500)
})

// 节点布局方式（用于行/列模式）
//  核心修复：Node 布局必须跟随父级布局，不能因为有坐标就乱跑
const nodeLayout = computed(() => {
  // 1. 核心修复：如果 Chapter 处于行列模式，Node 必须强制遵循流式布局
  // 无论 Node 数据里有没有 x/y，都不能让它变成 absolute
  if (chapterLayout.value !== 'free') {
    // 使用全局设定的节点布局 (通常是 'wrap')，或者强制 'wrap'
    return props.globalNodeLayout || 'wrap'
  }

  // 2. 只有在 Chapter 是 Free 模式时，才允许 Node 自由飞翔
  return 'free'
})

// 布局变化时强制重新计算节点位置
const layoutKey = ref(0)
watch(() => props.chapter.layout, (newLayout, oldLayout) => {
  if (newLayout !== oldLayout) {
    // 布局改变时，增加 key 值强制重新渲染
    layoutKey.value++
    // 清除所有节点的位置缓存
    nextTick(() => {
      // 触发容器样式重新计算
      containerStyleKey.value++
      //  新增：行列模式下，渲染完成后保存位置到后端
      if (newLayout !== 'free') {
        saveRowColumnPositions()
      }
    })
  }
})

// 监听节点排列方式变化，清除节点位置以重新计算
watch(() => props.nodeAlignment, (newAlignment, oldAlignment) => {
  if (newAlignment !== oldAlignment && oldAlignment !== undefined) {
    // 排列方式改变时，清除所有节点的保存位置，强制重新计算
    props.chapter.sections.forEach(section => {
      section.nodes.forEach(node => {
        node.x = null
        node.y = null
      })
    })
    // 触发重新渲染
    layoutKey.value++
    nextTick(() => {
      containerStyleKey.value++
      //  新增：行列模式下，渲染完成后保存位置到后端
      if (chapterLayout.value !== 'free') {
        saveRowColumnPositions()
      }
    })
  }
})

// 监听全局布局设置变化，重新计算节点位置
watch(() => [
  props.globalLayout, 
  props.nodeWidth, 
  props.nodeHeight, 
  props.horizontalSpacing, 
  props.verticalSpacing,
  props.chapterWidth,
  props.chapterHeight,
  props.sectionWidth,
  props.sectionHeight,
  props.sectionSpacing
], () => {
  // 设置改变时，增加 key 值强制重新渲染
  layoutKey.value++
  // 清除所有节点的位置缓存
  nextTick(() => {
    // 触发容器样式重新计算
    containerStyleKey.value++
    //  新增：行列模式下，渲染完成后保存位置到后端
    if (chapterLayout.value !== 'free') {
      adjustParentContainers()
      saveRowColumnPositions()
    }
  })
}, { deep: true })

//  Watchers for layout changes
watch(() => props.globalChapterLayout, (newVal) => {
  if (newVal === 'free') {
     // Switching TO Free mode: Styles will update via getSectionStyle using Pinia data
     adjustParentContainers()
  } else {
     // Switching TO Row/Column: Reset heights to auto/min, then save positions
     adjustParentContainers()
     saveRowColumnPositions()
  }
  containerStyleKey.value++
})

//  Helper: Get Padding of an element to calculate true absolute position
const getElementPadding = (el) => {
  if (!el) return { left: 0, top: 0 }
  const style = window.getComputedStyle(el)
  return {
    left: parseFloat(style.paddingLeft) || 0,
    top: parseFloat(style.paddingTop) || 0
  }
}

//  修改：保存行列模式下的位置到 Pinia（不保存到后端）
// This captures the "Static" DOM positions and converts them to "Absolute" coordinates
// 核心修复：使用 sectionsContainerRef 作为参考系，而不是 chapterRef
const saveRowColumnPositions = async () => {
  // 只在行列模式下执行
  if (chapterLayout.value === 'free') return
  
  // 延迟执行，确保 DOM 完全渲染
  await nextTick()
  setTimeout(() => {
    try {
      // 1. 获取中间容器 (Sections Container)
      const containerEl = sectionsContainerRef.value
      if (!containerEl) return
      
      props.chapter.sections.forEach((section) => {
        const sectionEl = document.querySelector(`[data-section-id="${section.id}"]`)
        if (sectionEl) {
          // 核心修复：计算相对于中间容器的坐标
          // 使用 getBoundingClientRect 做减法，防止 offsetParent 不一致导致的偏移
          const containerRect = containerEl.getBoundingClientRect()
          const sectionRect = sectionEl.getBoundingClientRect()
          
          // 获取容器边框宽度
          const containerStyle = window.getComputedStyle(containerEl)
          const borderLeft = parseFloat(containerStyle.borderLeftWidth) || 0
          const borderTop = parseFloat(containerStyle.borderTopWidth) || 0
          
          // 修正后的 X/Y (相对于中间容器)
          // 减去 borderLeft/Top 是为了抵消容器边框的影响，确保 (0,0) 贴合内容区
          const sX = sectionRect.left - containerRect.left - borderLeft + containerEl.scrollLeft
          const sY = sectionRect.top - containerRect.top - borderTop + containerEl.scrollTop
          
          const sW = sectionEl.offsetWidth
          const sH = sectionEl.offsetHeight
          
          // 保存到 Pinia
          projectStore.saveRowColumnLayout('section', section.id, {
            x: sX,
            y: sY,
            width: sW,
            height: sH
          })
          
          // 修复：Save Nodes (Relative to Section Container)
          // 注意：nodeEl.offsetLeft/offsetTop 已经是相对于最近的 position: relative 容器（节点容器），
          // 这里不需要再减去 section 的 padding，否则切换到自由模式时节点会整体偏移。
          section.nodes.forEach((node) => {
            const nodeEl = document.querySelector(`[data-node-id="${node.id}"]`)
            if (nodeEl) {
              const nX = nodeEl.offsetLeft
              const nY = nodeEl.offsetTop
              const nW = nodeEl.offsetWidth
              const nH = nodeEl.offsetHeight
              
              // 保存到 Pinia（不保存到后端）
              projectStore.saveRowColumnLayout('node', node.id, {
                x: nX,
                y: nY,
                width: nW,
                height: nH
              })
            }
          })
        }
      })
    } catch (error) {
      console.error('Failed to save row/column positions to Pinia:', error)
    }
  }, 150) // 延迟 150ms 确保 DOM 完全渲染
}

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

// 布局控制已移至全局布局控制模块（App.vue）

// 重命名章节
const renameChapter = async () => {
  if (!renameChapterName.value.trim()) {
    ElMessage.warning('章节名称不能为空')
    return
  }
  try {
    const { api } = await import('../api.js')
    await api.updateChapter(props.projectId, props.chapter.id, { name: renameChapterName.value.trim() })
    showRenameChapterModal.value = false
    renameChapterName.value = ''
    // 触发父组件重新加载项目数据
    emit('chapter-updated')
    ElMessage.success('章节重命名成功')
  } catch (error) {
    console.error('Failed to rename chapter:', error)
    ElMessage.error('重命名失败')
  }
}

// 显示重命名 section 模态框
const openRenameSectionModal = (sectionId, currentName) => {
  renamingSectionId.value = sectionId
  renameSectionName.value = currentName
  showRenameSectionModal.value = true
}

// 重命名 section
const renameSection = async () => {
  if (!renameSectionName.value.trim()) {
    ElMessage.warning('部分名称不能为空')
    return
  }
  if (!renamingSectionId.value) return
  try {
    const { api } = await import('../api.js')
    await api.updateSection(props.projectId, renamingSectionId.value, renameSectionName.value.trim())
    showRenameSectionModal.value = false
    renamingSectionId.value = null
    renameSectionName.value = ''
    // 触发父组件重新加载项目数据
    emit('section-updated')
    ElMessage.success('部分重命名成功')
  } catch (error) {
    console.error('Failed to rename section:', error)
    ElMessage.error('重命名失败')
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

// 获取 chapter 容器样式（确保始终包含所有 section）
const getChapterContainerStyle = () => {
  const _ = containerStyleKey.value
  
  //  修复：自由模式下，Chapter 使用弹性容器（与行列模式一致），不从 Pinia 加载位置
  // 只有 Section 和 Node 在自由模式下使用绝对定位
  
  // 默认最小高度
  let minHeight = props.chapterHeight || 400
  
  // 核心修复：实时计算所有 section 的实际高度，让 chapter 的 minHeight 跟随内部元素变化
  if (props.chapter.sections && props.chapter.sections.length > 0) {
    let maxContentBottom = 0
    
    // 获取 chapter 容器元素（用于计算相对位置）
    const chapterEl = chapterRef.value
    
    props.chapter.sections.forEach((section, index) => {
      let sectionBottom = 0
      
      // 优先使用 DOM 实时计算（最准确）
      const sectionElement = document.querySelector(`[data-section-id="${section.id}"]`)
      if (sectionElement) {
        if (chapterLayout.value === 'free' && section.y != null) {
          // Free 模式：使用数据模型 + DOM 验证
          const h = sectionElement.offsetHeight || section.height || 200
          sectionBottom = section.y + h
        } else {
          // Row/Column 模式：使用 DOM 实际高度
          if (chapterLayout.value === 'row') {
            // Row 模式：累加所有前面的 section 高度 + 当前 section 高度
            let accumulatedHeight = 0
            for (let i = 0; i <= index; i++) {
              const s = props.chapter.sections[i]
              const sEl = document.querySelector(`[data-section-id="${s.id}"]`)
              if (sEl) {
                const sH = sEl.offsetHeight || 200
                accumulatedHeight += sH + (i > 0 ? props.sectionSpacing : 0)
              } else {
                // 如果 DOM 不存在，使用估算值
                accumulatedHeight += (s.height || props.sectionHeight || 200) + (i > 0 ? props.sectionSpacing : 0)
              }
            }
            sectionBottom = accumulatedHeight
          } else {
            // Column 模式：取最高的 section（所有 section 在同一行）
            const h = sectionElement.offsetHeight || section.height || props.sectionHeight || 200
            sectionBottom = h
          }
        }
      } else if (section.y != null) {
        // DOM 不存在时，使用数据模型估算
        const h = section.height || props.sectionHeight || 200
        sectionBottom = chapterLayout.value === 'free' ? (section.y + h) : h
      }
      
      if (sectionBottom > maxContentBottom) {
        maxContentBottom = sectionBottom
      }
    })
    
    // 如果算出了内容高度，更新 minHeight
    if (maxContentBottom > 0) {
      // 加上底部 padding（chapter 的 padding-bottom 通常是 16px，加上一些安全边距）
      const PADDING_BOTTOM = 80
      minHeight = Math.max(minHeight, maxContentBottom + PADDING_BOTTOM)
    }
  }
  
  //  修复：行列模式下，也使用计算出的 minHeight，确保实时跟随
  const isRowColumnMode = chapterLayout.value !== 'free'
  
  return {
    borderColor: isHexColor(chapterColor.value.border) ? chapterColor.value.border : undefined,
    backgroundColor: isHexColor(chapterColor.value.bg) ? `${chapterColor.value.bg}30` : undefined,
    width: '100%',
    minWidth: props.chapterWidth ? `${props.chapterWidth}px` : '400px',
    maxWidth: '100%',
    
    // 核心修复：所有模式都使用计算出的 minHeight，实时跟随内部元素变化
    minHeight: `${minHeight}px`,
    height: 'auto',
    // 核心修复：自由模式下章节永远是纵向的（flex-col），仅高度可被调节
    display: chapterLayout.value === 'free' ? 'flex' : undefined,
    flexDirection: chapterLayout.value === 'free' ? 'column' : undefined,
    
    //  确保 Flex 布局下，如果 Chapter 是 Flex Item，它不会被拉伸填充空白
    alignSelf: isRowColumnMode ? 'flex-start' : undefined,
    
    position: 'relative',
    overflow: 'visible',
    transition: 'min-height 0.2s ease-out'
  }
}

// 获取 section 容器样式（确保高度足够容纳所有节点）
const getSectionContainerStyle = (section) => {
  // 使用 containerStyleKey 来触发重新计算
  const _ = containerStyleKey.value
  
  //  修复：行列模式下，容器完全自适应高度
  const isRowColumnMode = chapterLayout.value !== 'free' && nodeLayout.value !== 'free'
  
  const style = {
    minHeight: '80px',
    position: 'relative', //  核心修复：无论何种布局，始终声明为定位参考点
    width: '100%',         //  确保宽度撑开
    overflow: 'visible',    //  确保节点拖出边界不被遮挡
    height: 'auto',         //  关键：行列模式下自适应高度
    maxHeight: isRowColumnMode ? 'none' : undefined //  行列模式不限制最大高度
  }
  
  // 根据节点布局方式设置容器样式
  if (nodeLayout.value === 'row') {
    // 横向排列
    style.display = 'flex'
    style.flexDirection = 'row'
    style.gap = `${props.horizontalSpacing}px`
    style.flexWrap = 'nowrap'
    style.justifyContent = props.globalNodeAlignment || 'flex-start'
  } else if (nodeLayout.value === 'column') {
    // 纵向排列
    style.display = 'flex'
    style.flexDirection = 'column'
    style.gap = `${props.verticalSpacing}px`
    // 纵向排列时，使用 alignItems 控制对齐
    style.alignItems = props.globalNodeAlignment === 'flex-start' ? 'flex-start' : 
                       props.globalNodeAlignment === 'flex-end' ? 'flex-end' : 
                       props.globalNodeAlignment === 'center' ? 'center' : 'flex-start'
  } else if (nodeLayout.value === 'wrap') {
    // 自动换行
    style.display = 'flex'
    style.flexDirection = 'row'
    style.flexWrap = 'wrap'
    style.gap = `${props.verticalSpacing}px ${props.horizontalSpacing}px`
    style.justifyContent = props.globalNodeAlignment || 'flex-start'
  } else {
    // 自由模式（free）
    style.minHeight = '200px'
    // position: 'relative' 已在上面统一设置，不需要重复
  }
  
  // 计算所有节点的最大 y 坐标，确保容器高度足够（支持自动换行，高度不限制）
  if (section.nodes && section.nodes.length > 0 && nodeLayout.value === 'free') {
    const nodeMaxWidth = props.nodeWidth // 使用全局设置的节点宽度
    const nodeHeight = props.nodeHeight // 使用全局设置的节点高度
    const horizontalSpacing = props.horizontalSpacing // 使用全局设置的水平间距
    const verticalSpacing = props.verticalSpacing // 使用全局设置的垂直间距
    
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
    style.minHeight = `${Math.max(maxY + 40, 80)}px` // 至少 80px，加上足够的边距（40px）
  }
  
  // position, width, overflow 已在上面统一设置，不需要重复判断
  
  return style
}

//  新增：获取 Section 样式
const getSectionStyle = (section, index) => {
  // 1. 自由模式 (Free Mode)
  if (chapterLayout.value === 'free') {
    // 优先从 Pinia 缓存获取（用于拖拽时的流畅度），其次是 props 数据
    const cachedLayout = projectStore.getRowColumnLayout('section', section.id)
    
    // 确定坐标：如果缓存有就用缓存，没有就用数据中的 x/y，如果都没有默认为 0
    // 核心修复：直接使用数值，不要在此处进行 padding 计算，保持坐标系纯粹
    const x = cachedLayout?.x ?? section.x ?? 0
    const y = cachedLayout?.y ?? section.y ?? 0
    const w = cachedLayout?.width ?? section.width ?? (props.sectionWidth || 300)
    const h = cachedLayout?.height ?? section.height ?? (props.sectionHeight || 200)

    return {
      position: 'absolute',
      left: `${x}px`,
      top: `${y}px`,
      width: `${w}px`,
      height: `${h}px`,
      zIndex: draggingSectionId.value === section.id ? 100 : 1,
      borderColor: section.borderColor || undefined,
      backgroundColor: section.backgroundColor || undefined,
      borderStyle: section.borderColor ? 'solid' : undefined,
      // 加上这一行，防止 CSS transition 干扰拖拽时的实时性
      transition: isDraggingSection.value && draggingSectionId.value === section.id ? 'none' : 'box-shadow 0.2s, transform 0.1s' 
    }
  }
  //  核心修改：行列模式下，section 完全根据内容（Nodes）撑开
  const hasNodes = section.nodes && section.nodes.length > 0
  // 统一列模式的 minHeight，避免每个 section 高度不一致导致的视觉割裂
  const uniformColumnMinHeight = (() => {
    if (chapterLayout.value !== 'column') return null
    // 优先使用外部传入的 sectionHeight
    if (props.sectionHeight) return props.sectionHeight
    // 否则使用所有 section 中的最大高度作为统一 minHeight，默认 200
    const heights = props.chapter.sections.map(s => s.height).filter(Boolean)
    const maxHeight = heights.length ? Math.max(...heights) : 200
    return maxHeight
  })()
  
  return {
    width: chapterLayout.value === 'row' ? '100%' : (props.sectionWidth ? `${props.sectionWidth}px` : undefined),
    minWidth: chapterLayout.value === 'row' ? undefined : (chapterLayout.value === 'column' ? undefined : (props.sectionWidth ? `${props.sectionWidth}px` : undefined)),
    
    //  关键点 1: 如果有节点，minHeight 为 auto (由内容决定)
    //  关键点 2: 如果没节点，给一个最小高度 (如 100px) 放置"添加按钮"，防止塌陷无法点击
    //  列模式下强制使用统一的 minHeight
    minHeight: chapterLayout.value === 'column'
      ? `${uniformColumnMinHeight || 200}px`
      : (hasNodes ? 'auto' : '100px'),
    
    //  关键点 3: 强制忽略数据库中保存的 height (那是在自由模式下拉伸产生的)
    height: 'auto', 
    
    marginTop: (chapterLayout.value === 'row' && index > 0 && draggingSectionId.value !== section.id) ? `${props.sectionSpacing}px` : undefined,
    position: 'relative',
    zIndex: draggingSectionId.value === section.id ? 100 : undefined,
    left: undefined,
    top: undefined,
    
    //  关键点 4: Flex 布局顶格对齐，不拉伸
    //  这解决了 "flex 顶格" 的需求
    alignSelf: 'flex-start',
    borderColor: section.borderColor || undefined,
    backgroundColor: section.backgroundColor || undefined,
    borderStyle: section.borderColor ? 'solid' : undefined
  }
}

// 获取节点样式（绝对定位）
const getNodeStyle = (node, sectionId) => {
  // 1. 判断是否处于自由模式 (全局或当前)
  const isFreeMode = nodeLayout.value === 'free' || chapterLayout.value === 'free'
  
  // 2. 如果不是自由模式，直接返回空，交给 Flexbox 排列
  if (!isFreeMode) {
    return {}
  }

  //  修改：自由模式下，优先从 Pinia 加载位置数据
  const cachedLayout = projectStore.getRowColumnLayout('node', node.id)
  if (cachedLayout) {
    return {
      left: `${cachedLayout.x}px`,
      top: `${cachedLayout.y}px`,
      position: 'absolute',
      width: cachedLayout.width ? `${cachedLayout.width}px` : `${props.nodeWidth}px`,
      height: cachedLayout.height ? `${cachedLayout.height}px` : undefined,
      zIndex: 15
    }
  }
  
  // 如果没有 Pinia 缓存，使用后端数据
  if (node.x != null && node.y != null) {
    return {
      left: `${node.x}px`,
      top: `${node.y}px`,
      position: 'absolute',
      width: node.width ? `${node.width}px` : `${props.nodeWidth}px`, // 优先使用保存的宽度
      height: node.height ? `${node.height}px` : undefined, // 如果有保存的高度也使用
      zIndex: 15
    }
  }
  
  //  4. 核心修复：自由模式但没有坐标时的"智能兜底"
  // 绝不能返回空对象，否则所有节点会堆叠在 (0,0)
  // 我们根据索引计算一个默认的网格位置
  
  const section = props.chapter.sections.find(s => s.id === sectionId)
  if (!section) return {}

  // 获取当前 Section 的节点列表并找到当前节点的索引
  const nodes = section.nodes || []
  const index = nodes.findIndex(n => n.id === node.id)
  if (index === -1) return {}

  // 计算网格参数
  const nodeW = props.nodeWidth || 300
  const nodeH = props.nodeHeight || 70
  const gapX = props.horizontalSpacing || 50
  const gapY = props.verticalSpacing || 20
  
  // 获取容器宽度 (如果取不到，默认 1000)
  const container = sectionContainerRefs.value[sectionId]
  const containerWidth = container ? container.clientWidth : 1000
  
  // 计算每行能放几个
  const itemsPerRow = Math.max(1, Math.floor(containerWidth / (nodeW + gapX)))
  
  // 计算行列号
  const row = Math.floor(index / itemsPerRow)
  const col = index % itemsPerRow
  
  // 返回计算出的默认位置
  return {
    left: `${col * (nodeW + gapX)}px`,
    top: `${row * (nodeH + gapY)}px`,
    position: 'absolute',
    width: `${nodeW}px`,
    zIndex: 1
  }
}

// 拖曳性能优化：缓存容器和节点尺寸
const dragCache = {
  containerRect: null,
  nodeWidth: null,
  nodeHeight: null,
  containerWidth: null, // 缓存父容器宽度
  containerHeight: null, // 缓存父容器高度
  parentRect: null, // 缓存父容器 Rect
  parentElement: null, // 暂存父容器引用
  staticMaxBottom: 0, // 其他所有静态元素的最低点
  staticMaxRight: 0 // 其他所有静态元素的最右点 (如果需要横向扩展)
}

// ❄️ 1. 计算元素相对于定位父级(Padding Box)的精确坐标
const calculateRelativePosition = (el, container) => {
  const elRect = el.getBoundingClientRect()
  const containerRect = container.getBoundingClientRect()
  
  // 获取父容器的边框和内边距 (因为 absolute 是相对于 padding box 定位的)
  const style = window.getComputedStyle(container)
  const borderLeft = parseFloat(style.borderLeftWidth) || 0
  const borderTop = parseFloat(style.borderTopWidth) || 0
  const paddingLeft = parseFloat(style.paddingLeft) || 0
  const paddingTop = parseFloat(style.paddingTop) || 0
  
  // 核心公式：元素屏幕坐标 - 容器屏幕坐标 - 容器左侧厚度
  const x = elRect.left - containerRect.left - borderLeft - paddingLeft
  const y = elRect.top - containerRect.top - borderTop - paddingTop
  
  return { x, y, width: elRect.width, height: elRect.height }
}

// ❄️ 2. 全员冻结：把当前屏幕上所有 Section 和 Node 的视觉位置写入数据模型
// 核心修复：使用 sectionsContainerRef 作为参考系，而不是 chapterRef
const freezeEverything = () => {
  // 改为获取中间容器
  const containerEl = sectionsContainerRef.value
  if (!containerEl) return

  // A. 冻结所有 Section (相对于中间容器)
  props.chapter.sections.forEach(section => {
    const el = document.querySelector(`[data-section-id="${section.id}"]`)
    if (el) {
      // 使用之前定义的 calculateRelativePosition 逻辑 (针对 containerEl)
      const pos = calculateRelativePosition(el, containerEl)
      // 强制写入精确坐标和尺寸
      section.x = pos.x
      section.y = pos.y
      section.width = pos.width
      section.height = pos.height
    }
    
    // B. 冻结该 Section 下的所有 Node (相对于 Section)
    const sectionContainer = sectionContainerRefs.value[section.id]
    if (sectionContainer && section.nodes) {
      section.nodes.forEach(node => {
        // 获取 Node 的 DOM 元素
        let nodeEl = nodeRefs.value[`${section.id}-${node.id}`]
        // 兼容 Vue 组件 ref
        if (nodeEl && nodeEl.$el) nodeEl = nodeEl.$el 
        
        if (nodeEl) {
          const nodePos = calculateRelativePosition(nodeEl, sectionContainer)
          node.x = nodePos.x
          node.y = nodePos.y
          //  关键：必须锁死宽度，防止从 Flex 变 Absolute 时宽度塌陷
          node.width = nodePos.width 
          node.height = nodePos.height 
        }
      })
    }
  })
}

// 鼠标拖拽处理（节点拖拽）
const handleMouseDown = async (event, nodeId, index, sectionId) => {
  // 若点击的是交互控件，直接跳过拖拽逻辑
  if (
    event.target.closest('button') ||
    event.target.closest('input') ||
    event.target.closest('textarea') ||
    event.target.closest('a') ||
    event.target.closest('.no-drag')
  ) {
    return
  }

  event.stopPropagation()
  // ... (基础校验保持不变) ...
  if (event.ctrlKey || event.metaKey) return
  if (chapterLayout.value !== 'free') return // 仅自由模式

  event.preventDefault()
  
  const section = props.chapter.sections.find(s => s.id === sectionId)
  const node = section?.nodes.find(n => n.id === nodeId)
  if (!node) return

  // 1. 初始化
  isDraggingNode.value = true
  draggingNodeId.value = nodeId
  nodeDragStartSectionId.value = sectionId

  // 2. 记录初始数据 (Delta 核心)
  // Node 的 x/y 是相对于 Section 的
  // 如果 node.x 为空，尝试读取 DOM offsetLeft
  const el = event.currentTarget
  // 兼容 Vue 组件 ref
  const domNode = (el && el.$el) ? el.$el : el
  
  // 获取初始位置
  const initialLeft = node.x ?? domNode.offsetLeft ?? 0
  const initialTop = node.y ?? domNode.offsetTop ?? 0
  
  nodeDragStartData.value = {
    mouseX: event.clientX,
    mouseY: event.clientY,
    initialLeft: initialLeft,
    initialTop: initialTop
  }

  // 核心修复：保存初始样式到 dragStartNodeStyle，防止 Vue 重新渲染时闪回
  dragStartNodeStyle.value = {
    left: `${initialLeft}px`,
    top: `${initialTop}px`,
    position: 'absolute',
    width: domNode.offsetWidth ? `${domNode.offsetWidth}px` : `${props.nodeWidth}px`,
    height: domNode.offsetHeight ? `${domNode.offsetHeight}px` : undefined
  }

  // 核心修复：在拖拽开始时，直接禁用 DOM 元素的 transition
  if (domNode) {
    domNode.style.transition = 'none'
    domNode.style.willChange = 'transform' // 提示浏览器优化性能
    // 确保初始位置被设置（防止闪回）
    domNode.style.left = `${initialLeft}px`
    domNode.style.top = `${initialTop}px`
  }

  document.addEventListener('mousemove', handleNodeMouseMove, { passive: false })
  document.addEventListener('mouseup', handleNodeMouseUp)
}

// 修改 Node 的 handleNodeMouseMove
const handleNodeMouseMove = (event) => {
  if (!isDraggingNode.value || !draggingNodeId.value) return
  event.preventDefault()

  // 1. 计算差值 (Delta 算法)
  const deltaX = event.clientX - nodeDragStartData.value.mouseX
  const deltaY = event.clientY - nodeDragStartData.value.mouseY

  // 2. 计算新位置
  let newLeft = nodeDragStartData.value.initialLeft + deltaX
  let newTop = nodeDragStartData.value.initialTop + deltaY
  
  // 3. 边界限制 (防止拖出 Section 左上角)
  newLeft = Math.max(0, newLeft)
  newTop = Math.max(0, newTop)

  // 4. 获取相关对象
  const section = props.chapter.sections.find(s => s.id === nodeDragStartSectionId.value)
  const node = section?.nodes.find(n => n.id === draggingNodeId.value)
  
  // 获取 Node 和 Section 的 DOM 元素
  const nodeElement = nodeRefs.value[`${nodeDragStartSectionId.value}-${draggingNodeId.value}`]
  // 兼容 Vue 组件 ref
  const domNode = (nodeElement && nodeElement.$el) ? nodeElement.$el : nodeElement
  const sectionElement = document.querySelector(`[data-section-id="${nodeDragStartSectionId.value}"]`)

  if (node && domNode && sectionElement) {
    // --- 更新节点位置 ---
    // 核心修复：拖拽过程中只更新 DOM，不更新 Vue 响应式数据
    // 这样可以避免 Vue 重新渲染导致的延迟和样式覆盖
    // 直接操作 DOM 以获得最佳性能 (避免 Vue 渲染循环)
    domNode.style.left = `${newLeft}px`
    domNode.style.top = `${newTop}px`
    
    // 确保 transition 被禁用（防止被其他样式覆盖）
    domNode.style.transition = 'none'
    domNode.style.willChange = 'transform' // 提示浏览器优化性能
    
    // 核心修复：同时更新 dragStartNodeStyle，防止 Vue 重新渲染时闪回
    dragStartNodeStyle.value = {
      ...dragStartNodeStyle.value,
      left: `${newLeft}px`,
      top: `${newTop}px`
    }
    
    // 注意：这里不更新 node.x 和 node.y，避免触发 Vue 重新渲染
    // 最终位置会在 handleNodeMouseUp 中更新
    
    // --- 核心修复：父容器实时自动扩大 (Auto-Expand) ---
    const nodeWidth = domNode.offsetWidth || props.nodeWidth
    const nodeHeight = domNode.offsetHeight || props.nodeHeight
    const PADDING_RIGHT = 60 // 预留右侧空间
    const PADDING_BOTTOM = 60 // 预留底部空间

    // 计算节点右边界和下边界
    const nodeRightEdge = newLeft + nodeWidth + PADDING_RIGHT
    const nodeBottomEdge = newTop + nodeHeight + PADDING_BOTTOM
    
    // 获取当前 Section 的尺寸
    let currentSectionW = section.width || sectionElement.offsetWidth
    let currentSectionH = section.height || sectionElement.offsetHeight

    let needUpdateSection = false

    // 检查宽度是否需要扩大
    if (nodeRightEdge > currentSectionW) {
      currentSectionW = nodeRightEdge
      section.width = currentSectionW
      sectionElement.style.width = `${currentSectionW}px`
      needUpdateSection = true
    }

    // 检查高度是否需要扩大
    if (nodeBottomEdge > currentSectionH) {
      currentSectionH = nodeBottomEdge
      section.height = currentSectionH
      sectionElement.style.height = `${currentSectionH}px`
      // 如果是在 free 模式下，Section 高度变了，可能需要触发 Chapter 的高度重算（如果是自动高度的话）
      needUpdateSection = true
    }

    // 更新 Pinia 缓存 (防止重新渲染时闪烁)
    // 注意：这里更新缓存是为了防止重新渲染时闪烁，但不会触发 Vue 响应式更新
    // 因为 Pinia 的 reactive 对象更新不会触发组件的重新渲染（除非组件订阅了它）
    projectStore.saveRowColumnLayout('node', draggingNodeId.value, {
      x: newLeft,
      y: newTop,
      width: nodeWidth,
      height: nodeHeight
    })
    
    // 如果 Section 尺寸变了，也更新 Section 的缓存
    if (needUpdateSection) {
       projectStore.saveRowColumnLayout('section', section.id, {
          x: section.x, // 保持 x 不变
          y: section.y, // 保持 y 不变
          width: currentSectionW,
          height: currentSectionH
       })
       
       // 触发容器高度重算 key，确保背景等样式跟上
       // (使用 throttle 防止过于频繁触发)
       if (!window._resizeThrottle) {
         window._resizeThrottle = setTimeout(() => {
           containerStyleKey.value++ // 触发 section 容器重新计算
           // 核心修复：同时触发 chapter 高度重新计算
           nextTick(() => {
             adjustParentContainers()
           })
           window._resizeThrottle = null
         }, 100)
       }
    }
  }
}

// 修改 Node 的 handleNodeMouseUp
const handleNodeMouseUp = () => {
  if (!isDraggingNode.value) return
  
  const nodeId = draggingNodeId.value
  const sectionId = nodeDragStartSectionId.value

  document.removeEventListener('mousemove', handleNodeMouseMove)
  document.removeEventListener('mouseup', handleNodeMouseUp)
  
  isDraggingNode.value = false
  draggingNodeId.value = null
  nodeDragStartSectionId.value = null

  const section = props.chapter.sections.find(s => s.id === sectionId)
  const node = section?.nodes.find(n => n.id === nodeId)
  
  // 获取 DOM 元素以恢复 transition
  const nodeElement = nodeRefs.value[`${sectionId}-${nodeId}`]
  const domNode = (nodeElement && nodeElement.$el) ? nodeElement.$el : nodeElement
  
  if (node && section) {
    // 核心修复：从 DOM 读取最终位置，更新到响应式数据
    if (domNode) {
      const finalLeft = parseFloat(domNode.style.left) || domNode.offsetLeft || 0
      const finalTop = parseFloat(domNode.style.top) || domNode.offsetTop || 0
      
      // 更新响应式数据
      node.x = finalLeft
      node.y = finalTop
      
      // 恢复 transition（让 Vue 的样式绑定重新生效）
      domNode.style.transition = ''
      domNode.style.willChange = ''
    }
    
    // 清除 dragStartNodeStyle，让 Vue 的样式绑定重新生效
    dragStartNodeStyle.value = {}
    
    // 1. 发送节点位置更新
    emit('update-node-position', {
      nodeId, 
      sectionId, 
      chapterId: props.chapter.id, 
      position: { x: node.x, y: node.y, width: node.width, height: node.height }
    })
    
    // 2. 核心修复：发送 Section 尺寸更新
    // 因为拖拽过程中 Section 可能变大了，我们需要保存这个新尺寸到后端
    const sectionElement = document.querySelector(`[data-section-id="${sectionId}"]`)
    if (sectionElement) {
       const finalW = sectionElement.offsetWidth
       const finalH = sectionElement.offsetHeight
       
       // 只有当尺寸真的变化时才发送请求，或者总是发送以防万一
       // 注意：originalSectionState 是用于 Section 拖拽的，这里我们需要检查节点拖拽前的 Section 尺寸
       // 为了简化，我们总是发送更新，让后端处理去重
       emit('section-size-updated', {
          sectionId,
          chapterId: props.chapter.id,
          width: finalW,
          height: finalH, 
          x: section.x,
          y: section.y
       })
       
       // 核心修复：触发 chapter 高度重新计算
       nextTick(() => {
         containerStyleKey.value++
         adjustParentContainers()
       })
    }
  }
}

// Section 自由拖拽定位处理
const handleSectionMouseDown = (event, sectionId, index) => {
  // 基础校验：阻止冒泡、检查是否在调整大小、检查是否是自由模式
  if (resizingSectionId.value || (isDraggingNode.value && draggingNodeId.value) || event.ctrlKey || event.metaKey) return
  if (event.target.closest('button') || event.target.closest('[data-node-id]') || event.target.closest('.cursor-ew-resize')) return
  
  // 只在自由模式启用
  if (chapterLayout.value !== 'free') return

  event.preventDefault()
  event.stopPropagation()

  const section = props.chapter.sections.find(s => s.id === sectionId)
  if (!section) return

  // 1. 初始化拖拽状态
  draggingSectionId.value = sectionId
  isDraggingSection.value = true

  // 2. 记录初始数据 (Delta 算法的核心)
  // 我们只关心：鼠标在哪？元素原来在哪？
  // 不再关心父容器在哪，margin是多少，padding是多少。
  dragStartData.value = {
    mouseX: event.clientX,
    mouseY: event.clientY,
    // 如果数据中没有 x/y，尝试从 DOM 读取 offsetLeft (作为兜底)
    initialLeft: section.x ?? event.currentTarget.offsetLeft,
    initialTop: section.y ?? event.currentTarget.offsetTop
  }

  // 3. 添加监听
  document.addEventListener('mousemove', handleSectionMouseMove, { passive: false }) // passive: false 允许阻止默认行为
  document.addEventListener('mouseup', handleSectionMouseUp)
}

// 重写 handleSectionMouseMove
const handleSectionMouseMove = (event) => {
  if (!isDraggingSection.value || !draggingSectionId.value) return
  
  event.preventDefault() // 防止某些浏览器选中文本

  // 1. 计算鼠标位移差 (Delta)
  const deltaX = event.clientX - dragStartData.value.mouseX
  const deltaY = event.clientY - dragStartData.value.mouseY

  // 2. 计算新坐标 = 初始坐标 + 差值
  let newLeft = dragStartData.value.initialLeft + deltaX
  let newTop = dragStartData.value.initialTop + deltaY

  // 3. 边界限制 (可选：限制不能拖出左上角)
  newLeft = Math.max(0, newLeft)
  newTop = Math.max(0, newTop)

  // 4. 更新 Pinia 缓存 (用于平滑渲染)
  const sectionElement = document.querySelector(`[data-section-id="${draggingSectionId.value}"]`)
  const currentWidth = sectionElement ? sectionElement.offsetWidth : 300
  const currentHeight = sectionElement ? sectionElement.offsetHeight : 200

  projectStore.saveRowColumnLayout('section', draggingSectionId.value, {
    x: newLeft,
    y: newTop,
    width: currentWidth,
    height: currentHeight
  })

  // 5. 实时更新响应式数据 (让 Vue 重新渲染 Style)
  const section = props.chapter.sections.find(s => s.id === draggingSectionId.value)
  if (section) {
    section.x = newLeft
    section.y = newTop
  }
}

// 重写 handleSectionMouseUp
const handleSectionMouseUp = () => {
  if (!isDraggingSection.value) return

  const sectionId = draggingSectionId.value
  const section = props.chapter.sections.find(s => s.id === sectionId)

  // 移除监听
  document.removeEventListener('mousemove', handleSectionMouseMove)
  document.removeEventListener('mouseup', handleSectionMouseUp)
  
  isDraggingSection.value = false
  draggingSectionId.value = null

  // 保存最终位置到后端
  if (section) {
    const sectionElement = document.querySelector(`[data-section-id="${sectionId}"]`)
    emit('section-position-updated', {
      sectionId: section.id,
      chapterId: props.chapter.id,
      x: section.x,
      y: section.y,
      width: sectionElement ? sectionElement.offsetWidth : section.width,
      height: sectionElement ? sectionElement.offsetHeight : section.height
    })
  }
}

// =============== Section Resize (PPT-like) ===============
const resizingSectionId = ref(null)
const resizeDirection = ref(null) // 'n','s','w','e','nw','ne','sw','se'
const resizeStart = ref({ mouseX: 0, mouseY: 0, startW: 0, startH: 0, startX: 0, startY: 0 })
const MIN_SECTION_W = 160
const MIN_SECTION_H = 120

const startSectionResize = (event, section, direction) => {
  // 阻止事件冒泡，确保不会触发拖拽
  event.stopPropagation()
  event.preventDefault()
  
  const el = event.currentTarget.parentElement
  const parent = el.parentElement
  const rect = el.getBoundingClientRect()
  const parentRect = parent.getBoundingClientRect()
  
  resizingSectionId.value = section.id
  resizeDirection.value = direction
  resizeStart.value = {
    mouseX: event.clientX,
    mouseY: event.clientY,
    startW: section.width || rect.width,
    startH: section.height || rect.height,
    startX: (section.x != null ? section.x : rect.left - parentRect.left),
    startY: (section.y != null ? section.y : rect.top - parentRect.top)
  }
  
  document.addEventListener('mousemove', handleSectionResizeMove, { passive: true })
  document.addEventListener('mouseup', handleSectionResizeUp)
}

const handleSectionResizeMove = (event) => {
  if (!resizingSectionId.value) return
  const section = props.chapter.sections.find(s => s.id === resizingSectionId.value)
  if (!section) return
  
  const sectionElement = document.querySelector(`[data-section-id="${resizingSectionId.value}"]`)
  if (!sectionElement) return
  
  const parentElement = sectionElement.parentElement
  if (!parentElement) return
  const parentRect = parentElement.getBoundingClientRect()
  
  const dx = event.clientX - resizeStart.value.mouseX
  const dy = event.clientY - resizeStart.value.mouseY
  
  let newW = resizeStart.value.startW
  let newH = resizeStart.value.startH
  let newX = resizeStart.value.startX
  let newY = resizeStart.value.startY
  
  const dir = resizeDirection.value
  if (dir.includes('e')) newW = resizeStart.value.startW + dx
  if (dir.includes('s')) newH = resizeStart.value.startH + dy
  if (dir.includes('w')) {
    newW = resizeStart.value.startW - dx
    newX = resizeStart.value.startX + dx
  }
  if (dir.includes('n')) {
    newH = resizeStart.value.startH - dy
    newY = resizeStart.value.startY + dy
  }
  
  // 限制最小尺寸
  newW = Math.max(MIN_SECTION_W, newW)
  newH = Math.max(MIN_SECTION_H, newH)
  
  // 限制在父容器内
  if (chapterLayout.value === 'free') {
    if (newX < 0) {
      newW += newX
      newX = 0
      newW = Math.max(MIN_SECTION_W, newW)
    }
    if (newY < 0) {
      newH += newY
      newY = 0
      newH = Math.max(MIN_SECTION_H, newH)
    }
    if (newX + newW > parentRect.width) {
      newW = parentRect.width - newX
    }
    if (newY + newH > parentRect.height) {
      newH = parentRect.height - newY
    }
  } else {
    // 在 row/column 布局中，限制最大宽度为父容器的宽度
    if (newW > parentRect.width) {
      newW = parentRect.width
    }
  }
  
  // 应用尺寸（所有布局形态均可调整）
  section.width = newW
  section.height = newH
  
  // 实时更新元素样式
  sectionElement.style.width = `${newW}px`
  sectionElement.style.height = `${newH}px`
  
  // 在自由布局时，如果从左/上拉伸则同步移动 x/y
  if (chapterLayout.value === 'free') {
    section.x = newX
    section.y = newY
    sectionElement.style.left = `${newX}px`
    sectionElement.style.top = `${newY}px`
  }
}

const handleSectionResizeUp = () => {
  // 触发 chapter 高度重新计算
  nextTick(() => {
    containerStyleKey.value++
    // 核心修复：触发 chapter 高度重新计算
    adjustParentContainers()
  })
  if (!resizingSectionId.value) return
  const section = props.chapter.sections.find(s => s.id === resizingSectionId.value)
  if (section) {
    // 触发更新事件，保存尺寸和位置到后端
    emit('section-size-updated', {
      sectionId: section.id,
      chapterId: props.chapter.id,
      width: section.width,
      height: section.height,
      x: section.x,
      y: section.y
    })
    
    // 同时触发位置更新事件（如果是在自由布局）
    if (chapterLayout.value === 'free' && section.x != null && section.y != null) {
      emit('section-position-updated', {
        sectionId: section.id,
        chapterId: props.chapter.id,
        x: section.x,
        y: section.y,
        width: section.width,
        height: section.height
      })
    }
  }
  resizingSectionId.value = null
  resizeDirection.value = null
  document.removeEventListener('mousemove', handleSectionResizeMove)
  document.removeEventListener('mouseup', handleSectionResizeUp)
}
// Chapter 拖拽处理（仅在自由模式下启用）
const handleChapterMouseDown = (event, chapterId) => {
  // 如果按住 Ctrl 键，不触发拖拽
  if (event.ctrlKey || event.metaKey) {
    return
  }
  
  // 如果点击的是按钮或标题，不触发拖拽
  if (event.target.closest('button') || event.target.closest('h2')) {
    return
  }
  
  // 核心修复：自由模式下章节不允许被拖动，永远是纵向的，仅高度可被调节
  // 因此无论什么模式，都不允许章节拖拽
  emit('chapter-selected', chapterId)
  return
  
  // 以下代码已禁用（原章节拖拽功能）
  /*
  // 只在自由模式下允许拖拽
  if (chapterLayout.value !== 'free') {
    emit('chapter-selected', chapterId)
    return
  }
  
  // 开始拖拽
  draggingChapterId.value = chapterId
  const chapterElement = chapterRef.value
  if (!chapterElement) return
  
  const rect = chapterElement.getBoundingClientRect()
  const startX = event.clientX
  const startY = event.clientY
  const startLeft = rect.left
  const startTop = rect.top
  
  // 保存原始状态
  originalChapterState.value = {
    x: props.chapter.x ?? startLeft,
    y: props.chapter.y ?? startTop,
    width: props.chapter.width ?? rect.width,
    height: props.chapter.height ?? rect.height
  }
  
  // 设置初始样式
  chapterElement.style.position = 'absolute'
  chapterElement.style.left = `${startLeft}px`
  chapterElement.style.top = `${startTop}px`
  chapterElement.style.zIndex = '100'
  chapterElement.style.transition = 'none'
  
  const handleChapterMouseMove = (e) => {
    if (draggingChapterId.value !== chapterId) return
    
    const dx = e.clientX - startX
    const dy = e.clientY - startY
    
    const newLeft = startLeft + dx
    const newTop = startTop + dy
    
    if (chapterElement) {
      chapterElement.style.left = `${newLeft}px`
      chapterElement.style.top = `${newTop}px`
    }
    
    emit('chapter-dragging', { chapterId, x: newLeft, y: newTop })
  }
  
  const handleChapterMouseUp = async () => {
    if (draggingChapterId.value !== chapterId) return
    
    const chapterElement = chapterRef.value
    if (chapterElement) {
      const finalLeft = parseFloat(chapterElement.style.left)
      const finalTop = parseFloat(chapterElement.style.top)
      const finalWidth = chapterElement.offsetWidth
      const finalHeight = chapterElement.offsetHeight
      
      // 更新本地数据
      if (props.chapter) {
        props.chapter.x = finalLeft
        props.chapter.y = finalTop
        props.chapter.width = finalWidth
        props.chapter.height = finalHeight
      }
      
      // 发送位置更新事件
      emit('chapter-position-updated', {
        chapterId: chapterId,
        x: finalLeft,
        y: finalTop,
        width: finalWidth,
        height: finalHeight
      })
      
      // 恢复样式
      chapterElement.style.zIndex = '1'
      chapterElement.style.transition = ''
    }
    
    draggingChapterId.value = null
    document.removeEventListener('mousemove', handleChapterMouseMove)
    document.removeEventListener('mouseup', handleChapterMouseUp)
  }
  
  document.addEventListener('mousemove', handleChapterMouseMove)
  document.addEventListener('mouseup', handleChapterMouseUp)
  
  emit('chapter-selected', chapterId)
  */
}

// 旧的拖拽处理函数（保留用于兼容，但不再使用）
const handleDragStart = (event, nodeId, index, sectionId) => {
  draggingNodeId.value = nodeId
  nodeDragStartIndex.value = index
  nodeDragStartSectionId.value = sectionId
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', nodeId)
  // 添加拖拽样式
  if (event.target) {
    event.target.style.cursor = 'grabbing'
  }
}

const handleDragEnter = (event, index, sectionId) => {
  if (draggingNodeId.value && nodeDragStartSectionId.value === sectionId) {
    dragOverIndex.value = index
  }
}

const handleDragOver = (event, index, sectionId) => {
  if (draggingNodeId.value && nodeDragStartSectionId.value === sectionId) {
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
  
  if (!draggingNodeId.value || nodeDragStartSectionId.value !== sectionId) {
    return
  }
  
  const section = props.chapter.sections.find(s => s.id === sectionId)
  if (!section) return
  
  const sourceIndex = nodeDragStartIndex.value
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
  nodeDragStartIndex.value = null
  nodeDragStartSectionId.value = null
}

// 核心优化：注册节点引用
// 重写为纯 Ref 收集函数，去掉 useElementBounding 和 ResizeObserver，避免性能问题
const registerNodeRef = (nodeId, el, sectionId) => {
  if (!sectionId) return
  
  const key = `${sectionId}-${nodeId}`
  
  if (!el) {
    // 元素卸载时只清理引用
    delete nodeRefs.value[key]
    return
  }
  
  // 只保存引用，不做任何监听，极低开销
  nodeRefs.value[key] = el
  
  // 如果你需要初始化位置（用于连线），仅在第一次挂载时计算一次
  // 使用 setTimeout 宏任务，让出主线程，避免阻塞渲染
  setTimeout(() => {
    updateNodePosition(nodeId, sectionId)
  }, 0)
}

// 使用防抖优化节点位置更新（保留用于兼容性，但新代码应使用 registerNodeRef）
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
