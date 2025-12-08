// frontend/src/composables/useGraphLinks.js
import { computed } from 'vue'
import { useProjectStore } from '../stores/projectStore'

export function useGraphLinks() {
  const store = useProjectStore()

  // 计算所有边的路径
  const svgEdges = computed(() => {
    if (!store.projectData.edges) return []

    return store.projectData.edges
      .map(edge => {
        // 兼容新旧数据格式
        const sourceId = edge.source || edge[0]
        const targetId = edge.target || edge[1]

        // 直接从 Store 获取坐标，不再查询 DOM
        const sourcePos = store.getNodeRelativePosition(sourceId)
        const targetPos = store.getNodeRelativePosition(targetId)

        if (!sourcePos || !targetPos) return null

        // 计算贝塞尔曲线
        const dx = targetPos.x - sourcePos.x
        const dy = targetPos.y - sourcePos.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance === 0) return null

        // 控制点计算：根据距离动态调整曲率，形成优雅的弧线
        const controlX = sourcePos.x + dx / 2
        const curveAmount = Math.min(Math.abs(dx) * 0.4, distance * 0.35) 
        const controlY = sourcePos.y + dy / 2 - curveAmount

        const path = `M ${sourcePos.x} ${sourcePos.y} Q ${controlX} ${controlY} ${targetPos.x} ${targetPos.y}`

        // 计算标签位置（曲线中点近似值 t=0.5）
        const t = 0.5
        const labelX = (1 - t) * (1 - t) * sourcePos.x + 2 * (1 - t) * t * controlX + t * t * targetPos.x
        const labelY = (1 - t) * (1 - t) * sourcePos.y + 2 * (1 - t) * t * controlY + t * t * targetPos.y

        return {
          id: `${sourceId}-${targetId}`,
          path,
          label: edge.label || '',
          source: sourceId,
          target: targetId,
          labelX,
          labelY
        }
      })
      .filter(Boolean)
  })

  return {
    svgEdges
  }
}