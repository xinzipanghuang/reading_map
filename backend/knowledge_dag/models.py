"""Pydantic 数据模型定义"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class Node(BaseModel):
    """知识节点模型"""
    id: str = Field(..., description="节点唯一标识")
    name: str = Field(..., min_length=1, max_length=200, description="节点名称")
    content: str = Field(default="", description="节点内容/笔记")
    position: Optional[float] = Field(default=None, description="节点在section中的位置索引（用于排序）")
    x: Optional[float] = Field(default=None, description="节点在section中的X坐标（像素）")
    y: Optional[float] = Field(default=None, description="节点在section中的Y坐标（像素）")
    width: Optional[float] = Field(default=None, description="节点宽度（像素，自由布局时使用）")
    height: Optional[float] = Field(default=None, description="节点高度（像素，自由布局时使用）")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证节点名称"""
        if not v.strip():
            raise ValueError("节点名称不能为空")
        return v.strip()


class Section(BaseModel):
    """部分模型"""
    id: str = Field(..., description="部分唯一标识")
    name: str = Field(..., min_length=1, max_length=200, description="部分名称")
    nodes: List[Node] = Field(default_factory=list, description="节点列表")
    position: Optional[float] = Field(default=None, description="部分在章节中的位置索引（用于排序）")
    x: Optional[float] = Field(default=None, description="部分在章节中的X坐标（像素）")
    y: Optional[float] = Field(default=None, description="部分在章节中的Y坐标（像素）")
    width: Optional[float] = Field(default=None, description="部分的宽度（像素，自由布局时使用）")
    height: Optional[float] = Field(default=None, description="部分的高度（像素，自由布局时使用）")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证部分名称"""
        if not v.strip():
            raise ValueError("部分名称不能为空")
        return v.strip()


class Chapter(BaseModel):
    """章节模型"""
    id: str = Field(..., description="章节唯一标识")
    name: str = Field(..., min_length=1, max_length=200, description="章节名称")
    sections: List[Section] = Field(default_factory=list, description="部分列表")
    layout: Optional[str] = Field(default='row', description="布局方式：'row' 行排列，'column' 列排列，'free' 自由布局")
    x: Optional[float] = Field(default=None, description="章节在项目中的X坐标（像素）")
    y: Optional[float] = Field(default=None, description="章节在项目中的Y坐标（像素）")
    width: Optional[float] = Field(default=None, description="章节的宽度（像素，自由布局时使用）")
    height: Optional[float] = Field(default=None, description="章节的高度（像素，自由布局时使用）")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证章节名称"""
        if not v.strip():
            raise ValueError("章节名称不能为空")
        return v.strip()
    
    @field_validator('layout')
    @classmethod
    def validate_layout(cls, v: Optional[str]) -> str:
        """验证布局方式"""
        if v is None:
            return 'row'
        if v not in ['row', 'column', 'free']:
            raise ValueError("布局方式必须是 'row'、'column' 或 'free'")
        return v


class Edge(BaseModel):
    """边模型（连接）"""
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    label: str = Field(default="", description="边的标签/名称")
    
    @field_validator('source', 'target')
    @classmethod
    def validate_node_id(cls, v: str) -> str:
        """验证节点ID"""
        if not v.strip():
            raise ValueError("节点ID不能为空")
        return v.strip()


class Project(BaseModel):
    """项目模型"""
    id: str = Field(..., description="项目唯一标识")
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    chapters: List[Chapter] = Field(default_factory=list, description="章节列表")
    edges: List[Edge] = Field(
        default_factory=list, 
        description="边列表，包含源节点、目标节点和标签"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证项目名称"""
        if not v.strip():
            raise ValueError("项目名称不能为空")
        return v.strip()
    
    @field_validator('edges')
    @classmethod
    def validate_edges(cls, v: List[Edge]) -> List[Edge]:
        """验证边的格式"""
        return v


# --- 请求模型 ---

class CreateProjectRequest(BaseModel):
    """创建项目请求"""
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")


class UpdateProjectRequest(BaseModel):
    """更新项目请求"""
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证项目名称"""
        if not v.strip():
            raise ValueError("项目名称不能为空")
        return v.strip()


class AddChapterRequest(BaseModel):
    """添加章节请求"""
    chapter_name: str = Field(default="", max_length=200, description="章节名称，为空时使用默认名称")
    
    @field_validator('chapter_name')
    @classmethod
    def validate_chapter_name(cls, v: str) -> str:
        """验证章节名称，允许为空"""
        return v.strip() if v else ""


class UpdateChapterRequest(BaseModel):
    """更新章节请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="章节名称")
    layout: Optional[str] = Field(None, description="布局方式：'row' 行排列，'column' 列排列，'free' 自由布局")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """验证章节名称"""
        if v is not None and not v.strip():
            raise ValueError("章节名称不能为空")
        return v.strip() if v else None
    
    @field_validator('layout')
    @classmethod
    def validate_layout(cls, v: Optional[str]) -> Optional[str]:
        """验证布局方式"""
        if v is not None and v not in ['row', 'column', 'free']:
            raise ValueError("布局方式必须是 'row'、'column' 或 'free'")
        return v


class UpdateSectionRequest(BaseModel):
    """更新部分请求"""
    name: str = Field(..., min_length=1, max_length=200, description="部分名称")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证部分名称"""
        if not v.strip():
            raise ValueError("部分名称不能为空")
        return v.strip()


class UpdateChapterPositionRequest(BaseModel):
    """更新章节位置请求"""
    chapter_id: Optional[str] = Field(default=None, description="章节ID")
    x: Optional[float] = Field(default=0, description="X坐标（像素）")
    y: Optional[float] = Field(default=0, description="Y坐标（像素）")
    width: Optional[float] = Field(default=None, description="章节宽度（像素）")
    height: Optional[float] = Field(default=None, description="章节高度（像素）")
    
    @field_validator("x", "y", mode="before")
    @classmethod
    def validate_coord(cls, v):
        """验证坐标，转换失败时返回 0"""
        if v is None:
            return 0
        try:
            num = float(v)
            if num != num:  # NaN 检查
                return 0
            return num
        except (TypeError, ValueError):
            return 0

    @field_validator("width", "height", mode="before")
    @classmethod
    def validate_size(cls, v):
        """验证尺寸，转换失败时返回 None"""
        if v is None:
            return None
        try:
            num = float(v)
            if num != num:  # NaN 检查
                return None
            return num
        except (TypeError, ValueError):
            return None


class UpdateSectionPositionRequest(BaseModel):
    """更新部分位置请求"""
    section_id: Optional[str] = Field(default=None, description="部分ID")
    chapter_id: Optional[str] = Field(default=None, description="章节ID")
    # 坐标默认 0，宽高可空
    x: float = Field(default=0, description="X坐标（像素）")
    y: float = Field(default=0, description="Y坐标（像素）")
    width: Optional[float] = Field(default=None, description="部分宽度（像素）")
    height: Optional[float] = Field(default=None, description="部分高度（像素）")

    @field_validator("x", "y", mode="before")
    @classmethod
    def validate_coords(cls, v):
        """验证坐标，转换失败时返回 0"""
        if v is None:
            return 0
        try:
            num = float(v)
            # 检查 NaN
            if num != num:  # NaN 检查
                return 0
            return num
        except (TypeError, ValueError):
            return 0

    @field_validator("width", "height", mode="before")
    @classmethod
    def validate_size(cls, v):
        """验证尺寸，转换失败时返回 None"""
        if v is None:
            return None
        try:
            num = float(v)
            # 检查 NaN
            if num != num:  # NaN 检查
                return None
            return num
        except (TypeError, ValueError):
            return None


class AddSectionRequest(BaseModel):
    """添加部分请求"""
    chapter_id: str = Field(..., description="章节ID")
    section_name: str = Field(default="", max_length=200, description="部分名称，为空时使用默认名称")
    
    @field_validator('section_name')
    @classmethod
    def validate_section_name(cls, v: str) -> str:
        """验证部分名称，允许为空"""
        return v.strip() if v else ""


class AddNodeRequest(BaseModel):
    """添加节点请求"""
    chapter_id: str = Field(..., description="章节ID")
    section_id: str = Field(..., description="部分ID")
    node_name: str = Field(default="", max_length=200, description="节点名称，为空时使用默认名称")
    node_content: str = Field(default="", description="节点内容")
    
    @field_validator('node_name')
    @classmethod
    def validate_node_name(cls, v: str) -> str:
        """验证节点名称，允许为空"""
        return v.strip() if v else ""


class UpdateNodeRequest(BaseModel):
    """更新节点请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="节点名称")
    content: Optional[str] = Field(None, description="节点内容")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """验证节点名称"""
        if v is not None and not v.strip():
            raise ValueError("节点名称不能为空")
        return v.strip() if v else None


class ReorderNodesRequest(BaseModel):
    """重排序节点请求"""
    section_id: str = Field(..., description="部分ID")
    node_ids: List[str] = Field(..., description="节点ID列表，按新顺序排列")

class ReorderSectionsRequest(BaseModel):
    """重排序部分请求"""
    chapter_id: str = Field(..., description="章节ID")
    section_ids: List[str] = Field(..., description="部分ID列表，按新顺序排列")

class ReorderChaptersRequest(BaseModel):
    """重排序章节请求"""
    chapter_ids: List[str] = Field(..., description="章节ID列表，按新顺序排列")


class UpdateNodePositionRequest(BaseModel):
    """更新节点位置请求"""
    node_id: str = Field(..., description="节点ID")
    section_id: str = Field(..., description="部分ID")
    chapter_id: Optional[str] = Field(None, description="章节ID（可选，用于验证）")
    x: float = Field(..., description="X坐标（像素）")
    y: float = Field(..., description="Y坐标（像素）")
    width: Optional[float] = Field(None, description="节点宽度（像素）")
    height: Optional[float] = Field(None, description="节点高度（像素）")


class AddEdgeRequest(BaseModel):
    """添加边请求"""
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    label: str = Field(default="", description="边的标签/名称")
    
    @field_validator('source', 'target')
    @classmethod
    def validate_node_id(cls, v: str) -> str:
        """验证节点ID"""
        if not v.strip():
            raise ValueError("节点ID不能为空")
        return v.strip()


class UpdateEdgeRequest(BaseModel):
    """更新边请求"""
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    label: str = Field(..., max_length=100, description="边的标签/名称")
    
    @field_validator('source', 'target')
    @classmethod
    def validate_node_id(cls, v: str) -> str:
        """验证节点ID"""
        if not v.strip():
            raise ValueError("节点ID不能为空")
        return v.strip()


class GraphAnalysisResponse(BaseModel):
    """图谱分析响应"""
    highlight: List[str] = Field(default_factory=list, description="需要高亮的节点ID列表")
    paths: List[List[str]] = Field(default_factory=list, description="路径列表")
    ancestors: List[str] = Field(default_factory=list, description="祖先节点列表")
    descendants: List[str] = Field(default_factory=list, description="后代节点列表")


class NodeLocationResponse(BaseModel):
    """节点位置响应"""
    chapter_id: str
    chapter_name: str
    section_id: str
    section_name: str
    node: Node
