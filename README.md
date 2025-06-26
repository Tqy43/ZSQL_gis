# StudyGIS_demo

一个简单的GIS系统，用作课程作业。

## 项目简介

StudyGIS_demo是一个基于Python和PyQt5开发的地理信息系统，集成了Folium交互式地图和Plotly 3D可视化功能。

## 主要功能

- 🗺️ **真实地图底图显示** (OpenStreetMap, 卫星图, CartoDB)
- 🔄 **2D/3D显示模式切换**
- 🖱️ **交互式地图操作** (缩放, 拖拽, 测量)
- 📁 **数据导入导出** (CSV, GeoJSON, Shapefile, 栅格数据)
- 📊 **图层管理和统计分析**
- 🗄️ **数据库存储和查询** (PostgreSQL + PostGIS)
- 🏔️ **栅格数据显示** (DEM, GeoTIFF等)
- 🔺 **TIN生成** (从三维点数据创建三角不规则网络)
- 📈 **等高线生成** (从TIN或DEM数据生成等高线)
- 🎯 **茅山地区样本数据** (专门的TIN点位数据)

## 项目结构

```
StudyGIS_demo/
├── StudyGIS_demo.py          # 主应用程序
├── src/                      # 核心模块
│   └── database_config.py    # 数据库配置
├── utils/                    # 工具脚本
│   ├── create_app_icon.py    # 图标生成器
│   ├── create_simple_sample_data.py
│   └── create_sample_shapefiles.py
├── tests/                    # 测试文件
│   ├── test_*.py
│   ├── debug_geojson.py
│   └── check_db.py
├── assets/                   # 资源文件
│   ├── app_icon.ico          # 应用程序图标
│   └── app_icon_*.png        # 不同尺寸的图标
├── sample_data/              # 示例数据
│   ├── maoshan_TIN_points.csv # 茅山地区TIN点位数据
│   ├── img_sample/           # 栅格数据示例 (DEM等)
│   ├── *.geojson            # GeoJSON示例文件
│   └── *.shp                # Shapefile示例文件
├── docs/                     # 项目文档
│   ├── GIS_3D_FEATURES.md   # 3D功能说明
│   ├── USAGE_GUIDE.md       # 使用指南
│   ├── DATABASE_SETUP.md    # 数据库配置说明
│   └── QUICKSTART.md        # 快速开始指南
├── logs/                     # 日志文件
└── requirements_enhanced.txt # 依赖包列表
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements_enhanced.txt
```

### 2. 数据库配置 (可选)

如果需要使用数据库功能，请安装PostgreSQL和PostGIS：

```bash
pip install sqlalchemy psycopg2-binary geoalchemy2
```

### 3. 运行应用

```bash
python StudyGIS_demo.py
```

## 新功能使用指南

### 栅格数据显示
- 支持 GeoTIFF (*.tif), PNG, JPEG 等格式
- 自动坐标系转换和数据统计
- DEM数据以特殊样式显示（棕色虚线边框）

### TIN生成
1. 准备三维点数据文件 (CSV格式，包含经度、纬度、高程)
2. 通过"功能" → "创建TIN"选择数据文件
3. 系统自动生成三角不规则网络并显示在地图上

### 等高线生成
1. 选择TIN数据或DEM文件作为输入
2. 通过"功能" → "生成等高线"
3. 设置等高线间隔
4. 生成的等高线会以不同颜色显示不同高程

### 茅山地区数据
项目提供了茅山地区的专门TIN点位数据 (`sample_data/maoshan_TIN_points.csv`)，包含37个关键地标点位，可用于TIN和等高线生成的测试。

## 应用程序图标

本项目使用了一个可爱的青蛙趴在地球上的图标，象征着GIS系统对地球的关注和保护。

## 技术栈

- **界面框架**: PyQt5 + QWebEngine
- **地图引擎**: Folium + Leaflet.js
- **3D可视化**: Plotly + WebGL
- **数据处理**: Pandas + NumPy
- **图表绘制**: Matplotlib
- **GIS库**: GeoPandas + Rasterio + Shapely
- **空间分析**: SciPy (Delaunay三角化) + scikit-image (等高线)
- **数据库**: PostgreSQL + PostGIS (可选)

## 作者信息

感谢您的使用，欢迎联系作者！

**GitHub**: [https://github.com/Tqy43](https://github.com/Tqy43)

## 许可证

本项目仅用于课程作业和学习目的。