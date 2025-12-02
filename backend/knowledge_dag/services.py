"""业务逻辑服务模块"""
from datetime import datetime
from typing import Optional, Dict, List
import networkx as nx
import yaml
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
    def update_project(project_id: str, name: str) -> Project:
        """更新项目名称"""
        project = ProjectService.get_project(project_id)
        project.name = name.strip()
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project
    
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
        
        # 验证章节确实属于指定的项目
        chapter = next((ch for ch in project.chapters if ch.id == request.chapter_id), None)
        if not chapter:
            raise HTTPException(status_code=404, detail=f"Chapter {request.chapter_id} not found in project {project_id}")
        
        # 验证章节确实在项目中
        if chapter.id not in [ch.id for ch in project.chapters]:
            raise HTTPException(status_code=404, detail="Chapter not found in project")
        
        new_section_id = f"sec_{len(chapter.sections) + 1}_{int(datetime.now().timestamp())}"
        new_section = Section(id=new_section_id, name=request.section_name, nodes=[])
        chapter.sections.append(new_section)
        project.updated_at = datetime.now().isoformat()
        
        storage.update(project)
        return project
    
    @staticmethod
    def delete_section(project_id: str, section_id: str, chapter_id: Optional[str] = None) -> Project:
        """删除部分
        
        可以可选地提供 chapter_id 进行额外验证
        """
        project = ProjectService.get_project(project_id)
        
        # 使用辅助方法查找 section，如果提供了 chapter_id，会进行验证
        section_location = NodeService._find_section_location(
            project,
            section_id,
            chapter_id=chapter_id
        )
        if not section_location:
            error_msg = f"Section {section_id} not found"
            if chapter_id:
                error_msg += f" in chapter {chapter_id}"
            error_msg += f" in project {project_id}"
            raise HTTPException(status_code=404, detail=error_msg)
        
        section_to_delete = section_location["section"]
        
        # 验证 section 确实属于指定的项目
        found = False
        target_chapter = None
        for chapter in project.chapters:
            if chapter.id == section_location["chapter_id"]:
                if section_to_delete.id in [sec.id for sec in chapter.sections]:
                    found = True
                    target_chapter = chapter
                    break
        if not found:
            raise HTTPException(status_code=404, detail="Section not found in project")
        
        # 如果提供了 chapter_id，进行额外验证
        if chapter_id and section_location["chapter_id"] != chapter_id:
            raise HTTPException(status_code=400, detail="Chapter ID mismatch")
        
        # 收集所有节点ID
        node_ids_to_remove = [node.id for node in section_to_delete.nodes]
        
        # 删除 section
        target_chapter.sections = [s for s in target_chapter.sections if s.id != section_id]
        
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
    def _find_node_location(project: Project, node_id: str, chapter_id: Optional[str] = None, section_id: Optional[str] = None) -> Optional[Dict]:
        """查找节点所在的位置（内部方法）
        
        如果提供了 chapter_id 或 section_id，会进行验证，确保节点确实属于指定的章节/部分
        """
        for chapter in project.chapters:
            # 如果指定了 chapter_id，只在该章节中查找
            if chapter_id and chapter.id != chapter_id:
                continue
                
            for section in chapter.sections:
                # 如果指定了 section_id，只在该部分中查找
                if section_id and section.id != section_id:
                    continue
                    
                for node in section.nodes:
                    if node.id == node_id:
                        # 如果指定了 chapter_id 或 section_id，验证是否匹配
                        if chapter_id and chapter.id != chapter_id:
                            continue
                        if section_id and section.id != section_id:
                            continue
                            
                        return {
                            "chapter_id": chapter.id,
                            "chapter_name": chapter.name,
                            "section_id": section.id,
                            "section_name": section.name,
                            "node": node
                        }
        return None
    
    @staticmethod
    def _find_section_location(project: Project, section_id: str, chapter_id: Optional[str] = None) -> Optional[Dict]:
        """查找部分所在的位置（内部方法）
        
        如果提供了 chapter_id，会进行验证，确保部分确实属于指定的章节
        """
        for chapter in project.chapters:
            # 如果指定了 chapter_id，只在该章节中查找
            if chapter_id and chapter.id != chapter_id:
                continue
                
            for section in chapter.sections:
                if section.id == section_id:
                    # 如果指定了 chapter_id，验证是否匹配
                    if chapter_id and chapter.id != chapter_id:
                        continue
                        
                    return {
                        "chapter_id": chapter.id,
                        "chapter_name": chapter.name,
                        "section": section
                    }
        return None
    
    @staticmethod
    def update_node(project_id: str, node_id: str, request: UpdateNodeRequest) -> Project:
        """更新节点"""
        project = ProjectService.get_project(project_id)
        
        # 如果请求中提供了 chapter_id 或 section_id，进行验证
        location = NodeService._find_node_location(
            project, 
            node_id, 
            chapter_id=getattr(request, 'chapter_id', None),
            section_id=getattr(request, 'section_id', None)
        )
        if not location:
            raise HTTPException(status_code=404, detail="Node not found in the specified project/chapter/section")
        
        # 验证节点确实属于指定的项目
        if location["chapter_id"] not in [ch.id for ch in project.chapters]:
            raise HTTPException(status_code=404, detail="Node's chapter not found in project")
        if location["section_id"] not in [sec.id for ch in project.chapters for sec in ch.sections]:
            raise HTTPException(status_code=404, detail="Node's section not found in project")
        
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
        
        # 使用辅助方法查找 section，并验证它属于指定的项目
        section_location = NodeService._find_section_location(
            project, 
            request.section_id,
            chapter_id=getattr(request, 'chapter_id', None)
        )
        if not section_location:
            raise HTTPException(status_code=404, detail="Section not found in the specified project/chapter")
        
        section = section_location["section"]
        
        # 验证 section 确实属于指定的项目
        found = False
        for chapter in project.chapters:
            if chapter.id == section_location["chapter_id"]:
                if section.id in [sec.id for sec in chapter.sections]:
                    found = True
                    break
        if not found:
            raise HTTPException(status_code=404, detail="Section not found in project")
        
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
        
        # 验证节点确实属于指定的 section
        location = NodeService._find_node_location(
            project, 
            request.node_id,
            section_id=request.section_id
        )
        if not location:
            raise HTTPException(status_code=404, detail="Node not found in the specified project/section")
        
        # 双重验证：确保 section_id 匹配
        if location["section_id"] != request.section_id:
            raise HTTPException(status_code=400, detail="Section ID mismatch: node belongs to different section")
        
        # 验证 section 确实属于指定的项目
        section_found = False
        target_chapter = None
        for chapter in project.chapters:
            # 如果提供了 chapter_id，进行验证
            if request.chapter_id and chapter.id != request.chapter_id:
                continue
            for section in chapter.sections:
                if section.id == request.section_id:
                    section_found = True
                    target_chapter = chapter
                    break
            if section_found:
                break
        
        if not section_found:
            error_msg = "Section not found in the specified project"
            if request.chapter_id:
                error_msg += f"/chapter {request.chapter_id}"
            raise HTTPException(status_code=404, detail=error_msg)
        
        # 如果提供了 chapter_id，验证是否匹配
        if request.chapter_id and location["chapter_id"] != request.chapter_id:
            raise HTTPException(status_code=400, detail="Chapter ID mismatch: node belongs to different chapter")
        
        node = location["node"]
        node.x = request.x
        node.y = request.y
        
        project.updated_at = datetime.now().isoformat()
        storage.update(project)
        return project
    
    @staticmethod
    def delete_node(project_id: str, node_id: str, chapter_id: Optional[str] = None, section_id: Optional[str] = None) -> Project:
        """删除节点
        
        可以可选地提供 chapter_id 和 section_id 进行额外验证
        """
        project = ProjectService.get_project(project_id)
        
        # 使用辅助方法查找节点，如果提供了 chapter_id 或 section_id，会进行验证
        location = NodeService._find_node_location(
            project, 
            node_id,
            chapter_id=chapter_id,
            section_id=section_id
        )
        if not location:
            error_msg = "Node not found"
            if chapter_id or section_id:
                error_msg += " in the specified project/chapter/section"
            raise HTTPException(status_code=404, detail=error_msg)
        
        # 验证节点确实属于指定的项目
        chapter = next((ch for ch in project.chapters if ch.id == location["chapter_id"]), None)
        if not chapter:
            raise HTTPException(status_code=404, detail=f"Chapter {location['chapter_id']} not found in project")
        
        section = next((sec for sec in chapter.sections if sec.id == location["section_id"]), None)
        if not section:
            raise HTTPException(status_code=404, detail=f"Section {location['section_id']} not found in chapter")
        
        # 如果提供了 chapter_id 或 section_id，进行额外验证
        if chapter_id and chapter.id != chapter_id:
            raise HTTPException(status_code=400, detail="Chapter ID mismatch")
        if section_id and section.id != section_id:
            raise HTTPException(status_code=400, detail="Section ID mismatch")
        
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


class ExportService:
    """导出服务"""
    
    @staticmethod
    def export_to_yaml(project_id: str) -> str:
        """导出项目为 YAML 格式"""
        project = ProjectService.get_project(project_id)
        
        # 构建 YAML 数据结构（只包含三级结构和边、位置信息）
        yaml_data = {
            "project": {
                "id": project.id,
                "name": project.name
            },
            "chapters": []
        }
        
        # 遍历章节
        for chapter in project.chapters:
            chapter_data = {
                "id": chapter.id,
                "name": chapter.name,
                "sections": []
            }
            
            # 遍历部分
            for section in chapter.sections:
                section_data = {
                    "id": section.id,
                    "name": section.name,
                    "nodes": []
                }
                
                # 遍历节点
                for node in section.nodes:
                    node_data = {
                        "id": node.id,
                        "name": node.name,
                        "content": node.content or ""
                    }
                    
                    # 添加位置信息（如果有）
                    if node.position is not None:
                        node_data["position"] = node.position
                    if node.x is not None:
                        node_data["x"] = node.x
                    if node.y is not None:
                        node_data["y"] = node.y
                    
                    section_data["nodes"].append(node_data)
                
                chapter_data["sections"].append(section_data)
            
            yaml_data["chapters"].append(chapter_data)
        
        # 添加边信息
        yaml_data["edges"] = []
        for edge in project.edges:
            edge_data = {
                "source": edge.source,
                "target": edge.target
            }
            if edge.label:
                edge_data["label"] = edge.label
            yaml_data["edges"].append(edge_data)
        
        # 转换为 YAML 字符串
        yaml_str = yaml.dump(yaml_data, allow_unicode=True, sort_keys=False, default_flow_style=False, indent=2)
        return yaml_str
    
    @staticmethod
    def import_from_yaml(yaml_content: str, project_name: Optional[str] = None) -> Project:
        """从 YAML 内容导入项目"""
        try:
            # 解析 YAML
            data = yaml.safe_load(yaml_content)
            if not data:
                raise ValueError("YAML 文件为空或格式错误")
            
            # 验证基本结构
            if "project" not in data or "chapters" not in data:
                raise ValueError("YAML 文件缺少必要的字段: project 或 chapters")
            
            project_info = data["project"]
            chapters_data = data.get("chapters", [])
            edges_data = data.get("edges", [])
            
            # 验证 chapters_data 是列表
            if not isinstance(chapters_data, list):
                raise ValueError(f"chapters 必须是列表，当前类型: {type(chapters_data)}")
            
            # 验证每个章节的结构
            for idx, ch in enumerate(chapters_data):
                if not isinstance(ch, dict):
                    raise ValueError(f"章节 {idx + 1} 格式错误: 必须是字典")
                if "sections" not in ch:
                    raise ValueError(f"章节 {idx + 1} 缺少 sections 字段")
                sections = ch.get("sections", [])
                if not isinstance(sections, list):
                    raise ValueError(f"章节 {idx + 1} 的 sections 必须是列表")
            
            # 创建新项目（总是生成新的 ID，不覆盖现有项目）
            import time
            timestamp = int(time.time() * 1000)  # 使用毫秒时间戳提高唯一性
            project_id = f"proj_{timestamp}"
            project_name = project_name or project_info.get("name") or "导入的项目"
            now = datetime.now().isoformat()
            
            # 创建节点 ID 映射表（旧 ID -> 新 ID），用于更新边的引用
            # 先遍历所有节点，建立映射关系
            node_id_map = {}
            node_counter = 0
            
            # 第一遍：建立节点 ID 映射
            for chapter_data in chapters_data:
                sections_data = chapter_data.get("sections", [])
                for section_data in sections_data:
                    nodes_data = section_data.get("nodes", [])
                    for node_data in nodes_data:
                        old_node_id = node_data.get("id")
                        if not old_node_id:
                            raise ValueError(f"节点缺少 id 字段: {node_data}")
                        # 生成新的节点 ID
                        new_node_id = f"node_{timestamp}_{node_counter}"
                        node_id_map[old_node_id] = new_node_id
                        node_counter += 1
            
            # 第二遍：构建章节列表（生成新的 ID，避免与现有项目冲突）
            chapters = []
            for ch_idx, chapter_data in enumerate(chapters_data):
                # 使用章节索引确保唯一性
                chapter_id = f"ch_{ch_idx + 1}_{timestamp}"
                chapter_name = chapter_data.get("name") or f"第 {ch_idx + 1} 章"
                
                # 确保 sections 是列表
                sections_data = chapter_data.get("sections", [])
                if not isinstance(sections_data, list):
                    raise ValueError(f"章节 {ch_idx + 1} ({chapter_name}) 的 sections 必须是列表，当前类型: {type(sections_data)}")
                
                # 构建部分列表（生成新的 ID，包含章节索引确保唯一性）
                sections = []
                for sec_idx, section_data in enumerate(sections_data):
                    if not isinstance(section_data, dict):
                        raise ValueError(f"章节 {ch_idx + 1} 的部分 {sec_idx + 1} 格式错误: 必须是字典")
                    
                    section_id = f"sec_{ch_idx + 1}_{sec_idx + 1}_{timestamp}"
                    section_name = section_data.get("name") or f"部分 {sec_idx + 1}"
                    
                    # 确保 nodes 是列表
                    nodes_data = section_data.get("nodes", [])
                    if not isinstance(nodes_data, list):
                        raise ValueError(f"章节 {ch_idx + 1} 部分 {sec_idx + 1} ({section_name}) 的 nodes 必须是列表，当前类型: {type(nodes_data)}")
                    
                    # 构建节点列表（使用映射后的新 ID）
                    nodes = []
                    for node_data in nodes_data:
                        if not isinstance(node_data, dict):
                            raise ValueError(f"节点数据格式错误: 必须是字典")
                        
                        old_node_id = node_data.get("id")
                        if not old_node_id:
                            raise ValueError(f"节点缺少 id 字段: {node_data}")
                        
                        if old_node_id not in node_id_map:
                            raise ValueError(f"节点 ID {old_node_id} 未在映射表中找到，可能是在第一遍扫描时遗漏")
                        
                        new_node_id = node_id_map[old_node_id]
                        
                        node_name = node_data.get("name") or old_node_id
                        node_content = node_data.get("content", "")
                        node_position = node_data.get("position")
                        node_x = node_data.get("x")
                        node_y = node_data.get("y")
                        
                        node = Node(
                            id=new_node_id,
                            name=node_name,
                            content=node_content,
                            position=node_position,
                            x=node_x,
                            y=node_y
                        )
                        nodes.append(node)
                    
                    section = Section(
                        id=section_id,
                        name=section_name,
                        nodes=nodes
                    )
                    sections.append(section)
                
                chapter = Chapter(
                    id=chapter_id,
                    name=chapter_name,
                    sections=sections
                )
                chapters.append(chapter)
            
            # 构建边列表（使用新的节点 ID）
            edges = []
            for edge_data in edges_data:
                old_source = edge_data.get("source")
                old_target = edge_data.get("target")
                label = edge_data.get("label", "")
                
                if not old_source or not old_target:
                    raise ValueError(f"边缺少 source 或 target 字段: {edge_data}")
                
                # 将旧的节点 ID 映射到新的节点 ID
                new_source = node_id_map.get(old_source)
                new_target = node_id_map.get(old_target)
                
                if not new_source:
                    raise ValueError(f"边的源节点 ID 不存在: {old_source}")
                if not new_target:
                    raise ValueError(f"边的目标节点 ID 不存在: {old_target}")
                
                edge = Edge(
                    source=new_source,
                    target=new_target,
                    label=label
                )
                edges.append(edge)
            
            # 创建项目对象
            new_project = Project(
                id=project_id,
                name=project_name,
                created_at=now,
                updated_at=now,
                chapters=chapters,
                edges=edges
            )
            
            # 验证项目（检查节点 ID 是否存在）
            all_node_ids = set()
            for chapter in chapters:
                for section in chapter.sections:
                    for node in section.nodes:
                        if node.id in all_node_ids:
                            raise ValueError(f"重复的节点 ID: {node.id}")
                        all_node_ids.add(node.id)
            
            # 验证边的节点 ID 是否存在
            for edge in edges:
                if edge.source not in all_node_ids:
                    raise ValueError(f"边的源节点不存在: {edge.source}")
                if edge.target not in all_node_ids:
                    raise ValueError(f"边的目标节点不存在: {edge.target}")
            
            # 保存项目
            storage.add(new_project)
            
            return new_project
            
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 解析错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"导入失败: {str(e)}")

