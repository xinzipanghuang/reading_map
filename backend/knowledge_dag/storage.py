"""数据存储模块 - SQLite 版本"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from knowledge_dag.models import Project, Chapter, Section, Node, Edge
from knowledge_dag.config import settings


class Storage:
    """数据存储类 - 使用 SQLite"""
    
    def __init__(self, db_file: Path = None):
        self.db_file = db_file or (settings.data_file.parent / "knowledge_dag.db")
        self._init_db()
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # 使结果可以像字典一样访问
        return conn
    
    def _init_db(self):
        """初始化数据库表结构"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 项目表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # 章节表
            # 使用复合主键 (project_id, id) 确保项目内章节ID唯一
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    project_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    position INTEGER,
                    PRIMARY KEY (project_id, id),
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            
            # 部分表（使用复合主键确保项目内部分ID唯一）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sections (
                    project_id TEXT NOT NULL,
                    chapter_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    position INTEGER,
                    PRIMARY KEY (project_id, chapter_id, id),
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (project_id, chapter_id) REFERENCES chapters(project_id, id) ON DELETE CASCADE
                )
            """)
            
            # 节点表（使用复合主键确保项目内节点ID唯一）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    project_id TEXT NOT NULL,
                    chapter_id TEXT NOT NULL,
                    section_id TEXT NOT NULL,
                    id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    content TEXT DEFAULT '',
                    position INTEGER,
                    x REAL,
                    y REAL,
                    PRIMARY KEY (project_id, chapter_id, section_id, id),
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY (project_id, chapter_id, section_id) REFERENCES sections(project_id, chapter_id, id) ON DELETE CASCADE
                )
            """)
            
            # 数据库迁移：为现有数据库添加新列（如果不存在）
            # 为 sections 表添加 project_id 列（如果不存在）
            try:
                cursor.execute("ALTER TABLE sections ADD COLUMN project_id TEXT")
                # 为现有数据填充 project_id（通过 chapter_id 关联）
                cursor.execute("""
                    UPDATE sections 
                    SET project_id = (
                        SELECT project_id FROM chapters 
                        WHERE chapters.id = sections.chapter_id
                    )
                    WHERE project_id IS NULL
                """)
            except sqlite3.OperationalError:
                pass  # 列已存在
            
            # 为 nodes 表添加 project_id 列（如果不存在）
            try:
                cursor.execute("ALTER TABLE nodes ADD COLUMN project_id TEXT")
                # 为现有数据填充 project_id（通过 section_id -> chapter_id -> project_id 关联）
                cursor.execute("""
                    UPDATE nodes 
                    SET project_id = (
                        SELECT chapters.project_id 
                        FROM sections 
                        JOIN chapters ON sections.chapter_id = chapters.id
                        WHERE sections.id = nodes.section_id
                    )
                    WHERE project_id IS NULL
                """)
            except sqlite3.OperationalError:
                pass  # 列已存在
            
            # 为 nodes 表添加 chapter_id 列（如果不存在）
            try:
                cursor.execute("ALTER TABLE nodes ADD COLUMN chapter_id TEXT")
                # 为现有数据填充 chapter_id（通过 section_id 关联）
                cursor.execute("""
                    UPDATE nodes 
                    SET chapter_id = (
                        SELECT chapter_id FROM sections 
                        WHERE sections.id = nodes.section_id
                    )
                    WHERE chapter_id IS NULL
                """)
            except sqlite3.OperationalError:
                pass  # 列已存在
            
            # 为 nodes 表添加 x, y 列（如果不存在）
            try:
                cursor.execute("ALTER TABLE nodes ADD COLUMN x REAL")
            except sqlite3.OperationalError:
                pass  # 列已存在
            
            try:
                cursor.execute("ALTER TABLE nodes ADD COLUMN y REAL")
            except sqlite3.OperationalError:
                pass  # 列已存在
            
            # 边表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    label TEXT DEFAULT '',
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    UNIQUE(project_id, source, target)
                )
            """)
            
            # 创建索引以提升查询性能
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapters_project ON chapters(project_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_project ON sections(project_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_chapter ON sections(project_id, chapter_id)")
            # 检查 nodes 表是否有 chapter_id 列，如果有则创建复合索引
            try:
                cursor.execute("PRAGMA table_info(nodes)")
                nodes_info = cursor.fetchall()
                has_chapter_id = any(col[1] == 'chapter_id' for col in nodes_info)
                if has_chapter_id:
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_project ON nodes(project_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_section ON nodes(project_id, chapter_id, section_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_id ON nodes(project_id, id)")
                else:
                    # 旧结构：只有 project_id 和 section_id
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_project ON nodes(project_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_section ON nodes(project_id, section_id)")
            except sqlite3.OperationalError:
                # 表不存在，使用默认索引
                pass
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_project ON edges(project_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(project_id, source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(project_id, target)")
            
            conn.commit()
        finally:
            conn.close()
    
    
    def _load_project(self, project_id: str) -> Optional[Project]:
        """从数据库加载单个项目"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 加载项目基本信息
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            project_row = cursor.fetchone()
            if not project_row:
                return None
            
            # 加载章节
            cursor.execute("""
                SELECT * FROM chapters 
                WHERE project_id = ? 
                ORDER BY position, id
            """, (project_id,))
            chapter_rows = cursor.fetchall()
            
            chapters = []
            for ch_row in chapter_rows:
                chapter_id = ch_row['id']
                
                # 加载部分（通过 project_id 和 chapter_id 双重过滤）
                cursor.execute("""
                    SELECT * FROM sections 
                    WHERE project_id = ? AND chapter_id = ? 
                    ORDER BY position, id
                """, (project_id, chapter_id))
                section_rows = cursor.fetchall()
                
                sections = []
                for sec_row in section_rows:
                    section_id = sec_row['id']
                    
                    # 加载节点（使用复合主键查询：project_id, chapter_id, section_id）
                    cursor.execute("""
                        SELECT * FROM nodes 
                        WHERE project_id = ? AND chapter_id = ? AND section_id = ? 
                        ORDER BY position, id
                    """, (project_id, chapter_id, section_id))
                    node_rows = cursor.fetchall()
                    
                    nodes = []
                    for row in node_rows:
                        # 处理可能不存在的 x, y 列（兼容旧数据库）
                        x_value = None
                        y_value = None
                        try:
                            if 'x' in row.keys() and row['x'] is not None:
                                x_value = float(row['x'])
                        except (KeyError, IndexError):
                            pass
                        try:
                            if 'y' in row.keys() and row['y'] is not None:
                                y_value = float(row['y'])
                        except (KeyError, IndexError):
                            pass
                        
                        nodes.append(Node(
                            id=row['id'],
                            name=row['name'],
                            content=row['content'] or '',
                            position=float(row['position']) if row['position'] is not None else None,
                            x=x_value,
                            y=y_value
                        ))
                    
                    sections.append(Section(
                        id=section_id,
                        name=sec_row['name'],
                        nodes=nodes
                    ))
                
                chapters.append(Chapter(
                    id=chapter_id,
                    name=ch_row['name'],
                    sections=sections
                ))
            
            # 加载边
            cursor.execute("""
                SELECT source, target, label 
                FROM edges 
                WHERE project_id = ?
            """, (project_id,))
            edge_rows = cursor.fetchall()
            
            edges = [
                Edge(
                    source=row['source'],
                    target=row['target'],
                    label=row['label'] or ''
                )
                for row in edge_rows
            ]
            
            return Project(
                id=project_row['id'],
                name=project_row['name'],
                created_at=project_row['created_at'],
                updated_at=project_row['updated_at'],
                chapters=chapters,
                edges=edges
            )
        finally:
            conn.close()
    
    def get_all(self) -> Dict[str, Project]:
        """获取所有项目"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM projects")
            project_ids = [row['id'] for row in cursor.fetchall()]
            
            projects = {}
            for project_id in project_ids:
                project = self._load_project(project_id)
                if project:
                    projects[project_id] = project
            
            return projects
        finally:
            conn.close()
    
    def get(self, project_id: str) -> Project:
        """获取单个项目"""
        project = self._load_project(project_id)
        if not project:
            raise KeyError(f"Project {project_id} not found")
        return project
    
    def add(self, project: Project) -> None:
        """添加项目"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 插入项目
            cursor.execute("""
                INSERT INTO projects (id, name, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (project.id, project.name, project.created_at, project.updated_at))
            
            # 插入章节、部分和节点
            self._save_project_structure(cursor, project)
            
            # 插入边
            for edge in project.edges:
                cursor.execute("""
                    INSERT OR REPLACE INTO edges (project_id, source, target, label)
                    VALUES (?, ?, ?, ?)
                """, (project.id, edge.source, edge.target, edge.label or ''))
            
            conn.commit()
        finally:
            conn.close()
    
    def update(self, project: Project) -> None:
        """更新项目"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 检查项目是否存在
            cursor.execute("SELECT id FROM projects WHERE id = ?", (project.id,))
            if not cursor.fetchone():
                raise KeyError(f"Project {project.id} not found")
            
            # 更新项目基本信息
            cursor.execute("""
                UPDATE projects 
                SET name = ?, updated_at = ?
                WHERE id = ?
            """, (project.name, project.updated_at, project.id))
            
            # 删除旧的结构数据（通过 project_id 直接删除，更高效且安全）
            # 先删除边，避免外键约束问题
            cursor.execute("DELETE FROM edges WHERE project_id = ?", (project.id,))
            
            # 删除节点（直接通过 project_id）
            cursor.execute("DELETE FROM nodes WHERE project_id = ?", (project.id,))
            
            # 删除部分（直接通过 project_id）
            cursor.execute("DELETE FROM sections WHERE project_id = ?", (project.id,))
            
            # 删除章节
            cursor.execute("DELETE FROM chapters WHERE project_id = ?", (project.id,))
            
            # 重新插入结构数据
            self._save_project_structure(cursor, project)
            
            # 插入边
            for edge in project.edges:
                cursor.execute("""
                    INSERT INTO edges (project_id, source, target, label)
                    VALUES (?, ?, ?, ?)
                """, (project.id, edge.source, edge.target, edge.label or ''))
            
            # 提交事务
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error updating project {project.id}: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            conn.close()
    
    def _save_project_structure(self, cursor, project: Project):
        """保存项目结构（章节、部分、节点）"""
        total_nodes = 0
        saved_node_ids = []
        for ch_idx, chapter in enumerate(project.chapters):
            # 插入章节（使用复合主键：project_id, id）
            cursor.execute("""
                INSERT OR REPLACE INTO chapters (project_id, id, name, position)
                VALUES (?, ?, ?, ?)
            """, (project.id, chapter.id, chapter.name, ch_idx))
            
            for sec_idx, section in enumerate(chapter.sections):
                # 插入部分（使用复合主键：project_id, chapter_id, id）
                cursor.execute("""
                    INSERT OR REPLACE INTO sections (project_id, chapter_id, id, name, position)
                    VALUES (?, ?, ?, ?, ?)
                """, (project.id, chapter.id, section.id, section.name, sec_idx))
                
                for node_idx, node in enumerate(section.nodes):
                    # 插入节点（使用复合主键：project_id, chapter_id, section_id, id）
                    # 使用节点的 position 字段，如果为 None 则使用索引
                    node_position = node.position if node.position is not None else float(node_idx)
                    cursor.execute("""
                        INSERT OR REPLACE INTO nodes (project_id, chapter_id, section_id, id, name, content, position, x, y)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (project.id, chapter.id, section.id, node.id, node.name, node.content or '', node_position, node.x, node.y))
                    total_nodes += 1
                    saved_node_ids.append(node.id)
        
    
    def delete(self, project_id: str) -> None:
        """删除项目（级联删除会自动处理相关数据）"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
        finally:
            conn.close()
    
    def exists(self, project_id: str) -> bool:
        """检查项目是否存在"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()
    
    def migrate_from_json(self, json_file: Path = None):
        """从 JSON 文件迁移数据到 SQLite"""
        json_file = json_file or settings.data_file
        if not json_file.exists():
            print(f"JSON file not found: {json_file}")
            return
        
        print(f"Migrating data from {json_file} to SQLite...")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 兼容旧格式
            for project_id, project_data in data.items():
                if 'edges' in project_data and project_data['edges']:
                    if isinstance(project_data['edges'][0], list):
                        project_data['edges'] = [
                            {'source': e[0], 'target': e[1], 'label': ''}
                            for e in project_data['edges']
                        ]
                
                project = Project(**project_data)
                self.add(project)
                print(f"Migrated project: {project.name}")
            
            print(f"Migration completed! {len(data)} project(s) migrated.")
        except Exception as e:
            print(f"Migration failed: {e}")
            raise


# 全局存储实例
storage = Storage()

# 如果 JSON 文件存在但数据库为空，自动迁移
if settings.data_file.exists() and not storage.get_all():
    try:
        storage.migrate_from_json()
    except Exception as e:
        print(f"Auto-migration failed: {e}")
