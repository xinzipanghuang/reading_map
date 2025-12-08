# 知识图谱逻辑流程

## 快速概览

### 核心流程

```
1. 节点渲染 → 2. 位置汇报 → 3. 连线计算 → 4. SVG 绘制
```

## 详细流程

### 阶段 1: 节点渲染和位置汇报

**位置**: `ChapterSection.vue`

```javascript
// 模板中
<div :ref="(el) => registerNodeRef(node.id, el, section.id)">

// 脚本中
const registerNodeRef = (nodeId, el, sectionId) => {
  // 1. 使用 VueUse 监听元素位置
  const { top, left, width, height } = useElementBounding(el)
  
  // 2. 位置变化时自动更新 Store
  watch([top, left, width, height], () => {
    projectStore.updateNodeLayout(nodeId, {
      x: left.value,    // 视口绝对坐标
      y: top.value,
      width: width.value,
      height: height.value
    })
  })
}
```

**结果**: 节点位置自动存储到 `projectStore.nodeLayoutMap`

---

### 阶段 2: 画布状态同步

**位置**: `App.vue`

```javascript
// 1. 监听画布容器
const { top, left, width, height } = useElementBounding(canvasContainer)

// 2. 滚动时更新状态
const handleScroll = () => {
  projectStore.updateCanvasState(
    { top: top.value, left: left.value },
    { x: canvasContainer.value.scrollLeft, y: canvasContainer.value.scrollTop }
  )
}

// 3. 自动监听变化
watch([top, left, width, height], handleScroll)
```

**结果**: 画布位置和滚动状态存储到 `projectStore.canvasRect` 和 `projectStore.canvasScroll`

---

### 阶段 3: 连线计算

**位置**: `useGraphLinks.js`

```javascript
const svgEdges = computed(() => {
  return store.projectData.edges.map(edge => {
    // 1. 从 Store 获取节点相对坐标
    const sourcePos = store.getNodeRelativePosition(sourceId)
    const targetPos = store.getNodeRelativePosition(targetId)
    
    // 2. 计算贝塞尔曲线路径
    const path = `M ${sourcePos.x} ${sourcePos.y} Q ${controlX} ${controlY} ${targetPos.x} ${targetPos.y}`
    
    // 3. 返回 SVG 数据
    return { id, path, label, labelX, labelY }
  })
})
```

**坐标转换** (在 `projectStore.getNodeRelativePosition` 中):

```javascript
// 输入: 视口绝对坐标 (nodeLayoutMap)
// 输出: 画布相对坐标 (SVG 坐标)

x = layout.x - canvasRect.left + canvasScroll.x + layout.w / 2
y = layout.y - canvasRect.top + canvasScroll.y + layout.h / 2
```

**结果**: 自动计算所有连线的 SVG 路径

---

### 阶段 4: SVG 渲染

**位置**: `App.vue` 模板

```vue
<svg v-if="projectStore.projectData.edges.length > 0">
  <g v-for="edge in svgEdges" :key="edge.id">
    <path :d="edge.path" />
    <foreignObject v-if="edge.label">
      <div>{{ edge.label }}</div>
    </foreignObject>
  </g>
</svg>
```

**结果**: 连线自动显示在画布上

---

## 数据流图

```
┌─────────────────────────────────────────────────────────┐
│                   用户操作                                │
│  - 拖拽节点                                              │
│  - 滚动画布                                              │
│  - 添加/删除节点                                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            ChapterSection.vue                            │
│  registerNodeRef()                                       │
│    ↓                                                      │
│  useElementBounding 检测位置变化                          │
│    ↓                                                      │
│  projectStore.updateNodeLayout()                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            projectStore.js                               │
│  nodeLayoutMap.set(nodeId, {x, y, w, h})                │
│  canvasRect = { top, left }                              │
│  canvasScroll = { x, y }                                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            useGraphLinks.js                              │
│  computed(() => {                                        │
│    store.getNodeRelativePosition(nodeId)                 │
│      ↓                                                    │
│    计算贝塞尔曲线路径                                      │
│      ↓                                                    │
│    return svgEdges                                       │
│  })                                                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            App.vue (模板)                                │
│  <svg>                                                   │
│    <path :d="edge.path" />                               │
│  </svg>                                                  │
└─────────────────────────────────────────────────────────┘
```

## 关键优化点

### ✅ 自动响应式更新
- 节点位置变化 → 自动更新 Store → 自动重新计算连线 → 自动重绘
- **无需手动调用任何更新函数**

### ✅ 性能优化
- 防抖：位置变化超过 1px 才更新
- 缓存：节点位置缓存在 Map 中
- 自动清理：VueUse 自动管理生命周期

### ✅ 解耦设计
- Store 负责数据管理
- Composable 负责计算逻辑
- 组件负责渲染和汇报

## 常见问题

### Q: 为什么节点位置需要转换？
A: 节点位置是视口绝对坐标（相对于浏览器窗口），但 SVG 需要画布相对坐标（相对于 SVG 原点）。需要加上滚动偏移和容器位置。

### Q: 为什么不需要手动触发更新？
A: 使用 `useElementBounding` 和 `computed`，所有更新都是响应式的。位置变化会自动触发连线重新计算。

### Q: 拖拽时连线会实时更新吗？
A: 会的。`useElementBounding` 在拖拽过程中会持续监听位置变化，自动更新到 Store，连线会自动重新计算。

### Q: 如何调试节点位置？
A: 可以在 `projectStore.nodeLayoutMap` 中查看所有节点的位置数据，或者在浏览器控制台查看 `projectStore`。

