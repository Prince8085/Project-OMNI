"""
Data analysis tools for Project OMNI - Phase 2.
Provides pandas, numpy, and matplotlib integration.
"""

import logging
from typing import Dict, Any, Optional, List
import os

logger = logging.getLogger(__name__)


class DataAnalysisTools:
    """Tools for data analysis and visualization."""
    
    def __init__(self):
        """Initialize data analysis tools."""
        self.supported_formats = ['.csv', '.xlsx', '.json', '.parquet']
    
    def analyze_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a CSV file and return statistics.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            import pandas as pd
            
            df = pd.read_csv(file_path)
            
            analysis = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'missing_values': df.isnull().sum().to_dict(),
                'summary_stats': df.describe().to_dict()
            }
            
            logger.info(f"Analyzed CSV: {file_path}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing CSV {file_path}: {e}")
            raise
    
    def create_visualization(
        self, 
        data: Any, 
        chart_type: str = 'bar',
        output_path: str = 'chart.png',
        **kwargs
    ) -> str:
        """
        Create a visualization from data.
        
        Args:
            data: Data to visualize (DataFrame, dict, list)
            chart_type: Type of chart ('bar', 'line', 'scatter', 'pie')
            output_path: Where to save the chart
            **kwargs: Additional matplotlib arguments
            
        Returns:
            Path to saved chart
        """
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            
            plt.figure(figsize=kwargs.get('figsize', (10, 6)))
            
            if isinstance(data, pd.DataFrame):
                if chart_type == 'bar':
                    data.plot(kind='bar', **kwargs)
                elif chart_type == 'line':
                    data.plot(kind='line', **kwargs)
                elif chart_type == 'scatter':
                    data.plot(kind='scatter', **kwargs)
                elif chart_type == 'pie':
                    data.plot(kind='pie', **kwargs)
            
            plt.title(kwargs.get('title', 'Data Visualization'))
            plt.xlabel(kwargs.get('xlabel', ''))
            plt.ylabel(kwargs.get('ylabel', ''))
            plt.tight_layout()
            plt.savefig(output_path, dpi=kwargs.get('dpi', 300))
            plt.close()
            
            logger.info(f"Created {chart_type} chart: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            raise
    
    def process_excel(self, file_path: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an Excel file.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Specific sheet to read (None = all sheets)
            
        Returns:
            Dictionary with sheet data
        """
        try:
            import pandas as pd
            
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                return {sheet_name: df.to_dict()}
            else:
                excel_file = pd.ExcelFile(file_path)
                result = {}
                for sheet in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    result[sheet] = {
                        'rows': len(df),
                        'columns': list(df.columns),
                        'preview': df.head().to_dict()
                    }
                return result
                
        except Exception as e:
            logger.error(f"Error processing Excel {file_path}: {e}")
            raise
