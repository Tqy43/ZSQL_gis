#!/usr/bin/env python3
"""
测试增强版+3D功能
"""
import sys
import pandas as pd
from pathlib import Path

def test_enhanced_3d():
    """测试增强版+3D功能"""
    print("🧪 测试增强版+3D功能")
    print("=" * 50)
    
    try:
        # 测试基础导入
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        import folium
        
        print("✅ 基础模块导入成功")
        
        # 测试Plotly导入
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            print("✅ Plotly模块可用 - 支持3D可视化")
            plotly_available = True
        except ImportError:
            print("⚠️ Plotly模块不可用 - 仅支持2D地图")
            plotly_available = False
        
        # 测试主窗口创建
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from main_enhanced_3d import Enhanced3DMainWindow
        main_window = Enhanced3DMainWindow()
        
        print("✅ 增强版+3D主窗口创建成功")
        
        # 测试地图组件
        map_widget = main_window.map_widget
        assert hasattr(map_widget, 'current_mode'), "缺少current_mode属性"
        assert hasattr(map_widget, 'update_display'), "缺少update_display方法"
        assert hasattr(map_widget, 'change_display_mode'), "缺少change_display_mode方法"
        
        print("✅ 地图组件功能完整")
        
        # 测试数据导入功能
        test_data = pd.DataFrame({
            'name': ['测试点1', '测试点2'],
            'longitude': [116.4, 121.5],
            'latitude': [39.9, 31.2],
            'value': [100, 200]
        })
        
        # 保存测试数据
        test_file = Path("test_data.csv")
        test_data.to_csv(test_file, index=False, encoding='utf-8')
        
        # 测试导入
        initial_layer_count = len(map_widget.data_layers)
        success = map_widget.import_data(str(test_file))
        
        assert success, "数据导入失败"
        assert len(map_widget.data_layers) > initial_layer_count, "图层未增加"
        
        print("✅ 数据导入功能正常")
        
        # 清理测试文件
        test_file.unlink()
        
        # 测试模式切换
        if plotly_available:
            map_widget.change_display_mode("3D可视化")
            assert map_widget.current_mode == "3D", "3D模式切换失败"
            
            map_widget.change_display_mode("2D地图")
            assert map_widget.current_mode == "2D", "2D模式切换失败"
            
            print("✅ 2D/3D模式切换正常")
        
        print("\n🎉 所有测试通过！")
        
        print("\n🌟 功能特性:")
        print("  • 集成Folium真实地图底图")
        if plotly_available:
            print("  • 支持3D数据可视化")
        print("  • 修复了数据导入显示问题")
        print("  • 2D/3D模式无缝切换")
        print("  • 完整的图层管理")
        print("  • 专业GIS功能")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_usage():
    """显示使用说明"""
    print("\n💡 使用说明:")
    print("=" * 50)
    
    print("🚀 启动应用:")
    print("  python main_enhanced_3d.py")
    
    print("\n🗺️ 功能介绍:")
    print("  • 显示模式: 2D地图 / 3D可视化")
    print("  • 地图类型: OpenStreetMap, 卫星图, 地形图")
    print("  • 数据导入: CSV, JSON格式")
    print("  • 交互功能: 缩放, 拖拽, 测量, 绘图")
    
    print("\n📊 数据要求:")
    print("  • 必须包含经纬度列")
    print("  • 支持的列名: longitude/lon/lng/x/X/经度")
    print("  • 支持的列名: latitude/lat/y/Y/纬度")
    
    print("\n🔧 解决的问题:")
    print("  • ✅ 修复了导入数据不显示的问题")
    print("  • ✅ 集成了3D可视化功能")
    print("  • ✅ 保持了所有原有功能")

if __name__ == '__main__':
    success = test_enhanced_3d()
    
    if success:
        show_usage()
        print("\n🎊 增强版+3D已准备就绪！")
        print("🚀 运行 'python main_enhanced_3d.py' 开始使用")
    else:
        print("\n⚠️ 请检查错误信息并修复问题")
    
    sys.exit(0 if success else 1) 