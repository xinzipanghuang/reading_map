<template>
  <div class="relative">
    <!-- Connection Lines for edges -->
    <svg
      v-if="edges.length > 0"
      class="absolute inset-0 pointer-events-none z-0"
      style="overflow: visible;"
    >
      <line
        v-for="edge in visibleEdges"
        :key="`${edge[0]}-${edge[1]}`"
        :x1="getNodeX(edge[0])"
        :y1="getNodeY(edge[0])"
        :x2="getNodeX(edge[1])"
        :y2="getNodeY(edge[1])"
        stroke="#94a3b8"
        stroke-width="2"
        stroke-dasharray="4 4"
        marker-end="url(#arrowhead)"
      />
    </svg>
    <defs>
      <marker
        id="arrowhead"
        markerWidth="10"
        markerHeight="10"
        refX="9"
        refY="3"
        orient="auto"
      >
        <polygon points="0 0, 10 3, 0 6" fill="#94a3b8" />
      </marker>
    </defs>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  edges: {
    type: Array,
    default: () => []
  },
  nodes: {
    type: Array,
    default: () => []
  }
})

const visibleEdges = computed(() => {
  return props.edges.filter(edge => {
    const sourceNode = props.nodes.find(n => n.id === edge[0])
    const targetNode = props.nodes.find(n => n.id === edge[1])
    return sourceNode && targetNode
  })
})

const getNodeX = (nodeId) => {
  // 这里需要根据实际布局计算，暂时返回固定值
  // 实际应该通过 ref 获取节点位置
  return 100
}

const getNodeY = (nodeId) => {
  return 100
}
</script>

