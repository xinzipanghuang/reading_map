<template>
  <!-- Mobile Overlay -->
  <div
    v-if="isMobile && isExpanded"
    class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
    @click="toggleSidebar"
  ></div>
  
  <!-- Sidebar -->
  <div
    :class="[
      'bg-white border-r border-gray-200 h-screen flex flex-col transition-all duration-300 ease-in-out',
      isExpanded 
        ? 'w-64' 
        : 'w-0 lg:w-16 overflow-hidden',
      isMobile && !isExpanded ? 'hidden' : 'fixed lg:relative z-50 lg:z-auto'
    ]"
  >
    <!-- Header -->
    <div class="p-4 border-b border-gray-200 flex-shrink-0">
      <div class="flex items-center justify-between mb-3">
        <h2 v-if="isExpanded" class="text-lg font-bold text-gray-800">项目列表</h2>
        <button
          @click="toggleSidebar"
          class="p-2 text-gray-600 hover:bg-gray-100 rounded transition ml-auto lg:ml-0"
          :title="isExpanded ? '收起' : '展开'"
        >
          <i :class="isExpanded ? 'ph ph-sidebar-simple' : 'ph ph-sidebar'"></i>
        </button>
      </div>
      <button
        v-if="isExpanded"
        @click="showNewProjectModal = true"
        class="w-full bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition flex items-center justify-center gap-2"
      >
        <i class="ph ph-plus"></i>
        <span class="hidden lg:inline">新建项目</span>
      </button>
      <button
        v-else
        @click="showNewProjectModal = true"
        class="w-full p-2 text-gray-600 hover:bg-gray-100 rounded transition flex items-center justify-center"
        title="新建项目"
      >
        <i class="ph ph-plus text-lg"></i>
      </button>
    </div>

    <!-- Project List -->
    <div class="flex-1 overflow-y-auto p-2">
      <div
        v-for="project in sortedProjects"
        :key="project.id"
        :class="[
          'rounded-lg transition mb-2 group',
          currentProjectId === project.id
            ? 'bg-blue-50 border-2 border-blue-500'
            : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent',
          isExpanded ? 'p-3' : 'p-2 flex items-center justify-center'
        ]"
      >
        <div v-if="isExpanded" class="flex items-start justify-between gap-2">
          <div 
            @click="selectProject(project.id)"
            class="flex-1 cursor-pointer min-w-0"
          >
            <div class="font-medium text-gray-800 text-sm truncate">{{ project.name }}</div>
            <div class="text-xs text-gray-500 mt-1">
              {{ formatDate(project.updated_at) }}
            </div>
          </div>
          <!-- Action Buttons -->
          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click.stop="showRenameModal(project)"
              class="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition"
              title="重命名"
            >
              <i class="ph ph-pencil text-sm"></i>
            </button>
            <button
              @click.stop="showDeleteConfirm(project)"
              class="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition"
              title="删除"
            >
              <i class="ph ph-trash text-sm"></i>
            </button>
          </div>
        </div>
        <div 
          v-else
          @click="selectProject(project.id)"
          class="cursor-pointer w-full flex items-center justify-center"
          :title="project.name"
        >
          <div 
            :class="[
              'w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold',
              currentProjectId === project.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-600'
            ]"
          >
            {{ project.name.charAt(0).toUpperCase() }}
          </div>
        </div>
      </div>
    </div>

    <!-- New Project Modal -->
    <div
      v-if="showNewProjectModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showNewProjectModal = false"
    >
      <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4">新建项目</h3>
        <input
          v-model="newProjectName"
          @keyup.enter="createProject"
          class="w-full border p-2 rounded mb-4 focus:outline-none focus:border-blue-500"
          placeholder="项目名称"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="showNewProjectModal = false"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition"
          >
            取消
          </button>
          <button
            @click="createProject"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            创建
          </button>
        </div>
      </div>
    </div>

    <!-- Rename Project Modal -->
    <div
      v-if="isRenameModalVisible"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="isRenameModalVisible = false; renamingProject = null; renameProjectName = ''"
    >
      <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
        <h3 class="text-lg font-bold mb-4">重命名项目</h3>
        <input
          v-model="renameProjectName"
          @keyup.enter="renameProject"
          class="w-full border p-2 rounded mb-4 focus:outline-none focus:border-blue-500"
          placeholder="项目名称"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="isRenameModalVisible = false; renamingProject = null; renameProjectName = ''"
            class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded transition"
          >
            取消
          </button>
          <button
            @click="renameProject"
            class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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

const props = defineProps({
  projects: {
    type: Array,
    default: () => []
  },
  currentProjectId: {
    type: String,
    default: null
  }
})

// 按更新时间倒序排列，最新的在最上面
const sortedProjects = computed(() => {
  return [...props.projects].sort((a, b) => {
    const dateA = a.updated_at ? new Date(a.updated_at).getTime() : 0
    const dateB = b.updated_at ? new Date(b.updated_at).getTime() : 0
    return dateB - dateA // 倒序：最新的在前
  })
})

const emit = defineEmits(['project-selected', 'project-created', 'project-updated', 'project-deleted'])

const showNewProjectModal = ref(false)
const newProjectName = ref('')
const isRenameModalVisible = ref(false)
const renamingProject = ref(null)
const renameProjectName = ref('')

// 侧边栏展开/收起状态
const isExpanded = ref(localStorage.getItem('sidebarExpanded') !== 'false')
const isMobile = ref(window.innerWidth < 1024) // lg breakpoint

// 监听窗口大小变化
const handleResize = () => {
  isMobile.value = window.innerWidth < 1024
  // 在移动端默认收起
  if (isMobile.value) {
    isExpanded.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  // 初始化时检查移动端
  if (isMobile.value) {
    isExpanded.value = false
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 保存状态到 localStorage
watch(isExpanded, (newVal) => {
  localStorage.setItem('sidebarExpanded', String(newVal))
})

// 切换侧边栏
const toggleSidebar = () => {
  isExpanded.value = !isExpanded.value
}

// 打开侧边栏
const openSidebar = () => {
  isExpanded.value = true
}

// 关闭侧边栏
const closeSidebar = () => {
  isExpanded.value = false
}

// 暴露方法供父组件调用（必须在函数定义之后）
defineExpose({
  toggleSidebar,
  openSidebar,
  closeSidebar
})

const selectProject = (projectId) => {
  emit('project-selected', projectId)
}

const createProject = async () => {
  // 如果没有输入名称，使用默认名称
  const projectName = newProjectName.value.trim() || '新项目'
  try {
    const res = await axios.post(`${API_URL}/projects`, { name: projectName })
    newProjectName.value = ''
    showNewProjectModal.value = false
    emit('project-created', res.data)
    ElMessage.success('项目创建成功')
  } catch (e) {
    ElMessage.error('创建项目失败: ' + (e.response?.data?.detail || '未知错误'))
  }
}

const showRenameModal = (project) => {
  renamingProject.value = project
  renameProjectName.value = project.name
  isRenameModalVisible.value = true
}

const renameProject = async () => {
  if (!renamingProject.value) return
  
  const newName = renameProjectName.value.trim()
  if (!newName) {
    ElMessage.warning('项目名称不能为空')
    return
  }
  
  if (newName === renamingProject.value.name) {
    isRenameModalVisible.value = false
    return
  }
  
  try {
    await axios.put(`${API_URL}/projects/${renamingProject.value.id}`, { name: newName })
    emit('project-updated', { id: renamingProject.value.id, name: newName })
    isRenameModalVisible.value = false
    renamingProject.value = null
    renameProjectName.value = ''
    ElMessage.success('项目重命名成功')
  } catch (e) {
    ElMessage.error('重命名失败: ' + (e.response?.data?.detail || '未知错误'))
  }
}

const showDeleteConfirm = async (project) => {
  try {
    await ElMessageBox.confirm(
      `确定删除项目 "${project.name}" 吗？此操作将删除项目中的所有章节、节点和连接，且无法恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    // 用户确认删除
    try {
      await axios.delete(`${API_URL}/projects/${project.id}`)
      emit('project-deleted', project.id)
      ElMessage.success('项目删除成功')
    } catch (e) {
      ElMessage.error('删除失败: ' + (e.response?.data?.detail || '未知错误'))
    }
  } catch (e) {
    // 用户取消删除
    if (e !== 'cancel') {
      console.error('Delete error:', e)
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

