MYSQL_USER = "root"
MYSQL_PASSWORD = "123"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306

# Nếu muốn kết nối tới MySQL server mà KHÔNG chỉ định database
MYSQL_CONN = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/codecourse"
