"""
Chart Template Manager
Manages D3.js chart templates and rendering.
"""

import os
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, Template

from ..models import ChartType
from ..exceptions import D3TemplateError

class ChartTemplateManager:
    """Manages D3.js chart templates."""
    
    def __init__(self, template_dir: Path):
        """Initialize template manager."""
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
    
    def get_template(self, chart_type: ChartType) -> Template:
        """Get template for specific chart type."""
        template_name = f"{chart_type.value}.html"
        
        try:
            return self.env.get_template(template_name)
        except Exception as e:
            raise D3TemplateError(f"Template not found: {template_name} - {str(e)}")
    
    def get_template_source(self, chart_type: ChartType) -> str:
        """Get raw template source code."""
        template_path = self.template_dir / f"{chart_type.value}.html"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise D3TemplateError(f"Cannot read template: {template_path} - {str(e)}")
    
    def list_templates(self) -> list:
        """List available templates."""
        templates = []
        for file in self.template_dir.glob("*.html"):
            templates.append(file.stem)
        return templates 