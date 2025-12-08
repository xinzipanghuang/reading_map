# 全局布局控制实现进度

## 已完成

### 1. UI 界面（App.vue）
- ✅ 在布局设置面板顶部添加"全局布局控制"模块
- ✅ 添加 Chapter 排列方式控制（行/列/自由）
- ✅ 添加节点排列方式控制（横向/纵向/自动换行）
- ✅ 添加状态管理：`globalChapterLayout` 和 `globalNodeLayout`
- ✅ 添加 localStorage 持久化
- ✅ 添加 watch 监听布局变化

### 2. Props 传递（App.vue → ChapterSection.vue）
- ✅ 添加 `:global-chapter-layout` prop
- ✅ 添加 `:global-node-layout` prop

### 3. ChapterSection.vue 修改
- ✅ 删除章节头部的布局切换按钮
- ✅ 删除 `toggleLayout`、`getLayoutButtonTitle`、`getLayoutButtonIcon` 函数
- ✅ 添加 `globalChapterLayout` 和 `globalNodeLayout` props 定义

## 待完成

### 4. 实现全局布局逻辑（ChapterSection.vue）

#### 4.1 行排列模式（globalChapterLayout === 'row'）
**需求**：
- Section 横向排列（flex-row）
- 节点根据 `globalNodeLayout` 排列：
  - `row`: 横向排列
  - `column`: 纵向排列
  - `wrap`: 自动换行

**修改位置**：
- `chapterLayout` computed（line ~800）：需要改为使用 `props.globalChapterLayout`
- Section 容器样式（line ~70-90）：flex 方向
- Node 容器样式：根据 `globalNodeLayout` 设置

#### 4.2 列排列模式（globalChapterLayout === 'column'）
**需求**：
- Section 纵向排列（flex-column），均分宽度
- 高度由最高的 section 决定
- 节点按行排布（flex-row wrap）

**修改位置**：
- Section 容器样式：flex-column，均分宽度
- Section 高度计算逻辑

#### 4.3 自由模式（globalChapterLayout === 'free'）
**需求**：
- 可以通过点击按钮触发
- 可以通过拖动触发（已实现）
- 继承当前的视觉位置作为绝对坐标
- 可以自由编辑位置

**修改位置**：
- 保持现有的自由模式逻辑
- 添加从行/列模式切换到自由模式的过渡逻辑

## 关键代码位置

### ChapterSection.vue
1. **Props 定义**：line 387-490
2. **chapterLayout computed**：需要查找并修改
3. **Section 容器样式**：line 70-90
4. **Node 容器样式**：line 195-210
5. **getChapterContainerStyle**：line 972-1070
6. **拖拽逻辑**：line 1369-1700（已实现自由模式切换）

### App.vue
1. **全局布局控制 UI**：line 246-330
2. **状态定义**：line 1128-1130
3. **Props 传递**：line 933-945

## 下一步操作

1. 修改 `chapterLayout` computed，使其基于 `props.globalChapterLayout`
2. 修改 Section 容器的 flex 方向和样式
3. 添加 Node 容器的布局样式（基于 `globalNodeLayout`）
4. 测试三种模式的切换
5. 确保拖拽时自动切换到自由模式的逻辑正常工作

