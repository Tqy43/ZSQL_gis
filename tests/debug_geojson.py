"""
调试GeoJSON导入问题
"""
import json

def analyze_geojson():
    """分析GeoJSON文件结构"""
    try:
        with open('sample_data/provinces_simple.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        print("🔍 GeoJSON文件分析")
        print("=" * 50)
        
        print(f"类型: {geojson_data['type']}")
        print(f"要素数量: {len(geojson_data['features'])}")
        
        for i, feature in enumerate(geojson_data['features']):
            print(f"\n要素 {i+1}:")
            print(f"  几何类型: {feature['geometry']['type']}")
            print(f"  属性: {list(feature['properties'].keys())}")
            
            # 检查属性值类型
            for key, value in feature['properties'].items():
                print(f"    {key}: {type(value).__name__} = {value}")
        
        print("\n🔧 数据库导入分析")
        print("=" * 50)
        
        # 模拟导入逻辑
        for feature in geojson_data['features']:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            geom_type = geometry.get('type', '').upper()
            print(f"\n几何类型: {geom_type}")
            
            if geom_type == 'POLYGON':
                target_table = 'polygon_features'
                print(f"目标表: {target_table}")
                
                # 构建插入数据
                columns = ['name', 'type']
                values = [
                    properties.get('name', '未知'),
                    properties.get('type', geom_type.lower())
                ]
                
                print(f"基础列: {columns}")
                print(f"基础值: {values}")
                
                # 添加其他属性
                for key, value in properties.items():
                    if key not in ['name', 'type'] and isinstance(value, (int, float, str)):
                        columns.append(key)
                        values.append(value)
                        print(f"添加列: {key} = {value} ({type(value).__name__})")
                
                print(f"最终列: {columns}")
                print(f"最终值: {values}")
                
                # 检查数据库表结构匹配
                expected_columns = ['id', 'name', 'type', 'area', 'population', 'gdp', 'capital', 'created_at', 'geom']
                print(f"数据库表列: {expected_columns}")
                
                missing_columns = []
                for col in columns:
                    if col not in expected_columns:
                        missing_columns.append(col)
                
                if missing_columns:
                    print(f"⚠️  数据库表中不存在的列: {missing_columns}")
                else:
                    print("✅ 所有列都匹配")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    analyze_geojson() 