"""业务逻辑服务模块"""
from datetime import datetime
from typing import Optional, Dict, List
import networkx as nx
from fastapi import HTTPException

from knowledge_dag.models import (
    Project, Chapter, Section, Node, Edge,
    CreateProjectRequest, AddChapterRequest, AddSectionRequest,
    AddNodeRequest, UpdateNodeRequest, AddEdgeRequest, UpdateEdgeRequest,
    ReorderNodesRequest, UpdateNodePositionRequest
)
from knowledge_dag.storage import storage


class ProjectService:
    """项目服务"""
    
    @staticmethod
    def get_all_projects() -> List[Dict]:
        """获取所有项目列表"""
        projects = storage.get_all()
        return [
            {
                "id": project.id,
                "name": project.name,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            }
            for project in projects.values()
        ]
    
    @staticmethod
    def create_project(request: CreateProjectRequest) -> Project:
        """创建新项目"""
        project_id = f"proj_{len(storage.get_all()) + 1}_{int(datetime.now().timestamp())}"
        now = datetime.now().isoformat()
        
        new_project = Project(
            id=project_id,
            name=request.name,
            created_at=now,
            updated_at=now,
            chapters=[],
            edges=[]
        )
        storage.add(new_project)
        return new_project
    
    @staticmethod
    def get_project(project_id: str) -> Project:
        """获取项目详情"""
        if not storage.exists(project_id):
            raise HTTPException(status_code=404, detail="Project not found")
        return storage.get(project_id)
    
    @staticmethod
    def delete_project(project_id: str) -> None:
        """删除项目"""
        if not storage.exists(project_id):
            raise HTTPException(status_code=404, detail="Project not found")
        storage.delete(project_id)


class ChapterService:
    """章节服务"""
    
    @staticmethod
    def add_chapter(project_id: str, request: AddChapterRequest) -> Project:
        """添加章节"""
        project = ProjectService.get_project(project_id)
        
        # 如果没有提供名称，使用默认名称
        chapter_name = request.chapter_name.strip() if request.chapter_name.strip() else f"第 {len(project.chapters) + 1} 章"
        
        new_chapter_id = f"ch_{len(project.chapters) + 1}_{int(datetime.now().timestamp())}"
        new_chapter = Chapter(id=new_chapter_id, name=chapter_name, sections=[])
        project.chapters.append(new_chapter)
        project.updated_at = datetime.now().isoformat()
        
        storage.update(project)
        return project
    
    @staticmethod
    def delete_chapter(project_id: str, chapter_id: str) -> Project:
        """删除章节"""
        project = ProjectService.get_project(project_id)
        
        # 找到要删除的章节，并收集所有节点ID
        chapter_to_delete = None
        node_ids_to_remove = []
        
        for chapter in project.chapters:
            if chapter.id == chapter_id:
                chapter_to_delete = chapter
                for section in chapter.sections:
                    for node in section.nodes:
                        node_ids_to_remove.append(node.id)
                break
        
        if not chapter_to_delete:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        # 删除章节
        project.chapters = [ch for ch in project.chapters if ch.id != chapter_id]
        
        # 清理相关的边（删除所有包含这些节点的边）
        edges_before = len(project.edges)
        project.edges = [
            e for e in project.edges 
            if e.source not in node_ids_to_remove and e.target not in node_ids_to_remove
        ]
        edges_after = len(project.edges)
        edges_removed = edges_before - edges_after
        
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project


class SectionService:
    """部分服务"""
    
    @staticmethod
    def add_section(project_id: str, request: AddSectionRequest) -> Project:
        """添加部分"""
        project = ProjectService.get_project(project_id)
        
        chapter = next((ch for ch in project.chapters if ch.id == request.chapter_id), None)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        new_section_id = f"sec_{len(chapter.sections) + 1}_{int(datetime.now().timestamp())}"
        new_section = Section(id=new_section_id, name=request.section_name, nodes=[])
        chapter.sections.append(new_section)
        project.updated_at = datetime.now().isoformat()
        
        storage.update(project)
        return project
    
    @staticmethod
    def delete_section(project_id: str, section_id: str) -> Project:
        """删除部分"""
        project = ProjectService.get_project(project_id)
        
        # 找到要删除的部分，并收集所有节点ID
        node_ids_to_remove = []
        
        for chapter in project.chapters:
            for section in chapter.sections:
                if section.id == section_id:
                    for node in section.nodes:
                        node_ids_to_remove.append(node.id)
                    chapter.sections = [s for s in chapter.sections if s.id != section_id]
                    break
        
        if not node_ids_to_remove:
            raise HTTPException(status_code=404, detail="Section not found")
        
        # 清理相关的边（删除所有包含这些节点的边）
        edges_before = len(project.edges)
        project.edges = [
            e for e in project.edges 
            if e.source not in node_ids_to_remove and e.target not in node_ids_to_remove
        ]
        edges_after = len(project.edges)
        edges_removed = edges_before - edges_after
        
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project


class NodeService:
    """节点服务"""
    
    @staticmethod
    def _get_all_nodes(project: Project) -> Dict[str, Node]:
        """获取项目中所有节点的字典 {node_id: Node}"""
        nodes_dict = {}
        for chapter in project.chapters:
            for section in chapter.sections:
                for node in section.nodes:
                    nodes_dict[node.id] = node
        return nodes_dict
    
    @staticmethod
    def add_node(project_id: str, request: AddNodeRequest) -> Project:
        """添加知识节点"""
        project = ProjectService.get_project(project_id)
        
        chapter = next((ch for ch in project.chapters if ch.id == request.chapter_id), None)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        section = next((sec for sec in chapter.sections if sec.id == request.section_id), None)
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        
        # 如果没有提供名称，使用默认名称
        node_name = request.node_name.strip() if request.node_name.strip() else f"知识点 {len(section.nodes) + 1}"
        
        # 检查节点名称是否已存在（在同一项目中）
        all_nodes = NodeService._get_all_nodes(project)
        for node in all_nodes.values():
            if node.name == node_name:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Node name '{node_name}' already exists in this project"
                )
        
        new_node_id = f"node_{int(datetime.now().timestamp())}_{len(all_nodes)}"
        new_node = Node(
            id=new_node_id, 
            name=node_name, 
            content=request.node_content or "",
            position=float(len(section.nodes))  # 设置初始位置为列表末尾
        )
        section.nodes.append(new_node)
        project.updated_at = datetime.now().isoformat()
        
        storage.update(project)
        return project
    
    @staticmethod
    def _find_node_location(project: Project, node_id: str) -> Optional[Dict]:
        """查找节点所在的位置（内部方法）"""
        for chapter in project.chapters:
            for section in chapter.sections:
                for node in section.nodes:
                    if node.id == node_id:
                        return {
                            "chapter_id": chapter.id,
                            "chapter_name": chapter.name,
                            "section_id": section.id,
                            "section_name": section.name,
                            "node": node
                        }
        return None
    
    @staticmethod
    def update_node(project_id: str, node_id: str, request: UpdateNodeRequest) -> Project:
        """更新节点"""
        project = ProjectService.get_project(project_id)
        
        location = NodeService._find_node_location(project, node_id)
        if not location:
            raise HTTPException(status_code=404, detail="Node not found")
        
        node = location["node"]
        if request.name is not None:
            node.name = request.name
        if request.content is not None:
            node.content = request.content
        
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project
    
    @staticmethod
    def reorder_nodes(project_id: str, request: ReorderNodesRequest) -> Project:
        """重排序节点"""
        project = ProjectService.get_project(project_id)
        
        # 找到对应的 section
        section = None
        for chapter in project.chapters:
            for sec in chapter.sections:
                if sec.id == request.section_id:
                    section = sec
                    break
            if section:
                break
        
        if not section:
            raise HTTPException(status_code=404, detail="Section not found")
        
        # 验证所有节点ID都存在
        existing_node_ids = {node.id for node in section.nodes}
        if set(request.node_ids) != existing_node_ids:
            raise HTTPException(
                status_code=400,
                detail="Node IDs do not match existing nodes in section"
            )
        
        # 创建节点ID到节点的映射
        node_map = {node.id: node for node in section.nodes}
        
        # 按照新顺序重新排列节点，并更新位置索引
        section.nodes = []
        for index, node_id in enumerate(request.node_ids):
            node = node_map[node_id]
            node.position = float(index)  # 保存位置索引
            section.nodes.append(node)
        
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project
    
    @staticmethod
    def update_node_position(project_id: str, request: UpdateNodePositionRequest) -> Project:
        """更新节点位置"""
        project = ProjectService.get_project(project_id)
        
        location = NodeService._find_node_location(project, request.node_id)
        if not location:
            raise HTTPException(status_code=404, detail="Node not found")
        
        if location["section_id"] != request.section_id:
            raise HTTPException(status_code=400, detail="Section ID mismatch")
        
        node = location["node"]
        node.x = request.x
        node.y = request.y
        
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project
    
    @staticmethod
    def delete_node(project_id: str, node_id: str) -> Project:
        """删除节点"""
        project = ProjectService.get_project(project_id)
        
        location = NodeService._find_node_location(project, node_id)
        if not location:
            raise HTTPException(status_code=404, detail="Node not found")
        
        # 删除节点
        chapter = next((ch for ch in project.chapters if ch.id == location["chapter_id"]), None)
        if not chapter:
            raise HTTPException(status_code=404, detail=f"Chapter {location['chapter_id']} not found")
        
        section = next((sec for sec in chapter.sections if sec.id == location["section_id"]), None)
        if not section:
            raise HTTPException(status_code=404, detail=f"Section {location['section_id']} not found")
        
        # 从列表中删除节点
        nodes_before = len(section.nodes)
        section.nodes = [n for n in section.nodes if n.id != node_id]
        nodes_after = len(section.nodes)
        
        if nodes_before == nodes_after:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found in section {section.id}")
        
        # 清理相关的边（删除所有包含该节点的边）
        project.edges = [e for e in project.edges if e.source != node_id and e.target != node_id]
        
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        
        return project


class GraphService:
    """图谱服务"""
    
    @staticmethod
    def _get_graph(project: Project) -> nx.DiGraph:
        """构建 NetworkX 有向图"""
        G = nx.DiGraph()
        nodes_dict = NodeService._get_all_nodes(project)
        G.add_nodes_from(nodes_dict.keys())
        # 将 Edge 对象转换为 (source, target) 元组
        G.add_edges_from([(e.source, e.target) for e in project.edges])
        return G
    
    @staticmethod
    def find_node_location(project: Project, node_id: str) -> Optional[Dict]:
        """查找节点所在的位置"""
        # 使用 NodeService 的内部方法
        return NodeService._find_node_location(project, node_id)
    
    @staticmethod
    def add_edge(project_id: str, request: AddEdgeRequest) -> Project:
        """添加边（连接）"""
        project = ProjectService.get_project(project_id)
        
        all_nodes = NodeService._get_all_nodes(project)
        if request.source not in all_nodes or request.target not in all_nodes:
            raise HTTPException(status_code=404, detail="Source or Target node not found")
        
        # 检查边是否已存在
        existing_edge = next(
            (e for e in project.edges if e.source == request.source and e.target == request.target),
            None
        )
        if existing_edge:
            return project
        
        # DAG 环检测
        G = GraphService._get_graph(project)
        G.add_edge(request.source, request.target)
        if not nx.is_directed_acyclic_graph(G):
            raise HTTPException(
                status_code=400, 
                detail="Cycle detected! Knowledge graphs must be acyclic."
            )
        
        # 创建新的边对象
        new_edge = Edge(
            source=request.source,
            target=request.target,
            label=request.label or ""
        )
        project.edges.append(new_edge)
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project
    
    @staticmethod
    def delete_edge(project_id: str, request: AddEdgeRequest) -> Project:
        """删除边"""
        project = ProjectService.get_project(project_id)
        
        project.edges = [
            e for e in project.edges 
            if not (e.source == request.source and e.target == request.target)
        ]
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project
    
    @staticmethod
    def update_edge(project_id: str, request: UpdateEdgeRequest) -> Project:
        """更新边的标签"""
        project = ProjectService.get_project(project_id)
        
        edge = next(
            (e for e in project.edges if e.source == request.source and e.target == request.target),
            None
        )
        if not edge:
            raise HTTPException(status_code=404, detail="Edge not found")
        
        edge.label = request.label
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project
    
    @staticmethod
    def analyze_graph(project_id: str, focus_node: Optional[str] = None):
        """分析图谱，返回选中节点的DAG路径"""
        from knowledge_dag.models import GraphAnalysisResponse
        
        project = ProjectService.get_project(project_id)
        
        if not focus_node:
            return GraphAnalysisResponse()
        
        G = GraphService._get_graph(project)
        if focus_node not in G:
            return GraphAnalysisResponse()
        
        # 获取祖先和后代
        ancestors = list(nx.ancestors(G, focus_node))
        descendants = list(nx.descendants(G, focus_node))
        related = ancestors + descendants + [focus_node]
        
        # 获取所有路径
        paths = []
        # 从所有祖先到焦点节点的路径
        for ancestor in ancestors:
            try:
                for path in nx.all_simple_paths(G, ancestor, focus_node):
                    paths.append(path)
            except:
                pass
        
        # 从焦点节点到所有后代的路径
        for descendant in descendants:
            try:
                for path in nx.all_simple_paths(G, focus_node, descendant):
                    paths.append(path)
            except:
                pass
        
        return GraphAnalysisResponse(
            highlight=related,
            paths=paths,
            ancestors=ancestors,
            descendants=descendants
        )

