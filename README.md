# StudyGIS_demo

一个简单的GIS系统，用作课程作业。

## 项目简介

StudyGIS_demo是一个基于Python和PyQt5开发的地理信息系统，集成了Folium交互式地图和Plotly 3D可视化功能。

## 主要功能

- 🗺️ **真实地图底图显示** (OpenStreetMap, 卫星图, CartoDB)
- 🔄 **2D/3D显示模式切换**
- 🖱️ **交互式地图操作** (缩放, 拖拽, 测量)
- 📁 **数据导入导出** (CSV, GeoJSON)
- 📊 **图层管理和统计分析**
- 🗄️ **数据库存储和查询** (PostgreSQL + PostGIS)

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

## 应用程序图标

本项目使用了一个可爱的青蛙趴在地球上的图标，象征着GIS系统对地球的关注和保护。

## 技术栈

- **界面框架**: PyQt5 + QWebEngine
- **地图引擎**: Folium + Leaflet.js
- **3D可视化**: Plotly + WebGL
- **数据处理**: Pandas + NumPy
- **图表绘制**: Matplotlib
- **数据库**: PostgreSQL + PostGIS (可选)

## 作者信息

感谢您的使用，欢迎联系作者！

**GitHub**: [https://github.com/Tqy43](https://github.com/Tqy43)

## 许可证

本项目仅用于课程作业和学习目的。