"""
最终修复验证测试
"""
import sys
sys.path.append('.')
from database_config import DatabaseManager
import pandas as pd

def test_database_query():
    """测试数据库查询功能"""
    print("🔍 测试数据库查询功能")
    print("=" * 50)
    
    try:
        db = DatabaseManager()
        if not db.connect():
            print("❌ 数据库连接失败")
            return False
        
        print("✅ 数据库连接成功")
        
        # 测试各表的查询
        tables = ['point_features', 'line_features', 'polygon_features']
        
        for table in tables:
            print(f"\n📊 测试表: {table}")
            
            # 检查表是否存在和数据量
            try:
                count_result = db.execute_query(f'SELECT COUNT(*) as count FROM {table}')
                if count_result and len(count_result) > 0:
                    count = count_result[0]['count']
                    print(f"  数据量: {count} 条")
                    
                    if count > 0:
                        # 测试空间查询
                        df = db.query_spatial_data(table, limit=5)
                        if not df.empty:
                            print(f"  ✅ 查询成功，返回 {len(df)} 条记录")
                            print(f"  列名: {list(df.columns)}")
                            
                            # 检查是否有坐标列
                            if 'longitude' in df.columns and 'latitude' in df.columns:
                                print(f"  ✅ 坐标提取成功")
                                print(f"  经度范围: {df['longitude'].min():.2f} ~ {df['longitude'].max():.2f}")
                                print(f"  纬度范围: {df['latitude'].min():.2f} ~ {df['latitude'].max():.2f}")
                            else:
                                print(f"  ⚠️  缺少坐标列")
                        else:
                            print(f"  ❌ 查询返回空结果")
                    else:
                        print(f"  ℹ️  表为空")
                else:
                    print(f"  ❌ 无法获取表信息")
                    
            except Exception as e:
                print(f"  ❌ 查询失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_geojson_import():
    """测试GeoJSON导入功能"""
    print("\n🗺️  测试GeoJSON导入功能")
    print("=" * 50)
    
    try:
        import json
        
        # 检查GeoJSON文件
        geojson_file = 'sample_data/provinces_simple.geojson'
        with open(geojson_file, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        print(f"✅ GeoJSON文件读取成功")
        print(f"要素数量: {len(geojson_data['features'])}")
        
        # 测试数据库导入
        db = DatabaseManager()
        if db.connect():
            print("✅ 数据库连接成功")
            
            # 清空测试表
            try:
                result = db.execute_query("DELETE FROM polygon_features WHERE name LIKE '%测试%'")
                print("✅ 清理测试数据")
            except:
                pass
            
            # 导入GeoJSON
            success = db.import_geojson_to_postgis(geojson_file, 'auto')
            if success:
                print("✅ GeoJSON导入成功")
                
                # 验证导入结果
                count_result = db.execute_query('SELECT COUNT(*) as count FROM polygon_features')
                if count_result and len(count_result) > 0:
                    count = count_result[0]['count']
                    print(f"导入后数据量: {count} 条")
                    
                    # 测试查询
                    df = db.query_spatial_data('polygon_features', limit=3)
                    if not df.empty:
                        print(f"✅ 查询验证成功，返回 {len(df)} 条记录")
                        return True
                    else:
                        print("❌ 查询验证失败")
                        return False
                else:
                    print("❌ 无法验证导入结果")
                    return False
            else:
                print("❌ GeoJSON导入失败")
                return False
        else:
            print("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 最终修复验证测试")
    print("=" * 60)
    
    # 测试1: 数据库查询
    query_success = test_database_query()
    
    # 测试2: GeoJSON导入
    import_success = test_geojson_import()
    
    # 总结
    print("\n📋 测试总结")
    print("=" * 60)
    print(f"数据库查询: {'✅ 通过' if query_success else '❌ 失败'}")
    print(f"GeoJSON导入: {'✅ 通过' if import_success else '❌ 失败'}")
    
    if query_success and import_success:
        print("\n🎉 所有测试通过！")
        print("\n💡 使用说明:")
        print("1. 启动应用: python main_enhanced_3d.py")
        print("2. 点击菜单 → 数据库 → 数据库操作")
        print("3. 在查询标签页选择表并查询")
        print("4. 点击'加载到地图'将数据显示在地图上")
        print("5. 在导入标签页可以导入GeoJSON文件")
    else:
        print("\n❌ 部分测试失败，请检查配置")

if __name__ == "__main__":
    main() 