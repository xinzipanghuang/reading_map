<template>
  <svg
    v-if="edges.length > 0"
    class="absolute inset-0 pointer-events-none z-0"
    style="overflow: visible;"
  >
    <defs>
      <marker
        id="arrowhead-connection"
        markerWidth="10"
        markerHeight="10"
        refX="9"
        refY="3"
        orient="auto"
      >
        <polygon points="0 0, 10 3, 0 6" fill="#94a3b8" />
      </marker>
    </defs>
    <line
      v-for="edge in edges"
      :key="`${edge.source}-${edge.target}`"
      :x1="edge.x1"
      :y1="edge.y1"
      :x2="edge.x2"
      :y2="edge.y2"
      stroke="#94a3b8"
      stroke-width="2"
      stroke-dasharray="4 4"
      marker-end="url(#arrowhead-connection)"
      class="opacity-60"
    />
  </svg>
</template>

<script setup>
defineProps({
  edges: {
    type: Array,
    default: () => []
  }
})
</script>

