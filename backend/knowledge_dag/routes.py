"""API 路由模块"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from knowledge_dag.models import (
    CreateProjectRequest, AddChapterRequest, AddSectionRequest,
    AddNodeRequest, UpdateNodeRequest, AddEdgeRequest, UpdateEdgeRequest,
    ReorderNodesRequest, UpdateNodePositionRequest, NodeLocationResponse
)
from knowledge_dag.services import (
    ProjectService, ChapterService, SectionService,
    NodeService, GraphService
)

router = APIRouter()


@router.get("/")
def root():
    """根路径"""
    return {"message": "Knowledge DAG Builder API", "version": "1.0.0"}


@router.get("/projects")
def get_projects():
    """获取所有项目列表"""
    return ProjectService.get_all_projects()


@router.post("/projects")
def create_project(request: CreateProjectRequest):
    """创建新项目"""
    return ProjectService.create_project(request)


@router.get("/projects/{project_id}")
def get_project(project_id: str):
    """获取项目详情"""
    return ProjectService.get_project(project_id)


@router.delete("/projects/{project_id}")
def delete_project(project_id: str):
    """删除项目"""
    ProjectService.delete_project(project_id)
    return {"message": "Project deleted"}


@router.post("/projects/{project_id}/chapters")
def add_chapter(project_id: str, request: AddChapterRequest):
    """添加章节"""
    return ChapterService.add_chapter(project_id, request)


@router.delete("/projects/{project_id}/chapters/{chapter_id}")
def delete_chapter(project_id: str, chapter_id: str):
    """删除章节"""
    return ChapterService.delete_chapter(project_id, chapter_id)


@router.post("/projects/{project_id}/sections")
def add_section(project_id: str, request: AddSectionRequest):
    """添加部分"""
    return SectionService.add_section(project_id, request)


@router.delete("/projects/{project_id}/sections/{section_id}")
def delete_section(project_id: str, section_id: str):
    """删除部分"""
    return SectionService.delete_section(project_id, section_id)


@router.post("/projects/{project_id}/nodes")
def add_node(project_id: str, request: AddNodeRequest):
    """添加知识节点"""
    return NodeService.add_node(project_id, request)


@router.post("/projects/{project_id}/nodes/reorder")
def reorder_nodes(project_id: str, request: ReorderNodesRequest):
    """重排序节点"""
    return NodeService.reorder_nodes(project_id, request)


@router.put("/projects/{project_id}/nodes/position")
def update_node_position(project_id: str, request: UpdateNodePositionRequest):
    """更新节点位置"""
    return NodeService.update_node_position(project_id, request)


@router.put("/projects/{project_id}/nodes/{node_id}")
def update_node(project_id: str, node_id: str, request: UpdateNodeRequest):
    """更新节点"""
    return NodeService.update_node(project_id, node_id, request)


@router.delete("/projects/{project_id}/nodes/{node_id}")
def delete_node(project_id: str, node_id: str):
    """删除节点"""
    return NodeService.delete_node(project_id, node_id)


@router.post("/projects/{project_id}/edges")
def add_edge(project_id: str, request: AddEdgeRequest):
    """添加边（连接）"""
    return GraphService.add_edge(project_id, request)


@router.delete("/projects/{project_id}/edges")
def delete_edge(project_id: str, request: AddEdgeRequest):
    """删除边"""
    return GraphService.delete_edge(project_id, request)


@router.put("/projects/{project_id}/edges")
def update_edge(project_id: str, request: UpdateEdgeRequest):
    """更新边的标签"""
    return GraphService.update_edge(project_id, request)


@router.get("/projects/{project_id}/graph_analysis")
def analyze_graph(project_id: str, focus_node: Optional[str] = None):
    """分析图谱，返回选中节点的DAG路径"""
    return GraphService.analyze_graph(project_id, focus_node)


@router.get("/projects/{project_id}/nodes/{node_id}/location")
def get_node_location(project_id: str, node_id: str):
    """获取节点位置信息"""
    project = ProjectService.get_project(project_id)
    location = GraphService.find_node_location(project, node_id)
    if not location:
        raise HTTPException(status_code=404, detail="Node not found")
    return NodeLocationResponse(**location)

