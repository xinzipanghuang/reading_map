"""API 路由模块"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional

from knowledge_dag.models import (
    CreateProjectRequest, UpdateProjectRequest, AddChapterRequest, AddSectionRequest,
    AddNodeRequest, UpdateNodeRequest, AddEdgeRequest, UpdateEdgeRequest,
    ReorderNodesRequest, ReorderSectionsRequest, ReorderChaptersRequest,
    UpdateNodePositionRequest, UpdateSectionPositionRequest, NodeLocationResponse,
    UpdateChapterRequest, UpdateSectionRequest
)
from knowledge_dag.services import (
    ProjectService, ChapterService, SectionService,
    NodeService, GraphService, ExportService
)
from fastapi import UploadFile, File

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


@router.put("/projects/{project_id}")
def update_project(project_id: str, request: UpdateProjectRequest):
    """更新项目名称"""
    return ProjectService.update_project(project_id, request.name)


@router.delete("/projects/{project_id}")
def delete_project(project_id: str):
    """删除项目"""
    ProjectService.delete_project(project_id)
    return {"message": "Project deleted"}


@router.post("/projects/{project_id}/chapters")
def add_chapter(project_id: str, request: AddChapterRequest):
    """添加章节"""
    return ChapterService.add_chapter(project_id, request)


@router.put("/projects/{project_id}/chapters/position")
async def update_chapter_position(project_id: str, request: Request):
    """更新章节位置和尺寸（宽容模式，直接读取原始 JSON 避免验证冲突）"""
    import traceback, json
    payload = {}
    try:
        raw_body = await request.body()
        try:
            payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception:
            payload = {}
        print(f"\n[chapters/position] project_id={project_id}, payload={payload}")
        return ChapterService.update_chapter_position_payload(project_id, payload)
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR in update_chapter_position:")
        print(f"project_id: {project_id}")
        print(f"payload: {payload}")
        print(f"Exception: {e}")
        print(f"Exception type: {type(e)}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise

@router.put("/projects/{project_id}/chapters/{chapter_id}")
def update_chapter(project_id: str, chapter_id: str, request: UpdateChapterRequest):
    """更新章节名称和布局"""
    return ChapterService.update_chapter(project_id, chapter_id, request)

@router.post("/projects/{project_id}/chapters/reorder")
def reorder_chapters(project_id: str, request: ReorderChaptersRequest):
    """重排序章节"""
    return ChapterService.reorder_chapters(project_id, request)

@router.delete("/projects/{project_id}/chapters/{chapter_id}")
def delete_chapter(project_id: str, chapter_id: str):
    """删除章节"""
    return ChapterService.delete_chapter(project_id, chapter_id)


@router.put("/projects/{project_id}/sections/position")
async def update_section_position(project_id: str, request: Request):
    """更新部分位置和尺寸（宽容模式，直接读取原始 JSON 避免验证冲突）"""
    import traceback, json
    payload = {}
    try:
        raw_body = await request.body()
        try:
            payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception:
            payload = {}
        print(f"\n[sections/position] project_id={project_id}, payload={payload}")
        return SectionService.update_section_position_payload(project_id, payload)
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR in update_section_position:")
        print(f"project_id: {project_id}")
        print(f"payload: {payload}")
        print(f"Exception: {e}")
        print(f"Exception type: {type(e)}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise


@router.post("/projects/{project_id}/sections")
def add_section(project_id: str, request: AddSectionRequest):
    """添加部分"""
    return SectionService.add_section(project_id, request)


@router.put("/projects/{project_id}/sections/{section_id}")
def update_section(project_id: str, section_id: str, request: UpdateSectionRequest):
    """更新部分名称"""
    return SectionService.update_section(project_id, section_id, request)

@router.post("/projects/{project_id}/sections/reorder")
def reorder_sections(project_id: str, request: ReorderSectionsRequest):
    """重排序部分"""
    return SectionService.reorder_sections(project_id, request)

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


@router.get("/projects/{project_id}/export")
def export_project(project_id: str):
    """导出项目为 YAML 格式"""
    from fastapi.responses import Response
    import re
    
    yaml_content = ExportService.export_to_yaml(project_id)
    project = ProjectService.get_project(project_id)
    
    # 创建完全 ASCII 安全的文件名
    # 只保留 ASCII 字母、数字、下划线和连字符
    safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', project.name)
    safe_filename = re.sub(r'_+', '_', safe_filename)  # 将多个下划线合并为一个
    safe_filename = safe_filename.strip('_')
    if not safe_filename:
        safe_filename = "project"
    filename = f"{safe_filename}.yaml"
    
    # 确保 filename 完全是 ASCII
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    
    # 构建 Content-Disposition header，确保完全是 ASCII
    content_disposition = f'attachment; filename="{filename}"'
    
    # 使用 Response，但只使用 ASCII 安全的文件名
    # 浏览器会使用这个文件名，虽然可能不是原始的中文名称，但可以正常下载
    return Response(
        content=yaml_content.encode('utf-8'),  # 确保内容使用 UTF-8 编码
        media_type="application/x-yaml; charset=utf-8",
        headers={
            "Content-Disposition": content_disposition
        }
    )


@router.get("/projects/{project_id}/nodes/{node_id}/location")
def get_node_location(project_id: str, node_id: str):
    """获取节点位置信息"""
    project = ProjectService.get_project(project_id)
    location = GraphService.find_node_location(project, node_id)
    if not location:
        raise HTTPException(status_code=404, detail="Node not found")
    return NodeLocationResponse(**location)


@router.post("/projects/import")
def import_project(file: UploadFile = File(...), project_name: Optional[str] = None):
    """从 YAML 文件导入项目"""
    try:
        # 读取文件内容
        content = file.file.read()
        yaml_content = content.decode('utf-8')
        
        # 导入项目
        project = ExportService.import_from_yaml(yaml_content, project_name)
        
        return {
            "message": "项目导入成功",
            "project": {
                "id": project.id,
                "name": project.name,
                "chapters_count": len(project.chapters),
                "edges_count": len(project.edges)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")

