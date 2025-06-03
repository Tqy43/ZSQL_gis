"""
创建示例Shapefile数据
"""
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
import numpy as np
import os

def create_sample_shapefiles():
    """创建示例Shapefile数据"""
    
    # 确保目录存在
    os.makedirs('sample_data', exist_ok=True)
    
    try:
        # 创建点要素Shapefile
        points_data = {
            'name': ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都'],
            'population': [21540000, 24280000, 15300000, 13440000, 12200000, 8500000, 11200000, 16330000],
            'gdp': [4027.1, 4321.5, 2501.9, 3103.6, 1810.0, 1482.9, 1768.1, 2001.2],
            'type': ['直辖市', '直辖市', '省会', '特区', '省会', '省会', '省会', '省会'],
            'geometry': [
                Point(116.4074, 39.9042),
                Point(121.4737, 31.2304),
                Point(113.2644, 23.1291),
                Point(114.0579, 22.5431),
                Point(120.1551, 30.2741),
                Point(118.7969, 32.0603),
                Point(114.3054, 30.5928),
                Point(104.0665, 30.6598)
            ]
        }
        points_gdf = gpd.GeoDataFrame(points_data, crs='EPSG:4326')
        points_gdf.to_file('sample_data/cities.shp', encoding='utf-8')
        print("✅ 点要素Shapefile创建成功: cities.shp")
        
        # 创建线要素Shapefile
        lines_data = {
            'name': ['长江', '黄河', '珠江', '松花江'],
            'length': [6300, 5464, 2320, 1897],
            'basin_area': [1800000, 752000, 453690, 557180],
            'source': ['青藏高原', '青海巴颜喀拉山', '云南曲靖', '长白山天池'],
            'geometry': [
                LineString([(90.9, 32.7), (104.1, 30.7), (114.3, 30.6), (121.9, 31.2)]),
                LineString([(96.2, 35.2), (108.6, 39.4), (114.5, 38.0), (119.1, 37.2)]),
                LineString([(103.8, 25.5), (110.3, 23.1), (113.3, 23.1), (113.9, 22.5)]),
                LineString([(128.1, 42.0), (126.9, 45.3), (124.4, 46.8), (131.0, 48.2)])
            ]
        }
        lines_gdf = gpd.GeoDataFrame(lines_data, crs='EPSG:4326')
        lines_gdf.to_file('sample_data/rivers.shp', encoding='utf-8')
        print("✅ 线要素Shapefile创建成功: rivers.shp")
        
        # 创建面要素Shapefile
        polygons_data = {
            'name': ['北京市', '上海市', '广东省', '江苏省', '浙江省'],
            'area': [16410.54, 6340.5, 179800, 107200, 105500],
            'population': [21540000, 24280000, 126012510, 84748016, 64567588],
            'gdp': [4027.1, 4321.5, 12970.8, 11640.8, 7352.9],
            'capital': ['北京', '上海', '广州', '南京', '杭州'],
            'geometry': [
                Polygon([(115.7, 39.4), (117.4, 39.4), (117.4, 41.6), (115.7, 41.6), (115.7, 39.4)]),
                Polygon([(120.9, 30.7), (122.0, 30.7), (122.0, 31.9), (120.9, 31.9), (120.9, 30.7)]),
                Polygon([(109.7, 20.2), (117.2, 20.2), (117.2, 25.5), (109.7, 25.5), (109.7, 20.2)]),
                Polygon([(116.4, 30.8), (121.9, 30.8), (121.9, 35.3), (116.4, 35.3), (116.4, 30.8)]),
                Polygon([(118.0, 27.0), (123.0, 27.0), (123.0, 31.5), (118.0, 31.5), (118.0, 27.0)])
            ]
        }
        polygons_gdf = gpd.GeoDataFrame(polygons_data, crs='EPSG:4326')
        polygons_gdf.to_file('sample_data/provinces.shp', encoding='utf-8')
        print("✅ 面要素Shapefile创建成功: provinces.shp")
        
        # 创建模拟栅格数据信息文件
        raster_info = {
            "name": "中国高程数据",
            "type": "DEM",
            "resolution": "30m",
            "extent": {
                "min_lon": 73.0,
                "max_lon": 135.0,
                "min_lat": 18.0,
                "max_lat": 54.0
            },
            "description": "中国地区数字高程模型数据，分辨率30米",
            "note": "实际栅格数据文件较大，此处仅提供元数据信息"
        }
        
        import json
        with open('sample_data/raster_info.json', 'w', encoding='utf-8') as f:
            json.dump(raster_info, f, ensure_ascii=False, indent=2)
        print("✅ 栅格数据信息文件创建成功: raster_info.json")
        
        print("\n🎉 所有示例数据创建完成！")
        print("📁 文件列表:")
        print("  • cities.shp - 城市点要素")
        print("  • rivers.shp - 河流线要素") 
        print("  • provinces.shp - 省份面要素")
        print("  • raster_info.json - 栅格数据信息")
        
    except Exception as e:
        print(f"❌ 创建Shapefile时出错: {e}")
        print("💡 请确保已安装geopandas: pip install geopandas")

if __name__ == "__main__":
    create_sample_shapefiles() 