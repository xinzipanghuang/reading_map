<template>
  <div
    :class="[
      'p-2 rounded-lg border-2 bg-white shadow-sm flex items-center space-x-2 min-w-[180px] cursor-pointer transition-all duration-200',
      props.class || (isSelected ? 'ring-2 ring-blue-400 border-blue-500 bg-blue-50' : cardColor),
      !props.class && !isSelected ? 'hover:shadow-md' : ''
    ]"
    @click="handleClick"
    @dblclick="handleDoubleClick"
  >
    <div :class="['p-1.5 rounded-full', iconBgColor]">
      <i :class="[iconClass, iconColor]"></i>
    </div>
    <div class="flex-1 min-w-0">
      <div class="font-bold text-gray-800 text-sm truncate">{{ title }}</div>
      <div v-if="subtitle" class="text-xs text-gray-500 truncate">{{ subtitle }}</div>
    </div>
    <div v-if="showActions" class="flex gap-1">
      <button
        @click.stop="handleEdit"
        class="p-1 text-gray-400 hover:text-blue-600 transition"
        title="编辑"
      >
        <i class="ph ph-pencil text-xs"></i>
      </button>
      <button
        @click.stop="handleDelete"
        class="p-1 text-gray-400 hover:text-red-600 transition"
        title="删除"
      >
        <i class="ph ph-trash text-xs"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: 'blue'
  },
  icon: {
    type: String,
    default: 'ph-book-open'
  },
  isSelected: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click', 'dblclick', 'edit', 'delete'])

const colorMap = {
  blue: {
    border: 'border-blue-200',
    bg: 'bg-blue-100',
    text: 'text-blue-600'
  },
  orange: {
    border: 'border-orange-200',
    bg: 'bg-orange-100',
    text: 'text-orange-600'
  },
  green: {
    border: 'border-green-200',
    bg: 'bg-green-100',
    text: 'text-green-600'
  },
  purple: {
    border: 'border-purple-200',
    bg: 'bg-purple-100',
    text: 'text-purple-600'
  },
  indigo: {
    border: 'border-indigo-200',
    bg: 'bg-indigo-100',
    text: 'text-indigo-600'
  }
}

const colorConfig = colorMap[props.color] || colorMap.blue
const cardColor = colorConfig.border
const iconBgColor = colorConfig.bg + ' bg-opacity-20'
const iconColor = colorConfig.text
const iconClass = props.icon

const handleClick = (event) => {
  emit('click', event)
}

const handleDoubleClick = (event) => {
  emit('dblclick', event)
}

const handleEdit = () => {
  emit('edit')
}

const handleDelete = () => {
  // 直接 emit 事件，由父组件处理确认和删除
  emit('delete')
}
</script>

