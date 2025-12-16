"""
Configuración para usar PyMySQL como reemplazo de mysqlclient en Windows
"""
import pymysql

# Hacer que PyMySQL funcione como mysqlclient
pymysql.install_as_MySQLdb()
