"""
D3.js Service Data Models
Type-safe models for chart configurations, data, and results.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ChartType(Enum):
    """Supported chart types."""
    SUNBURST = "sunburst"
    ICICLE = "icicle" 
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    TREEMAP = "treemap"
    FORCE_DIRECTED = "force_directed"
    HIERARCHY = "hierarchy"

class DataFormat(Enum):
    """Supported data formats."""
    HIERARCHICAL = "hierarchical"
    TABULAR = "tabular"
    NETWORK = "network"
    TIME_SERIES = "time_series"

@dataclass
class ChartDimensions:
    """Chart dimensions and margins."""
    width: int = 800
    height: int = 600
    margin: Dict[str, int] = field(default_factory=lambda: {
        "top": 20, "right": 20, "bottom": 40, "left": 40
    })

@dataclass
class ChartColors:
    """Chart color configuration."""
    scheme: str = "d3.schemeCategory10"  # D3 color scheme
    custom_colors: Optional[List[str]] = None
    background: str = "#ffffff"
    text: str = "#000000"

@dataclass
class ChartInteraction:
    """Chart interaction settings."""
    hover_enabled: bool = True
    click_enabled: bool = True
    zoom_enabled: bool = False
    brush_enabled: bool = False
    tooltip_enabled: bool = True

@dataclass
class ChartAnimation:
    """Chart animation settings."""
    enabled: bool = True
    duration: int = 750  # milliseconds
    easing: str = "d3.easeLinear"
    delay: int = 0

@dataclass
class ChartConfig:
    """Complete chart configuration."""
    chart_type: ChartType
    title: str
    dimensions: ChartDimensions = field(default_factory=ChartDimensions)
    colors: ChartColors = field(default_factory=ChartColors)
    interaction: ChartInteraction = field(default_factory=ChartInteraction)
    animation: ChartAnimation = field(default_factory=ChartAnimation)
    data_format: DataFormat = DataFormat.TABULAR
    custom_options: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "chart_type": self.chart_type.value,
            "title": self.title,
            "dimensions": {
                "width": self.dimensions.width,
                "height": self.dimensions.height,
                "margin": self.dimensions.margin
            },
            "colors": {
                "scheme": self.colors.scheme,
                "custom_colors": self.colors.custom_colors,
                "background": self.colors.background,
                "text": self.colors.text
            },
            "interaction": {
                "hover_enabled": self.interaction.hover_enabled,
                "click_enabled": self.interaction.click_enabled,
                "zoom_enabled": self.interaction.zoom_enabled,
                "brush_enabled": self.interaction.brush_enabled,
                "tooltip_enabled": self.interaction.tooltip_enabled
            },
            "animation": {
                "enabled": self.animation.enabled,
                "duration": self.animation.duration,
                "easing": self.animation.easing,
                "delay": self.animation.delay
            },
            "data_format": self.data_format.value,
            "custom_options": self.custom_options
        }

@dataclass
class ChartData:
    """Chart data container."""
    data: Union[List[Dict[str, Any]], Dict[str, Any]]
    format: DataFormat
    columns: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "data": self.data,
            "format": self.format.value,
            "columns": self.columns,
            "metadata": self.metadata
        }

@dataclass
class ChartResult:
    """Chart generation result."""
    success: bool
    html_content: Optional[str] = None
    chart_id: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "html_content": self.html_content,
            "chart_id": self.chart_id,
            "file_path": self.file_path,
            "error": self.error,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

# Predefined configurations for common chart types
SUNBURST_CONFIG = ChartConfig(
    chart_type=ChartType.SUNBURST,
    title="Sunburst Chart",
    data_format=DataFormat.HIERARCHICAL,
    dimensions=ChartDimensions(width=600, height=600),
    interaction=ChartInteraction(hover_enabled=True, click_enabled=True),
    custom_options={
        "inner_radius": 0,
        "show_labels": True,
        "show_percentages": True
    }
)

ICICLE_CONFIG = ChartConfig(
    chart_type=ChartType.ICICLE,
    title="Icicle Chart", 
    data_format=DataFormat.HIERARCHICAL,
    dimensions=ChartDimensions(width=800, height=400),
    interaction=ChartInteraction(hover_enabled=True, click_enabled=True),
    custom_options={
        "show_breadcrumbs": True,
        "show_percentages": True
    }
) 