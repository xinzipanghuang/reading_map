<template>
  <div
    :class="[
      'p-2 rounded-lg border-2 bg-white shadow-sm flex items-start space-x-2 min-w-[180px] max-w-[300px] cursor-pointer transition-shadow duration-200',
      props.class || (isSelected ? 'ring-2 ring-blue-400 border-blue-500 bg-blue-50' : (hasCustomColors ? '' : cardColor)),
      !props.class && !isSelected ? 'hover:shadow-lg' : ''
    ]"
    :style="cardStyle"
    @click="handleClick"
    @dblclick="handleDoubleClick"
  >
    <div :class="['p-1.5 rounded-full flex-shrink-0', iconBgColor]">
      <i :class="[iconClass, iconColor]"></i>
    </div>
    <div class="flex-1 min-w-0">
      <div 
        class="font-bold text-sm break-words"
        :class="textColorClass || (textColor ? '' : 'text-gray-800')"
        :style="textColor && !textColorClass ? { color: textColor } : undefined"
      >{{ title }}</div>
      <div 
        v-if="subtitle" 
        class="text-xs break-words mt-1"
        :class="textColorClass ? (textColorClass.includes('800') ? textColorClass.replace('800', '600') : textColorClass.replace(/\d+$/, '500')) : (textColor ? '' : 'text-gray-500')"
        :style="textColor && !textColorClass ? { color: textColor, opacity: 0.7 } : undefined"
      >{{ subtitle }}</div>
    </div>
    <div v-if="showActions" class="flex gap-1">
      <button
        @click.stop="handleDelete"
        @mousedown.stop
        class="p-1 text-gray-400 hover:text-red-600 transition"
        title="删除"
      >
        <i class="ph ph-trash text-xs"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

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
  },
  textColor: {
    type: String,
    default: null // 如果提供，使用提供的颜色（十六进制）；否则使用默认的 text-gray-800
  },
  textColorClass: {
    type: String,
    default: null // 如果提供，使用提供的 Tailwind 类名（如 text-blue-800）
  },
  borderColor: {
    type: String,
    default: null
  },
  backgroundColor: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['click', 'dblclick', 'delete'])

const hasCustomColors = computed(() => !!props.borderColor || !!props.backgroundColor)

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
const cardStyle = computed(() => ({
  borderColor: props.borderColor || undefined,
  backgroundColor: props.backgroundColor || undefined,
  borderStyle: props.borderColor ? 'solid' : undefined,
  borderWidth: props.borderColor ? '2px' : undefined
}))

const handleClick = (event) => {
  emit('click', event)
}

const handleDoubleClick = (event) => {
  emit('dblclick', event)
}

const handleDelete = () => {
  // 直接 emit 事件，由父组件处理确认和删除
  emit('delete')
}
</script>

