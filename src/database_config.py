"""
PostgreSQL + PostGIS 数据库配置和连接管理
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
import pandas as pd
from datetime import datetime
import json

# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'gis_app',
    'username': 'postgres',
    'password': '132318'  # 请修改为实际密码
}

# SQLAlchemy基类
Base = declarative_base()

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config=None):
        self.config = config or DATABASE_CONFIG
        self.engine = None
        self.Session = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """连接数据库"""
        try:
            # 构建连接字符串
            connection_string = (
                f"postgresql://{self.config['username']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
            
            # 创建引擎
            self.engine = create_engine(connection_string, echo=False)
            
            # 创建会话工厂
            self.Session = sessionmaker(bind=self.engine)
            
            # 测试连接
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                self.logger.info(f"成功连接到PostgreSQL: {version}")
                
                # 检查PostGIS扩展
                result = conn.execute(text("SELECT PostGIS_Version()"))
                postgis_version = result.fetchone()[0]
                self.logger.info(f"PostGIS版本: {postgis_version}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            return False
    
    def create_tables(self):
        """创建数据表"""
        try:
            # 确保PostGIS扩展已启用
            with self.engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
                conn.commit()
            
            # 创建所有表
            Base.metadata.create_all(self.engine)
            self.logger.info("数据表创建成功")
            return True
            
        except Exception as e:
            self.logger.error(f"创建数据表失败: {e}")
            return False
    
    def get_session(self):
        """获取数据库会话"""
        if self.Session:
            return self.Session()
        else:
            raise Exception("数据库未连接")
    
    def execute_query(self, query, params=None):
        """执行SQL查询"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                # 对于SELECT查询，获取所有结果
                if query.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    if rows:
                        # 获取列名
                        columns = result.keys()
                        # 转换为字典列表
                        return [dict(zip(columns, row)) for row in rows]
                    else:
                        return []
                else:
                    # 对于非SELECT查询，提交事务
                    conn.commit()
                    return True
        except Exception as e:
            self.logger.error(f"查询执行失败: {e}")
            return None
    
    def import_csv_to_postgis(self, csv_file, table_name, lon_col='longitude', lat_col='latitude'):
        """将CSV数据导入PostGIS"""
        try:
            # 读取CSV
            df = pd.read_csv(csv_file)
            
            # 检查必要的列
            if lon_col not in df.columns or lat_col not in df.columns:
                raise ValueError(f"CSV文件缺少坐标列: {lon_col}, {lat_col}")
            
            # 创建会话
            session = self.get_session()
            
            # 构建插入SQL
            columns = list(df.columns)
            placeholders = ', '.join([f':{col}' for col in columns])
            
            # 添加几何列
            insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(columns)}, geom)
            VALUES ({placeholders}, ST_SetSRID(ST_MakePoint(:{lon_col}, :{lat_col}), 4326))
            """
            
            # 批量插入
            for _, row in df.iterrows():
                session.execute(text(insert_sql), row.to_dict())
            
            session.commit()
            session.close()
            
            self.logger.info(f"成功导入 {len(df)} 条记录到表 {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"CSV导入失败: {e}")
            return False
    
    def query_spatial_data(self, table_name, bbox=None, limit=1000):
        """查询空间数据"""
        try:
            # 修复查询SQL，确保正确提取坐标
            base_query = f"""
            SELECT *, 
                   ST_X(ST_Centroid(geom)) as longitude, 
                   ST_Y(ST_Centroid(geom)) as latitude,
                   ST_AsText(geom) as geometry_wkt
            FROM {table_name}
            WHERE geom IS NOT NULL
            """
            
            if bbox:
                # bbox格式: [min_lon, min_lat, max_lon, max_lat]
                base_query += f"""
                AND ST_Intersects(geom, ST_MakeEnvelope({bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}, 4326))
                """
            
            base_query += f" LIMIT {limit}"
            
            self.logger.info(f"执行查询: {base_query}")
            result = self.execute_query(base_query)
            
            if result:
                # result现在是字典列表
                df = pd.DataFrame(result)
                self.logger.info(f"查询成功，返回 {len(df)} 条记录")
                return df
            else:
                self.logger.warning(f"查询 {table_name} 返回空结果")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"空间数据查询失败: {e}")
            # 尝试简单查询
            try:
                simple_query = f"SELECT * FROM {table_name} LIMIT {limit}"
                self.logger.info(f"尝试简单查询: {simple_query}")
                result = self.execute_query(simple_query)
                if result:
                    df = pd.DataFrame(result)
                    self.logger.info(f"简单查询成功，返回 {len(df)} 条记录")
                    return df
            except Exception as simple_error:
                self.logger.error(f"简单查询也失败: {simple_error}")
            
            return pd.DataFrame()
    
    def import_geojson_to_postgis(self, geojson_file, table_name):
        """将GeoJSON数据导入PostGIS"""
        try:
            # 读取GeoJSON
            with open(geojson_file, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            if geojson_data['type'] != 'FeatureCollection':
                raise ValueError("不支持的GeoJSON格式")
            
            # 创建会话
            session = self.get_session()
            imported_count = 0
            
            for feature in geojson_data['features']:
                try:
                    properties = feature.get('properties', {})
                    geometry = feature.get('geometry', {})
                    
                    # 根据几何类型选择表
                    geom_type = geometry.get('type', '').upper()
                    
                    if geom_type == 'POINT':
                        target_table = 'point_features'
                    elif geom_type == 'LINESTRING':
                        target_table = 'line_features'
                    elif geom_type == 'POLYGON':
                        target_table = 'polygon_features'
                    else:
                        self.logger.warning(f"跳过不支持的几何类型: {geom_type}")
                        continue
                    
                    # 构建插入SQL
                    columns = ['name', 'type']
                    values = [
                        properties.get('name', '未知'),
                        properties.get('type', geom_type.lower())
                    ]
                    
                    # 添加其他属性
                    for key, value in properties.items():
                        if key not in ['name', 'type'] and isinstance(value, (int, float, str)):
                            columns.append(key)
                            values.append(value)
                    
                    # 构建几何对象
                    geom_wkt = self.geometry_to_wkt(geometry)
                    
                    placeholders = ', '.join([f':{col}' for col in columns])
                    insert_sql = f"""
                    INSERT INTO {target_table} ({', '.join(columns)}, geom)
                    VALUES ({placeholders}, ST_GeomFromText('{geom_wkt}', 4326))
                    """
                    
                    # 创建参数字典
                    params = dict(zip(columns, values))
                    
                    # 执行插入
                    session.execute(text(insert_sql), params)
                    imported_count += 1
                    
                    self.logger.info(f"成功导入要素: {properties.get('name', '未知')} 到表 {target_table}")
                    
                except Exception as feature_error:
                    self.logger.error(f"导入要素失败: {feature_error}")
                    self.logger.error(f"要素数据: {feature}")
                    # 继续处理下一个要素，不中断整个导入过程
                    continue
            
            session.commit()
            session.close()
            
            self.logger.info(f"GeoJSON导入完成，成功导入 {imported_count} 个要素")
            return imported_count > 0
            
        except Exception as e:
            self.logger.error(f"GeoJSON导入失败: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def geometry_to_wkt(self, geometry):
        """将GeoJSON几何转换为WKT格式"""
        geom_type = geometry['type']
        coordinates = geometry['coordinates']
        
        if geom_type == 'Point':
            return f"POINT({coordinates[0]} {coordinates[1]})"
        elif geom_type == 'LineString':
            coords_str = ', '.join([f"{coord[0]} {coord[1]}" for coord in coordinates])
            return f"LINESTRING({coords_str})"
        elif geom_type == 'Polygon':
            # 处理外环
            exterior = coordinates[0]
            coords_str = ', '.join([f"{coord[0]} {coord[1]}" for coord in exterior])
            return f"POLYGON(({coords_str}))"
        else:
            raise ValueError(f"不支持的几何类型: {geom_type}")
    
    def get_all_layers(self):
        """获取所有图层信息"""
        try:
            layers = []
            
            # 查询点要素
            points_query = "SELECT COUNT(*) as count FROM point_features"
            result = self.execute_query(points_query)
            if result and len(result) > 0:
                count = result[0]['count']
                if count > 0:
                    layers.append({
                        'name': f'点要素 ({count}个)',
                        'table': 'point_features',
                        'type': 'point',
                        'count': count
                    })
            
            # 查询线要素
            lines_query = "SELECT COUNT(*) as count FROM line_features"
            result = self.execute_query(lines_query)
            if result and len(result) > 0:
                count = result[0]['count']
                if count > 0:
                    layers.append({
                        'name': f'线要素 ({count}个)',
                        'table': 'line_features',
                        'type': 'line',
                        'count': count
                    })
            
            # 查询面要素
            polygons_query = "SELECT COUNT(*) as count FROM polygon_features"
            result = self.execute_query(polygons_query)
            if result and len(result) > 0:
                count = result[0]['count']
                if count > 0:
                    layers.append({
                        'name': f'面要素 ({count}个)',
                        'table': 'polygon_features',
                        'type': 'polygon',
                        'count': count
                    })
            
            return layers
            
        except Exception as e:
            self.logger.error(f"获取图层信息失败: {e}")
            return []
    
    def export_layer_to_geojson(self, table_name, output_file):
        """导出图层为GeoJSON格式"""
        try:
            # 查询数据
            query = f"""
            SELECT *, ST_AsGeoJSON(geom) as geometry_json
            FROM {table_name}
            """
            
            result = self.execute_query(query)
            
            if not result:
                return False
            
            # 构建GeoJSON
            features = []
            for row in result:
                geometry_json = row.get('geometry_json')
                geom = json.loads(geometry_json) if geometry_json else None
                
                # 移除不需要的列
                properties = {k: v for k, v in row.items() 
                            if k not in ['id', 'geom', 'created_at', 'geometry_json']}
                
                feature = {
                    "type": "Feature",
                    "properties": properties,
                    "geometry": geom
                }
                features.append(feature)
            
            geojson = {
                "type": "FeatureCollection",
                "features": features
            }
            
            # 保存文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"成功导出图层到 {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出图层失败: {e}")
            return False

# 数据模型定义
class PointFeature(Base):
    """点要素表"""
    __tablename__ = 'point_features'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(String(100))
    population = Column(Float)
    gdp = Column(Float)
    area = Column(Float)
    elevation = Column(Float)
    province = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    geom = Column(Geometry('POINT', srid=4326))

class LineFeature(Base):
    """线要素表"""
    __tablename__ = 'line_features'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(String(100))
    length = Column(Float)
    source = Column(String(255))
    mouth = Column(String(255))
    basin_area = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    geom = Column(Geometry('LINESTRING', srid=4326))

class PolygonFeature(Base):
    """面要素表"""
    __tablename__ = 'polygon_features'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(String(100))
    area = Column(Float)
    population = Column(Float)
    gdp = Column(Float)
    capital = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    geom = Column(Geometry('POLYGON', srid=4326))

# 数据库初始化函数
def initialize_database():
    """初始化数据库"""
    db_manager = DatabaseManager()
    
    if db_manager.connect():
        if db_manager.create_tables():
            logging.info("数据库初始化成功")
            return db_manager
        else:
            logging.error("数据表创建失败")
            return None
    else:
        logging.error("数据库连接失败")
        return None

# 示例使用
if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 初始化数据库
    db = initialize_database()
    
    if db:
        # 测试查询
        result = db.execute_query("SELECT PostGIS_Version()")
        if result:
            print(f"PostGIS版本: {result[0][0]}")
        
        # 测试空间查询
        # df = db.query_spatial_data('point_features', limit=10)
        # print(f"查询到 {len(df)} 条记录") 