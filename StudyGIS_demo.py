"""
StudyGIS_demo - 简单的GIS系统课程作业
集成Folium交互式地图和Plotly 3D可视化功能
"""
import sys
import os
import logging
import tempfile
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QTextEdit, QTreeWidget, 
                             QTreeWidgetItem, QTabWidget, QLabel, QMenuBar, 
                             QToolBar, QAction, QMessageBox, QFileDialog,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QCheckBox, QSlider, QSpinBox, QDialog,
                             QLineEdit)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QTimer
from PyQt5.QtGui import QIcon
import pandas as pd
import numpy as np
import folium
from folium import plugins
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 尝试导入Plotly (可选)
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.offline import plot
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# 尝试导入数据库模块 (可选)
try:
    from src.database_config import DatabaseManager, initialize_database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# 配置
APP_NAME = "StudyGIS_demo"
APP_VERSION = "1.0.0"
BASE_DIR = Path(__file__).parent

def setup_logging():
    """设置日志"""
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'app_enhanced_3d.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

class DatabaseDialog(QDialog):
    """数据库操作对话框"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("数据库操作")
        self.setGeometry(200, 200, 800, 600)
        self.current_data = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 查询标签页
        self.query_tab = QWidget()
        self.init_query_tab()
        self.tab_widget.addTab(self.query_tab, "查询数据")
        
        # 导入标签页
        self.import_tab = QWidget()
        self.init_import_tab()
        self.tab_widget.addTab(self.import_tab, "导入数据")
        
        # 导出标签页
        self.export_tab = QWidget()
        self.init_export_tab()
        self.tab_widget.addTab(self.export_tab, "导出数据")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def init_query_tab(self):
        """初始化查询标签页"""
        layout = QVBoxLayout()
        
        # 查询控制
        query_control = QHBoxLayout()
        query_control.addWidget(QLabel("选择表:"))
        
        self.table_combo = QComboBox()
        self.table_combo.addItems(["point_features", "line_features", "polygon_features"])
        query_control.addWidget(self.table_combo)
        
        self.query_btn = QPushButton("查询")
        self.query_btn.clicked.connect(self.query_data)
        query_control.addWidget(self.query_btn)
        
        self.load_to_map_btn = QPushButton("加载到地图")
        self.load_to_map_btn.clicked.connect(self.load_to_map)
        query_control.addWidget(self.load_to_map_btn)
        
        layout.addLayout(query_control)
        
        # 数据表格
        self.data_table = QTableWidget()
        layout.addWidget(self.data_table)
        
        # 状态信息
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        self.query_tab.setLayout(layout)
    
    def init_import_tab(self):
        """初始化导入标签页"""
        layout = QVBoxLayout()
        
        # 文件选择
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("选择文件:"))
        
        self.file_path_edit = QLineEdit()
        file_layout.addWidget(self.file_path_edit)
        
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        
        layout.addLayout(file_layout)
        
        # 导入选项
        options_layout = QHBoxLayout()
        options_layout.addWidget(QLabel("目标表:"))
        
        self.target_table_combo = QComboBox()
        self.target_table_combo.addItems(["自动选择", "point_features", "line_features", "polygon_features"])
        options_layout.addWidget(self.target_table_combo)
        
        self.import_btn = QPushButton("导入")
        self.import_btn.clicked.connect(self.import_data)
        options_layout.addWidget(self.import_btn)
        
        layout.addLayout(options_layout)
        
        # 导入日志
        self.import_log = QTextEdit()
        self.import_log.setMaximumHeight(200)
        layout.addWidget(self.import_log)
        
        self.import_tab.setLayout(layout)
    
    def init_export_tab(self):
        """初始化导出标签页"""
        layout = QVBoxLayout()
        
        # 导出控制
        export_control = QHBoxLayout()
        export_control.addWidget(QLabel("选择表:"))
        
        self.export_table_combo = QComboBox()
        self.export_table_combo.addItems(["point_features", "line_features", "polygon_features"])
        export_control.addWidget(self.export_table_combo)
        
        self.export_btn = QPushButton("导出为GeoJSON")
        self.export_btn.clicked.connect(self.export_data)
        export_control.addWidget(self.export_btn)
        
        layout.addLayout(export_control)
        
        # 导出选项
        options_layout = QVBoxLayout()
        self.include_geom_cb = QCheckBox("包含几何信息")
        self.include_geom_cb.setChecked(True)
        options_layout.addWidget(self.include_geom_cb)
        
        layout.addLayout(options_layout)
        
        # 导出日志
        self.export_log = QTextEdit()
        layout.addWidget(self.export_log)
        
        self.export_tab.setLayout(layout)
    
    def query_data(self):
        """查询数据"""
        if not self.db_manager:
            self.status_label.setText("数据库未连接")
            return
        
        try:
            table_name = self.table_combo.currentText()
            self.status_label.setText(f"正在查询 {table_name}...")
            
            df = self.db_manager.query_spatial_data(table_name, limit=100)
            
            if not df.empty:
                # 显示数据
                self.data_table.setRowCount(len(df))
                self.data_table.setColumnCount(len(df.columns))
                self.data_table.setHorizontalHeaderLabels(df.columns.tolist())
                
                for i, row in df.iterrows():
                    for j, value in enumerate(row):
                        self.data_table.setItem(i, j, QTableWidgetItem(str(value)))
                
                self.status_label.setText(f"查询到 {len(df)} 条记录")
                self.current_data = df
            else:
                self.status_label.setText("没有查询到数据")
                self.current_data = None
                
                # 提供更多信息
                try:
                    # 检查表是否存在
                    count_result = self.db_manager.execute_query(f'SELECT COUNT(*) FROM {table_name}')
                    if count_result and len(count_result) > 0:
                        count = count_result[0].get('count', 0) if isinstance(count_result[0], dict) else count_result[0][0]
                        if count == 0:
                            self.status_label.setText(f"表 {table_name} 存在但为空")
                        else:
                            self.status_label.setText(f"表 {table_name} 有 {count} 条记录，但查询失败")
                except Exception as check_error:
                    self.status_label.setText(f"表 {table_name} 可能不存在或无法访问")
                
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg.lower():
                self.status_label.setText(f"表 {table_name} 不存在")
            elif "connection" in error_msg.lower():
                self.status_label.setText("数据库连接失败")
            else:
                self.status_label.setText(f"查询失败: {error_msg}")
            
            # 在数据表中显示错误信息
            self.data_table.setRowCount(1)
            self.data_table.setColumnCount(1)
            self.data_table.setHorizontalHeaderLabels(["错误信息"])
            self.data_table.setItem(0, 0, QTableWidgetItem(f"查询失败: {error_msg}"))
    
    def load_to_map(self):
        """加载数据到地图"""
        if hasattr(self, 'current_data') and self.current_data is not None:
            # 发送信号给主窗口加载数据
            self.accept()  # 关闭对话框
            # 这里需要主窗口处理数据加载
        else:
            self.status_label.setText("没有数据可加载")
    
    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "CSV文件 (*.csv);;GeoJSON文件 (*.geojson)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def import_data(self):
        """导入数据"""
        if not self.db_manager:
            self.import_log.append("错误: 数据库未连接")
            return
        
        file_path = self.file_path_edit.text()
        if not file_path:
            self.import_log.append("错误: 请选择文件")
            return
        
        try:
            self.import_log.append(f"开始导入文件: {file_path}")
            
            if file_path.endswith('.csv'):
                self.import_log.append("检测到CSV文件，导入到point_features表")
                success = self.db_manager.import_csv_to_postgis(file_path, 'point_features')
            elif file_path.endswith('.geojson'):
                self.import_log.append("检测到GeoJSON文件，自动选择目标表")
                success = self.db_manager.import_geojson_to_postgis(file_path, 'auto')
            else:
                self.import_log.append("错误: 不支持的文件格式")
                return
            
            if success:
                self.import_log.append(f"✅ 成功: 文件 {file_path} 导入完成")
                
                # 检查导入结果
                if file_path.endswith('.geojson'):
                    # 检查各表的数据量
                    tables = ['point_features', 'line_features', 'polygon_features']
                    for table in tables:
                        try:
                            count_result = self.db_manager.execute_query(f'SELECT COUNT(*) FROM {table}')
                            count = count_result[0][0] if count_result else 0
                            if count > 0:
                                self.import_log.append(f"  {table}: {count} 条记录")
                        except Exception as e:
                            self.import_log.append(f"  检查{table}失败: {e}")
            else:
                self.import_log.append(f"❌ 失败: 文件 {file_path} 导入失败")
                
        except Exception as e:
            self.import_log.append(f"❌ 错误: {str(e)}")
            import traceback
            self.import_log.append(f"详细错误: {traceback.format_exc()}")
    
    def export_data(self):
        """导出数据"""
        if not self.db_manager:
            self.export_log.append("错误: 数据库未连接")
            return
        
        table_name = self.export_table_combo.currentText()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", f"{table_name}.geojson", "GeoJSON文件 (*.geojson)"
        )
        
        if file_path:
            try:
                success = self.db_manager.export_layer_to_geojson(table_name, file_path)
                if success:
                    self.export_log.append(f"成功: 数据已导出到 {file_path}")
                else:
                    self.export_log.append(f"失败: 导出失败")
            except Exception as e:
                self.export_log.append(f"错误: {str(e)}")

class StatisticsDialog(QDialog):
    """统计图表对话框"""
    
    def __init__(self, data_layers, parent=None):
        super().__init__(parent)
        self.data_layers = data_layers
        self.setWindowTitle("数据统计分析")
        self.setGeometry(200, 200, 800, 600)
        
        # 为3D图表准备文件路径
        self.temp_dir = tempfile.mkdtemp()
        self.plotly_file = os.path.join(self.temp_dir, "stats_3d.html")
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 图层选择
        layer_layout = QHBoxLayout()
        layer_layout.addWidget(QLabel("选择图层:"))
        self.layer_combo = QComboBox()
        for layer in self.data_layers:
            self.layer_combo.addItem(layer['name'])
        self.layer_combo.currentTextChanged.connect(self.update_statistics)
        layer_layout.addWidget(self.layer_combo)
        
        # 图表类型选择
        chart_layout = QHBoxLayout()
        chart_layout.addWidget(QLabel("图表类型:"))
        self.chart_combo = QComboBox()
        chart_types = ["柱状图", "饼图", "散点图", "直方图"]
        if PLOTLY_AVAILABLE:
            chart_types.extend(["3D散点图"])  # 只保留3D散点图
        self.chart_combo.addItems(chart_types)
        self.chart_combo.currentTextChanged.connect(self.update_statistics)
        chart_layout.addWidget(self.chart_combo)
        
        layout.addLayout(layer_layout)
        layout.addLayout(chart_layout)
        
        # 图表显示区域 - 支持2D和3D
        self.chart_stack = QTabWidget()
        
        # 2D图表标签页
        self.chart_2d_widget = QWidget()
        chart_2d_layout = QVBoxLayout()
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        chart_2d_layout.addWidget(self.canvas)
        self.chart_2d_widget.setLayout(chart_2d_layout)
        self.chart_stack.addTab(self.chart_2d_widget, "2D图表")
        
        # 3D图表标签页
        if PLOTLY_AVAILABLE:
            self.chart_3d_widget = QWidget()
            chart_3d_layout = QVBoxLayout()
            self.web_view = QWebEngineView()
            chart_3d_layout.addWidget(self.web_view)
            self.chart_3d_widget.setLayout(chart_3d_layout)
            self.chart_stack.addTab(self.chart_3d_widget, "3D图表")
        
        layout.addWidget(self.chart_stack)
        
        # 统计信息文本
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(150)
        layout.addWidget(self.stats_text)
        
        self.setLayout(layout)
        
        # 初始化显示
        if self.data_layers:
            self.update_statistics()
    
    def update_statistics(self):
        """更新统计信息"""
        if not self.data_layers:
            return
            
        layer_name = self.layer_combo.currentText()
        chart_type = self.chart_combo.currentText()
        
        # 找到对应图层
        current_layer = None
        for layer in self.data_layers:
            if layer['name'] == layer_name:
                current_layer = layer
                break
        
        if not current_layer:
            return
            
        data = current_layer['data']
        
        # 清除之前的图表
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # 根据图表类型绘制
        try:
            if chart_type == "柱状图":
                self.draw_bar_chart(ax, data)
            elif chart_type == "饼图":
                self.draw_pie_chart(ax, data)
            elif chart_type == "散点图":
                self.draw_scatter_chart(ax, data)
            elif chart_type == "直方图":
                self.draw_histogram(ax, data)
            elif chart_type == "3D散点图" and PLOTLY_AVAILABLE:
                self.draw_3d_scatter(data)
                return  # 3D图表不使用matplotlib
        except Exception as e:
            ax.text(0.5, 0.5, f"绘图错误: {str(e)}", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes)
        
        self.canvas.draw()
        
        # 更新统计文本
        self.update_stats_text(data)
    
    def draw_bar_chart(self, ax, data):
        """绘制柱状图"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            if 'name' in data.columns:
                ax.bar(data['name'][:10], data[col][:10])  # 只显示前10个
                ax.set_xlabel('名称')
                ax.set_ylabel(col)
                ax.set_title(f'{col} 柱状图')
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            else:
                ax.bar(range(len(data[:10])), data[col][:10])
                ax.set_xlabel('索引')
                ax.set_ylabel(col)
                ax.set_title(f'{col} 柱状图')
    
    def draw_pie_chart(self, ax, data):
        """绘制饼图"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        if 'type' in data.columns:
            type_counts = data['type'].value_counts()
            ax.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
            ax.set_title('类型分布饼图')
        elif len(data) <= 10:  # 数据量小时按名称分组
            if 'name' in data.columns:
                ax.pie([1]*len(data), labels=data['name'], autopct='%1.1f%%')
                ax.set_title('数据分布饼图')
    
    def draw_scatter_chart(self, ax, data):
        """绘制散点图"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            x_col, y_col = numeric_cols[0], numeric_cols[1]
            ax.scatter(data[x_col], data[y_col])
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f'{x_col} vs {y_col} 散点图')
    
    def draw_histogram(self, ax, data):
        """绘制直方图"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            ax.hist(data[col].dropna(), bins=20, alpha=0.7)
            ax.set_xlabel(col)
            ax.set_ylabel('频次')
            ax.set_title(f'{col} 直方图')
    
    def draw_3d_scatter(self, data):
        """绘制3D散点图"""
        if not PLOTLY_AVAILABLE:
            QMessageBox.warning(self, "警告", "Plotly未安装，无法显示3D散点图")
            return
        
        # 检查必要的列
        if 'longitude' not in data.columns or 'latitude' not in data.columns:
            QMessageBox.warning(self, "警告", "数据中缺少经纬度列")
            return
        
        # 选择数值列作为Z轴
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col not in ['longitude', 'latitude']]
        
        if not numeric_cols:
            QMessageBox.warning(self, "警告", "没有可用的数值列进行3D可视化")
            return
        
        z_col = numeric_cols[0]  # 使用第一个数值列
        z_data = pd.to_numeric(data[z_col], errors='coerce').fillna(0)
        
        fig = go.Figure(data=go.Scatter3d(
            x=data['longitude'],
            y=data['latitude'],
            z=z_data,
            mode='markers+text',
            marker=dict(
                size=8,
                color=z_data,
                colorscale='Viridis',
                opacity=0.8,
                colorbar=dict(title=z_col)
            ),
            text=data.get('name', ''),
            textposition="top center"
        ))
        
        fig.update_layout(
            title=f"3D散点图 (经度-纬度-{z_col})",
            scene=dict(
                xaxis_title="经度",
                yaxis_title="纬度",
                zaxis_title=z_col,
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            height=500,
            font=dict(family="Microsoft YaHei, Arial", size=12)
        )
        
        plot(fig, filename=self.plotly_file, auto_open=False, 
             config={'displayModeBar': True, 'responsive': True})
        
        self.web_view.setUrl(QUrl.fromLocalFile(self.plotly_file))
        self.chart_stack.setCurrentIndex(1)  # 切换到3D标签页
    
    def draw_3d_bar(self, data):
        """绘制3D柱状图"""
        if not PLOTLY_AVAILABLE:
            QMessageBox.warning(self, "警告", "Plotly未安装，无法显示3D柱状图")
            return
        
        # 检查必要的列
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 1:
            QMessageBox.warning(self, "警告", "没有可用的数值列进行3D可视化")
            return
        
        y_col = numeric_cols[0]
        x_labels = data.get('name', range(len(data)))
        
        fig = go.Figure(data=go.Bar(
            x=x_labels,
            y=data[y_col],
            marker=dict(
                color=data[y_col],
                colorscale='Viridis',
                opacity=0.8
            )
        ))
        
        fig.update_layout(
            title=f"3D柱状图 ({y_col})",
            xaxis_title="名称",
            yaxis_title=y_col,
            height=500,
            font=dict(family="Microsoft YaHei, Arial", size=12)
        )
        
        plot(fig, filename=self.plotly_file, auto_open=False, 
             config={'displayModeBar': True, 'responsive': True})
        
        self.web_view.setUrl(QUrl.fromLocalFile(self.plotly_file))
        self.chart_stack.setCurrentIndex(1)  # 切换到3D标签页
    
    def draw_3d_surface(self, data):
        """绘制3D表面图"""
        if not PLOTLY_AVAILABLE:
            QMessageBox.warning(self, "警告", "Plotly未安装，无法显示3D表面图")
            return
        
        # 检查必要的列
        if 'longitude' not in data.columns or 'latitude' not in data.columns:
            QMessageBox.warning(self, "警告", "数据中缺少经纬度列")
            return
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col not in ['longitude', 'latitude']]
        
        if not numeric_cols:
            QMessageBox.warning(self, "警告", "没有可用的数值列进行3D可视化")
            return
        
        z_col = numeric_cols[0]
        z_data = pd.to_numeric(data[z_col], errors='coerce').fillna(0)
        
        # 创建网格数据
        import numpy as np
        x = np.array(data['longitude'])
        y = np.array(data['latitude'])
        z = np.array(z_data)
        
        fig = go.Figure(data=go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(
                size=5,
                color=z,
                colorscale='Viridis',
                opacity=0.8,
                colorbar=dict(title=z_col)
            )
        ))
        
        fig.update_layout(
            title=f"3D表面图 (经度-纬度-{z_col})",
            scene=dict(
                xaxis_title="经度",
                yaxis_title="纬度",
                zaxis_title=z_col,
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            height=500,
            font=dict(family="Microsoft YaHei, Arial", size=12)
        )
        
        plot(fig, filename=self.plotly_file, auto_open=False, 
             config={'displayModeBar': True, 'responsive': True})
        
        self.web_view.setUrl(QUrl.fromLocalFile(self.plotly_file))
        self.chart_stack.setCurrentIndex(1)  # 切换到3D标签页
    
    def update_stats_text(self, data):
        """更新统计文本信息"""
        stats_text = f"数据统计信息:\n\n"
        stats_text += f"总记录数: {len(data)}\n"
        stats_text += f"列数: {len(data.columns)}\n\n"
        
        # 数值列统计
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            stats_text += f"{col}:\n"
            stats_text += f"  最小值: {data[col].min():.2f}\n"
            stats_text += f"  最大值: {data[col].max():.2f}\n"
            stats_text += f"  平均值: {data[col].mean():.2f}\n"
            stats_text += f"  标准差: {data[col].std():.2f}\n\n"
        
        self.stats_text.setText(stats_text)

class Enhanced3DMapWidget(QWidget):
    """增强的地图组件 - 集成Folium和Plotly 3D"""
    
    def __init__(self):
        super().__init__()
        self.data_layers = []
        self.current_map = None
        self.temp_dir = tempfile.mkdtemp()
        self.map_file = os.path.join(self.temp_dir, "map.html")
        self.plotly_file = os.path.join(self.temp_dir, "plotly_3d.html")
        
        # 地图配置
        self.map_configs = {
            "OpenStreetMap": {
                "tiles": "OpenStreetMap",
                "attr": None
            },
            "卫星地图": {
                "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                "attr": "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
            },
            "地形图": {
                "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}",
                "attr": "Tiles &copy; Esri &mdash; Source: Esri, USGS, NOAA"
            },
            "CartoDB": {
                "tiles": "CartoDB positron",
                "attr": None
            }
        }
        
        # 当前显示模式
        self.current_mode = "2D"  # "2D" 或 "3D"
        
        self.init_ui()
        self.create_initial_map()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 控制面板
        control_panel = self.create_control_panel()
        layout.addLayout(control_panel)
        
        # Web视图
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        self.setLayout(layout)
    
    def create_control_panel(self):
        """创建控制面板"""
        panel = QHBoxLayout()
        
        # 显示模式选择
        panel.addWidget(QLabel("显示模式:"))
        self.mode_combo = QComboBox()
        if PLOTLY_AVAILABLE:
            self.mode_combo.addItems(["2D地图", "3D可视化"])
        else:
            self.mode_combo.addItems(["2D地图"])
        self.mode_combo.currentTextChanged.connect(self.change_display_mode)
        panel.addWidget(self.mode_combo)
        
        # 地图类型选择 (仅2D模式) - 移除地形图
        panel.addWidget(QLabel("地图类型:"))
        self.map_type_combo = QComboBox()
        # 只保留三种地图类型
        map_types = ["OpenStreetMap", "卫星地图", "CartoDB"]
        self.map_type_combo.addItems(map_types)
        self.map_type_combo.currentTextChanged.connect(self.change_map_type)
        panel.addWidget(self.map_type_combo)
        
        # 功能按钮
        self.locate_btn = QPushButton("适应数据")
        self.locate_btn.clicked.connect(self.fit_bounds)
        panel.addWidget(self.locate_btn)
        
        # 移除全屏按钮
        # self.fullscreen_btn = QPushButton("全屏")
        # self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        # panel.addWidget(self.fullscreen_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_map)
        panel.addWidget(self.refresh_btn)
        
        # 统计按钮
        self.stats_btn = QPushButton("统计")
        self.stats_btn.clicked.connect(self.show_statistics)
        panel.addWidget(self.stats_btn)
        
        panel.addStretch()
        return panel
    
    def create_initial_map(self):
        """创建初始地图"""
        # 创建基础地图 - 以中国为中心
        map_config = self.map_configs["OpenStreetMap"]
        if map_config["attr"]:
            self.current_map = folium.Map(
                location=[35.0, 105.0],  # 中国中心
                zoom_start=5,
                tiles=map_config["tiles"],
                attr=map_config["attr"]
            )
        else:
            self.current_map = folium.Map(
                location=[35.0, 105.0],  # 中国中心
                zoom_start=5,
                tiles=map_config["tiles"]
            )
        
        # 添加地图插件
        self.add_map_plugins()
        
        # 添加示例数据
        self.add_sample_data()
        
        # 保存并加载地图
        self.save_and_load_map()
    
    def add_map_plugins(self):
        """添加地图插件"""
        try:
            # 全屏插件
            plugins.Fullscreen().add_to(self.current_map)
            
            # 定位插件
            plugins.LocateControl().add_to(self.current_map)
            
            # 测量插件
            plugins.MeasureControl().add_to(self.current_map)
            
            # 绘图插件 - 移除export功能
            draw = plugins.Draw(export=False)
            draw.add_to(self.current_map)
            
            # 小地图插件
            minimap = plugins.MiniMap()
            self.current_map.add_child(minimap)
        except Exception as e:
            logging.warning(f"添加地图插件时出错: {e}")
    
    def add_sample_data(self):
        """添加示例数据"""
        # 中国主要城市数据
        cities_data = {
            'name': ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆'],
            'longitude': [116.4074, 121.4737, 113.2644, 114.0579, 120.1551, 118.7969, 114.3054, 104.0665, 108.9398, 106.5516],
            'latitude': [39.9042, 31.2304, 23.1291, 22.5431, 30.2741, 32.0603, 30.5928, 30.6598, 34.3416, 29.5630],
            'population': [21540000, 24280000, 15300000, 13440000, 12200000, 8500000, 11200000, 16330000, 12950000, 32050000],
            'type': ['直辖市', '直辖市', '省会', '特区', '省会', '省会', '省会', '省会', '省会', '直辖市'],
            'gdp': [4027.1, 4321.5, 2501.9, 3103.6, 1810.0, 1482.9, 1768.1, 2001.2, 1020.9, 2503.2]  # 万亿元
        }
        
        df = pd.DataFrame(cities_data)
        self.add_points_layer(df, '中国主要城市')
    
    def add_points_layer(self, data, layer_name):
        """添加点图层"""
        if 'longitude' not in data.columns or 'latitude' not in data.columns:
            QMessageBox.warning(self, "警告", "数据中缺少经纬度列")
            return
        
        # 保存图层数据
        self.data_layers.append({
            'name': layer_name,
            'data': data,
            'type': 'points',
            'visible': True  # 新增可见性属性
        })
        
        # 根据当前模式更新显示
        self.update_display()
    
    def update_display(self):
        """根据当前模式更新显示"""
        try:
            if self.current_mode == "2D":
                self.update_2d_map()
            elif self.current_mode == "3D" and PLOTLY_AVAILABLE:
                self.update_3d_visualization()
        except Exception as e:
            logging.error(f"更新显示时出错: {e}")
            QMessageBox.warning(self, "警告", f"更新显示失败: {str(e)}")
    
    def update_2d_map(self):
        """更新2D地图显示"""
        try:
            # 重新创建地图
            map_config = self.map_configs[self.map_type_combo.currentText()]
            if map_config["attr"]:
                self.current_map = folium.Map(
                    location=[35.0, 105.0],
                    zoom_start=5,
                    tiles=map_config["tiles"],
                    attr=map_config["attr"]
                )
            else:
                self.current_map = folium.Map(
                    location=[35.0, 105.0],
                    zoom_start=5,
                    tiles=map_config["tiles"]
                )
            
            # 添加插件
            self.add_map_plugins()
            
            # 添加所有可见图层数据
            for layer in self.data_layers:
                if layer.get('visible', True):  # 只显示可见图层
                    if layer['type'] == 'points':
                        self.add_points_to_folium_map(layer['data'], layer['name'])
                    elif layer['type'] == 'lines':
                        self.add_line_features_to_map(layer['data'], layer['name'])
                    elif layer['type'] == 'polygons':
                        self.add_polygon_features_to_map(layer['data'], layer['name'])
            
            # 保存并加载地图
            self.save_and_load_map()
            
        except Exception as e:
            logging.error(f"更新2D地图时出错: {e}")
            QMessageBox.critical(self, "错误", f"更新2D地图失败: {str(e)}")
    
    def add_points_to_folium_map(self, data, layer_name):
        """向Folium地图添加点数据"""
        try:
            # 创建标记聚类
            marker_cluster = plugins.MarkerCluster(name=layer_name).add_to(self.current_map)
            
            for idx, row in data.iterrows():
                # 检查经纬度是否有效
                if pd.isna(row['longitude']) or pd.isna(row['latitude']):
                    continue
                    
                # 根据人口大小设置图标颜色（简化版本）
                if 'population' in data.columns and not pd.isna(row.get('population')):
                    pop = row['population']
                    if pop > 20000000:
                        color = 'red'
                    elif pop > 15000000:
                        color = 'orange'
                    elif pop > 10000000:
                        color = 'green'
                    else:
                        color = 'blue'
                else:
                    color = 'blue'
                
                # 创建弹出信息
                popup_text = f"<b>{row.get('name', '未知')}</b><br>"
                for col in data.columns:
                    if col not in ['longitude', 'latitude', 'name']:
                        popup_text += f"{col}: {row[col]}<br>"
                
                # 使用简单的颜色图标（不依赖外部字体）
                icon = folium.Icon(color=color)
                
                folium.Marker(
                    location=[float(row['latitude']), float(row['longitude'])],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=str(row.get('name', '点')),
                    icon=icon
                ).add_to(marker_cluster)
                
        except Exception as e:
            logging.error(f"添加点到地图时出错: {e}")
            QMessageBox.warning(self, "警告", f"添加数据点失败: {str(e)}")
    
    def add_line_features_to_map(self, line_features, layer_name):
        """向地图添加线要素（不保存到图层列表）"""
        try:
            for feature in line_features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                coordinates = geometry.get('coordinates', [])
                
                if coordinates:
                    # 转换坐标格式 [lon, lat] -> [lat, lon]
                    folium_coords = [[coord[1], coord[0]] for coord in coordinates]
                    
                    # 创建弹出信息
                    popup_text = f"<b>{properties.get('name', '线要素')}</b><br>"
                    for key, value in properties.items():
                        if key != 'name':
                            popup_text += f"{key}: {value}<br>"
                    
                    # 添加线要素
                    folium.PolyLine(
                        locations=folium_coords,
                        popup=folium.Popup(popup_text, max_width=300),
                        tooltip=properties.get('name', '线要素'),
                        color='blue',
                        weight=3,
                        opacity=0.8
                    ).add_to(self.current_map)
        except Exception as e:
            logging.error(f"添加线要素到地图失败: {e}")
    
    def add_polygon_features_to_map(self, polygon_features, layer_name):
        """向地图添加面要素（不保存到图层列表）"""
        try:
            for feature in polygon_features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                coordinates = geometry.get('coordinates', [])
                
                if coordinates and len(coordinates) > 0:
                    # 处理外环坐标 [lon, lat] -> [lat, lon]
                    exterior_coords = coordinates[0]
                    folium_coords = [[coord[1], coord[0]] for coord in exterior_coords]
                    
                    # 创建弹出信息
                    popup_text = f"<b>{properties.get('name', '面要素')}</b><br>"
                    for key, value in properties.items():
                        if key != 'name':
                            popup_text += f"{key}: {value}<br>"
                    
                    # 添加面要素
                    folium.Polygon(
                        locations=folium_coords,
                        popup=folium.Popup(popup_text, max_width=300),
                        tooltip=properties.get('name', '面要素'),
                        color='red',
                        weight=2,
                        fill=True,
                        fillColor='red',
                        fillOpacity=0.3
                    ).add_to(self.current_map)
        except Exception as e:
            logging.error(f"添加面要素到地图失败: {e}")
    
    def update_3d_visualization(self):
        """更新3D可视化显示 - 真实3D地图"""
        if not PLOTLY_AVAILABLE:
            QMessageBox.warning(self, "警告", "Plotly未安装，无法显示3D可视化")
            return
        
        if not self.data_layers:
            return
        
        # 创建3D地形地图的HTML内容
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>3D地形地图</title>
            <script src="https://cesium.com/downloads/cesiumjs/releases/1.95/Build/Cesium/Cesium.js"></script>
            <link href="https://cesium.com/downloads/cesiumjs/releases/1.95/Build/Cesium/Widgets/widgets.css" rel="stylesheet">
            <style>
                html, body, #cesiumContainer {
                    width: 100%; height: 100%; margin: 0; padding: 0; overflow: hidden;
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                }
                .info-panel {
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background: rgba(42, 42, 42, 0.8);
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 14px;
                    max-width: 300px;
                }
            </style>
        </head>
        <body>
            <div id="cesiumContainer"></div>
            <div class="info-panel">
                <h3>🌍 3D实景地图</h3>
                <p>• 真实地形渲染</p>
                <p>• 卫星影像叠加</p>
                <p>• 数据点3D标注</p>
                <p>• 支持飞行浏览</p>
                <br>
                <p><strong>注意:</strong> 完整的3D地形功能需要Cesium或类似的3D地图引擎。</p>
                <p>当前显示为演示版本。</p>
            </div>
            
            <script>
                // 初始化Cesium 3D地球
                try {
                    // 如果有Cesium，创建3D地球
                    if (typeof Cesium !== 'undefined') {
                        const viewer = new Cesium.Viewer('cesiumContainer', {
                            terrainProvider: Cesium.createWorldTerrain(),
                            imageryProvider: new Cesium.BingMapsImageryProvider({
                                url: 'https://dev.virtualearth.net',
                                key: 'your-bing-maps-key',
                                mapStyle: Cesium.BingMapsStyle.AERIAL
                            })
                        });
                        
                        // 设置初始视角到中国
                        viewer.camera.setView({
                            destination: Cesium.Cartesian3.fromDegrees(105.0, 35.0, 2000000.0)
                        });
                        
                        // 添加数据点
                        const dataPoints = [
                            {name: '北京', lon: 116.4074, lat: 39.9042, height: 100000},
                            {name: '上海', lon: 121.4737, lat: 31.2304, height: 120000},
                            {name: '广州', lon: 113.2644, lat: 23.1291, height: 80000}
                        ];
                        
                        dataPoints.forEach(point => {
                            viewer.entities.add({
                                position: Cesium.Cartesian3.fromDegrees(point.lon, point.lat, point.height),
                                point: {
                                    pixelSize: 10,
                                    color: Cesium.Color.YELLOW,
                                    outlineColor: Cesium.Color.BLACK,
                                    outlineWidth: 2,
                                    heightReference: Cesium.HeightReference.RELATIVE_TO_GROUND
                                },
                                label: {
                                    text: point.name,
                                    font: '14pt Microsoft YaHei',
                                    fillColor: Cesium.Color.WHITE,
                                    outlineColor: Cesium.Color.BLACK,
                                    outlineWidth: 2,
                                    style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                                    pixelOffset: new Cesium.Cartesian2(0, -40)
                                }
                            });
                        });
                    }
                } catch (error) {
                    // 如果Cesium不可用，显示替代内容
                    document.getElementById('cesiumContainer').innerHTML = `
                        <div style="display: flex; align-items: center; justify-content: center; height: 100%; 
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; 
                                    text-align: center; font-family: 'Microsoft YaHei', Arial;">
                            <div>
                                <h2>🌍 3D实景地图模式</h2>
                                <p style="font-size: 18px; margin: 20px 0;">正在开发中...</p>
                                <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px;">
                                    <h3>🚀 即将支持的功能:</h3>
                                    <ul style="text-align: left; display: inline-block;">
                                        <li>真实地形3D渲染</li>
                                        <li>卫星影像叠加</li>
                                        <li>数据点立体标注</li>
                                        <li>飞行路径浏览</li>
                                        <li>地形剖面分析</li>
                                        <li>3D测量工具</li>
                                    </ul>
                                </div>
                                <p style="margin-top: 30px; opacity: 0.8;">
                                    💡 提示: 3D图表功能已移至"统计"按钮中
                                </p>
                            </div>
                        </div>
                    `;
                }
            </script>
        </body>
        </html>
        """
        
        # 保存HTML文件
        with open(self.plotly_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 加载到WebView
        self.web_view.setUrl(QUrl.fromLocalFile(self.plotly_file))
    
    def change_display_mode(self, mode):
        """切换显示模式"""
        try:
            if mode == "2D地图":
                self.current_mode = "2D"
            elif mode == "3D可视化":
                self.current_mode = "3D"
            
            self.update_display()
        except Exception as e:
            logging.error(f"切换显示模式时出错: {e}")
    
    def change_map_type(self, map_type):
        """切换地图类型 (仅2D模式)"""
        if self.current_mode == "2D":
            try:
                self.update_2d_map()
            except Exception as e:
                logging.error(f"切换地图类型时出错: {e}")
    
    def fit_bounds(self):
        """适应数据边界"""
        try:
            if not self.data_layers:
                QMessageBox.information(self, "提示", "没有数据可以适应")
                return
            
            if self.current_mode == "2D":
                all_coords = []
                for layer in self.data_layers:
                    data = layer['data']
                    if 'longitude' in data.columns and 'latitude' in data.columns:
                        # 过滤有效坐标
                        valid_data = data.dropna(subset=['longitude', 'latitude'])
                        coords = list(zip(valid_data['latitude'], valid_data['longitude']))
                        all_coords.extend(coords)
                
                if all_coords:
                    # 计算边界
                    lats = [coord[0] for coord in all_coords]
                    lngs = [coord[1] for coord in all_coords]
                    
                    # 计算中心点和缩放级别
                    center_lat = (min(lats) + max(lats)) / 2
                    center_lng = (min(lngs) + max(lngs)) / 2
                    
                    # 重新创建地图以适应数据
                    map_config = self.map_configs[self.map_type_combo.currentText()]
                    if map_config["attr"]:
                        self.current_map = folium.Map(
                            location=[center_lat, center_lng],
                            zoom_start=6,  # 适中的缩放级别
                            tiles=map_config["tiles"],
                            attr=map_config["attr"]
                        )
                    else:
                        self.current_map = folium.Map(
                            location=[center_lat, center_lng],
                            zoom_start=6,
                            tiles=map_config["tiles"]
                        )
                    
                    # 添加插件和数据
                    self.add_map_plugins()
                    for layer in self.data_layers:
                        self.add_points_to_folium_map(layer['data'], layer['name'])
                    
                    self.save_and_load_map()
                    
            elif self.current_mode == "3D":
                # 3D模式下重新生成图表
                self.update_3d_visualization()
                
        except Exception as e:
            logging.error(f"适应数据边界时出错: {e}")
            QMessageBox.warning(self, "警告", f"适应数据失败: {str(e)}")
    
    def toggle_fullscreen(self):
        """切换全屏"""
        try:
            if self.current_mode == "2D":
                # 创建全屏对话框
                fullscreen_dialog = QDialog(self)
                fullscreen_dialog.setWindowTitle("全屏地图")
                fullscreen_dialog.setWindowFlags(Qt.Window)
                fullscreen_dialog.showMaximized()
                
                # 创建新的WebView显示地图
                layout = QVBoxLayout()
                web_view = QWebEngineView()
                web_view.setUrl(QUrl.fromLocalFile(self.map_file))
                layout.addWidget(web_view)
                
                # 添加退出全屏按钮
                exit_btn = QPushButton("退出全屏 (ESC)")
                exit_btn.clicked.connect(fullscreen_dialog.close)
                layout.addWidget(exit_btn)
                
                fullscreen_dialog.setLayout(layout)
                
                # 设置ESC键退出全屏
                fullscreen_dialog.keyPressEvent = lambda event: (
                    fullscreen_dialog.close() if event.key() == Qt.Key_Escape else None
                )
                
                fullscreen_dialog.exec_()
                
            else:
                QMessageBox.information(self, "提示", "3D模式下暂不支持全屏功能")
        except Exception as e:
            logging.error(f"切换全屏时出错: {e}")
            QMessageBox.warning(self, "警告", f"全屏功能暂时不可用: {str(e)}")
    
    def refresh_map(self):
        """刷新地图"""
        try:
            self.update_display()
            QMessageBox.information(self, "提示", "地图已刷新")
        except Exception as e:
            logging.error(f"刷新地图时出错: {e}")
    
    def save_and_load_map(self):
        """保存并加载地图 (2D模式)"""
        try:
            # 不添加图层控制，避免重复显示
            # folium.LayerControl().add_to(self.current_map)
            
            # 保存地图
            self.current_map.save(self.map_file)
            
            # 加载到WebView
            self.web_view.setUrl(QUrl.fromLocalFile(self.map_file))
            
        except Exception as e:
            logging.error(f"保存/加载地图失败: {e}")
            QMessageBox.critical(self, "错误", f"地图加载失败: {str(e)}")
    
    def import_data(self, file_path):
        """导入数据"""
        try:
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path, encoding='utf-8')
                # 检查坐标列
                coord_cols = ['longitude', 'lon', 'lng', 'x', 'X', '经度']
                lat_cols = ['latitude', 'lat', 'y', 'Y', '纬度']
                
                lon_col = None
                lat_col = None
                
                for col in coord_cols:
                    if col in data.columns:
                        lon_col = col
                        break
                
                for col in lat_cols:
                    if col in data.columns:
                        lat_col = col
                        break
                
                if lon_col and lat_col:
                    # 标准化列名
                    data = data.rename(columns={lon_col: 'longitude', lat_col: 'latitude'})
                    
                    # 确保坐标为数值类型
                    data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')
                    data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
                    
                    # 移除无效坐标
                    data = data.dropna(subset=['longitude', 'latitude'])
                    
                    if len(data) == 0:
                        QMessageBox.warning(self, "警告", "没有有效的坐标数据")
                        return False
                    
                    layer_name = Path(file_path).stem
                    self.add_points_layer(data, layer_name)
                    return True
                else:
                    QMessageBox.warning(self, "警告", "文件中未找到坐标列")
                    return False
                    
            elif file_path.endswith('.json') or file_path.endswith('.geojson'):
                # 处理GeoJSON数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    geojson_data = json.load(f)
                
                if geojson_data.get('type') == 'FeatureCollection':
                    layer_name = Path(file_path).stem
                    self.add_geojson_layer(geojson_data, layer_name)
                    return True
                else:
                    QMessageBox.warning(self, "警告", "不支持的GeoJSON格式")
                    return False
            else:
                QMessageBox.warning(self, "警告", "不支持的文件格式")
                return False
                
        except Exception as e:
            logging.error(f"导入数据失败: {e}")
            QMessageBox.critical(self, "错误", f"导入数据失败: {str(e)}")
            return False
    
    def add_geojson_layer(self, geojson_data, layer_name):
        """添加GeoJSON图层"""
        try:
            features = geojson_data.get('features', [])
            if not features:
                QMessageBox.warning(self, "警告", "GeoJSON文件中没有要素")
                return
            
            # 分析要素类型
            point_features = []
            line_features = []
            polygon_features = []
            
            for feature in features:
                geometry = feature.get('geometry', {})
                properties = feature.get('properties', {})
                geom_type = geometry.get('type', '')
                
                if geom_type == 'Point':
                    coords = geometry.get('coordinates', [])
                    if len(coords) >= 2:
                        point_data = {
                            'longitude': coords[0],
                            'latitude': coords[1],
                            'name': properties.get('name', '未知点'),
                            'type': properties.get('type', 'point')
                        }
                        # 添加其他属性
                        for key, value in properties.items():
                            if key not in ['name', 'type']:
                                point_data[key] = value
                        point_features.append(point_data)
                
                elif geom_type == 'LineString':
                    line_features.append(feature)
                
                elif geom_type == 'Polygon':
                    polygon_features.append(feature)
            
            # 添加点要素
            if point_features:
                df = pd.DataFrame(point_features)
                self.add_points_layer(df, f"{layer_name}_点要素")
            
            # 添加线要素
            if line_features:
                self.add_line_features(line_features, f"{layer_name}_线要素")
            
            # 添加面要素
            if polygon_features:
                self.add_polygon_features(polygon_features, f"{layer_name}_面要素")
                
        except Exception as e:
            logging.error(f"添加GeoJSON图层失败: {e}")
            QMessageBox.critical(self, "错误", f"添加GeoJSON图层失败: {str(e)}")
    
    def add_line_features(self, line_features, layer_name):
        """添加线要素到地图"""
        try:
            # 保存图层数据
            self.data_layers.append({
                'name': layer_name,
                'data': line_features,
                'type': 'lines',
                'visible': True  # 新增可见性属性
            })
            
            # 添加到地图
            for feature in line_features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                coordinates = geometry.get('coordinates', [])
                
                if coordinates:
                    # 转换坐标格式 [lon, lat] -> [lat, lon]
                    folium_coords = [[coord[1], coord[0]] for coord in coordinates]
                    
                    # 创建弹出信息
                    popup_text = f"<b>{properties.get('name', '线要素')}</b><br>"
                    for key, value in properties.items():
                        if key != 'name':
                            popup_text += f"{key}: {value}<br>"
                    
                    # 添加线要素
                    folium.PolyLine(
                        locations=folium_coords,
                        popup=folium.Popup(popup_text, max_width=300),
                        tooltip=properties.get('name', '线要素'),
                        color='blue',
                        weight=3,
                        opacity=0.8
                    ).add_to(self.current_map)
            
            logging.info(f"成功添加 {len(line_features)} 个线要素")
            
        except Exception as e:
            logging.error(f"添加线要素失败: {e}")
    
    def add_polygon_features(self, polygon_features, layer_name):
        """添加面要素到地图"""
        try:
            # 保存图层数据
            self.data_layers.append({
                'name': layer_name,
                'data': polygon_features,
                'type': 'polygons',
                'visible': True  # 新增可见性属性
            })
            
            # 添加到地图
            for feature in polygon_features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                coordinates = geometry.get('coordinates', [])
                
                if coordinates and len(coordinates) > 0:
                    # 处理外环坐标 [lon, lat] -> [lat, lon]
                    exterior_coords = coordinates[0]
                    folium_coords = [[coord[1], coord[0]] for coord in exterior_coords]
                    
                    # 创建弹出信息
                    popup_text = f"<b>{properties.get('name', '面要素')}</b><br>"
                    for key, value in properties.items():
                        if key != 'name':
                            popup_text += f"{key}: {value}<br>"
                    
                    # 添加面要素
                    folium.Polygon(
                        locations=folium_coords,
                        popup=folium.Popup(popup_text, max_width=300),
                        tooltip=properties.get('name', '面要素'),
                        color='red',
                        weight=2,
                        fill=True,
                        fillColor='red',
                        fillOpacity=0.3
                    ).add_to(self.current_map)
            
            logging.info(f"成功添加 {len(polygon_features)} 个面要素")
            
        except Exception as e:
            logging.error(f"添加面要素失败: {e}")
    
    def show_statistics(self):
        """显示统计分析对话框"""
        if not self.data_layers:
            QMessageBox.information(self, "提示", "没有数据可以统计")
            return
        
        dialog = StatisticsDialog(self.data_layers, self)
        dialog.exec_()
    
    def toggle_layer_visibility(self, layer_name, is_visible):
        """切换图层可见性"""
        try:
            # 找到对应图层
            for layer in self.data_layers:
                if layer['name'] == layer_name:
                    layer['visible'] = is_visible
                    break
            
            # 重新更新地图显示
            self.update_display()
            
        except Exception as e:
            logging.error(f"切换图层可见性时出错: {e}")

class Enhanced3DLayerPanel(QWidget):
    """增强的图层面板"""
    
    layer_selected = pyqtSignal(dict)
    layer_visibility_changed = pyqtSignal(str, bool)  # 新增信号
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 图层树
        self.layer_tree = QTreeWidget()
        self.layer_tree.setHeaderLabel("图层")
        self.layer_tree.itemClicked.connect(self.on_layer_selected)
        self.layer_tree.itemChanged.connect(self.on_layer_visibility_changed)  # 新增
        
        # 按钮面板
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加图层")
        self.remove_btn = QPushButton("移除图层")
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        
        layout.addWidget(self.layer_tree)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def add_layer(self, layer_info):
        """添加图层到面板"""
        item = QTreeWidgetItem([layer_info['name']])
        item.setData(0, Qt.UserRole, layer_info)
        item.setCheckState(0, Qt.Checked)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # 启用复选框
        self.layer_tree.addTopLevelItem(item)
    
    def on_layer_selected(self, item):
        """图层选择事件"""
        layer_info = item.data(0, Qt.UserRole)
        if layer_info:
            self.layer_selected.emit(layer_info)
    
    def on_layer_visibility_changed(self, item, column):
        """图层可见性改变事件"""
        if column == 0:  # 只处理第一列的复选框
            layer_info = item.data(0, Qt.UserRole)
            if layer_info:
                is_visible = item.checkState(0) == Qt.Checked
                self.layer_visibility_changed.emit(layer_info['name'], is_visible)

class Enhanced3DAttributePanel(QWidget):
    """增强的属性面板"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 图层信息标签
        self.layer_info_tab = QTextEdit()
        self.layer_info_tab.setReadOnly(True)
        self.tab_widget.addTab(self.layer_info_tab, "图层信息")
        
        # 属性表标签
        self.attribute_table = QTableWidget()
        self.tab_widget.addTab(self.attribute_table, "属性表")
        
        # 统计信息标签
        self.stats_tab = QTextEdit()
        self.stats_tab.setReadOnly(True)
        self.tab_widget.addTab(self.stats_tab, "统计信息")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def show_layer_info(self, layer_info):
        """显示图层信息"""
        mode_info = "2D/3D切换" if PLOTLY_AVAILABLE else "2D地图"
        info_text = f"""
图层名称: {layer_info['name']}
图层类型: {layer_info['type']}
要素数量: {len(layer_info['data']) if hasattr(layer_info['data'], '__len__') else '未知'}
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
地图引擎: Folium + Leaflet + Plotly
显示模式: {mode_info}
        """
        self.layer_info_tab.setText(info_text)
        
        # 显示属性表 - 处理不同数据类型
        data = layer_info['data']
        
        if isinstance(data, pd.DataFrame):
            # 处理DataFrame数据
            self.attribute_table.setRowCount(len(data))
            self.attribute_table.setColumnCount(len(data.columns))
            self.attribute_table.setHorizontalHeaderLabels(data.columns.tolist())
            
            for i, row in data.iterrows():
                for j, value in enumerate(row):
                    self.attribute_table.setItem(i, j, QTableWidgetItem(str(value)))
            
            # 显示统计信息
            stats_text = "数据统计:\n\n"
            for col in data.columns:
                if data[col].dtype in ['int64', 'float64']:
                    stats_text += f"{col}:\n"
                    stats_text += f"  最小值: {data[col].min()}\n"
                    stats_text += f"  最大值: {data[col].max()}\n"
                    stats_text += f"  平均值: {data[col].mean():.2f}\n"
                    stats_text += f"  标准差: {data[col].std():.2f}\n\n"
            
        elif isinstance(data, list):
            # 处理GeoJSON要素列表
            if data and isinstance(data[0], dict):
                # 提取属性信息
                properties_list = []
                for feature in data:
                    props = feature.get('properties', {})
                    properties_list.append(props)
                
                if properties_list:
                    # 获取所有属性键
                    all_keys = set()
                    for props in properties_list:
                        all_keys.update(props.keys())
                    all_keys = list(all_keys)
                    
                    self.attribute_table.setRowCount(len(properties_list))
                    self.attribute_table.setColumnCount(len(all_keys))
                    self.attribute_table.setHorizontalHeaderLabels(all_keys)
                    
                    for i, props in enumerate(properties_list):
                        for j, key in enumerate(all_keys):
                            value = props.get(key, '')
                            self.attribute_table.setItem(i, j, QTableWidgetItem(str(value)))
            
            stats_text = f"GeoJSON要素统计:\n\n要素数量: {len(data)}\n"
            
        else:
            # 其他数据类型
            self.attribute_table.setRowCount(0)
            self.attribute_table.setColumnCount(0)
            stats_text = "无法显示此类型的数据统计信息"
        
        self.stats_tab.setText(stats_text)

class Enhanced3DMainWindow(QMainWindow):
    """增强的主窗口 - 集成3D功能"""
    
    def __init__(self):
        super().__init__()
        self.current_project = None
        self.db_manager = None  # 数据库管理器
        self.init_ui()
        self.setup_connections()
        self.init_database()  # 初始化数据库连接
        
    def init_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置应用程序图标
        icon_path = BASE_DIR / "assets" / "app_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧图层面板
        self.layer_panel = Enhanced3DLayerPanel()
        splitter.addWidget(self.layer_panel)
        
        # 中央地图
        self.map_widget = Enhanced3DMapWidget()
        splitter.addWidget(self.map_widget)
        
        # 右侧属性面板
        self.attribute_panel = Enhanced3DAttributePanel()
        splitter.addWidget(self.attribute_panel)
        
        # 设置分割器比例
        splitter.setSizes([250, 800, 350])
        
        # 设置布局
        layout = QHBoxLayout()
        layout.addWidget(splitter)
        central_widget.setLayout(layout)
        
        # 状态栏
        plotly_status = " + 3D可视化" if PLOTLY_AVAILABLE else ""
        self.statusBar().showMessage(f"增强版GIS应用已就绪 - Folium地图引擎{plotly_status}")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_action = QAction('新建项目', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction('打开项目', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction('保存项目', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        import_action = QAction('导入数据', self)
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
        export_action = QAction('导出地图', self)
        export_action.triggered.connect(self.export_map)
        file_menu.addAction(export_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        fit_action = QAction('适应数据', self)
        fit_action.triggered.connect(self.fit_to_data)
        view_menu.addAction(fit_action)
        
        # 移除全屏功能
        # fullscreen_action = QAction('全屏地图', self)
        # fullscreen_action.triggered.connect(self.toggle_fullscreen)
        # view_menu.addAction(fullscreen_action)
        
        if PLOTLY_AVAILABLE:
            view_menu.addSeparator()
            toggle_3d_action = QAction('切换3D模式', self)
            toggle_3d_action.triggered.connect(self.toggle_3d_mode)
            view_menu.addAction(toggle_3d_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # 数据库菜单
        if DATABASE_AVAILABLE:
            db_menu = menubar.addMenu('数据库')
            
            db_operations_action = QAction('数据库操作', self)
            db_operations_action.triggered.connect(self.open_database_operations)
            db_menu.addAction(db_operations_action)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 新建
        new_action = QAction('新建', self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        # 打开
        open_action = QAction('打开', self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        # 保存
        save_action = QAction('保存', self)
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 导入
        import_action = QAction('导入', self)
        import_action.triggered.connect(self.import_data)
        toolbar.addAction(import_action)
        
        # 移除适应数据按钮
        
        if PLOTLY_AVAILABLE:
            toolbar.addSeparator()
            # 3D切换
            toggle_3d_action = QAction('3D模式', self)
            toggle_3d_action.triggered.connect(self.toggle_3d_mode)
            toolbar.addAction(toggle_3d_action)
    
    def setup_connections(self):
        """设置信号连接"""
        self.layer_panel.layer_selected.connect(self.attribute_panel.show_layer_info)
        self.layer_panel.layer_visibility_changed.connect(self.map_widget.toggle_layer_visibility)  # 新增
        self.layer_panel.add_btn.clicked.connect(self.import_data)
        self.layer_panel.remove_btn.clicked.connect(self.remove_layer)
    
    def new_project(self):
        """新建项目"""
        self.map_widget.data_layers.clear()
        self.layer_panel.layer_tree.clear()
        self.map_widget.create_initial_map()
        self.statusBar().showMessage("新项目创建完成")
    
    def open_project(self):
        """打开项目"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "", "JSON文件 (*.json)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                # 清空当前数据
                self.map_widget.data_layers.clear()
                self.layer_panel.layer_tree.clear()
                
                # 加载项目数据
                for layer_data in project_data.get('layers', []):
                    df = pd.DataFrame(layer_data['data'])
                    self.map_widget.add_points_layer(df, layer_data['name'])
                    self.layer_panel.add_layer(self.map_widget.data_layers[-1])
                
                self.statusBar().showMessage(f"项目已打开: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开项目失败: {str(e)}")
    
    def save_project(self):
        """保存项目"""
        if not self.map_widget.data_layers:
            QMessageBox.warning(self, "警告", "没有数据可保存")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存项目", "", "JSON文件 (*.json)"
        )
        if file_path:
            try:
                project_data = {
                    'name': f"GIS项目_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'created_time': datetime.now().isoformat(),
                    'version': APP_VERSION,
                    'layers': []
                }
                
                for layer in self.map_widget.data_layers:
                    layer_data = {
                        'name': layer['name'],
                        'type': layer['type'],
                        'data': layer['data'].to_dict('records')
                    }
                    project_data['layers'].append(layer_data)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)
                
                self.statusBar().showMessage(f"项目已保存: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存项目失败: {str(e)}")
    
    def import_data(self):
        """导入数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入数据", "", "CSV文件 (*.csv);;GeoJSON文件 (*.geojson);;JSON文件 (*.json)"
        )
        if file_path:
            if self.map_widget.import_data(file_path):
                # 添加到图层面板 - 修复：确保添加最新的图层
                if self.map_widget.data_layers:
                    latest_layer = self.map_widget.data_layers[-1]
                    self.layer_panel.add_layer(latest_layer)
                    # 立即更新显示
                    self.map_widget.update_display()
                self.statusBar().showMessage(f"数据导入成功: {file_path}")
            else:
                self.statusBar().showMessage(f"数据导入失败: {file_path}")
    
    def export_map(self):
        """导出地图"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出地图", "map.html", "HTML文件 (*.html)"
        )
        if file_path:
            try:
                # 根据当前模式导出不同文件
                if self.map_widget.current_mode == "2D":
                    import shutil
                    shutil.copy2(self.map_widget.map_file, file_path)
                elif self.map_widget.current_mode == "3D":
                    import shutil
                    shutil.copy2(self.map_widget.plotly_file, file_path)
                
                self.statusBar().showMessage(f"地图已导出: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出地图失败: {str(e)}")
    
    def remove_layer(self):
        """移除图层"""
        current_item = self.layer_panel.layer_tree.currentItem()
        if current_item:
            layer_info = current_item.data(0, Qt.UserRole)
            if layer_info:
                # 从图层列表中移除
                self.map_widget.data_layers = [
                    layer for layer in self.map_widget.data_layers 
                    if layer['name'] != layer_info['name']
                ]
                
                # 从树中移除
                self.layer_panel.layer_tree.takeTopLevelItem(
                    self.layer_panel.layer_tree.indexOfTopLevelItem(current_item)
                )
                
                # 更新显示
                self.map_widget.update_display()
                
                self.statusBar().showMessage("图层已移除")
    
    def toggle_3d_mode(self):
        """切换3D模式"""
        if PLOTLY_AVAILABLE:
            current_mode = self.map_widget.mode_combo.currentText()
            if current_mode == "2D地图":
                self.map_widget.mode_combo.setCurrentText("3D可视化")
            else:
                self.map_widget.mode_combo.setCurrentText("2D地图")
    
    def show_statistics(self):
        """显示统计分析对话框"""
        if not self.map_widget.data_layers:
            QMessageBox.information(self, "提示", "没有数据可以统计")
            return
        
        dialog = StatisticsDialog(self.map_widget.data_layers, self)
        dialog.exec_()
    
    def fit_to_data(self):
        """适应数据范围"""
        if hasattr(self, 'map_widget'):
            self.map_widget.fit_bounds()
    
    def toggle_fullscreen(self):
        """切换全屏"""
        if hasattr(self, 'map_widget'):
            self.map_widget.toggle_fullscreen()
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, 
            "关于", 
            f"""
{APP_NAME} v{APP_VERSION}

这是一个简单的GIS系统，用作课程作业

主要功能:
• 真实地图底图显示 (OpenStreetMap, 卫星图, CartoDB)
• 2D/3D显示模式切换
• 交互式地图操作 (缩放, 拖拽, 测量)
• 数据导入导出 (CSV, GeoJSON)
• 图层管理和统计分析
• 数据库存储和查询 (PostgreSQL + PostGIS)

感谢您的使用，欢迎联系作者
GitHub: https://github.com/Tqy43
            """
        )
    
    def init_database(self):
        """初始化数据库连接"""
        if DATABASE_AVAILABLE:
            try:
                self.db_manager = initialize_database()
                if self.db_manager:
                    self.statusBar().showMessage("数据库连接成功")
                else:
                    self.statusBar().showMessage("数据库连接失败 - 使用文件模式")
            except Exception as e:
                logging.warning(f"数据库初始化失败: {e}")
                self.statusBar().showMessage("数据库不可用 - 使用文件模式")
    
    def open_database_operations(self):
        """打开数据库操作窗口"""
        if not DATABASE_AVAILABLE:
            QMessageBox.warning(self, "警告", "数据库模块不可用")
            return
        
        # 确保数据库已连接
        if not self.db_manager:
            try:
                self.db_manager = initialize_database()
                if not self.db_manager:
                    QMessageBox.warning(self, "警告", "数据库连接失败，请检查配置")
                    return
            except Exception as e:
                QMessageBox.critical(self, "错误", f"数据库连接错误: {str(e)}")
                return
        
        try:
            dialog = DatabaseDialog(self.db_manager, self)
            if dialog.exec_() == QDialog.Accepted:
                # 如果用户点击了"加载到地图"，处理数据加载
                if hasattr(dialog, 'current_data') and dialog.current_data is not None:
                    df = dialog.current_data
                    layer_name = f"数据库查询_{datetime.now().strftime('%H%M%S')}"
                    self.map_widget.add_points_layer(df, layer_name)
                    self.layer_panel.add_layer(self.map_widget.data_layers[-1])
                    
                    QMessageBox.information(self, "成功", f"从数据库加载了 {len(df)} 条记录")
                    self.statusBar().showMessage(f"数据库查询完成: {len(df)} 条记录")
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库操作失败: {str(e)}")

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"启动 {APP_NAME} v{APP_VERSION}")
    
    # 创建QApplication
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # 设置应用程序图标
    icon_path = BASE_DIR / "assets" / "app_icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    try:
        # 创建主窗口
        main_window = Enhanced3DMainWindow()
        main_window.show()
        
        logger.info("StudyGIS_demo应用程序启动成功")
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        QMessageBox.critical(
            None, 
            "启动错误", 
            f"应用程序启动失败:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == '__main__':
    main() 