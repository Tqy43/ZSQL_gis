# PostgreSQL + PostGIS 数据库配置指南

## 📋 概述

本指南将帮助您在Windows系统上安装和配置PostgreSQL + PostGIS，以支持GIS应用系统的空间数据存储功能。

## 🚀 安装步骤

### 1. 安装PostgreSQL

#### 下载PostgreSQL
1. 访问 [PostgreSQL官网](https://www.postgresql.org/download/windows/)
2. 下载适合您系统的PostgreSQL安装包（推荐版本14或15）
3. 运行安装程序

#### 安装配置
- **端口**: 5432 (默认)
- **超级用户**: postgres
- **密码**: 请设置一个强密码并记住
- **区域设置**: Chinese (Simplified), China

### 2. 安装PostGIS扩展

#### 方法一：通过Application Stack Builder
1. 在PostgreSQL安装完成后，启动"Application Stack Builder"
2. 选择您的PostgreSQL服务器
3. 在"Spatial Extensions"分类下选择PostGIS
4. 按照向导完成安装

#### 方法二：手动下载安装
1. 访问 [PostGIS官网](https://postgis.net/windows_downloads/)
2. 下载对应PostgreSQL版本的PostGIS
3. 运行安装程序

### 3. 创建GIS数据库

#### 使用pgAdmin
1. 启动pgAdmin 4
2. 连接到PostgreSQL服务器
3. 右键"Databases" → "Create" → "Database"
4. 数据库名称: `gis_app`
5. 所有者: `postgres`

#### 启用PostGIS扩展
在查询工具中执行以下SQL：
```sql
-- 连接到gis_app数据库
\c gis_app

-- 启用PostGIS扩展
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- 验证安装
SELECT PostGIS_Version();
```

## ⚙️ 配置应用程序

### 1. 修改数据库配置

编辑 `database_config.py` 文件中的数据库连接参数：

```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'gis_app',
    'username': 'postgres',
    'password': '您的密码'  # 修改为实际密码
}
```

### 2. 安装Python依赖

```bash
pip install psycopg2-binary sqlalchemy geoalchemy2
```

### 3. 测试连接

运行数据库配置脚本：
```bash
python database_config.py
```

预期输出：
```
INFO:__main__:成功连接到PostgreSQL: PostgreSQL 14.x on x86_64-pc-windows...
INFO:__main__:PostGIS版本: 3.x USE_GEOS=1 USE_PROJ=1 USE_STATS=1
INFO:__main__:数据表创建成功
INFO:__main__:数据库初始化成功
```

## 📊 数据表结构

应用程序会自动创建以下数据表：

### point_features (点要素表)
- `id`: 主键
- `name`: 名称
- `type`: 类型
- `population`: 人口
- `gdp`: GDP
- `area`: 面积
- `elevation`: 海拔
- `province`: 省份
- `created_at`: 创建时间
- `geom`: 几何信息 (POINT)

### line_features (线要素表)
- `id`: 主键
- `name`: 名称
- `type`: 类型
- `length`: 长度
- `source`: 源头
- `mouth`: 入海口
- `basin_area`: 流域面积
- `created_at`: 创建时间
- `geom`: 几何信息 (LINESTRING)

### polygon_features (面要素表)
- `id`: 主键
- `name`: 名称
- `type`: 类型
- `area`: 面积
- `population`: 人口
- `gdp`: GDP
- `capital`: 首府
- `created_at`: 创建时间
- `geom`: 几何信息 (POLYGON)

## 🔧 使用功能

### 1. 连接数据库
- 启动应用程序
- 菜单栏 → "数据库" → "连接数据库"

### 2. 导入数据
- 菜单栏 → "数据库" → "导入到数据库"
- 选择CSV文件进行导入

### 3. 查询数据
- 菜单栏 → "数据库" → "查询数据库"
- 数据将自动加载到地图上

## 🛠️ 故障排除

### 常见问题

#### 1. 连接被拒绝
**错误**: `connection refused`
**解决**: 
- 检查PostgreSQL服务是否启动
- 确认端口5432未被占用
- 检查防火墙设置

#### 2. 密码认证失败
**错误**: `password authentication failed`
**解决**:
- 确认密码正确
- 检查pg_hba.conf配置文件

#### 3. PostGIS扩展不存在
**错误**: `extension "postgis" does not exist`
**解决**:
- 重新安装PostGIS
- 确认PostGIS版本与PostgreSQL兼容

#### 4. Python模块导入错误
**错误**: `ModuleNotFoundError: No module named 'psycopg2'`
**解决**:
```bash
pip install psycopg2-binary
```

### 性能优化

#### 1. 创建空间索引
```sql
-- 为几何列创建空间索引
CREATE INDEX idx_point_features_geom ON point_features USING GIST (geom);
CREATE INDEX idx_line_features_geom ON line_features USING GIST (geom);
CREATE INDEX idx_polygon_features_geom ON polygon_features USING GIST (geom);
```

#### 2. 优化查询
```sql
-- 使用空间查询优化
EXPLAIN ANALYZE SELECT * FROM point_features 
WHERE ST_Intersects(geom, ST_MakeEnvelope(116, 39, 117, 40, 4326));
```

## 📚 参考资料

- [PostgreSQL官方文档](https://www.postgresql.org/docs/)
- [PostGIS官方文档](https://postgis.net/documentation/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [GeoAlchemy2文档](https://geoalchemy-2.readthedocs.io/)

## 🆘 技术支持

如果遇到问题，请：
1. 检查日志文件 `logs/app_enhanced_3d.log`
2. 确认所有依赖包已正确安装
3. 验证数据库服务状态
4. 查看错误信息并对照故障排除指南

---

**最后更新**: 2024年6月3日  
**适用版本**: GIS应用系统 v2.3.0 