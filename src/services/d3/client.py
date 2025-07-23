"""
D3.js Visualization Service Client
Professional service for generating dynamic D3.js charts and visualizations.
"""

import os
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

from ..base_service import BaseService
from .models import ChartConfig, ChartData, ChartResult, ChartType, DataFormat
from .exceptions import D3Error, D3ValidationError, D3RenderError, D3TemplateError
from .templates import ChartTemplateManager

class D3Service(BaseService):
    """
    Professional D3.js visualization service.
    
    Generates interactive charts using D3.js with support for:
    - Sunburst and Icicle charts (hierarchical data)
    - Bar, line, pie charts (tabular data)  
    - Force-directed graphs (network data)
    - Custom visualizations with templates
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize D3 service.
        
        Args:
            config: Service configuration including output paths and CDN settings
        """
        super().__init__(config)
        
        # Configuration
        self.output_dir = Path(config.get('output_dir', 'data/visualizations'))
        self.template_dir = Path(config.get('template_dir', 'src/services/d3/templates'))
        self.d3_version = config.get('d3_version', '7.9.0')
        self.cdn_base = config.get('cdn_base', 'https://d3js.org')
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize template manager
        self.template_manager = ChartTemplateManager(self.template_dir)
        
        self.logger.info(f"D3Service initialized - output: {self.output_dir}")
    
    def create_chart(self, config: ChartConfig, data: ChartData) -> ChartResult:
        """
        Create a D3.js chart with the given configuration and data.
        
        Args:
            config: Chart configuration
            data: Chart data
            
        Returns:
            ChartResult with HTML content and metadata
        """
        try:
            # Validate inputs
            self._validate_config(config)
            self._validate_data(data, config.data_format)
            
            # Generate unique chart ID
            chart_id = f"chart_{uuid.uuid4().hex[:8]}"
            
            # Process data for chart type
            processed_data = self._process_data(data, config)
            
            # Generate HTML content
            html_content = self._generate_html(config, processed_data, chart_id)
            
            # Save to file if requested
            file_path = None
            if self.config.get('save_files', True):
                file_path = self._save_chart(html_content, chart_id)
            
            self.logger.info(f"Chart created successfully: {chart_id}")
            
            return ChartResult(
                success=True,
                html_content=html_content,
                chart_id=chart_id,
                file_path=str(file_path) if file_path else None,
                metadata={
                    "chart_type": config.chart_type.value,
                    "data_points": len(processed_data) if isinstance(processed_data, list) else 1,
                    "dimensions": f"{config.dimensions.width}x{config.dimensions.height}"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Chart creation failed: {str(e)}")
            return ChartResult(
                success=False,
                error=str(e)
            )
    
    def create_sunburst_chart(self, data: Union[Dict, List], title: str = "Sunburst Chart", **kwargs) -> ChartResult:
        """
        Create a sunburst chart for hierarchical data.
        
        Args:
            data: Hierarchical data (nested dict or list of dicts)
            title: Chart title
            **kwargs: Additional configuration options
            
        Returns:
            ChartResult with sunburst visualization
        """
        from .models import SUNBURST_CONFIG
        
        config = SUNBURST_CONFIG
        config.title = title
        
        # Apply custom options
        if kwargs:
            config.custom_options.update(kwargs)
        
        chart_data = ChartData(
            data=data,
            format=DataFormat.HIERARCHICAL
        )
        
        return self.create_chart(config, chart_data)
    
    def create_icicle_chart(self, data: Union[Dict, List], title: str = "Icicle Chart", **kwargs) -> ChartResult:
        """
        Create an icicle chart for hierarchical data.
        
        Args:
            data: Hierarchical data (nested dict or list of dicts)
            title: Chart title
            **kwargs: Additional configuration options
            
        Returns:
            ChartResult with icicle visualization
        """
        from .models import ICICLE_CONFIG
        
        config = ICICLE_CONFIG
        config.title = title
        
        # Apply custom options
        if kwargs:
            config.custom_options.update(kwargs)
        
        chart_data = ChartData(
            data=data,
            format=DataFormat.HIERARCHICAL
        )
        
        return self.create_chart(config, chart_data)
    
    def create_bar_chart(self, data: List[Dict], x_field: str, y_field: str, title: str = "Bar Chart", **kwargs) -> ChartResult:
        """
        Create a bar chart for tabular data.
        
        Args:
            data: List of data records
            x_field: Field name for x-axis
            y_field: Field name for y-axis  
            title: Chart title
            **kwargs: Additional configuration options
            
        Returns:
            ChartResult with bar chart visualization
        """
        config = ChartConfig(
            chart_type=ChartType.BAR_CHART,
            title=title,
            data_format=DataFormat.TABULAR,
            custom_options={
                "x_field": x_field,
                "y_field": y_field,
                **kwargs
            }
        )
        
        chart_data = ChartData(
            data=data,
            format=DataFormat.TABULAR,
            columns=[x_field, y_field]
        )
        
        return self.create_chart(config, chart_data)
    
    def _validate_config(self, config: ChartConfig) -> None:
        """Validate chart configuration."""
        if not isinstance(config, ChartConfig):
            raise D3ValidationError("Config must be a ChartConfig instance")
        
        if not config.title:
            raise D3ValidationError("Chart title is required")
        
        if config.dimensions.width <= 0 or config.dimensions.height <= 0:
            raise D3ValidationError("Chart dimensions must be positive")
    
    def _validate_data(self, data: ChartData, expected_format: DataFormat) -> None:
        """Validate chart data."""
        if not isinstance(data, ChartData):
            raise D3ValidationError("Data must be a ChartData instance")
        
        if data.format != expected_format:
            raise D3ValidationError(f"Data format mismatch: expected {expected_format.value}, got {data.format.value}")
        
        if not data.data:
            raise D3ValidationError("Chart data cannot be empty")
    
    def _process_data(self, data: ChartData, config: ChartConfig) -> Union[Dict, List]:
        """Process and transform data for the specific chart type."""
        try:
            if config.chart_type in [ChartType.SUNBURST, ChartType.ICICLE]:
                return self._process_hierarchical_data(data.data)
            elif config.chart_type == ChartType.BAR_CHART:
                return self._process_tabular_data(data.data, config)
            else:
                return data.data
                
        except Exception as e:
            raise D3RenderError(f"Data processing failed: {str(e)}")
    
    def _process_hierarchical_data(self, data: Union[Dict, List]) -> Dict:
        """Process hierarchical data for sunburst/icicle charts."""
        if isinstance(data, dict):
            return data
        elif isinstance(data, list):
            # Convert list to hierarchical structure
            return {"name": "root", "children": data}
        else:
            raise D3ValidationError("Hierarchical data must be dict or list")
    
    def _process_tabular_data(self, data: List[Dict], config: ChartConfig) -> List[Dict]:
        """Process tabular data for bar/line/pie charts."""
        if not isinstance(data, list):
            raise D3ValidationError("Tabular data must be a list of dictionaries")
        
        # Validate required fields exist
        x_field = config.custom_options.get('x_field')
        y_field = config.custom_options.get('y_field')
        
        if x_field and y_field:
            for record in data:
                if x_field not in record or y_field not in record:
                    raise D3ValidationError(f"Required fields {x_field}, {y_field} missing from data")
        
        return data
    
    def _generate_html(self, config: ChartConfig, data: Union[Dict, List], chart_id: str) -> str:
        """Generate complete HTML content for the chart."""
        try:
            # Get chart template
            template = self.template_manager.get_template(config.chart_type)
            
            # Prepare template context
            context = {
                "chart_id": chart_id,
                "config": config.to_dict(),
                "data": json.dumps(data, default=str),
                "d3_version": self.d3_version,
                "cdn_base": self.cdn_base,
                "timestamp": datetime.now().isoformat()
            }
            
            # Render template
            html_content = template.render(**context)
            
            return html_content
            
        except Exception as e:
            raise D3RenderError(f"HTML generation failed: {str(e)}")
    
    def _save_chart(self, html_content: str, chart_id: str) -> Path:
        """Save chart HTML to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{chart_id}_{timestamp}.html"
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Chart saved to: {file_path}")
            return file_path
            
        except Exception as e:
            raise D3RenderError(f"Failed to save chart: {str(e)}")
    
    def list_chart_types(self) -> List[str]:
        """Get list of supported chart types."""
        return [chart_type.value for chart_type in ChartType]
    
    def get_chart_template(self, chart_type: ChartType) -> str:
        """Get the template content for a specific chart type."""
        return self.template_manager.get_template_source(chart_type)
    
    def authenticate(self) -> bool:
        """D3 service doesn't require authentication."""
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Check D3 service health."""
        return {
            "status": "healthy",
            "output_dir": str(self.output_dir),
            "template_dir": str(self.template_dir),
            "d3_version": self.d3_version
        } 