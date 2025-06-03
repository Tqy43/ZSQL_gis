"""
创建应用程序图标 - 趴在地球上的青蛙
"""
from PIL import Image, ImageDraw
import math

def create_app_icon():
    """创建应用程序图标"""
    # 创建256x256的图像
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 地球背景
    earth_center = (size // 2, size // 2)
    earth_radius = size // 3
    
    # 绘制地球 - 蓝色背景
    draw.ellipse([
        earth_center[0] - earth_radius,
        earth_center[1] - earth_radius,
        earth_center[0] + earth_radius,
        earth_center[1] + earth_radius
    ], fill=(70, 130, 180), outline=(30, 90, 140), width=3)
    
    # 绘制大陆 - 绿色
    # 大陆1 (类似亚洲)
    continent1_points = [
        (earth_center[0] - 20, earth_center[1] - 30),
        (earth_center[0] + 10, earth_center[1] - 40),
        (earth_center[0] + 30, earth_center[1] - 20),
        (earth_center[0] + 25, earth_center[1]),
        (earth_center[0] + 15, earth_center[1] + 20),
        (earth_center[0] - 10, earth_center[1] + 15),
        (earth_center[0] - 25, earth_center[1] - 5)
    ]
    draw.polygon(continent1_points, fill=(34, 139, 34))
    
    # 大陆2 (类似非洲)
    continent2_points = [
        (earth_center[0] - 40, earth_center[1] - 10),
        (earth_center[0] - 30, earth_center[1] - 25),
        (earth_center[0] - 20, earth_center[1] - 15),
        (earth_center[0] - 25, earth_center[1] + 10),
        (earth_center[0] - 35, earth_center[1] + 25),
        (earth_center[0] - 45, earth_center[1] + 15)
    ]
    draw.polygon(continent2_points, fill=(34, 139, 34))
    
    # 青蛙身体位置 (趴在地球上方)
    frog_center_x = earth_center[0]
    frog_center_y = earth_center[1] - earth_radius + 20
    
    # 青蛙身体 - 椭圆形
    body_width = 40
    body_height = 30
    draw.ellipse([
        frog_center_x - body_width // 2,
        frog_center_y - body_height // 2,
        frog_center_x + body_width // 2,
        frog_center_y + body_height // 2
    ], fill=(50, 205, 50), outline=(34, 139, 34), width=2)
    
    # 青蛙头部
    head_radius = 18
    head_y = frog_center_y - 15
    draw.ellipse([
        frog_center_x - head_radius,
        head_y - head_radius,
        frog_center_x + head_radius,
        head_y + head_radius
    ], fill=(50, 205, 50), outline=(34, 139, 34), width=2)
    
    # 青蛙眼睛
    eye_radius = 6
    eye_offset = 8
    # 左眼
    draw.ellipse([
        frog_center_x - eye_offset - eye_radius,
        head_y - 8 - eye_radius,
        frog_center_x - eye_offset + eye_radius,
        head_y - 8 + eye_radius
    ], fill=(255, 255, 255), outline=(0, 0, 0), width=1)
    # 左眼瞳孔
    draw.ellipse([
        frog_center_x - eye_offset - 3,
        head_y - 8 - 3,
        frog_center_x - eye_offset + 3,
        head_y - 8 + 3
    ], fill=(0, 0, 0))
    
    # 右眼
    draw.ellipse([
        frog_center_x + eye_offset - eye_radius,
        head_y - 8 - eye_radius,
        frog_center_x + eye_offset + eye_radius,
        head_y - 8 + eye_radius
    ], fill=(255, 255, 255), outline=(0, 0, 0), width=1)
    # 右眼瞳孔
    draw.ellipse([
        frog_center_x + eye_offset - 3,
        head_y - 8 - 3,
        frog_center_x + eye_offset + 3,
        head_y - 8 + 3
    ], fill=(0, 0, 0))
    
    # 青蛙嘴巴
    mouth_points = [
        (frog_center_x - 8, head_y + 5),
        (frog_center_x, head_y + 8),
        (frog_center_x + 8, head_y + 5)
    ]
    draw.polygon(mouth_points, fill=(255, 20, 147))
    
    # 青蛙前腿 (趴着的姿势)
    # 左前腿
    left_arm_points = [
        (frog_center_x - 25, frog_center_y - 5),
        (frog_center_x - 35, frog_center_y + 5),
        (frog_center_x - 30, frog_center_y + 15),
        (frog_center_x - 20, frog_center_y + 10)
    ]
    draw.polygon(left_arm_points, fill=(50, 205, 50), outline=(34, 139, 34), width=1)
    
    # 右前腿
    right_arm_points = [
        (frog_center_x + 25, frog_center_y - 5),
        (frog_center_x + 35, frog_center_y + 5),
        (frog_center_x + 30, frog_center_y + 15),
        (frog_center_x + 20, frog_center_y + 10)
    ]
    draw.polygon(right_arm_points, fill=(50, 205, 50), outline=(34, 139, 34), width=1)
    
    # 青蛙后腿
    # 左后腿
    left_leg_points = [
        (frog_center_x - 15, frog_center_y + 10),
        (frog_center_x - 25, frog_center_y + 25),
        (frog_center_x - 15, frog_center_y + 30),
        (frog_center_x - 5, frog_center_y + 20)
    ]
    draw.polygon(left_leg_points, fill=(50, 205, 50), outline=(34, 139, 34), width=1)
    
    # 右后腿
    right_leg_points = [
        (frog_center_x + 15, frog_center_y + 10),
        (frog_center_x + 25, frog_center_y + 25),
        (frog_center_x + 15, frog_center_y + 30),
        (frog_center_x + 5, frog_center_y + 20)
    ]
    draw.polygon(right_leg_points, fill=(50, 205, 50), outline=(34, 139, 34), width=1)
    
    # 添加一些装饰性的斑点
    spot_positions = [
        (frog_center_x - 10, frog_center_y - 5),
        (frog_center_x + 8, frog_center_y + 2),
        (frog_center_x - 5, frog_center_y + 8)
    ]
    for spot_x, spot_y in spot_positions:
        draw.ellipse([
            spot_x - 3, spot_y - 3,
            spot_x + 3, spot_y + 3
        ], fill=(34, 139, 34))
    
    # 保存不同尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256]
    for icon_size in sizes:
        resized_img = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        resized_img.save(f'../assets/app_icon_{icon_size}.png')
    
    # 保存ICO格式 (Windows图标)
    img.save('../assets/app_icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    
    print("✅ 应用程序图标创建完成!")
    print("生成的文件:")
    for size in sizes:
        print(f"  - app_icon_{size}.png")
    print("  - app_icon.ico")

if __name__ == "__main__":
    create_app_icon() 