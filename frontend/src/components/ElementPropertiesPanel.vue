<template>
  <div
    v-if="element"
    class="h-full flex flex-col bg-white border-l border-gray-200 w-80 shadow-xl z-50 transition-all duration-300"
  >
    <div class="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
      <h3 class="font-semibold text-gray-700 flex items-center gap-2">
        <i class="ph" :class="iconClass"></i>
        {{ title }}属性
      </h3>
      <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
        <i class="ph ph-x text-lg"></i>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-6">
      <div class="space-y-3">
        <label class="text-xs font-bold text-gray-500 uppercase">基础信息</label>

        <div class="space-y-1">
          <label class="text-sm text-gray-600">名称</label>
          <input
            v-model="element.name"
            class="w-full px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="输入名称"
          />
        </div>

        <div v-if="type === 'node'" class="space-y-1">
          <label class="text-sm text-gray-600">内容备注</label>
          <textarea
            v-model="element.content"
            rows="4"
            class="w-full px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"
            placeholder="输入详细内容..."
          ></textarea>
        </div>
      </div>

      <hr class="border-gray-100" />

      <div class="space-y-3">
        <label class="text-xs font-bold text-gray-500 uppercase">尺寸与布局</label>

        <div class="grid grid-cols-2 gap-3">
          <div v-if="type !== 'chapter'" class="space-y-1">
            <label class="text-sm text-gray-600">宽度 (px)</label>
            <input
              v-model.number="element.width"
              type="number"
              class="w-full px-3 py-2 border rounded-md text-sm outline-none"
              placeholder="自动"
            />
          </div>

          <div class="space-y-1">
            <label class="text-sm text-gray-600">高度 (px)</label>
            <input
              v-model.number="element.height"
              type="number"
              class="w-full px-3 py-2 border rounded-md text-sm outline-none"
              placeholder="自动"
            />
          </div>

          <div class="col-span-2 grid grid-cols-2 gap-3" v-if="element.x != null">
            <div class="space-y-1">
              <label class="text-sm text-gray-600">X 坐标</label>
              <input
                v-model.number="element.x"
                type="number"
                class="w-full px-3 py-2 border rounded-md text-sm bg-gray-50"
              />
            </div>
            <div class="space-y-1">
              <label class="text-sm text-gray-600">Y 坐标</label>
              <input
                v-model.number="element.y"
                type="number"
                class="w-full px-3 py-2 border rounded-md text-sm bg-gray-50"
              />
            </div>
          </div>
        </div>
      </div>

      <hr class="border-gray-100" />

      <div class="space-y-3">
        <label class="text-xs font-bold text-gray-500 uppercase">外观样式</label>

        <div class="flex items-center justify-between">
          <label class="text-sm text-gray-600">边框颜色</label>
          <div class="flex items-center gap-2">
            <input
              v-model="element.borderColor"
              type="color"
              class="h-8 w-14 cursor-pointer rounded overflow-hidden border-0 p-0"
            />
            <span class="text-xs text-gray-400 font-mono">{{ element.borderColor || '默认' }}</span>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <label class="text-sm text-gray-600">背景颜色</label>
          <div class="flex items-center gap-2">
            <input
              v-model="element.backgroundColor"
              type="color"
              class="h-8 w-14 cursor-pointer rounded overflow-hidden border-0 p-0"
            />
            <span class="text-xs text-gray-400 font-mono">{{ element.backgroundColor || '默认' }}</span>
          </div>
        </div>

        <button @click="resetColors" class="text-xs text-blue-500 hover:underline w-full text-right mt-1">
          重置为默认主题色
        </button>
      </div>
    </div>

    <div class="p-4 border-t border-gray-200 bg-gray-50 text-right">
      <span class="text-xs text-gray-400">修改即时生效</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  element: {
    type: Object,
    default: null
  },
  type: {
    type: String,
    default: ''
  }
})

defineEmits(['close', 'update'])

const title = computed(() => {
  switch (props.type) {
    case 'chapter':
      return '章节'
    case 'section':
      return '部分'
    case 'node':
      return '知识点'
    default:
      return '元素'
  }
})

const iconClass = computed(() => {
  switch (props.type) {
    case 'chapter':
      return 'ph-book-bookmark'
    case 'section':
      return 'ph-columns'
    case 'node':
      return 'ph-lightbulb'
    default:
      return 'ph-pencil'
  }
})

const resetColors = () => {
  if (props.element) {
    props.element.borderColor = null
    props.element.backgroundColor = null
  }
}
</script>

