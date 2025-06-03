"""
检查数据库表结构和数据
"""
import sys
sys.path.append('.')
from database_config import DatabaseManager

def check_database():
    db = DatabaseManager()
    if db.connect():
        # 检查表结构
        result = db.execute_query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'polygon_features' ORDER BY ordinal_position")
        print('polygon_features表结构:')
        for row in result:
            print(f'  {row[0]}: {row[1]}')
        
        # 检查是否有数据
        count_result = db.execute_query('SELECT COUNT(*) FROM polygon_features')
        print(f'\n数据条数: {count_result[0][0] if count_result else 0}')
        
        # 查看实际数据
        data_result = db.execute_query('SELECT id, name, type, area, population, capital, gdp FROM polygon_features LIMIT 5')
        if data_result:
            print('\n实际数据:')
            for row in data_result:
                print(f'  ID: {row[0]}, Name: {row[1]}, Type: {row[2]}, Area: {row[3]}, Population: {row[4]}, Capital: {row[5]}, GDP: {row[6]}')
        else:
            print('\n没有数据')
    else:
        print("数据库连接失败")

if __name__ == "__main__":
    check_database() 