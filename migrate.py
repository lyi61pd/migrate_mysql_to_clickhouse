import config
from clickhouse_driver import Client
# 连接数据库
client = Client(**config.CLICKHOUSE_CONFIG)
def get_table_column_info():
    '''获取数据库中所有表名和列名'''
    table_name_list = [item[0] for item in client.execute(f"SHOW TABLES FROM {config.CLICKHOUSE_CONFIG['database']}")] # type: ignore
    table_column_info = {}
    for table_name in table_name_list:
        columns = client.execute(f"DESCRIBE TABLE {config.CLICKHOUSE_CONFIG['database']}.{table_name}")
        column_names = [col[0] for col in columns] # type: ignore
        table_column_info[table_name] = column_names
    return table_column_info
# 获取数据库中所有表名和列名
table_column_info = get_table_column_info()
# 遍历各个表，生成迁移的SQL，执行SQL
for table_name,columns in table_column_info.items():
    if table_name == 'django_migrations':
        continue
    migrate_sql=f"insert into {table_name} select {','.join(columns)} from mysql('{config.MYSQL_CONFIG['host']}:{config.MYSQL_CONFIG['port']}','{config.MYSQL_CONFIG['database']}','{table_name}','{config.MYSQL_CONFIG['user']}','{config.MYSQL_CONFIG['password']}')"
    client.execute(migrate_sql)
    print(f"{table_name}迁移成功")