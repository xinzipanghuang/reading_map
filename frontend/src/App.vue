<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden">
    <!-- Left Sidebar: Projects -->
    <ProjectSidebar
      ref="sidebarRef"
      :projects="projects"
      :current-project-id="currentProjectId"
      @project-selected="handleProjectSelected"
      @project-created="handleProjectCreated"
      @project-updated="handleProjectUpdated"
      @project-deleted="handleProjectDeleted"
    />

    <!-- Right Canvas: Knowledge Map -->
    <div class="flex-1 flex flex-col overflow-hidden lg:ml-0">
    <!-- Header -->
      <header class="bg-white border-b border-gray-200 px-4 lg:px-6 py-4 flex justify-between items-center shadow-sm">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <!-- Mobile Menu Button -->
        <button 
            @click="openSidebar"
            class="lg:hidden p-2 text-gray-600 hover:bg-gray-100 rounded transition"
            title="打开菜单"
        >
            <i class="ph ph-list text-xl"></i>
        </button>
          <div class="min-w-0 flex-1">
            <h1 class="text-xl lg:text-2xl font-bold text-gray-800 truncate">
              {{ currentProject?.name || '知识图谱构建器' }}
            </h1>
            <p v-if="currentProject" class="text-xs lg:text-sm text-gray-600 mt-1 hidden lg:block">
              从直觉到综合：构建你的知识路径
            </p>
      </div>
          </div>
      <div class="flex items-center gap-2 lg:gap-3 flex-shrink-0">
          <!-- 第一组：数据操作菜单（最左边） -->
          <div class="relative" @click.stop>
            <button 
              @click="showDataMenu = !showDataMenu"
              class="px-3 py-2 bg-white border border-gray-300 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition text-xs lg:text-sm flex items-center gap-1.5 shadow-sm text-gray-700"
              title="数据操作"
            >
              <i class="ph ph-dots-three-vertical"></i>
              <span class="hidden sm:inline">数据</span>
              <i :class="showDataMenu ? 'ph ph-caret-up' : 'ph ph-caret-down'" class="text-xs"></i>
            </button>
            
            <!-- 下拉菜单 -->
            <transition
              enter-active-class="transition-all duration-200 ease-out"
              enter-from-class="opacity-0 translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-150 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 translate-y-2"
            >
              <div
                v-if="showDataMenu"
                class="absolute left-0 mt-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-[100] py-1"
            >
            <button 
                  @click="triggerImport(); showDataMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-purple-50 hover:text-purple-700 transition flex items-center gap-2"
                >
                  <i class="ph ph-upload text-purple-600"></i>
                  <span>导入 YAML</span>
                </button>
                <input 
                  ref="fileInput"
                  type="file"
                  accept=".yaml,.yml"
                  style="display: none"
                  @change="handleFileImport"
                />
                <button 
                  v-if="currentProjectId"
                  @click="exportProject(); showDataMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-green-50 hover:text-green-700 transition flex items-center gap-2"
                >
                  <i class="ph ph-download text-green-600"></i>
                  <span>导出 YAML</span>
            </button>
          </div>
            </transition>
        </div>

          <!-- 分隔线 -->
          <div class="hidden md:block w-px h-6 bg-gray-300"></div>
          
          <!-- 第二组：配色方案（中间） -->
          <div class="relative hidden md:block" @click.stop>
            <button 
              @click="showColorMenu = !showColorMenu"
              class="px-3 py-2 bg-white border border-gray-300 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition text-xs lg:text-sm flex items-center gap-1.5 shadow-sm text-gray-700"
              title="配色方案"
            >
              <i class="ph ph-palette"></i>
              <span class="hidden sm:inline">配色</span>
              <i :class="showColorMenu ? 'ph ph-caret-up' : 'ph ph-caret-down'" class="text-xs"></i>
            </button>
            
            <!-- 下拉菜单 -->
            <transition
              enter-active-class="transition-all duration-200 ease-out"
              enter-from-class="opacity-0 translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-150 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 translate-y-2"
            >
              <div
                v-if="showColorMenu"
                class="absolute left-0 mt-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-[100] py-1 max-h-64 overflow-y-auto"
              >
              <button 
                  @click="colorScheme = 'default'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'default' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>默认</span>
                </button>
                <button 
                  @click="colorScheme = 'seaborn-set1'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'seaborn-set1' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>Set1</span>
                </button>
                <button 
                  @click="colorScheme = 'seaborn-set2'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'seaborn-set2' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>Set2</span>
                </button>
                <button 
                  @click="colorScheme = 'seaborn-set3'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'seaborn-set3' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>Set3</span>
                </button>
                <button 
                  @click="colorScheme = 'seaborn-pastel1'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'seaborn-pastel1' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>Pastel1</span>
                </button>
                <button 
                  @click="colorScheme = 'seaborn-pastel2'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'seaborn-pastel2' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>Pastel2</span>
                </button>
                <button 
                  @click="colorScheme = 'seaborn-dark2'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'seaborn-dark2' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>Dark2</span>
                </button>
                <button 
                  @click="colorScheme = 'seaborn-accent'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'seaborn-accent' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>Accent</span>
                </button>
                <button 
                  @click="colorScheme = 'seaborn-paired'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'seaborn-paired' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>Paired</span>
                </button>
                <button 
                  @click="colorScheme = 'seaborn-spectral'; showColorMenu = false"
                  class="w-full px-4 py-2 text-left text-xs lg:text-sm text-gray-700 hover:bg-gray-50 transition flex items-center gap-2"
                  :class="colorScheme === 'seaborn-spectral' ? 'bg-blue-50 text-blue-700' : ''"
                >
                  <i class="ph ph-palette"></i>
                  <span>Spectral</span>
              </button>
              </div>
            </transition>
            </div>
            
          <!-- 分隔线 -->
          <div class="hidden md:block w-px h-6 bg-gray-300"></div>
          
          <!-- 第三组：布局设置（最右边） -->
                  <button 
            @click.stop="showLayoutSettings = !showLayoutSettings"
            class="px-3 py-2 bg-white border border-gray-300 rounded-lg hover:border-gray-400 hover:bg-gray-50 transition text-xs lg:text-sm flex items-center gap-2 shadow-sm"
            :class="showLayoutSettings ? 'bg-blue-50 border-blue-400 text-blue-700' : 'text-gray-700'"
            title="布局设置"
          >
            <i :class="showLayoutSettings ? 'ph ph-sliders-horizontal' : 'ph ph-sliders'"></i>
            <span class="hidden sm:inline">布局</span>
                  </button>
                </div>
    </header>
    
    <!-- Layout Settings Sidebar (Right Side) -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="translate-x-full opacity-0"
      enter-to-class="translate-x-0 opacity-100"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="translate-x-0 opacity-100"
      leave-to-class="translate-x-full opacity-0"
    >
      <div
        v-if="showLayoutSettings"
        class="fixed top-[80px] right-0 bottom-0 bg-white border-l border-gray-200 shadow-2xl z-50 flex flex-col"
        :style="{ width: `${layoutSettingsWidth}px` }"
        @click.stop
      >
        <!-- Sidebar Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 bg-gray-50">
          <h3 class="text-base font-bold text-gray-800 flex items-center gap-2">
            <i class="ph ph-sliders"></i>
            <span>布局设置</span>
          </h3>
                  <button 
            @click.stop="showLayoutSettings = false"
            class="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full p-1 transition"
                  >
            <i class="ph ph-x text-lg"></i>
                  </button>
                </div>
                
        <!-- Sidebar Content -->
        <div class="flex-1 overflow-y-auto layout-settings-scrollbar p-5">
          <div class="space-y-3">
            <!-- Selected Item Properties (选中项属性，放在最前面) -->
            <div v-if="editingItem.type" class="border border-gray-200 rounded-lg overflow-hidden border-blue-300">
              <button 
                @click.stop="expandedSections.editingItem = !expandedSections.editingItem"
                class="w-full px-4 py-3 bg-blue-50 hover:bg-blue-100 transition-all duration-200 flex items-center justify-between"
              >
                <div class="flex items-center gap-2">
                  <i :class="editingItem.type === 'chapter' ? 'ph ph-book-open text-base text-blue-600' : editingItem.type === 'section' ? 'ph ph-stack text-base text-green-600' : 'ph ph-circle text-base text-purple-600'"></i>
                  <span class="text-sm font-semibold text-gray-800">
                    {{ editingItem.type === 'chapter' ? '章节属性' : editingItem.type === 'section' ? '部分属性' : '节点属性' }}
                    </span>
                  </div>
                <div class="flex items-center gap-2">
                  <button
                    @click.stop="editingItem = { type: null, id: null, chapterId: null, sectionId: null }"
                    class="text-gray-400 hover:text-gray-600 hover:bg-white rounded-full p-1 transition"
                    title="关闭编辑"
                  >
                    <i class="ph ph-x text-sm"></i>
                  </button>
                  <i :class="expandedSections.editingItem ? 'ph ph-chevron-up text-gray-500' : 'ph ph-chevron-down text-gray-500'"></i>
                  </div>
              </button>
              <div v-show="expandedSections.editingItem" class="p-4 space-y-4 bg-white">
                <!-- Chapter Properties -->
                <div v-if="editingItem.type === 'chapter'" class="space-y-4">
                  <div>
                    <label class="text-xs font-medium text-gray-700 mb-2 block">章节名称</label>
                <input 
                      v-model="selectedChapterName"
                      @blur="updateChapterName"
                      @click.stop
                      class="w-full px-3 py-2 border-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label class="text-xs font-medium text-gray-700 mb-2 block">布局方式</label>
                <button 
                      @click.stop="toggleChapterLayout"
                      class="w-full px-3 py-2 border-2 border-gray-300 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-1.5 bg-white hover:border-blue-400 hover:bg-blue-50"
                >
                      <i :class="getChapterLayoutIcon(selectedChapterLayout)" class="text-base"></i>
                      <span>{{ getChapterLayoutText(selectedChapterLayout) }}</span>
                </button>
                  </div>
              </div>
              
                <!-- Section Properties -->
                <div v-else-if="editingItem.type === 'section'" class="space-y-4">
                  <div>
                    <label class="text-xs font-medium text-gray-700 mb-2 block">部分名称</label>
                <input 
                      v-model="selectedSectionName"
                      @blur="updateSectionName"
                      @click.stop
                      class="w-full px-3 py-2 border-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                
                <!-- Node Properties -->
                <div v-else-if="editingItem.type === 'node'" class="space-y-4">
                  <div>
                    <label class="text-xs font-medium text-gray-700 mb-2 block">节点名称</label>
                    <input
                      v-model="selectedNodeName"
                      @blur="updateNodeName"
                      @click.stop
                      class="w-full px-3 py-2 border-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label class="text-xs font-medium text-gray-700 mb-2 block">节点内容</label>
                    <textarea
                      v-model="selectedNodeContent"
                      @blur="updateNodeContent"
                      @click.stop
                      rows="4"
                      class="w-full px-3 py-2 border-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                    ></textarea>
                  </div>
                </div>
              </div>
              </div>
              
            <!-- Node Settings Section (节点设置，最前面，默认展开) -->
            <div class="border border-gray-200 rounded-lg overflow-hidden">
                <button 
                @click.stop="expandedSections.node = !expandedSections.node"
                class="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-all duration-200 flex items-center justify-between"
              >
                <div class="flex items-center gap-2">
                  <i class="ph ph-circle text-base text-purple-600"></i>
                  <span class="text-sm font-semibold text-gray-800">节点设置</span>
                </div>
                <i :class="expandedSections.node ? 'ph ph-chevron-up text-gray-500' : 'ph ph-chevron-down text-gray-500'"></i>
                </button>
              <div v-show="expandedSections.node" class="p-4 space-y-4 bg-white">
                <!-- Node Width Slider -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <label class="text-xs font-medium text-gray-700">节点宽度</label>
                    <span class="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">{{ nodeWidth }}px</span>
              </div>
                  <input
                    v-model.number="nodeWidth"
                    type="range"
                    min="150"
                    max="500"
                    step="10"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
            </div>
                
                <!-- Node Height Slider -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <label class="text-xs font-medium text-gray-700">节点高度</label>
                    <span class="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">{{ nodeHeight }}px</span>
          </div>
                  <input
                    v-model.number="nodeHeight"
                    type="range"
                    min="50"
                    max="200"
                    step="5"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
        </div>
                
                <!-- Horizontal Spacing Slider -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <label class="text-xs font-medium text-gray-700">水平间距</label>
                    <span class="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">{{ horizontalSpacing }}px</span>
                  </div>
                  <input
                    v-model.number="horizontalSpacing"
                    type="range"
                    min="20"
                    max="300"
                    step="10"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
      </div>

                <!-- Vertical Spacing Slider -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <label class="text-xs font-medium text-gray-700">垂直间距</label>
                    <span class="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">{{ verticalSpacing }}px</span>
                  </div>
                  <input
                    v-model.number="verticalSpacing"
                    type="range"
                    min="10"
                    max="100"
                    step="5"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
                
                <!-- Node Alignment Selector -->
                <div>
                  <label class="text-xs font-medium text-gray-700 mb-2 block">节点排列方式</label>
                  <select
                    v-model="nodeAlignment"
                    @click.stop
                    class="w-full px-3 py-2 border-2 border-gray-300 rounded-lg text-sm bg-white hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition cursor-pointer"
                  >
                    <option value="left">左对齐</option>
                    <option value="center">居中</option>
                    <option value="right">右对齐</option>
                    <option value="justify-between">两端对齐</option>
                    <option value="space-evenly">均匀分布</option>
                    <option value="space-around">环绕分布</option>
                  </select>
            </div>
              </div>
            </div>
            
            <!-- Section Settings Section (部分设置，默认展开) -->
            <div class="border border-gray-200 rounded-lg overflow-hidden">
              <button 
                @click.stop="expandedSections.section = !expandedSections.section"
                class="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-all duration-200 flex items-center justify-between"
              >
                <div class="flex items-center gap-2">
                  <i class="ph ph-stack text-base text-green-600"></i>
                  <span class="text-sm font-semibold text-gray-800">部分设置</span>
                </div>
                <i :class="expandedSections.section ? 'ph ph-chevron-up text-gray-500' : 'ph ph-chevron-down text-gray-500'"></i>
              </button>
              <div v-show="expandedSections.section" class="p-4 space-y-4 bg-white">
                <!-- Section Width Slider -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <label class="text-xs font-medium text-gray-700">部分宽度</label>
                    <span class="text-xs font-semibold" :class="sectionWidth ? 'text-blue-600 bg-blue-50' : 'text-gray-500 bg-gray-100'">
                      {{ sectionWidth || '自动' }}{{ sectionWidth ? 'px' : '' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2">
                    <input 
                      v-model.number="sectionWidth"
                      type="range"
                      min="200"
                      max="1500"
                      step="50"
                      class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                    />
              <button 
                      @click.stop="sectionWidth = null"
                      class="px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 border border-gray-300 rounded-lg transition whitespace-nowrap"
                      title="设为自动"
              >
                      自动
              </button>
            </div>
                </div>
                
                <!-- Section Height Slider -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <label class="text-xs font-medium text-gray-700">部分高度</label>
                    <span class="text-xs font-semibold" :class="sectionHeight ? 'text-blue-600 bg-blue-50' : 'text-gray-500 bg-gray-100'">
                      {{ sectionHeight || '自动' }}{{ sectionHeight ? 'px' : '' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2">
                    <input
                      v-model.number="sectionHeight"
                      type="range"
                      min="100"
                      max="1500"
                      step="50"
                      class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <button 
                      @click.stop="sectionHeight = null"
                      class="px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 border border-gray-300 rounded-lg transition whitespace-nowrap"
                      title="设为自动"
                    >
                      自动
                    </button>
          </div>
        </div>

                <!-- Section Spacing Slider -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <label class="text-xs font-medium text-gray-700">部分间隔</label>
                    <span class="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">{{ sectionSpacing }}px</span>
                  </div>
                  <input
                    v-model.number="sectionSpacing"
                    type="range"
                    min="0"
                    max="100"
                    step="4"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  />
                </div>
              </div>
            </div>
            
            <!-- Chapter Settings Section (章节设置，默认展开) -->
            <div class="border border-gray-200 rounded-lg overflow-hidden">
            <button 
                @click.stop="expandedSections.chapter = !expandedSections.chapter"
                class="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-all duration-200 flex items-center justify-between"
              >
                <div class="flex items-center gap-2">
                  <i class="ph ph-book-open text-base text-blue-600"></i>
                  <span class="text-sm font-semibold text-gray-800">章节设置</span>
                </div>
                <i :class="expandedSections.chapter ? 'ph ph-chevron-up text-gray-500' : 'ph ph-chevron-down text-gray-500'"></i>
            </button>
              <div v-show="expandedSections.chapter" class="p-4 space-y-4 bg-white">
                <!-- Chapter Width Slider -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <label class="text-xs font-medium text-gray-700">章节宽度</label>
                    <span class="text-xs font-semibold" :class="chapterWidth ? 'text-blue-600 bg-blue-50' : 'text-gray-500 bg-gray-100'">
                      {{ chapterWidth || '自动' }}{{ chapterWidth ? 'px' : '' }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2">
                    <input
                      v-model.number="chapterWidth"
                      type="range"
                      min="400"
                      max="2000"
                      step="50"
                      class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                    />
            <button 
                      @click.stop="chapterWidth = null"
                      class="px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 border border-gray-300 rounded-lg transition whitespace-nowrap"
                      title="设为自动"
                    >
                      自动
            </button>
          </div>
        </div>
        
                <!-- Chapter Height Slider -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <label class="text-xs font-medium text-gray-700">章节高度</label>
                    <span class="text-xs font-semibold" :class="chapterHeight ? 'text-blue-600 bg-blue-50' : 'text-gray-500 bg-gray-100'">
                      {{ chapterHeight || '自动' }}{{ chapterHeight ? 'px' : '' }}
          </span>
        </div>
                  <div class="flex items-center gap-2">
                    <input
                      v-model.number="chapterHeight"
                      type="range"
                      min="200"
                      max="2000"
                      step="50"
                      class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <button
                      @click.stop="chapterHeight = null"
                      class="px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 border border-gray-300 rounded-lg transition whitespace-nowrap"
                      title="设为自动"
                    >
                      自动
                    </button>
      </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
    
    <!-- Canvas Area -->
    <div 
      class="flex-1 overflow-y-auto overflow-x-hidden p-4 relative transition-all duration-300" 
      v-if="currentProjectId" 
      ref="canvasContainer"
      :style="{ 
        width: showLayoutSettings ? `calc(100% - ${layoutSettingsWidth}px)` : '100%',
        maxWidth: showLayoutSettings ? `calc(100% - ${layoutSettingsWidth}px)` : '100%'
      }"
    >
        <!-- Connection Lines SVG Overlay (统一处理所有连接) -->
        <svg
          v-if="crossChapterEdges.length > 0"
          class="absolute inset-0 pointer-events-none"
          style="z-index: 5; overflow: visible;"
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
            @mousemove="(e) => checkEdgeHover(e, edge)"
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
              :x="getEdgeLabelX(edge) - (edge.label ? 40 : 35)"
              :y="getEdgeLabelY(edge) - ((edge.label ? edge.label.split('\n').length : 1) * 16 + 12) / 2"
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
            @mousemove="(e) => checkEdgeHover(e, edge)"
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
              :x="getEdgeLabelX(edge) - (edge.label ? 40 : 35)"
              :y="getEdgeLabelY(edge) - ((edge.label ? edge.label.split('\n').length : 1) * 16 + 12) / 2"
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
        <div v-if="projectData.chapters && projectData.chapters.length > 0" class="w-[90%] mx-auto space-y-6 px-2">
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
            :color-scheme="colorScheme"
            :global-layout="globalLayout"
            :node-width="nodeWidth"
            :node-height="nodeHeight"
            :horizontal-spacing="horizontalSpacing"
            :vertical-spacing="verticalSpacing"
            :chapter-width="chapterWidth"
            :chapter-height="chapterHeight"
            :section-width="sectionWidth"
            :section-height="sectionHeight"
            :section-spacing="sectionSpacing"
            :node-alignment="nodeAlignment"
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
            @edit-item="handleEditItem"
            @section-reorder="handleSectionReorder"
            @chapter-reorder="handleChapterReorder"
            @section-position-updated="handleSectionPositionUpdated"
            @section-dragging="handleSectionDragging"
            @section-size-updated="handleSectionSizeUpdated"
            @chapter-layout-change="handleChapterLayoutChange"
            @chapter-updated="handleChapterUpdated"
            @section-updated="handleSectionUpdated"
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

    <!-- 连接模式状态（右下角浮动） -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-y-4"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-4"
    >
      <div
        v-if="linkMode.source"
        class="fixed bottom-6 right-6 bg-white border border-gray-200 rounded-lg shadow-xl z-40 px-4 py-3 min-w-[280px]"
        :style="{ right: showLayoutSettings ? `${layoutSettingsWidth + 20}px` : '24px' }"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2 text-sm font-semibold text-gray-700">
            <i class="ph ph-link text-blue-600"></i>
            <span>创建连接</span>
          </div>
          <button @click="resetLinkMode" class="text-gray-400 hover:text-gray-600 transition">
            <i class="ph ph-x text-lg"></i>
          </button>
        </div>
        <div class="flex items-center gap-2 text-xs mb-3">
          <span class="px-2 py-1 bg-blue-100 text-blue-700 rounded font-medium">{{ getNodeName(linkMode.source) }}</span>
          <i class="ph ph-arrow-right text-gray-400"></i>
          <span v-if="!linkMode.target" class="px-2 py-1 bg-gray-100 text-gray-500 rounded">选择终点...</span>
          <span v-else class="px-2 py-1 bg-green-100 text-green-700 rounded font-medium">{{ getNodeName(linkMode.target) }}</span>
        </div>
        <button 
          v-if="linkMode.target" 
          @click="createEdge" 
          class="w-full px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium flex items-center justify-center gap-2"
        >
          <i class="ph ph-check"></i>
          <span>确认连接</span>
        </button>
      </div>
    </transition>
    
    <!-- 点击外部关闭菜单 -->
    <div
      v-if="showDataMenu || showColorMenu"
      class="fixed inset-0 z-30"
      @click="showDataMenu = false; showColorMenu = false"
    ></div>

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
import { api } from './api.js'
import ProjectSidebar from './components/ProjectSidebar.vue'
import ChapterSection from './components/ChapterSection.vue'
import DAGPanel from './components/DAGPanel.vue'

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

const projects = ref([])
const currentProjectId = ref(null)
const projectData = reactive({ chapters: [], edges: [] })
const fileInput = ref(null)
// 颜色方案：'default' 或 'seaborn-set2'，从 localStorage 读取或使用默认值
const colorScheme = ref(localStorage.getItem('colorScheme') || 'seaborn-set2')

// 监听颜色方案变化，保存到 localStorage
watch(colorScheme, (newScheme) => {
  localStorage.setItem('colorScheme', newScheme)
})

// 全局布局设置
const showLayoutSettings = ref(true)
const showDataMenu = ref(false)
const showColorMenu = ref(false)
const layoutSettingsWidth = 360 // 页面设置侧边栏宽度（px）
const globalLayout = ref(localStorage.getItem('globalLayout') || 'row')
const nodeWidth = ref(Number(localStorage.getItem('nodeWidth')) || 300)
const nodeHeight = ref(Number(localStorage.getItem('nodeHeight')) || 70)
const horizontalSpacing = ref(Number(localStorage.getItem('horizontalSpacing')) || 100)
const verticalSpacing = ref(Number(localStorage.getItem('verticalSpacing')) || 20)
const chapterWidth = ref(localStorage.getItem('chapterWidth') ? Number(localStorage.getItem('chapterWidth')) : null)
const chapterHeight = ref(localStorage.getItem('chapterHeight') ? Number(localStorage.getItem('chapterHeight')) : null)
const sectionWidth = ref(localStorage.getItem('sectionWidth') ? Number(localStorage.getItem('sectionWidth')) : null)
const sectionHeight = ref(localStorage.getItem('sectionHeight') ? Number(localStorage.getItem('sectionHeight')) : null)
const sectionSpacing = ref(Number(localStorage.getItem('sectionSpacing')) || 12)
const nodeAlignment = ref(localStorage.getItem('nodeAlignment') || 'left')

// 折叠面板状态
const expandedSections = ref({
  editingItem: true, // 编辑项属性默认展开
  node: true,     // 节点设置默认展开
  section: true,  // 部分设置默认展开
  chapter: true  // 章节设置默认展开
})

// 选中状态管理
const editingItem = ref({
  type: null, // 'node' | 'chapter' | 'section'
  id: null,
  chapterId: null,
  sectionId: null
})

// 选中项的属性编辑
const selectedChapterName = ref('')
const selectedChapterLayout = ref('row')
const selectedChapterWidth = ref(null)
const selectedChapterHeight = ref(null)
const selectedChapterBorderColor = ref('#e5e7eb')
const selectedChapterFillColor = ref('#ffffff')
const selectedChapterAlign = ref('left')

const selectedSectionName = ref('')
const selectedSectionWidth = ref(null)
const selectedSectionHeight = ref(null)
const selectedSectionBorderColor = ref('#e5e7eb')
const selectedSectionFillColor = ref('#ffffff')
const selectedSectionAlign = ref('left')

const selectedNodeName = ref('')
const selectedNodeContent = ref('')
const selectedNodeBorderColor = ref('#e5e7eb')
const selectedNodeFillColor = ref('#ffffff')
const selectedNodeAlign = ref('left')

// 处理编辑项事件
const handleEditItem = (item) => {
  editingItem.value = { ...item }
  // 展开编辑面板
  expandedSections.editingItem = true
  
  // 根据类型加载对应的属性值
  if (item.type === 'chapter' && item.chapterId) {
    const chapter = projectData.value.chapters.find(ch => ch.id === item.chapterId)
    if (chapter) {
      selectedChapterName.value = chapter.name
      selectedChapterLayout.value = chapter.layout || 'row'
      selectedChapterWidth.value = chapterWidth.value
      selectedChapterHeight.value = chapterHeight.value
      selectedChapterBorderColor.value = chapter.borderColor || '#e5e7eb'
      selectedChapterFillColor.value = chapter.fillColor || '#ffffff'
      selectedChapterAlign.value = chapter.align || 'left'
    }
  } else if (item.type === 'section' && item.sectionId && item.chapterId) {
    const chapter = projectData.value.chapters.find(ch => ch.id === item.chapterId)
    const section = chapter?.sections.find(sec => sec.id === item.sectionId)
    if (section) {
      selectedSectionName.value = section.name
      selectedSectionWidth.value = sectionWidth.value
      selectedSectionHeight.value = sectionHeight.value
      selectedSectionBorderColor.value = section.borderColor || '#e5e7eb'
      selectedSectionFillColor.value = section.fillColor || '#ffffff'
      selectedSectionAlign.value = section.align || 'left'
    }
  } else if (item.type === 'node' && item.id) {
    // 查找节点
    for (const chapter of projectData.value.chapters) {
      for (const section of chapter.sections) {
        const node = section.nodes.find(n => n.id === item.id)
        if (node) {
          selectedNodeName.value = node.name
          selectedNodeContent.value = node.content || ''
          selectedNodeBorderColor.value = node.borderColor || '#e5e7eb'
          selectedNodeFillColor.value = node.fillColor || '#ffffff'
          selectedNodeAlign.value = node.align || 'left'
          break
        }
      }
    }
  }
}

// 更新章节名称
const updateChapterName = async () => {
  if (!editingItem.value.chapterId) return
  try {
    const { api } = await import('./api.js')
    await api.updateChapter(currentProjectId.value, editingItem.value.chapterId, {
      name: selectedChapterName.value
    })
    await loadProject()
  } catch (error) {
    console.error('Failed to update chapter name:', error)
  }
}

// 切换章节布局（循环：row -> column -> free -> row）
const toggleChapterLayout = async () => {
  if (!editingItem.value.chapterId) return
  
  // 确定下一个布局模式
  let nextLayout = 'row'
  if (selectedChapterLayout.value === 'row') {
    nextLayout = 'column'
  } else if (selectedChapterLayout.value === 'column') {
    nextLayout = 'free'
  } else if (selectedChapterLayout.value === 'free') {
    nextLayout = 'row'
  }
  
  selectedChapterLayout.value = nextLayout
  await updateChapterLayout()
}

// 更新章节布局
const updateChapterLayout = async () => {
  if (!editingItem.value.chapterId) return
  try {
    const { api } = await import('./api.js')
    await api.updateChapter(currentProjectId.value, editingItem.value.chapterId, {
      layout: selectedChapterLayout.value
    })
    await loadProject()
    triggerLayoutUpdate()
  } catch (error) {
    console.error('Failed to update chapter layout:', error)
  }
}

// 获取布局图标
const getChapterLayoutIcon = (layout) => {
  if (layout === 'row') return 'ph ph-rows'
  if (layout === 'column') return 'ph ph-columns'
  if (layout === 'free') return 'ph ph-arrows-out'
  return 'ph ph-rows'
}

// 获取布局文本
const getChapterLayoutText = (layout) => {
  if (layout === 'row') return '行排列'
  if (layout === 'column') return '列排列'
  if (layout === 'free') return '编辑模式'
  return '行排列'
}

// 更新部分名称
const updateSectionName = async () => {
  if (!editingItem.value.sectionId) return
  try {
    const { api } = await import('./api.js')
    await api.updateSection(currentProjectId.value, editingItem.value.sectionId, {
      name: selectedSectionName.value
    })
    await loadProject()
  } catch (error) {
    console.error('Failed to update section name:', error)
  }
}

// 更新节点名称和内容
const updateNodeName = async () => {
  if (!editingItem.value.id || !editingItem.value.sectionId) return
  try {
    const { api } = await import('./api.js')
    await api.updateNode(currentProjectId.value, editingItem.value.id, editingItem.value.sectionId, {
      name: selectedNodeName.value
    })
    await loadProject()
  } catch (error) {
    console.error('Failed to update node name:', error)
  }
}

const updateNodeContent = async () => {
  if (!editingItem.value.id || !editingItem.value.sectionId) return
  try {
    const { api } = await import('./api.js')
    await api.updateNode(currentProjectId.value, editingItem.value.id, editingItem.value.sectionId, {
      content: selectedNodeContent.value
    })
    await loadProject()
  } catch (error) {
    console.error('Failed to update node content:', error)
  }
}

// 更新章节边框颜色
const updateChapterBorderColor = () => {
  if (!editingItem.value.chapterId) return
  const chapter = projectData.value.chapters.find(ch => ch.id === editingItem.value.chapterId)
  if (chapter) {
    chapter.borderColor = selectedChapterBorderColor.value
    triggerLayoutUpdate()
  }
}

// 更新章节填充颜色
const updateChapterFillColor = () => {
  if (!editingItem.value.chapterId) return
  const chapter = projectData.value.chapters.find(ch => ch.id === editingItem.value.chapterId)
  if (chapter) {
    chapter.fillColor = selectedChapterFillColor.value
    triggerLayoutUpdate()
  }
}

// 更新章节对齐方式
const updateChapterAlign = () => {
  if (!editingItem.value.chapterId) return
  const chapter = projectData.value.chapters.find(ch => ch.id === editingItem.value.chapterId)
  if (chapter) {
    chapter.align = selectedChapterAlign.value
    triggerLayoutUpdate()
  }
}

// 更新部分边框颜色
const updateSectionBorderColor = () => {
  if (!editingItem.value.sectionId) return
  const chapter = projectData.value.chapters.find(ch => ch.id === editingItem.value.chapterId)
  const section = chapter?.sections.find(sec => sec.id === editingItem.value.sectionId)
  if (section) {
    section.borderColor = selectedSectionBorderColor.value
    triggerLayoutUpdate()
  }
}

// 更新部分填充颜色
const updateSectionFillColor = () => {
  if (!editingItem.value.sectionId) return
  const chapter = projectData.value.chapters.find(ch => ch.id === editingItem.value.chapterId)
  const section = chapter?.sections.find(sec => sec.id === editingItem.value.sectionId)
  if (section) {
    section.fillColor = selectedSectionFillColor.value
    triggerLayoutUpdate()
  }
}

// 更新部分对齐方式
const updateSectionAlign = () => {
  if (!editingItem.value.sectionId) return
  const chapter = projectData.value.chapters.find(ch => ch.id === editingItem.value.chapterId)
  const section = chapter?.sections.find(sec => sec.id === editingItem.value.sectionId)
  if (section) {
    section.align = selectedSectionAlign.value
    triggerLayoutUpdate()
  }
}

// 更新节点边框颜色
const updateNodeBorderColor = () => {
  if (!editingItem.value.id) return
  for (const chapter of projectData.value.chapters) {
    for (const section of chapter.sections) {
      const node = section.nodes.find(n => n.id === editingItem.value.id)
      if (node) {
        node.borderColor = selectedNodeBorderColor.value
        triggerLayoutUpdate()
        break
      }
    }
  }
}

// 更新节点填充颜色
const updateNodeFillColor = () => {
  if (!editingItem.value.id) return
  for (const chapter of projectData.value.chapters) {
    for (const section of chapter.sections) {
      const node = section.nodes.find(n => n.id === editingItem.value.id)
      if (node) {
        node.fillColor = selectedNodeFillColor.value
        triggerLayoutUpdate()
        break
      }
    }
  }
}

// 更新节点对齐方式
const updateNodeAlign = () => {
  if (!editingItem.value.id) return
  for (const chapter of projectData.value.chapters) {
    for (const section of chapter.sections) {
      const node = section.nodes.find(n => n.id === editingItem.value.id)
      if (node) {
        node.align = selectedNodeAlign.value
        triggerLayoutUpdate()
        break
      }
    }
  }
}

// 监听布局设置变化，保存到 localStorage
// 触发连接线和节点重绘的函数
// 全局连接线重绘函数（统一入口）
const redrawConnections = () => {
  // 清除所有缓存
  nodeLocationCache.clear()
  edgePathCache.clear()
  cachedCrossEdges = []
  cachedEdgesHash = ''
  edgeUpdateTrigger.value++
}

// 保持 triggerLayoutUpdate 作为别名，用于向后兼容（带延迟）
const triggerLayoutUpdate = () => {
  if (!currentProjectId.value) return
  nextTick(() => {
    setTimeout(() => {
      redrawConnections()
    }, 150) // 延迟150ms，确保节点位置已重新计算
  })
}

watch(globalLayout, (newLayout) => {
  localStorage.setItem('globalLayout', newLayout)
  triggerLayoutUpdate()
})

watch(nodeWidth, (newWidth) => {
  localStorage.setItem('nodeWidth', String(newWidth))
  triggerLayoutUpdate()
})

watch(nodeHeight, (newHeight) => {
  localStorage.setItem('nodeHeight', String(newHeight))
  triggerLayoutUpdate()
})

watch(horizontalSpacing, (newSpacing) => {
  localStorage.setItem('horizontalSpacing', String(newSpacing))
  triggerLayoutUpdate()
})

watch(verticalSpacing, (newSpacing) => {
  localStorage.setItem('verticalSpacing', String(newSpacing))
  triggerLayoutUpdate()
})

watch(chapterWidth, (newWidth) => {
  if (newWidth !== null) {
    localStorage.setItem('chapterWidth', String(newWidth))
  } else {
    localStorage.removeItem('chapterWidth')
  }
  triggerLayoutUpdate()
})

watch(chapterHeight, (newHeight) => {
  if (newHeight !== null) {
    localStorage.setItem('chapterHeight', String(newHeight))
  } else {
    localStorage.removeItem('chapterHeight')
  }
  triggerLayoutUpdate()
})

watch(sectionWidth, (newWidth) => {
  if (newWidth !== null) {
    localStorage.setItem('sectionWidth', String(newWidth))
  } else {
    localStorage.removeItem('sectionWidth')
  }
  triggerLayoutUpdate()
})

watch(sectionHeight, (newHeight) => {
  if (newHeight !== null) {
    localStorage.setItem('sectionHeight', String(newHeight))
  } else {
    localStorage.removeItem('sectionHeight')
  }
  triggerLayoutUpdate()
})

watch(sectionSpacing, (newSpacing) => {
  localStorage.setItem('sectionSpacing', String(newSpacing))
  triggerLayoutUpdate()
})

watch(nodeAlignment, (newAlignment) => {
  localStorage.setItem('nodeAlignment', newAlignment)
  triggerLayoutUpdate()
})

// 切换全局布局
const toggleGlobalLayout = () => {
  globalLayout.value = globalLayout.value === 'row' ? 'column' : 'row'
  // 全局布局切换时，触发所有章节的布局更新
  triggerLayoutUpdate()
}

// 重置布局设置
const resetLayoutSettings = () => {
  globalLayout.value = 'row'
  nodeWidth.value = 300
  nodeHeight.value = 70
  horizontalSpacing.value = 100
  verticalSpacing.value = 20
  chapterWidth.value = null
  chapterHeight.value = null
  sectionWidth.value = null
  sectionHeight.value = null
  sectionSpacing.value = 12
  nodeAlignment.value = 'left'
  // 重置后也会触发更新（通过 watch 自动触发）
}
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
    
    // 如果有项目但没有选中项目，自动选中最近更新的项目
    if (projects.value.length > 0 && !currentProjectId.value) {
      // 按 updated_at 倒序排序，最新的在前
      const sortedProjects = [...projects.value].sort((a, b) => {
        const dateA = a.updated_at ? new Date(a.updated_at).getTime() : 0
        const dateB = b.updated_at ? new Date(b.updated_at).getTime() : 0
        return dateB - dateA // 倒序：最新的在前
      })
      
      // 选择最近更新的项目
      currentProjectId.value = sortedProjects[0].id
      loadProject()
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
    
    // 清空所有缓存
    redrawConnections()
    
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
    
    // 等待 DOM 更新后触发连接线更新
    await nextTick()
    // 延迟触发，确保所有节点都已渲染完成
    setTimeout(() => {
      redrawConnections()
    }, 200)
  } catch (e) {
    console.error('Failed to load project:', e)
    ElMessage.error('加载项目失败: ' + (e.response?.data?.detail || e.message))
  }
}

const handleProjectSelected = (projectId) => {
  currentProjectId.value = projectId
  loadProject()
}

const exportProject = async () => {
  if (!currentProjectId.value) return
  
  try {
    const response = await api.exportProject(currentProjectId.value)
    
    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/x-yaml' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 从响应头获取文件名，或使用默认名称
    const contentDisposition = response.headers['content-disposition']
    let filename = 'project.yaml'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i)
      if (filenameMatch) {
        filename = filenameMatch[1]
      }
    }
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('项目导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败: ' + (error.response?.data?.detail || error.message))
  }
}

const triggerImport = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const handleFileImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 检查文件类型
  if (!file.name.endsWith('.yaml') && !file.name.endsWith('.yml')) {
    ElMessage.error('请选择 YAML 文件 (.yaml 或 .yml)')
    return
  }
  
  try {
    // 询问项目名称
    const { value: projectName } = await ElMessageBox.prompt(
      '请输入项目名称（留空使用 YAML 中的名称）',
      '导入项目',
      {
        confirmButtonText: '导入',
        cancelButtonText: '取消',
        inputPlaceholder: '项目名称'
      }
    ).catch(() => ({ value: null }))
    
    if (projectName === null) {
      // 用户取消
      event.target.value = '' // 重置文件选择
      return
    }
    
    // 上传文件
    const response = await api.importProject(file, projectName || undefined)
    
    ElMessage.success(`项目导入成功: ${response.data.project.name}`)
    
    // 刷新项目列表
    await fetchProjects()
    
    // 自动选择导入的项目
    if (response.data.project.id) {
      currentProjectId.value = response.data.project.id
      await loadProject()
    }
    
    // 重置文件选择
    event.target.value = ''
  } catch (error) {
    console.error('Import failed:', error)
    if (error !== 'cancel') {
      ElMessage.error('导入失败: ' + (error.response?.data?.detail || error.message))
    }
    // 重置文件选择
    event.target.value = ''
  }
}

const handleProjectCreated = (project) => {
  projects.value.push(project)
  currentProjectId.value = project.id
  loadProject()
}

const handleProjectUpdated = ({ id, name }) => {
  const project = projects.value.find(p => p.id === id)
  if (project) {
    project.name = name
  }
  // 如果当前项目被重命名，更新显示
  if (currentProjectId.value === id) {
    // 触发重新加载以更新 header 中的项目名称
    loadProject()
  }
}

const handleProjectDeleted = async (projectId) => {
  // 从列表中移除
  projects.value = projects.value.filter(p => p.id !== projectId)
  
  // 如果删除的是当前项目，选择其他项目或清空
  if (currentProjectId.value === projectId) {
    if (projects.value.length > 0) {
      currentProjectId.value = projects.value[0].id
      await loadProject()
    } else {
      currentProjectId.value = null
      projectData.chapters = []
      projectData.edges = []
    }
  }
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

const handleChapterUpdated = () => {
  loadProject()
  // 布局切换后，延迟触发连接线更新，确保节点位置已重新计算
  nextTick(() => {
    setTimeout(() => {
      redrawConnections()
    }, 200) // 延迟200ms，确保节点位置已重新计算
  })
}

const handleSectionUpdated = () => {
  loadProject()
  // 清除缓存并触发连接线更新
  nextTick(() => {
    setTimeout(() => {
      redrawConnections()
    }, 150)
  })
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


const handleSectionReorder = async (data) => {
  try {
    const { api } = await import('./api.js')
    await api.reorderSections(currentProjectId.value, data.chapterId, data.sectionIds)
    await loadProject()
  } catch (error) {
    console.error('Failed to reorder sections:', error)
  }
}

const handleChapterReorder = async (data) => {
  try {
    const { api } = await import('./api.js')
    await api.reorderChapters(currentProjectId.value, data.chapterIds)
    await loadProject()
  } catch (error) {
    console.error('Failed to reorder chapters:', error)
  }
}

const handleSectionPositionUpdated = async (data) => {
  // 触发连接线重绘
  redrawConnections()
  // 更新 section 位置和尺寸到后端
  try {
    // 更新本地数据
    const chapter = projectData.value.chapters.find(ch => ch.id === data.chapterId)
    if (chapter) {
      const section = chapter.sections.find(sec => sec.id === data.sectionId)
      if (section) {
        section.x = data.x
        section.y = data.y
        if (data.width) section.width = data.width
        if (data.height) section.height = data.height
      }
    }
    // TODO: 添加后端API来保存 section 的位置和尺寸
    // const { api } = await import('./api.js')
    // await api.updateSectionPosition(currentProjectId.value, data.sectionId, data)
    // 触发连线更新
    triggerLayoutUpdate()
  } catch (error) {
    console.error('Failed to update section position:', error)
  }
}

// 处理 section 拖拽过程中的连线更新
const handleSectionDragging = (data) => {
  // 更新本地数据
  const chapter = projectData.value.chapters.find(ch => ch.id === data.chapterId)
  if (chapter) {
    const section = chapter.sections.find(sec => sec.id === data.sectionId)
    if (section) {
      section.x = data.x
      section.y = data.y
    }
  }
  
  // 统一处理：触发连接线更新（与节点拖动类似）
  if (handleSectionDragging.rafId) {
    cancelAnimationFrame(handleSectionDragging.rafId)
  }
  
  handleSectionDragging.rafId = requestAnimationFrame(() => {
    redrawConnections()
    handleSectionDragging.rafId = null
  })
}

const handleSectionSizeUpdated = async (data) => {
  // 更新 section 尺寸到后端
  try {
    // 更新本地数据
    const chapter = projectData.value.chapters.find(ch => ch.id === data.chapterId)
    if (chapter) {
      const section = chapter.sections.find(sec => sec.id === data.sectionId)
      if (section) {
        section.width = data.width
        section.height = data.height
        if (data.x != null) section.x = data.x
        if (data.y != null) section.y = data.y
      }
    }
    // TODO: 添加后端API来保存 section 的尺寸
    // const { api } = await import('./api.js')
    // await api.updateSectionSize(currentProjectId.value, data.sectionId, data)
    
    // 触发连接线重绘
    redrawConnections()
  } catch (error) {
    console.error('Failed to update section size:', error)
  }
}

const handleChapterLayoutChange = async (data) => {
  // 切换章节布局为自由模式
  try {
    const { api } = await import('./api.js')
    await api.updateChapter(currentProjectId.value, data.chapterId, {
      layout: 'free'
    })
    await loadProject()
    triggerLayoutUpdate()
    
    // 触发连接线重绘
    redrawConnections()
  } catch (error) {
    console.error('Failed to change chapter layout:', error)
  }
}

const handleNodeClick = (nodeId, event) => {
  console.log('handleNodeClick called:', { nodeId, event, linkMode: { ...linkMode } })
  
  // 如果按住 Ctrl 或 Cmd
  if (event?.ctrlKey || event?.metaKey) {
    // Ctrl + 左键：处理连接逻辑
    // 阻止事件冒泡
    if (event) {
      event.stopPropagation()
      event.preventDefault() // 防止拖拽
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
    return
  }

  // 普通左键点击不做任何处理，让拖拽功能正常工作
  // 如果需要显示 DAG，可以使用其他快捷键或双击
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

// 边的路径缓存
let edgePathCache = new Map()
let edgePathUpdateTimer = null

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

// 检查鼠标是否在连接线的触发范围内
const checkEdgeHover = (event, edge) => {
  const svgElement = event.currentTarget.closest('svg')
  if (!svgElement) return
  
  const canvasContainerEl = canvasContainer.value
  if (!canvasContainerEl) return
  
  const svgRect = svgElement.getBoundingClientRect()
  
  // 获取鼠标在 SVG 坐标系中的位置
  const mouseX = event.clientX - svgRect.left
  const mouseY = event.clientY - svgRect.top
  
  // 获取连接线的路径
  const sourcePos = getNodeAbsolutePosition(edge.source)
  const targetPos = getNodeAbsolutePosition(edge.target)
  
  if (!sourcePos || !targetPos) return
  
  const sourceEdge = getNodeEdgePointCrossChapter(sourcePos, targetPos)
  const targetEdge = getNodeEdgePointCrossChapter(targetPos, sourcePos)
  
  if (!sourceEdge || !targetEdge) return
  
  const dx = targetEdge.x - sourceEdge.x
  const dy = targetEdge.y - sourceEdge.y
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  if (distance === 0) return
  
  const controlX = sourceEdge.x + dx / 2
  const curveAmount = Math.min(Math.abs(dx) * 0.4, distance * 0.35)
  const controlY = sourceEdge.y + dy / 2 - curveAmount
  
  // 计算点到二次贝塞尔曲线的距离
  // 对于二次贝塞尔曲线 Q(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
  // 使用采样法找到最近的点
  
  let minDistance = Infinity
  
  // 采样曲线上的点，找到距离鼠标最近的点
  for (let t = 0; t <= 1; t += 0.01) {
    const x = (1 - t) * (1 - t) * sourceEdge.x + 2 * (1 - t) * t * controlX + t * t * targetEdge.x
    const y = (1 - t) * (1 - t) * sourceEdge.y + 2 * (1 - t) * t * controlY + t * t * targetEdge.y
    
    const dist = Math.sqrt((mouseX - x) ** 2 + (mouseY - y) ** 2)
    if (dist < minDistance) {
      minDistance = dist
    }
  }
  
  // 触发范围：16px（与背景线的 stroke-width 一致）
  const hoverThreshold = 16
  
  // 如果鼠标在触发范围内，设置 hover 状态
  if (minDistance <= hoverThreshold) {
    hoveredCrossEdge.value = { source: edge.source, target: edge.target }
    } else {
    // 如果不在范围内，清除 hover 状态（但保留当前 hover 的，避免闪烁）
    if (hoveredCrossEdge.value && 
        hoveredCrossEdge.value.source === edge.source && 
        hoveredCrossEdge.value.target === edge.target) {
      hoveredCrossEdge.value = null
    }
  }
}

// 获取边标签的位置（基于连接线的边缘点，计算贝塞尔曲线上的中点）
const getEdgeLabelX = (edge) => {
  const sourcePos = getNodeAbsolutePosition(edge.source)
  const targetPos = getNodeAbsolutePosition(edge.target)
  
  if (!sourcePos || !targetPos) return 0
  
  // 获取源节点和目标节点的边缘点（与连接线计算保持一致）
  const sourceEdge = getNodeEdgePointCrossChapter(sourcePos, targetPos)
  const targetEdge = getNodeEdgePointCrossChapter(targetPos, sourcePos)
  
  if (!sourceEdge || !targetEdge) {
    // 如果无法获取边缘点，回退到节点中心
    return (sourcePos.x + targetPos.x) / 2
  }
  
  // 计算连接线的参数（与 calculateEdgePath 保持一致）
  const dx = targetEdge.x - sourceEdge.x
  const dy = targetEdge.y - sourceEdge.y
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  if (distance === 0) {
    return sourceEdge.x
  }
  
  // 计算控制点（与 calculateEdgePath 保持一致）
  const controlX = sourceEdge.x + dx / 2
  const curveAmount = Math.min(Math.abs(dx) * 0.4, distance * 0.35)
  const controlY = sourceEdge.y + dy / 2 - curveAmount
  
  // 计算贝塞尔曲线在 t=0.5 时的点（曲线中点）
  // 对于二次贝塞尔曲线 Q: P(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
  // 当 t=0.5 时: P(0.5) = 0.25P₀ + 0.5P₁ + 0.25P₂
  const t = 0.5
  const labelX = (1 - t) * (1 - t) * sourceEdge.x + 2 * (1 - t) * t * controlX + t * t * targetEdge.x
  
  return labelX
}

const getEdgeLabelY = (edge) => {
  const sourcePos = getNodeAbsolutePosition(edge.source)
  const targetPos = getNodeAbsolutePosition(edge.target)
  
  if (!sourcePos || !targetPos) return 0
  
  // 获取源节点和目标节点的边缘点（与连接线计算保持一致）
  const sourceEdge = getNodeEdgePointCrossChapter(sourcePos, targetPos)
  const targetEdge = getNodeEdgePointCrossChapter(targetPos, sourcePos)
  
  if (!sourceEdge || !targetEdge) {
    // 如果无法获取边缘点，回退到节点中心
    const dy = targetPos.y - sourcePos.y
    const dx = targetPos.x - sourcePos.x
    const distance = Math.sqrt(dx * dx + dy * dy)
    const curveAmount = Math.min(Math.abs(dx) * 0.4, distance * 0.35)
    return (sourcePos.y + targetPos.y) / 2 - curveAmount - 8
  }
  
  // 计算连接线的参数（与 calculateEdgePath 保持一致）
  const dx = targetEdge.x - sourceEdge.x
  const dy = targetEdge.y - sourceEdge.y
  const distance = Math.sqrt(dx * dx + dy * dy)
  
  if (distance === 0) {
    return sourceEdge.y
  }
  
  // 计算控制点（与 calculateEdgePath 保持一致）
  const controlX = sourceEdge.x + dx / 2
  const curveAmount = Math.min(Math.abs(dx) * 0.4, distance * 0.35)
  const controlY = sourceEdge.y + dy / 2 - curveAmount
  
  // 计算贝塞尔曲线在 t=0.5 时的点（曲线中点）
  // 对于二次贝塞尔曲线 Q: P(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
  // 当 t=0.5 时: P(0.5) = 0.25P₀ + 0.5P₁ + 0.25P₂
  const t = 0.5
  let labelY = (1 - t) * (1 - t) * sourceEdge.y + 2 * (1 - t) * t * controlY + t * t * targetEdge.y
  
  // 标签尺寸
  const labelHeight = 24
  const labelWidth = 80
  // 使用贝塞尔曲线中点计算 labelX，与 getEdgeLabelX 保持一致
  const labelX = getEdgeLabelX(edge)
  
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

// 处理节点拖拽事件
const handleNodeDragging = ({ nodeId, x, y }) => {
  // 统一处理：触发连接线更新（与 section 拖动类似）
  if (handleNodeDragging.rafId) {
    cancelAnimationFrame(handleNodeDragging.rafId)
  }
  
  handleNodeDragging.rafId = requestAnimationFrame(() => {
    redrawConnections()
    handleNodeDragging.rafId = null
  })
}

// 处理节点拖拽结束事件
const handleNodeDragEnd = ({ nodeId }) => {
  // 清理动画帧
  if (handleNodeDragging.rafId) {
    cancelAnimationFrame(handleNodeDragging.rafId)
    handleNodeDragging.rafId = null
  }
  
  // 立即更新连接线，不使用 requestAnimationFrame（与 section 拖拽结束保持一致，更快）
  redrawConnections()
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
    redrawConnections()
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
  redrawConnections()
})

// 使用 shallow watch 减少深度监听的开销，只监听长度变化
watch(() => projectData.chapters?.length, () => {
  nextTick(() => {
    if (canvasContainer.value) {
      debouncedUpdateCanvasSize()
    }
    // 清除缓存并触发连接线更新
    setTimeout(() => {
      redrawConnections()
    }, 150)
  })
})

watch(() => projectData.edges?.length, () => {
  // 当边数据更新时，重新计算画布尺寸
  nextTick(() => {
    if (canvasContainer.value) {
      debouncedUpdateCanvasSize()
    }
    // 清除缓存并触发连接线更新
    setTimeout(() => {
      redrawConnections()
    }, 150)
  })
})

// 深度监听章节数据变化，确保连接线及时更新
watch(() => projectData.chapters, () => {
  nextTick(() => {
    // 延迟触发，确保 DOM 已完全渲染
    setTimeout(() => {
      redrawConnections()
    }, 200)
  })
  }, { deep: true })
</script>

<style scoped>
/* 布局设置面板滚动条样式 */
.layout-settings-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.layout-settings-scrollbar::-webkit-scrollbar-track {
  background: #f8f9fa;
  border-radius: 4px;
}

.layout-settings-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 4px;
}

.layout-settings-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

/* Firefox 滚动条样式 */
.layout-settings-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #e2e8f0 #f8f9fa;
}

/* 滑块样式优化 */
.slider::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

.slider::-webkit-slider-thumb:active {
  transform: scale(0.95);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.slider::-moz-range-thumb:hover {
  background: #2563eb;
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}
</style>


