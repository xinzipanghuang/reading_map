# 知识图谱系统 - 逻辑总结

## 📋 核心逻辑概览

### 一句话总结
**节点位置自动汇报 → Store 缓存 → 响应式计算连线 → 自动渲染**

---

## 🔑 关键代码位置

### 1. 节点位置汇报
**文件**: `frontend/src/components/ChapterSection.vue`

**关键函数**: `registerNodeRef()`
```javascript
// 行 2347-2372
const registerNodeRef = (nodeId, el, sectionId) => {
  const { top, left, width, height } = useElementBounding(el)
  watch([top, left, width, height], () => {
    projectStore.updateNodeLayout(nodeId, {
      x: left.value,
      y: top.value,
      width: width.value,
      height: height.value
    })
  })
}
```

**模板绑定**: 行 201
```vue
:ref="(el) => registerNodeRef(node.id, el, section.id)"
```

---

### 2. 画布状态同步
**文件**: `frontend/src/App.vue`

**关键函数**: `handleScroll()`
```javascript
// 行 2981-2995 (大约)
const handleScroll = () => {
  if (!canvasContainer.value) return
  projectStore.updateCanvasState(
    { top: top.value, left: left.value },
    { x: canvasContainer.value.scrollLeft, y: canvasContainer.value.scrollTop }
  )
  canvasSize.value = {
    w: Math.max(canvasContainer.value.scrollWidth, width.value),
    h: Math.max(canvasContainer.value.scrollHeight, height.value)
  }
}
```

**监听设置**: 
```javascript
const { top, left, width, height } = useElementBounding(canvasContainer)
watch([top, left, width, height], handleScroll)
```

---

### 3. 数据存储
**文件**: `frontend/src/stores/projectStore.js`

**核心状态**:
```javascript
// 行 8-17
const currentProjectId = ref(null)
const projectData = ref({ chapters: [], edges: [] })
const nodeLayoutMap = reactive(new Map())  // 节点位置缓存
const canvasRect = ref({ top: 0, left: 0 })  // 画布位置
const canvasScroll = ref({ x: 0, y: 0 })    // 画布滚动
```

**关键方法**:
- `updateNodeLayout(nodeId, rect)` - 更新节点位置 (行 35-52)
- `updateCanvasState(rect, scroll)` - 更新画布状态 (行 55-58)
- `getNodeRelativePosition(nodeId)` - 获取节点相对坐标 (行 61-73)

---

### 4. 连线计算
**文件**: `frontend/src/composables/useGraphLinks.js`

**核心计算**:
```javascript
// 行 9-54
const svgEdges = computed(() => {
  return store.projectData.edges.map(edge => {
    const sourcePos = store.getNodeRelativePosition(sourceId)
    const targetPos = store.getNodeRelativePosition(targetId)
    // 计算贝塞尔曲线路径
    const path = `M ${sourcePos.x} ${sourcePos.y} Q ${controlX} ${controlY} ${targetPos.x} ${targetPos.y}`
    return { id, path, label, labelX, labelY }
  })
})
```

---

## 🔄 数据流

```
1. 节点渲染 (ChapterSection.vue)
   ↓
2. registerNodeRef 注册节点
   ↓
3. useElementBounding 监听位置变化
   ↓
4. projectStore.updateNodeLayout() 更新位置
   ↓
5. nodeLayoutMap 存储位置数据
   ↓
6. useGraphLinks 的 computed 自动重新计算
   ↓
7. svgEdges 更新
   ↓
8. SVG 自动重绘
```

---

## 📊 坐标系统

### 视口绝对坐标 (存储在 nodeLayoutMap)
- 来源: `getBoundingClientRect()`
- 相对于: 浏览器视口
- 用途: 计算相对坐标

### 画布相对坐标 (用于 SVG)
- 来源: `getNodeRelativePosition()` 计算
- 相对于: SVG 原点 (0, 0)
- 用途: 绘制连线

### 转换公式
```javascript
relativeX = absoluteX - canvasRect.left + canvasScroll.x + width / 2
relativeY = absoluteY - canvasRect.top + canvasScroll.y + height / 2
```

---

## ⚡ 性能优化

1. **防抖机制**
   - 位置变化超过 1px 才更新 (projectStore.js 行 38-43)
   - 避免浮点数抖动

2. **缓存策略**
   - 节点位置缓存在 Map 中
   - 避免重复查询 DOM

3. **响应式计算**
   - 使用 computed 自动缓存
   - 只有依赖变化时才重新计算

4. **自动清理**
   - VueUse 的 watch 自动管理生命周期
   - 组件卸载时自动清理

---

## 🎯 关键设计决策

### ✅ 为什么使用 useElementBounding？
- 自动监听位置变化
- 使用 ResizeObserver + requestAnimationFrame
- 性能优于手动监听

### ✅ 为什么位置存储在 Store？
- 连线计算需要访问所有节点位置
- 避免跨组件查询 DOM
- 响应式更新更高效

### ✅ 为什么使用 computed？
- 自动响应依赖变化
- 自动缓存计算结果
- 无需手动触发更新

---

## 🐛 调试技巧

### 查看节点位置
```javascript
// 浏览器控制台
projectStore.nodeLayoutMap
```

### 查看画布状态
```javascript
projectStore.canvasRect
projectStore.canvasScroll
```

### 查看连线数据
```javascript
// 在 useGraphLinks 中
console.log(svgEdges.value)
```

### 检查位置更新
在 `registerNodeRef` 中添加日志：
```javascript
watch([top, left, width, height], () => {
  console.log('Node position updated:', nodeId, { x: left.value, y: top.value })
  projectStore.updateNodeLayout(nodeId, {...})
})
```

---

## 📝 注意事项

1. **节点 ref 绑定**
   - 必须使用 `registerNodeRef` 绑定
   - 必须传递 `sectionId` 保持兼容性

2. **画布滚动监听**
   - 必须在 `handleScroll` 中更新状态
   - 确保 `useElementBounding` 正确监听

3. **坐标转换**
   - 节点位置是视口绝对坐标
   - 连线需要画布相对坐标
   - 必须通过 `getNodeRelativePosition` 转换

4. **响应式更新**
   - 所有更新都是自动的
   - 无需手动调用 `redrawConnections()`

---

## 🔗 相关文件

- `frontend/src/stores/projectStore.js` - 数据存储
- `frontend/src/composables/useGraphLinks.js` - 连线计算
- `frontend/src/components/ChapterSection.vue` - 节点渲染
- `frontend/src/App.vue` - 画布管理

---

## 📚 更多文档

- `ARCHITECTURE.md` - 详细架构说明
- `LOGIC_FLOW.md` - 逻辑流程图

