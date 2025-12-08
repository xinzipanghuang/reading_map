# 知识图谱架构说明

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        App.vue                               │
│  - 画布容器管理                                              │
│  - 使用 useElementBounding 监听画布位置和滚动              │
│  - 同步画布状态到 Store                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    projectStore.js                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ projectData: { chapters, edges }                      │  │
│  │ nodeLayoutMap: Map<nodeId, {x, y, w, h}>             │  │
│  │ canvasRect: { top, left }                            │  │
│  │ canvasScroll: { x, y }                               │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                              │
│  Actions:                                                    │
│  - loadProject(id)                                          │
│  - updateNodeLayout(nodeId, rect)                           │
│  - updateCanvasState(rect, scroll)                          │
│  - getNodeRelativePosition(nodeId)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                              │
        ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│ ChapterSection   │          │  useGraphLinks   │
│                  │          │                  │
│ registerNodeRef  │          │  svgEdges        │
│ (自动汇报位置)    │          │  (计算连线路径)   │
└──────────────────┘          └──────────────────┘
```

## 数据流

### 1. 节点位置汇报流程

```
ChapterSection.vue (节点渲染)
    │
    │ :ref="(el) => registerNodeRef(node.id, el, section.id)"
    │
    ▼
registerNodeRef()
    │
    │ useElementBounding(el)  // 自动监听元素位置变化
    │
    │ watch([top, left, width, height])
    │
    ▼
projectStore.updateNodeLayout(nodeId, {x, y, width, height})
    │
    ▼
nodeLayoutMap.set(nodeId, {x, y, w, h})  // 存储视口绝对坐标
```

**关键点：**
- 使用 `useElementBounding` 自动监听，无需手动触发
- 位置变化时自动更新到 Store
- 存储的是**视口绝对坐标**（getBoundingClientRect）

### 2. 画布状态同步流程

```
App.vue (画布容器)
    │
    │ ref="canvasContainer"
    │ @scroll="handleScroll"
    │
    ▼
useElementBounding(canvasContainer)
    │
    │ watch([top, left, width, height])
    │
    ▼
handleScroll()
    │
    │ projectStore.updateCanvasState(rect, scroll)
    │
    ▼
canvasRect = { top, left }
canvasScroll = { x, y }
```

**关键点：**
- 滚动时自动更新画布状态
- 用于计算节点的相对坐标

### 3. 连线计算流程

```
useGraphLinks.js
    │
    │ computed(() => {
    │   store.projectData.edges.map(edge => {
    │     const sourcePos = store.getNodeRelativePosition(sourceId)
    │     const targetPos = store.getNodeRelativePosition(targetId)
    │     // 计算贝塞尔曲线路径
    │   })
    │ })
    │
    ▼
getNodeRelativePosition(nodeId)
    │
    │ layout = nodeLayoutMap.get(nodeId)  // 视口绝对坐标
    │
    │ 计算公式：
    │ x = layout.x - canvasRect.left + canvasScroll.x + layout.w / 2
    │ y = layout.y - canvasRect.top + canvasScroll.y + layout.h / 2
    │
    ▼
返回画布内相对坐标（用于 SVG 绘制）
```

**关键点：**
- 从 Store 直接读取，不查询 DOM
- 自动响应式更新（computed）
- 坐标转换：视口绝对坐标 → 画布相对坐标

## 核心优化

### 1. 自动位置汇报
- **之前**：需要手动触发 `redrawConnections()`，在拖拽、滚动等事件中调用
- **现在**：使用 `useElementBounding` 自动监听，位置变化时自动更新

### 2. 响应式连线计算
- **之前**：需要手动查询 DOM 获取节点位置
- **现在**：从 Store 的 `nodeLayoutMap` 直接读取，computed 自动响应

### 3. 性能优化
- 防抖：位置变化超过 1px 才更新（避免浮点数抖动）
- 缓存：节点位置缓存在 Map 中，避免重复计算
- 自动清理：VueUse 的 watch 在组件卸载时自动清理

## 文件职责

### `projectStore.js`
- **职责**：全局状态管理
- **存储**：
  - `projectData`: 项目数据（章节、边）
  - `nodeLayoutMap`: 节点位置缓存
  - `canvasRect/canvasScroll`: 画布状态
- **方法**：
  - `loadProject()`: 加载项目
  - `updateNodeLayout()`: 更新节点位置
  - `updateCanvasState()`: 更新画布状态
  - `getNodeRelativePosition()`: 获取节点相对坐标

### `useGraphLinks.js`
- **职责**：连线计算
- **输入**：`store.projectData.edges` + `store.nodeLayoutMap`
- **输出**：`svgEdges` (computed)
- **计算**：贝塞尔曲线路径、标签位置

### `ChapterSection.vue`
- **职责**：节点渲染和位置汇报
- **关键函数**：
  - `registerNodeRef()`: 注册节点，自动汇报位置
  - 使用 `useElementBounding` 监听位置变化

### `App.vue`
- **职责**：画布管理和状态同步
- **关键函数**：
  - `handleScroll()`: 滚动时更新画布状态
  - 使用 `useElementBounding` 监听画布容器

## 坐标系统

### 视口绝对坐标（getBoundingClientRect）
- 存储在 `nodeLayoutMap` 中
- 相对于浏览器视口的坐标
- 用于计算相对坐标

### 画布相对坐标（SVG 坐标）
- 通过 `getNodeRelativePosition()` 计算
- 相对于 SVG 原点 (0,0) 的坐标
- 用于绘制连线

### 转换公式
```javascript
relativeX = absoluteX - canvasRect.left + canvasScroll.x + width / 2
relativeY = absoluteY - canvasRect.top + canvasScroll.y + height / 2
```

## 响应式更新链

```
节点位置变化
    │
    ▼
useElementBounding 检测到变化
    │
    ▼
projectStore.updateNodeLayout()
    │
    ▼
nodeLayoutMap 更新
    │
    ▼
useGraphLinks 的 computed 自动重新计算
    │
    ▼
svgEdges 更新
    │
    ▼
SVG 连线自动重绘
```

**无需手动触发任何更新！**

## 注意事项

1. **节点位置汇报**
   - 必须在 `registerNodeRef` 中正确绑定 ref
   - 确保传递 `sectionId` 以保持兼容性

2. **画布状态同步**
   - 必须在 `handleScroll` 中调用 `updateCanvasState`
   - 确保 `useElementBounding` 正确监听容器

3. **坐标转换**
   - 节点位置是视口绝对坐标
   - 连线需要画布相对坐标
   - 通过 `getNodeRelativePosition` 转换

4. **性能考虑**
   - 防抖机制避免频繁更新
   - 使用 Map 缓存提高查找效率
   - computed 自动缓存计算结果

