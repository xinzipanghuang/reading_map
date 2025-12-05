<template>
  <div
    :class="[
      'relative p-3 rounded-2xl border-2 transition cursor-move',
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
          @click="toggleLayout"
          class="p-1.5 text-gray-400 hover:text-blue-600 transition rounded"
          :title="getLayoutButtonTitle"
        >
          <i :class="getLayoutButtonIcon" class="text-base"></i>
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
      :class="[
        chapterLayout === 'free' ? 'relative' : '',
        chapterLayout === 'row' ? '' : chapterLayout === 'free' ? '' : 'flex flex-row flex-wrap'
      ]"
      :style="{
        gap: chapterLayout === 'free' ? '0' : `${props.sectionSpacing}px`,
        marginTop: chapterLayout === 'row' ? `${props.sectionSpacing}px` : undefined,
        minHeight: chapterLayout === 'free' ? '400px' : undefined
      }"
    >
      <div
        v-for="(section, index) in chapter.sections"
        :key="section.id"
        :data-section-id="section.id"
        :class="[
          'bg-white p-2 rounded-lg border-2 shadow-sm cursor-move transition',
          chapterLayout === 'free' ? 'absolute' : '',
          (chapterLayout === 'column' && !section.width) ? 'flex-1 min-w-[300px]' : '',
'border-gray-200',
          draggingSectionId === section.id ? 'opacity-50 scale-95' : 'hover:shadow-md'
        ]"
        :style="{
          width: section.width ? `${section.width}px` : (props.sectionWidth ? `${props.sectionWidth}px` : undefined),
          minWidth: props.sectionWidth ? `${props.sectionWidth}px` : undefined,
          minHeight: section.height ? `${section.height}px` : (props.sectionHeight ? `${props.sectionHeight}px` : undefined),
          marginTop: (chapterLayout === 'row' && index > 0 && draggingSectionId !== section.id) ? `${props.sectionSpacing}px` : undefined,
          position: (chapterLayout === 'free' || (isDraggingSection && section.x != null)) ? 'absolute' : undefined,
          zIndex: draggingSectionId === section.id ? 100 : (chapterLayout === 'free' ? 1 : undefined),
          left: (chapterLayout === 'free' || (isDraggingSection && section.x != null)) && section.x != null ? `${section.x}px` : undefined,
          top: (chapterLayout === 'free' || (isDraggingSection && section.x != null)) && section.y != null ? `${section.y}px` : undefined
        }"
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
            :key="`${node.id}-${layoutKey}`"
            :ref="el => setNodeRef(node.id, el, idx, section.id)"
            :data-node-id="node.id"
            :class="[
              'absolute',
              draggingNodeId === node.id 
                ? 'opacity-50 scale-95 cursor-grabbing' 
                : 'cursor-grab'
            ]"
            :style="{
              ...getNodeStyle(node, section.id),
              zIndex: draggingNodeId === node.id ? 20 : 15
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
              :class="getLinkStatusClass(node.id)"
              :style="{ maxWidth: `${props.nodeWidth}px`, minWidth: `${Math.min(props.nodeWidth * 0.6, 180)}px` }"
              @click="(e) => { handleNodeClick(node.id, e); }"
              @dblclick="() => handleNodeDoubleClick(node.id)"
              @edit.stop="emit('edit-item', { type: 'node', id: node.id, nodeId: node.id, sectionId: section.id, chapterId: chapter.id })"
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

    <!-- Rename Chapter Modal -->
    <div
      v-if="showRenameChapterModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showRenameChapterModal = false"
    >
      <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4">重命名章节</h3>
        <input
          v-model="renameChapterName"
          @keyup.enter="renameChapter"
          class="w-full border p-2 rounded mb-4 focus:outline-none focus:border-blue-500"
          placeholder="章节名称"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="showRenameChapterModal = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition"
          >
            取消
          </button>
          <button
            @click="renameChapter"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
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
      <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4">重命名部分</h3>
        <input
          v-model="renameSectionName"
          @keyup.enter="renameSection"
          class="w-full border p-2 rounded mb-4 focus:outline-none focus:border-blue-500"
          placeholder="部分名称"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="showRenameSectionModal = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition"
          >
            取消
          </button>
          <button
            @click="renameSection"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
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
  },
  globalLayout: {
    type: String,
    default: 'row',
    validator: (value) => ['row', 'column'].includes(value)
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
  'add-section',
  'delete-chapter',
  'delete-section',
  'add-node',
  'edit-node',
  'delete-node',
  'node-click',
  'node-dblclick',
  'update-node-positions',
  'edit-item',
  'node-dragging',
  'node-drag-end',
  'section-reorder',
  'chapter-reorder',
  'section-position-updated',
  'section-dragging',
  'chapter-layout-change',
  'chapter-updated',
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

// 节点拖拽时的原始状态（用于保持尺寸和位置）
const originalNodeState = ref({
  width: null,
  height: null,
  x: null,
  y: null
})

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

// 章节布局（行/列）- 优先使用全局布局，全局布局会覆盖章节自己的布局
const chapterLayout = computed(() => {
  // 如果章节有 section 被拖拽过（有 x, y 坐标），自动切换到自由布局
  const hasPositionedSections = props.chapter.sections.some(s => s.x != null || s.y != null)
  if (hasPositionedSections) {
    return 'free'
  }
  // 全局布局优先，如果全局布局已设置，则使用全局布局
  // 只有当全局布局未设置时，才使用章节自己的布局
  return props.globalLayout || props.chapter.layout || 'row'
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
  })
}, { deep: true })

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

// 切换布局（章节内的布局切换会覆盖全局布局）
const toggleLayout = async () => {
  try {
    const { api } = await import('../api.js')
    
    // 三种模式循环切换：行排列 -> 列排列 -> 编辑模式（自由布局）-> 行排列
    // 使用实际的章节布局，而不是 computed 的 chapterLayout（它可能受全局布局影响）
    const actualLayout = props.chapter.layout || 'row'
    let newLayout = 'row'
    
    if (actualLayout === 'row') {
      newLayout = 'column'
    } else if (actualLayout === 'column') {
      newLayout = 'free'
    } else {
      // 从自由布局切换到行布局，清除所有 section 的坐标
      newLayout = 'row'
      for (const section of props.chapter.sections) {
        section.x = null
        section.y = null
      }
    }
    
    await api.updateChapter(props.projectId, props.chapter.id, { layout: newLayout })
    // 布局改变会触发 watch，自动清除节点位置并重新计算
    // 触发父组件重新加载项目数据
    emit('chapter-updated')
    const layoutNames = { row: '行排列', column: '列排列', free: '编辑模式' }
    ElMessage.success(`已切换为${layoutNames[newLayout]}，节点位置已重新计算`)
  } catch (error) {
    console.error('Failed to update chapter layout:', error)
    ElMessage.error('更新布局失败')
  }
}

// 获取布局按钮标题
const getLayoutButtonTitle = computed(() => {
  // 使用实际的章节布局，而不是 computed 的 chapterLayout
  const actualLayout = props.chapter.layout || 'row'
  if (actualLayout === 'row') {
    return '切换为列排列'
  } else if (actualLayout === 'column') {
    return '切换为编辑模式'
  } else {
    return '切换为行排列'
  }
})

// 获取布局按钮图标
const getLayoutButtonIcon = computed(() => {
  // 使用实际的章节布局，而不是 computed 的 chapterLayout
  const actualLayout = props.chapter.layout || 'row'
  if (actualLayout === 'row') {
    return 'ph ph-columns'
  } else if (actualLayout === 'column') {
    return 'ph ph-arrows-out'
  } else {
    return 'ph ph-rows'
  }
})

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
// 使用 containerStyleKey 来触发重新计算
const getChapterContainerStyle = () => {
  const _ = containerStyleKey.value
  
  // chapter 宽度自适应，但设置最小宽度
  const minChapterWidth = props.chapterWidth ? props.chapterWidth : 400
  let minHeight = props.chapterHeight ? props.chapterHeight : 400
  
  if (props.chapter.sections && props.chapter.sections.length > 0) {
    if (chapterLayout.value === 'free') {
      // 在自由布局模式下，计算所有 section 的边界
      let maxY = 0
      let minY = Infinity
      
      props.chapter.sections.forEach((section) => {
        if (section.y != null) {
          const sectionHeight = section.height || props.sectionHeight || 200
          const sectionBottom = section.y + sectionHeight
          
          minY = Math.min(minY, section.y)
          maxY = Math.max(maxY, sectionBottom)
        } else {
          // 如果 section 没有 y 坐标，尝试从 DOM 获取位置
          const sectionElement = document.querySelector(`[data-section-id="${section.id}"]`)
          if (sectionElement) {
            const rect = sectionElement.getBoundingClientRect()
            const parentElement = sectionElement.parentElement
            if (parentElement) {
              const parentRect = parentElement.getBoundingClientRect()
              const relativeY = rect.top - parentRect.top
              const sectionHeight = section.height || rect.height || props.sectionHeight || 200
              const sectionBottom = relativeY + sectionHeight
              
              minY = Math.min(minY, relativeY)
              maxY = Math.max(maxY, sectionBottom)
            }
          }
        }
      })
      
      if (minY !== Infinity) {
        // 添加边距（上下各 20px），宽度固定不变
        minHeight = Math.max(maxY - minY + 40, props.chapterHeight || 400)
      }
    } else {
      // 在 row/column 布局模式下，计算所有 section 的实际高度
      let maxBottom = 0
      
      props.chapter.sections.forEach((section, index) => {
        // 获取 section 的实际高度
        const sectionElement = document.querySelector(`[data-section-id="${section.id}"]`)
        let sectionHeight = section.height || props.sectionHeight || 200
        
        if (sectionElement) {
          const rect = sectionElement.getBoundingClientRect()
          sectionHeight = Math.max(rect.height || sectionHeight, props.sectionHeight || 200)
        }
        
        // 计算 section 的底部位置
        let sectionBottom = 0
        if (chapterLayout.value === 'row') {
          // row 布局：每个 section 垂直排列
          let accumulatedHeight = 0
          for (let i = 0; i <= index; i++) {
            if (i < index) {
              const prevSection = props.chapter.sections[i]
              const prevSectionElement = document.querySelector(`[data-section-id="${prevSection.id}"]`)
              let prevSectionHeight = prevSection.height || props.sectionHeight || 200
              if (prevSectionElement) {
                const prevRect = prevSectionElement.getBoundingClientRect()
                prevSectionHeight = Math.max(prevRect.height || prevSectionHeight, props.sectionHeight || 200)
              }
              accumulatedHeight += prevSectionHeight + (i > 0 ? props.sectionSpacing : 0)
            } else {
              accumulatedHeight += sectionHeight
            }
          }
          sectionBottom = accumulatedHeight
        } else {
          // column 布局：section 在同一行，取最高的
          sectionBottom = sectionHeight
        }
        
        maxBottom = Math.max(maxBottom, sectionBottom)
      })
      
      // 添加 padding 和间距
      const padding = 24 // p-3 = 12px * 2
      const headerHeight = 60 // 章节标题区域高度
      minHeight = Math.max(maxBottom + padding + headerHeight, props.chapterHeight || 400)
    }
  }
  
  return {
    borderColor: isHexColor(chapterColor.value.border) ? chapterColor.value.border : undefined,
    backgroundColor: isHexColor(chapterColor.value.bg) ? `${chapterColor.value.bg}30` : undefined,
    width: '100%', // 宽度自适应父容器
    minWidth: props.chapterWidth ? `${props.chapterWidth}px` : '400px', // 最小宽度
    maxWidth: '100%', // 最大宽度不超过父容器
    minHeight: `${minHeight}px`, // 高度根据内容自动调整
    position: 'relative',
    overflow: 'visible' // 确保内容不被裁剪
  }
}

// 获取 section 容器样式（确保高度足够容纳所有节点）
const getSectionContainerStyle = (section) => {
  // 使用 containerStyleKey 来触发重新计算
  const _ = containerStyleKey.value
  
  let minHeight = '80px'
  
  // 计算所有节点的最大 y 坐标，确保容器高度足够（支持自动换行，高度不限制）
  if (section.nodes && section.nodes.length > 0) {
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
  // 如果节点有保存的位置（x 和 y 都不为空），且排列方式是 'left'，使用保存的位置
  // 当排列方式不是 'left' 时，应该忽略保存的位置，强制使用排列方式计算
  // 布局改变或排列方式改变后，位置会被清除，所以这里会重新计算
  const shouldUseSavedPosition = node.x != null && node.y != null && props.nodeAlignment === 'left'
  
  if (shouldUseSavedPosition) {
    return {
      left: `${node.x}px`,
      top: `${node.y}px`
    }
  }
  
  // 否则使用默认位置（按 position 排序，根据布局类型自动排列）
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
  const nodeMaxWidth = props.nodeWidth // 使用全局设置的节点宽度
  const nodeMinWidth = Math.min(props.nodeWidth * 0.6, 180) // 节点最小宽度
  const nodeHeight = props.nodeHeight // 使用全局设置的节点高度
  const horizontalSpacing = props.horizontalSpacing // 使用全局设置的水平间距
  const verticalSpacing = props.verticalSpacing // 使用全局设置的垂直间距
  
  // 获取容器宽度（如果容器还没准备好，使用默认值）
  const container = sectionContainerRefs.value[sectionId]
  const containerWidth = container ? container.clientWidth : 800 // 默认800px
  const availableWidth = containerWidth - 40 // 减去左右padding
  
  // 根据布局类型计算位置
  if (chapterLayout.value === 'column') {
    // 列布局：节点横向排列，自动换行
    const nodesPerRow = Math.max(1, Math.floor((availableWidth + horizontalSpacing) / (nodeMaxWidth + horizontalSpacing)))
    const row = Math.floor(nodeIndex / nodesPerRow)
    const col = nodeIndex % nodesPerRow
    
    // 计算当前行的节点数量（可能少于 nodesPerRow）
    const nodesInCurrentRow = Math.min(nodesPerRow, sortedNodes.length - row * nodesPerRow)
    
    let defaultX = 0
    const defaultY = row * (nodeHeight + verticalSpacing)

    // 应用对齐方式
    if (nodesInCurrentRow > 1) {
      // 多节点情况下的对齐
      const totalNodesWidth = nodesInCurrentRow * nodeMaxWidth
      const remainingSpace = availableWidth - totalNodesWidth
      
      if (props.nodeAlignment === 'left') {
        // 左对齐：从左边开始排列
        defaultX = col * (nodeMaxWidth + horizontalSpacing)
      } else if (props.nodeAlignment === 'center') {
        // 居中：整体居中
        const totalSpacing = (nodesInCurrentRow - 1) * horizontalSpacing
        const totalUsedWidth = totalNodesWidth + totalSpacing
        const startX = (availableWidth - totalUsedWidth) / 2
        defaultX = startX + col * (nodeMaxWidth + horizontalSpacing)
      } else if (props.nodeAlignment === 'right') {
        // 右对齐：从右边开始排列
        const totalSpacing = (nodesInCurrentRow - 1) * horizontalSpacing
        const totalUsedWidth = totalNodesWidth + totalSpacing
        const startX = availableWidth - totalUsedWidth
        defaultX = startX + col * (nodeMaxWidth + horizontalSpacing)
      } else if (props.nodeAlignment === 'justify-between') {
        // 两端对齐：第一个在左边，最后一个在右边，中间均匀分布
        if (nodesInCurrentRow === 1) {
          defaultX = 0
        } else {
          const spaceBetween = (availableWidth - totalNodesWidth) / (nodesInCurrentRow - 1)
          defaultX = col * (nodeMaxWidth + spaceBetween)
        }
      } else if (props.nodeAlignment === 'space-evenly') {
        // 均匀分布：节点和间距都均匀
        const space = (availableWidth - totalNodesWidth) / (nodesInCurrentRow + 1)
        defaultX = space + col * (nodeMaxWidth + space)
      } else if (props.nodeAlignment === 'space-around') {
        // 环绕分布：节点两侧的间距相等
        const space = (availableWidth - totalNodesWidth) / (2 * nodesInCurrentRow)
        defaultX = space + col * (nodeMaxWidth + 2 * space)
      }
    } else {
      // 单节点情况下的对齐
      const nodeElement = nodeRefs.value[`${sectionId}-${node.id}`]
      const actualNodeWidth = nodeElement ? nodeElement.clientWidth : nodeMaxWidth
      const remainingSpace = availableWidth - actualNodeWidth

      if (props.nodeAlignment === 'center') {
        defaultX = remainingSpace / 2
      } else if (props.nodeAlignment === 'right') {
        defaultX = remainingSpace
      } else {
        defaultX = 0 // 左对齐
      }
    }

    return {
      left: `${defaultX}px`,
      top: `${defaultY}px`,
      width: `${nodeMaxWidth}px`,
      height: `${nodeHeight}px`
    }
  } else {
    // 行布局：节点纵向排列，每个 section 独占一行
    const nodesPerRow = Math.max(1, Math.floor((availableWidth + horizontalSpacing) / (nodeMaxWidth + horizontalSpacing)))
    const row = Math.floor(nodeIndex / nodesPerRow)
    const col = nodeIndex % nodesPerRow

    let defaultX = col * (nodeMaxWidth + horizontalSpacing)
    const defaultY = row * (nodeHeight + verticalSpacing)

    // 应用对齐方式
    if (nodesPerRow > 1) {
      const remainingSpace = availableWidth - (nodesPerRow * nodeMaxWidth + (nodesPerRow - 1) * horizontalSpacing)
      if (props.nodeAlignment === 'center') {
        defaultX += remainingSpace / 2
      } else if (props.nodeAlignment === 'right') {
        defaultX += remainingSpace
      } else if (props.nodeAlignment === 'justify-between') {
        const space = remainingSpace / (nodesPerRow - 1)
        defaultX = col * (nodeMaxWidth + horizontalSpacing + space)
      } else if (props.nodeAlignment === 'space-evenly') {
        const space = remainingSpace / (nodesPerRow + 1)
        defaultX = space + col * (nodeMaxWidth + space)
      } else if (props.nodeAlignment === 'space-around') {
        const space = remainingSpace / (2 * nodesPerRow)
        defaultX = space + col * (nodeMaxWidth + 2 * space)
      }
    } else {
      // 单列时的对齐
      const nodeElement = nodeRefs.value[`${sectionId}-${node.id}`]
      const actualNodeWidth = nodeElement ? nodeElement.clientWidth : nodeMaxWidth
      const remainingSpace = availableWidth - actualNodeWidth

      if (props.nodeAlignment === 'center') {
        defaultX = remainingSpace / 2
      } else if (props.nodeAlignment === 'right') {
        defaultX = remainingSpace
      }
    }

    return {
      left: `${defaultX}px`,
      top: `${defaultY}px`,
      width: `${nodeMaxWidth}px`,
      height: `${nodeHeight}px`
    }
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

// 鼠标拖拽处理（节点拖拽）
const handleMouseDown = async (event, nodeId, index, sectionId) => {
  // 如果按住 Ctrl 键，不触发拖拽（用于连接功能）
  if (event.ctrlKey || event.metaKey) {
    return
  }
  
  // 如果点击的是按钮，不触发拖拽
  if (event.target.closest('button') || event.target.closest('i')) {
    return
  }
  
  // 如果正在拖拽 section，不触发节点拖拽
  if (isDraggingSection.value && draggingSectionId.value) {
    return
  }
  
  // 阻止事件冒泡，防止触发 section 拖拽
  event.stopPropagation()
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
  
  // 计算当前节点在容器中的位置（无论当前是什么布局）
  const currentX = nodeRect.left - containerRect.left
  const currentY = nodeRect.top - containerRect.top
  
  // 保存原始状态（位置和大小），确保拖拽过程中尺寸不变
  originalNodeState.value = {
    width: nodeRect.width,
    height: nodeRect.height,
    x: node.x != null ? node.x : currentX,
    y: node.y != null ? node.y : currentY
  }
  
  // 如果节点没有保存的位置，先保存当前位置
  if (node.x == null) {
    node.x = currentX
  }
  if (node.y == null) {
    node.y = currentY
  }
  
  // 为所有其他节点也保存当前位置和大小（如果还没有保存的话）
  // 这样当拖拽时，其他节点不会因为布局变化而移动或改变大小
  const section = props.chapter.sections.find(s => s.id === sectionId)
  otherNodesOriginalSize.value.clear() // 清空之前的记录
  if (section) {
    section.nodes.forEach((otherNode) => {
      if (otherNode.id !== nodeId) {
        const otherElement = nodeRefs.value[`${sectionId}-${otherNode.id}`]
        if (otherElement) {
          const otherRect = otherElement.getBoundingClientRect()
          // 保存其他节点的原始大小
          otherNodesOriginalSize.value.set(otherNode.id, {
            width: otherRect.width,
            height: otherRect.height
          })
          // 如果其他节点还没有保存位置，获取其当前位置并保存
          if (otherNode.x == null || otherNode.y == null) {
            otherNode.x = otherRect.left - containerRect.left
            otherNode.y = otherRect.top - containerRect.top
          }
        }
      }
    })
  }
  
  dragCache.containerRect = containerRect
  dragCache.nodeWidth = nodeRect.width
  dragCache.nodeHeight = nodeRect.height
  dragCache.containerWidth = containerRect.width
  dragCache.containerHeight = containerRect.height
  
  // 计算鼠标相对于节点的偏移（相对于节点元素）
  nodeDragOffset.value = {
    x: event.clientX - nodeRect.left,
    y: event.clientY - nodeRect.top
  }
  
  // 先设置拖拽状态，确保事件监听器能正常工作
  isDraggingNode.value = true
  draggingNodeId.value = nodeId
  nodeDragStartIndex.value = index
  nodeDragStartSectionId.value = sectionId
  
  // 添加全局事件监听（在切换布局之前添加，确保能捕获事件）
  document.addEventListener('mousemove', handleMouseMove, { passive: true })
  document.addEventListener('mouseup', handleMouseUp)
  
  // 如果当前是行或列布局，拖动时自动切换到自由布局（编辑模式）
  if (chapterLayout.value !== 'free') {
    // 切换到自由布局
    try {
      const { api } = await import('../api.js')
      await api.updateChapter(props.projectId, props.chapter.id, { layout: 'free' })
      // 触发父组件重新加载项目数据
      emit('chapter-updated')
    } catch (error) {
      console.error('Failed to switch to free layout:', error)
    }
  }
  
  // 立即应用绝对定位，避免影响其他节点
  nextTick(() => {
    // 为被拖拽的节点设置绝对定位
    nodeElement.style.position = 'absolute'
    nodeElement.style.left = `${currentX}px`
    nodeElement.style.top = `${currentY}px`
    
    // 为所有其他节点也设置绝对定位，保持它们的位置
    const section = props.chapter.sections.find(s => s.id === sectionId)
    if (section) {
      section.nodes.forEach((otherNode) => {
        if (otherNode.id !== nodeId && otherNode.x != null && otherNode.y != null) {
          const otherElement = nodeRefs.value[`${sectionId}-${otherNode.id}`]
          if (otherElement) {
            otherElement.style.position = 'absolute'
            otherElement.style.left = `${otherNode.x}px`
            otherElement.style.top = `${otherNode.y}px`
            // 保持原始大小（使用保存的原始大小，防止拖拽时改变）
            const originalSize = otherNodesOriginalSize.value.get(otherNode.id)
            if (originalSize) {
              otherElement.style.width = `${originalSize.width}px`
              otherElement.style.height = `${originalSize.height}px`
            }
          }
        }
      })
    }
  })
  
  // 防止文本选择
  event.preventDefault()
}

const handleMouseMove = (event) => {
  // 只处理节点拖拽，如果正在拖拽 section 则忽略
  if (!isDraggingNode.value || !draggingNodeId.value) return
  
  // 如果正在拖拽 section，不处理节点拖拽
  if (isDraggingSection.value && draggingSectionId.value) return
  
  const sectionId = nodeDragStartSectionId.value
  if (!sectionId) return
  
  // 重新获取容器元素和尺寸（因为 section 可能被拖动，容器位置可能改变）
  const container = sectionContainerRefs.value[sectionId]
  if (!container) return
  
  // 实时获取容器位置和尺寸（相对于父容器，确保位置是相对的）
  const containerRect = container.getBoundingClientRect()
  
  // 计算新位置（相对于容器，确保位置是相对于 section 容器的）
  const newX = event.clientX - containerRect.left - nodeDragOffset.value.x
  const newY = event.clientY - containerRect.top - nodeDragOffset.value.y
  
  // 使用保存的原始尺寸，确保拖拽过程中尺寸不变
  const nodeWidth = originalNodeState.value.width || dragCache.nodeWidth
  const nodeHeight = originalNodeState.value.height || dragCache.nodeHeight
  
  const minX = 0
  const minY = 0
  const maxX = containerRect.width - nodeWidth
  const maxY = containerRect.height - nodeHeight
  
  const clampedX = Math.max(minX, Math.min(maxX, newX))
  const clampedY = Math.max(minY, Math.min(maxY, newY))
  
  // 更新节点位置（立即更新UI，位置相对于 section 容器）
  const node = props.chapter.sections.find(s => s.id === sectionId)?.nodes.find(n => n.id === draggingNodeId.value)
  if (!node) return
  
  const nodeElement = nodeRefs.value[`${sectionId}-${draggingNodeId.value}`]
  if (!nodeElement) return
  
  // 在拖拽过程中强制保持原始尺寸不变
  nodeElement.style.width = `${nodeWidth}px`
  nodeElement.style.height = `${nodeHeight}px`
  
  // 确保节点对象的尺寸也保持为原始值（防止被其他地方修改）
  // 注意：节点可能没有 width/height 属性，所以不强制设置
  
  // 确保使用绝对定位，不影响其他节点
  nodeElement.style.position = 'absolute'
  
  // 应用位置（直接设置 left 和 top，不使用 transform，因为已经是 absolute）
  nodeElement.style.left = `${clampedX}px`
  nodeElement.style.top = `${clampedY}px`
  nodeElement.style.zIndex = '20'
  
  // 更新节点对象的位置（用于其他节点的位置计算）
  node.x = clampedX
  node.y = clampedY
  
  // 确保所有其他节点也保持绝对定位和它们的位置和大小
  const section = props.chapter.sections.find(s => s.id === sectionId)
  if (section) {
    section.nodes.forEach((otherNode) => {
      if (otherNode.id !== draggingNodeId.value && otherNode.x != null && otherNode.y != null) {
        const otherElement = nodeRefs.value[`${sectionId}-${otherNode.id}`]
        if (otherElement) {
          // 保持绝对定位和位置
          otherElement.style.position = 'absolute'
          otherElement.style.left = `${otherNode.x}px`
          otherElement.style.top = `${otherNode.y}px`
          // 保持原始大小（使用保存的原始大小，防止拖拽时改变）
          const originalSize = otherNodesOriginalSize.value.get(otherNode.id)
          if (originalSize) {
            otherElement.style.width = `${originalSize.width}px`
            otherElement.style.height = `${originalSize.height}px`
          }
        }
      }
    })
  }
}

const handleMouseUp = async (event) => {
  // 只处理节点拖拽结束
  if (!isDraggingNode.value || !draggingNodeId.value) return
  
  // 如果正在拖拽 section，不处理节点拖拽结束
  if (isDraggingSection.value && draggingSectionId.value) return
  
  const sectionId = nodeDragStartSectionId.value
  if (!sectionId) {
    // 清理状态
    isDraggingNode.value = false
    draggingNodeId.value = null
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    return
  }
  
  const container = sectionContainerRefs.value[sectionId]
  if (container) {
    const containerRect = container.getBoundingClientRect()
    
    // 获取最终位置
    const finalX = event.clientX - containerRect.left - nodeDragOffset.value.x
    const finalY = event.clientY - containerRect.top - nodeDragOffset.value.y
    
    // 使用保存的原始尺寸
    const nodeWidth = originalNodeState.value.width || dragCache.nodeWidth
    const nodeHeight = originalNodeState.value.height || dragCache.nodeHeight
    
    // 节点不能超过容器边缘
    const minX = 0
    const minY = 0
    const maxX = containerRect.width - nodeWidth
    const maxY = containerRect.height - nodeHeight
    
    const constrainedX = Math.max(minX, Math.min(maxX, finalX))
    const constrainedY = Math.max(minY, Math.min(maxY, finalY))
    
    // 保存位置到节点（保持原始尺寸）
    const node = props.chapter.sections.find(s => s.id === sectionId)?.nodes.find(n => n.id === draggingNodeId.value)
    if (node) {
      node.x = constrainedX
      node.y = constrainedY
      
      // 保存位置到后端
      try {
        const { api } = await import('../api.js')
        await api.updateNodePosition(
          props.projectId,
          draggingNodeId.value,
          sectionId,
          constrainedX,
          constrainedY
        )
      } catch (error) {
        console.error('Failed to update node position:', error)
      }
    }
    
    const nodeElement = nodeRefs.value[`${sectionId}-${draggingNodeId.value}`]
    if (nodeElement) {
      // 保持绝对定位和原始尺寸
      nodeElement.style.position = 'absolute'
      nodeElement.style.left = `${constrainedX}px`
      nodeElement.style.top = `${constrainedY}px`
      nodeElement.style.zIndex = ''
      nodeElement.style.width = `${nodeWidth}px`
      nodeElement.style.height = `${nodeHeight}px`
    }
    
  // 确保所有其他节点也保持绝对定位和它们的位置和大小
  const section = props.chapter.sections.find(s => s.id === sectionId)
  if (section) {
    section.nodes.forEach((otherNode) => {
      if (otherNode.id !== draggingNodeId.value && otherNode.x != null && otherNode.y != null) {
        const otherElement = nodeRefs.value[`${sectionId}-${otherNode.id}`]
        if (otherElement) {
          otherElement.style.position = 'absolute'
          otherElement.style.left = `${otherNode.x}px`
          otherElement.style.top = `${otherNode.y}px`
          // 保持原始大小（使用保存的原始大小，防止拖拽时改变）
          const originalSize = otherNodesOriginalSize.value.get(otherNode.id)
          if (originalSize) {
            otherElement.style.width = `${originalSize.width}px`
            otherElement.style.height = `${originalSize.height}px`
          }
        }
      }
    })
  }
  }
  
  // 清理事件监听
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
  
  // 清理拖拽状态（只清理节点相关状态）
  draggingNodeId.value = null
  nodeDragStartIndex.value = null
  nodeDragStartSectionId.value = null
  
  // 清除 isDraggingNode（节点拖拽结束）
  isDraggingNode.value = false
  
  // 清理缓存
  dragCache.containerRect = null
  dragCache.nodeWidth = null
  dragCache.nodeHeight = null
  dragCache.containerWidth = null
  dragCache.containerHeight = null
  
  // 清理原始状态
  originalNodeState.value = {
    width: null,
    height: null,
    x: null,
    y: null
  }
  
  // 清理其他节点的原始大小记录
  otherNodesOriginalSize.value.clear()
  
  // 通知父组件拖拽结束，更新连接线（最终更新）
  emit('node-drag-end', { nodeId: draggingNodeId.value })
}

// Section 自由拖拽定位处理
const handleSectionMouseDown = async (event, sectionId, index) => {
  // 如果正在拉伸，不触发拖拽
  if (resizingSectionId.value) {
    return
  }
  
  // 如果正在拖拽节点，不触发 section 拖拽
  if (isDraggingNode.value && draggingNodeId.value) {
    return
  }
  
  // 如果按住 Ctrl 键，不触发拖拽
  if (event.ctrlKey || event.metaKey) {
    return
  }
  
  // 如果点击的是按钮或标题，不触发拖拽
  if (event.target.closest('button') || event.target.closest('h3')) {
    return
  }
  
  // 如果点击的是节点或其内部元素，不触发 section 拖拽
  if (event.target.closest('[data-node-id]') || event.target.closest('.knowledge-card')) {
    return
  }
  
  // 如果点击的是拉伸手柄，不触发拖拽
  if (event.target.classList.contains('cursor-ew-resize') || 
      event.target.classList.contains('cursor-ns-resize') ||
      event.target.classList.contains('cursor-nwse-resize') ||
      event.target.classList.contains('cursor-nesw-resize') ||
      event.target.closest('.cursor-ew-resize') ||
      event.target.closest('.cursor-ns-resize') ||
      event.target.closest('.cursor-nwse-resize') ||
      event.target.closest('.cursor-nesw-resize')) {
    return
  }
  
  event.preventDefault()
  event.stopPropagation()
  
  const section = props.chapter.sections.find(s => s.id === sectionId)
  if (!section) return
  
  const sectionElement = event.currentTarget
  const sectionRect = sectionElement.getBoundingClientRect()
  const parentElement = sectionElement.parentElement
  const parentRect = parentElement.getBoundingClientRect()
  
  // 计算当前元素在父容器中的位置（无论当前是什么布局）
  const currentX = sectionRect.left - parentRect.left
  const currentY = sectionRect.top - parentRect.top
  
  // 保存原始状态（位置和大小）
  originalSectionState.value = {
    width: section.width || sectionRect.width,
    height: section.height || sectionRect.height,
    x: section.x != null ? section.x : currentX,
    y: section.y != null ? section.y : currentY
  }
  
  // 如果 section 没有保存的尺寸，先保存当前尺寸
  if (!section.width) {
    section.width = originalSectionState.value.width
  }
  if (!section.height) {
    section.height = originalSectionState.value.height
  }
  
  // 立即设置位置，使 section 从流式布局切换到绝对定位
  section.x = currentX
  section.y = currentY
  
  // 为所有其他 section 也保存当前位置（如果还没有保存的话）
  // 这样当拖拽时，其他 section 不会因为布局变化而移动
  props.chapter.sections.forEach((otherSection) => {
    if (otherSection.id !== sectionId) {
      // 如果其他 section 还没有保存位置，获取其当前位置并保存
      if (otherSection.x == null || otherSection.y == null) {
        const otherElement = document.querySelector(`[data-section-id="${otherSection.id}"]`)
        if (otherElement) {
          const otherRect = otherElement.getBoundingClientRect()
          otherSection.x = otherRect.left - parentRect.left
          otherSection.y = otherRect.top - parentRect.top
          
          // 如果还没有保存尺寸，也保存当前尺寸
          if (!otherSection.width) {
            otherSection.width = otherRect.width
          }
          if (!otherSection.height) {
            otherSection.height = otherRect.height
          }
        }
      }
    }
  })
  
  sectionDragOffset.value = {
    x: event.clientX - sectionRect.left,
    y: event.clientY - sectionRect.top
  }
  
  draggingSectionId.value = sectionId
  isDraggingSection.value = true
  
  // 如果当前是行或列布局，拖动时自动切换到自由布局（编辑模式）
  if (chapterLayout.value !== 'free') {
    // 切换到自由布局
    try {
      const { api } = await import('../api.js')
      await api.updateChapter(props.projectId, props.chapter.id, { layout: 'free' })
      // 触发父组件重新加载项目数据
      emit('chapter-updated')
    } catch (error) {
      console.error('Failed to switch to free layout:', error)
    }
  }
  
  // 立即应用绝对定位，避免影响其他 section
  nextTick(() => {
    // 为被拖拽的 section 设置绝对定位
    sectionElement.style.position = 'absolute'
    sectionElement.style.left = `${currentX}px`
    sectionElement.style.top = `${currentY}px`
    sectionElement.style.marginTop = '0'
    
    // 为所有其他 section 也设置绝对定位，保持它们的位置
    props.chapter.sections.forEach((otherSection) => {
      if (otherSection.id !== sectionId && otherSection.x != null && otherSection.y != null) {
        const otherElement = document.querySelector(`[data-section-id="${otherSection.id}"]`)
        if (otherElement) {
          otherElement.style.position = 'absolute'
          otherElement.style.left = `${otherSection.x}px`
          otherElement.style.top = `${otherSection.y}px`
          otherElement.style.marginTop = '0'
          if (otherSection.width) {
            otherElement.style.width = `${otherSection.width}px`
          }
          if (otherSection.height) {
            otherElement.style.height = `${otherSection.height}px`
          }
        }
      }
    })
  })
  
  // 添加全局事件监听
  document.addEventListener('mousemove', handleSectionMouseMove, { passive: true })
  document.addEventListener('mouseup', handleSectionMouseUp)
}

const handleSectionMouseMove = (event) => {
  // 只处理 section 拖拽，如果正在拖拽节点则忽略
  if (!isDraggingSection.value || !draggingSectionId.value) return
  
  // 如果正在拖拽节点，不处理 section 拖拽
  if (isDraggingNode.value && draggingNodeId.value) return
  
  const sectionElement = document.querySelector(`[data-section-id="${draggingSectionId.value}"]`)
  if (!sectionElement) return
  
  const section = props.chapter.sections.find(s => s.id === draggingSectionId.value)
  if (!section) return
  
  const parentElement = sectionElement.parentElement
  const parentRect = parentElement.getBoundingClientRect()
  
  // 计算新位置（相对于父容器）
  const newX = event.clientX - parentRect.left - sectionDragOffset.value.x
  const newY = event.clientY - parentRect.top - sectionDragOffset.value.y
  
  // 使用保存的原始尺寸，确保拖拽过程中尺寸不变
  const sectionWidth = originalSectionState.value.width
  const sectionHeight = originalSectionState.value.height
  
  // Section 不能超过父容器边缘
  // X 坐标限制在父容器宽度内
  const constrainedX = Math.max(0, Math.min(newX, parentRect.width - sectionWidth))
  // Y 坐标：允许向下移动以拉伸 chapter，但需要确保不超出父容器边缘
  // 先更新 section 位置，然后触发 chapter 高度重新计算，最后再约束位置
  const currentParentHeight = parentElement.scrollHeight || parentRect.height
  // 临时允许超出当前高度，以便触发 chapter 扩展
  let constrainedY = Math.max(0, newY)
  
  // 如果超出当前父容器高度，先触发 chapter 高度更新
  if (constrainedY + sectionHeight > currentParentHeight) {
    // 立即触发 chapter 高度重新计算
    containerStyleKey.value++
    // 使用 requestAnimationFrame 等待 DOM 更新
    requestAnimationFrame(() => {
      const updatedParentHeight = parentElement.scrollHeight || parentRect.height
      // 重新约束位置，确保不超出更新后的父容器高度
      constrainedY = Math.max(0, Math.min(constrainedY, updatedParentHeight - sectionHeight))
      section.y = constrainedY
      sectionElement.style.top = `${constrainedY}px`
    })
  } else {
    // 如果未超出，正常约束
    constrainedY = Math.max(0, Math.min(newY, currentParentHeight - sectionHeight))
  }
  
  // 在拖拽过程中强制保持原始尺寸不变
  sectionElement.style.width = `${sectionWidth}px`
  sectionElement.style.height = `${sectionHeight}px`
  
  // 确保 section 对象的尺寸也保持为原始值（防止被其他地方修改）
  section.width = sectionWidth
  section.height = sectionHeight
  
  // 确保使用绝对定位，不影响其他 section
  sectionElement.style.position = 'absolute'
  sectionElement.style.marginTop = '0'
  
  // 应用位置（直接设置 left 和 top，不使用 transform，因为已经是 absolute）
  sectionElement.style.left = `${constrainedX}px`
  sectionElement.style.top = `${constrainedY}px`
  sectionElement.style.zIndex = '100'
  
  // 更新 section 对象的位置（用于其他 section 的位置计算）
  section.x = constrainedX
  section.y = constrainedY
  
  // 确保所有其他 section 也保持绝对定位和它们的位置
  props.chapter.sections.forEach((otherSection) => {
    if (otherSection.id !== draggingSectionId.value && otherSection.x != null && otherSection.y != null) {
      const otherElement = document.querySelector(`[data-section-id="${otherSection.id}"]`)
      if (otherElement) {
        otherElement.style.position = 'absolute'
        otherElement.style.left = `${otherSection.x}px`
        otherElement.style.top = `${otherSection.y}px`
        otherElement.style.marginTop = '0'
      }
    }
  })
  
  // 触发 chapter 高度重新计算（使用节流，避免过于频繁）
  if (!handleSectionMouseMove.chapterUpdateTimer) {
    handleSectionMouseMove.chapterUpdateTimer = setTimeout(() => {
      containerStyleKey.value++
      handleSectionMouseMove.chapterUpdateTimer = null
    }, 100) // 每100ms最多更新一次
  }
  
  // 触发连接线更新（节流：每 50ms 更新一次）
  // 暂时禁用实时连接线更新，测试拖拽性能
  // const now = Date.now()
  // if (now - lastConnectionUpdateTime >= CONNECTION_UPDATE_INTERVAL) {
  //   lastConnectionUpdateTime = now
  //   emit('section-dragging', {
  //     sectionId: draggingSectionId.value,
  //     chapterId: props.chapter.id,
  //     x: constrainedX,
  //     y: constrainedY
  //   })
  // }
}

const handleSectionMouseUp = async (event) => {
  // 只处理 section 拖拽结束
  if (!isDraggingSection.value || !draggingSectionId.value) return
  
  // 如果正在拖拽节点，不处理 section 拖拽结束
  if (isDraggingNode.value && draggingNodeId.value) return
  
  const sectionElement = document.querySelector(`[data-section-id="${draggingSectionId.value}"]`)
  if (sectionElement) {
    const parentElement = sectionElement.parentElement
    const parentRect = parentElement.getBoundingClientRect()
    
    // 获取最终位置
    const finalX = event.clientX - parentRect.left - sectionDragOffset.value.x
    const finalY = event.clientY - parentRect.top - sectionDragOffset.value.y
    
    // 使用保存的原始尺寸
    const sectionWidth = originalSectionState.value.width
    const sectionHeight = originalSectionState.value.height
    
    // Section 不能超过父容器边缘
    // X 坐标限制在父容器宽度内
    const constrainedX = Math.max(0, Math.min(finalX, parentRect.width - sectionWidth))
    // Y 坐标限制在父容器高度内（但父容器高度会根据 section 位置自动调整）
    // 获取当前父容器的实际高度（可能已经因为其他 section 而扩展）
    const currentParentHeight = parentElement.scrollHeight || parentRect.height
    const constrainedY = Math.max(0, Math.min(finalY, currentParentHeight - sectionHeight))
    
    // 保存位置到 section（保持原始尺寸）
    const section = props.chapter.sections.find(s => s.id === draggingSectionId.value)
    if (section) {
      section.x = constrainedX
      section.y = constrainedY
      // 确保尺寸保持为原始值
      section.width = sectionWidth
      section.height = sectionHeight
      
      // 触发更新事件，保存位置和尺寸到后端
      emit('section-position-updated', {
        sectionId: draggingSectionId.value,
        chapterId: props.chapter.id,
        x: constrainedX,
        y: constrainedY,
        width: sectionWidth,
        height: sectionHeight
      })
    }
    
    // 保持绝对定位和原始尺寸
    sectionElement.style.position = 'absolute'
    sectionElement.style.left = `${constrainedX}px`
    sectionElement.style.top = `${constrainedY}px`
    sectionElement.style.marginTop = '0'
    sectionElement.style.zIndex = ''
    sectionElement.style.width = `${sectionWidth}px`
    sectionElement.style.height = `${sectionHeight}px`
    
    // 确保所有其他 section 也保持绝对定位和它们的位置
    props.chapter.sections.forEach((otherSection) => {
      if (otherSection.id !== draggingSectionId.value && otherSection.x != null && otherSection.y != null) {
        const otherElement = document.querySelector(`[data-section-id="${otherSection.id}"]`)
        if (otherElement) {
          otherElement.style.position = 'absolute'
          otherElement.style.left = `${otherSection.x}px`
          otherElement.style.top = `${otherSection.y}px`
          otherElement.style.marginTop = '0'
          if (otherSection.width) {
            otherElement.style.width = `${otherSection.width}px`
          }
          if (otherSection.height) {
            otherElement.style.height = `${otherSection.height}px`
          }
        }
      }
    })
    
    // 触发 chapter 高度重新计算
    nextTick(() => {
      containerStyleKey.value++
    })
    
    // 清除原始状态
    originalSectionState.value = {
      width: null,
      height: null,
      x: null,
      y: null
    }
  }
  
  // 清理拖拽状态（只清理 section 相关状态）
  draggingSectionId.value = null
  
  // 清除 isDraggingSection（section 拖拽结束）
  isDraggingSection.value = false
  
  // 清理定时器
  if (handleSectionMouseMove.chapterUpdateTimer) {
    clearTimeout(handleSectionMouseMove.chapterUpdateTimer)
    handleSectionMouseMove.chapterUpdateTimer = null
  }
  
  document.removeEventListener('mousemove', handleSectionMouseMove)
  document.removeEventListener('mouseup', handleSectionMouseUp)
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
// Chapter 拖拽处理（暂时不实现，因为章节在列布局中位置相对固定）
const handleChapterMouseDown = (event, chapterId) => {
  // 如果按住 Ctrl 键，不触发拖拽
  if (event.ctrlKey || event.metaKey) {
    return
  }
  
  // 如果点击的是按钮或标题，不触发拖拽
  if (event.target.closest('button') || event.target.closest('h2')) {
    return
  }
  
  // 章节拖拽暂时不实现，只触发选中
  emit('chapter-selected', chapterId)
  
  // 清理缓存和重置时间戳
  dragCache.containerRect = null
  dragCache.nodeWidth = null
  dragCache.nodeHeight = null
  dragCache.containerWidth = null
  dragCache.containerHeight = null
  lastConnectionUpdateTime = 0
  
  draggingNodeId.value = null
  nodeDragStartIndex.value = null
  nodeDragStartSectionId.value = null
  isDraggingNode.value = false
  nodeDragOffset.value = { x: 0, y: 0 }
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

