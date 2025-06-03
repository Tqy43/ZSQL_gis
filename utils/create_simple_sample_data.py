"""
创建简化的示例数据（不依赖geopandas）
"""
import json
import csv
import os

def create_simple_sample_data():
    """创建简化的示例数据"""
    
    # 确保目录存在
    os.makedirs('sample_data', exist_ok=True)
    
    try:
        # 创建更多城市CSV数据
        cities_data = [
            ['name', 'longitude', 'latitude', 'population', 'gdp', 'type', 'province'],
            ['北京', 116.4074, 39.9042, 21540000, 4027.1, '直辖市', '北京'],
            ['上海', 121.4737, 31.2304, 24280000, 4321.5, '直辖市', '上海'],
            ['广州', 113.2644, 23.1291, 15300000, 2501.9, '省会', '广东'],
            ['深圳', 114.0579, 22.5431, 13440000, 3103.6, '特区', '广东'],
            ['杭州', 120.1551, 30.2741, 12200000, 1810.0, '省会', '浙江'],
            ['南京', 118.7969, 32.0603, 8500000, 1482.9, '省会', '江苏'],
            ['武汉', 114.3054, 30.5928, 11200000, 1768.1, '省会', '湖北'],
            ['成都', 104.0665, 30.6598, 16330000, 2001.2, '省会', '四川'],
            ['西安', 108.9398, 34.3416, 12950000, 1020.9, '省会', '陕西'],
            ['重庆', 106.5516, 29.5630, 32050000, 2503.2, '直辖市', '重庆'],
            ['天津', 117.2008, 39.1189, 15600000, 1573.0, '直辖市', '天津'],
            ['苏州', 120.6197, 31.3017, 12748000, 2235.4, '地级市', '江苏'],
            ['青岛', 120.3826, 36.0671, 10071000, 1240.7, '地级市', '山东'],
            ['无锡', 120.3019, 31.5804, 7462000, 1237.4, '地级市', '江苏'],
            ['宁波', 121.5440, 29.8683, 9404000, 1240.9, '地级市', '浙江']
        ]
        
        with open('sample_data/cities_full.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(cities_data)
        print("✅ 完整城市CSV数据创建成功: cities_full.csv")
        
        # 创建河流线要素GeoJSON（简化版）
        rivers_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "长江主干",
                        "length": 6300,
                        "basin_area": 1800000,
                        "source": "青藏高原",
                        "mouth": "东海",
                        "type": "主要河流"
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [90.9, 32.7], [94.2, 32.3], [97.4, 31.8], [100.2, 31.2],
                            [102.7, 30.6], [104.1, 30.7], [106.5, 29.6], [108.4, 30.8],
                            [110.5, 30.3], [112.9, 30.4], [114.3, 30.6], [115.9, 30.2],
                            [117.2, 31.8], [118.8, 32.1], [119.9, 32.4], [121.2, 31.4], [121.9, 31.2]
                        ]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "黄河主干",
                        "length": 5464,
                        "basin_area": 752000,
                        "source": "青海巴颜喀拉山",
                        "mouth": "渤海",
                        "type": "主要河流"
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [96.2, 35.2], [98.2, 35.6], [100.2, 36.1], [101.8, 36.9],
                            [103.7, 37.6], [105.9, 38.5], [108.6, 39.4], [110.8, 40.8],
                            [111.7, 40.2], [112.5, 39.0], [113.7, 38.9], [114.5, 38.0],
                            [115.5, 37.8], [116.7, 37.4], [117.8, 37.5], [118.9, 37.8], [119.1, 37.2]
                        ]
                    }
                }
            ]
        }
        
        with open('sample_data/rivers_simple.geojson', 'w', encoding='utf-8') as f:
            json.dump(rivers_geojson, f, ensure_ascii=False, indent=2)
        print("✅ 简化河流GeoJSON创建成功: rivers_simple.geojson")
        
        # 创建省份面要素GeoJSON（简化版）
        provinces_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "北京市",
                        "area": 16410.54,
                        "population": 21540000,
                        "capital": "北京",
                        "type": "直辖市",
                        "gdp": 4027.1
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [115.7, 39.4], [117.4, 39.4], [117.4, 41.6], [115.7, 41.6], [115.7, 39.4]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "广东省",
                        "area": 179800,
                        "population": 126012510,
                        "capital": "广州",
                        "type": "省",
                        "gdp": 12970.8
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [109.7, 20.2], [117.2, 20.2], [117.2, 25.5], [109.7, 25.5], [109.7, 20.2]
                        ]]
                    }
                }
            ]
        }
        
        with open('sample_data/provinces_simple.geojson', 'w', encoding='utf-8') as f:
            json.dump(provinces_geojson, f, ensure_ascii=False, indent=2)
        print("✅ 简化省份GeoJSON创建成功: provinces_simple.geojson")
        
        # 创建Shapefile元数据信息
        shapefile_info = {
            "note": "Shapefile支持说明",
            "description": "本系统支持读取Shapefile格式数据",
            "supported_formats": [
                "点要素 (.shp)",
                "线要素 (.shp)", 
                "面要素 (.shp)"
            ],
            "requirements": [
                "需要安装geopandas: pip install geopandas",
                "Shapefile文件包含: .shp, .shx, .dbf, .prj等文件"
            ],
            "example_usage": "将Shapefile文件拖拽到应用程序中即可导入"
        }
        
        with open('sample_data/shapefile_info.json', 'w', encoding='utf-8') as f:
            json.dump(shapefile_info, f, ensure_ascii=False, indent=2)
        print("✅ Shapefile信息文件创建成功: shapefile_info.json")
        
        # 创建栅格数据信息
        raster_info = {
            "name": "栅格数据支持",
            "supported_formats": [
                "GeoTIFF (.tif, .tiff)",
                "JPEG2000 (.jp2)",
                "PNG (.png)",
                "NetCDF (.nc)"
            ],
            "description": "栅格数据处理功能",
            "requirements": [
                "需要安装rasterio: pip install rasterio",
                "支持多波段栅格数据",
                "支持地理坐标系统"
            ],
            "example_data": {
                "name": "中国高程数据模拟",
                "type": "DEM",
                "resolution": "30m",
                "extent": {
                    "min_lon": 73.0,
                    "max_lon": 135.0,
                    "min_lat": 18.0,
                    "max_lat": 54.0
                }
            }
        }
        
        with open('sample_data/raster_info.json', 'w', encoding='utf-8') as f:
            json.dump(raster_info, f, ensure_ascii=False, indent=2)
        print("✅ 栅格数据信息文件创建成功: raster_info.json")
        
        print("\n🎉 所有示例数据创建完成！")
        print("📁 文件列表:")
        print("  • cities_full.csv - 完整城市数据")
        print("  • rivers_simple.geojson - 简化河流数据")
        print("  • provinces_simple.geojson - 简化省份数据")
        print("  • shapefile_info.json - Shapefile支持信息")
        print("  • raster_info.json - 栅格数据支持信息")
        print("\n💡 提示:")
        print("  • 安装geopandas后可支持完整Shapefile功能")
        print("  • 安装rasterio后可支持栅格数据处理")
        
    except Exception as e:
        print(f"❌ 创建示例数据时出错: {e}")

if __name__ == "__main__":
    create_simple_sample_data() 