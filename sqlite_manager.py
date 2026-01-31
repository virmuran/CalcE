# CalcE/sqlite_manager.py
import sqlite3
import os
import json
from datetime import datetime

class SQLiteManager:
    # 初始化数据库（默认路径和原JSON同目录）
    def __init__(self, db_name="CalcE_app.db"):
        # 数据库存储路径（和原JSON文件同目录：AppData/Roaming/CalcE）
        self.db_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "CalcE")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, db_name)
        # 初始化所有表
        self.init_tables()

    # 连接数据库（通用方法，内部使用）
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        # 支持中文+返回字典格式（不用手动解析元组）
        conn.execute("PRAGMA encoding = 'UTF-8'")
        conn.row_factory = sqlite3.Row
        return conn

    # 初始化所有核心表（设备、物料、MSDS、流程图、质量平衡）
    def init_tables(self):
        tables = [
            # 1. 设备清单表
            """
            CREATE TABLE IF NOT EXISTS equipment (
                id TEXT PRIMARY KEY,  # 设备唯一ID（如EQ_A5A43368）
                name TEXT NOT NULL,   # 设备名称（如反应器）
                type TEXT,            # 设备类型
                parameters TEXT,      # 设备参数（JSON字符串存储）
                create_time TEXT,
                update_time TEXT
            )
            """,
            # 2. 物料数据表
            """
            CREATE TABLE IF NOT EXISTS material (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_name TEXT NOT NULL UNIQUE,  # 物料名称（唯一）
                properties TEXT,                     # 物料属性（JSON字符串）
                create_time TEXT,
                update_time TEXT
            )
            """,
            # 3. MSDS文档表
            """
            CREATE TABLE IF NOT EXISTS msds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_id INTEGER,                 # 关联物料表ID
                document_content TEXT,               # MSDS文档内容
                version TEXT,                        # 版本号
                create_time TEXT,
                update_time TEXT,
                FOREIGN KEY (material_id) REFERENCES material(id)
            )
            """,
            # 4. 工艺流程图表
            """
            CREATE TABLE IF NOT EXISTS process_flow (
                id TEXT PRIMARY KEY,  # 流程图唯一ID
                nodes TEXT,           # 节点数据（设备/物料节点，JSON字符串）
                edges TEXT,           # 连线数据，JSON字符串
                create_time TEXT,
                update_time TEXT
            )
            """,
            # 5. 质量平衡表
            """
            CREATE TABLE IF NOT EXISTS mass_balance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flow_id TEXT,         # 关联流程图ID
                material_id INTEGER,  # 关联物料ID
                input_amount REAL,    # 输入量
                output_amount REAL,   # 输出量
                loss_amount REAL,     # 损耗量
                create_time TEXT,
                update_time TEXT,
                FOREIGN KEY (flow_id) REFERENCES process_flow(id),
                FOREIGN KEY (material_id) REFERENCES material(id)
            )
            """
        ]

        conn = self._connect()
        cursor = conn.cursor()
        try:
            for sql in tables:
                cursor.execute(sql)
            conn.commit()
            print(f"✅ SQLite表初始化完成，数据库路径：{self.db_path}")
        except Exception as e:
            print(f"❌ SQLite表初始化失败：{e}")
            conn.rollback()
        finally:
            conn.close()

    # 通用新增/修改方法（兼容所有表）
    def save_data(self, table_name, data, where=None):
        """
        :param table_name: 表名（如equipment、material）
        :param data: 字典，要保存的数据（如{"id":"EQ_123", "name":"反应器"}）
        :param where: 字典，更新条件（如{"id":"EQ_123"}），None则新增
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["update_time"] = now
        if not where:  # 新增数据
            data["create_time"] = now
            keys = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data.values()])
            sql = f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})"
            params = list(data.values())
        else:  # 更新数据
            set_clause = ", ".join([f"{k}=?" for k in data.keys()])
            where_clause = " AND ".join([f"{k}=?" for k in where.keys()])
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            params = list(data.values()) + list(where.values())

        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"❌ 数据重复/约束失败：{e}")
            return False
        except Exception as e:
            print(f"❌ 保存数据失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # 通用查询方法（兼容所有表）
    def get_data(self, table_name, where=None, one=False):
        """
        :param table_name: 表名
        :param where: 字典，查询条件（如{"id":"EQ_123"}），None则查所有
        :param one: 是否只查一条数据
        :return: 字典/列表（查询结果）
        """
        conn = self._connect()
        cursor = conn.cursor()
        try:
            if where:
                where_clause = " AND ".join([f"{k}=?" for k in where.keys()])
                sql = f"SELECT * FROM {table_name} WHERE {where_clause}"
                cursor.execute(sql, list(where.values()))
            else:
                sql = f"SELECT * FROM {table_name}"
                cursor.execute(sql)

            if one:
                row = cursor.fetchone()
                return dict(row) if row else None
            else:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ 查询数据失败：{e}")
            return [] if not one else None
        finally:
            conn.close()

    # 通用删除方法
    def delete_data(self, table_name, where):
        if not where:
            print("❌ 删除必须传条件（where），禁止全表删除")
            return False
        conn = self._connect()
        cursor = conn.cursor()
        try:
            where_clause = " AND ".join([f"{k}=?" for k in where.keys()])
            sql = f"DELETE FROM {table_name} WHERE {where_clause}"
            cursor.execute(sql, list(where.values()))
            conn.commit()
            return cursor.rowcount > 0  # 返回是否删除成功
        except Exception as e:
            print(f"❌ 删除数据失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # 【迁移专用】从JSON文件导入数据到SQLite
    def migrate_from_json(self, json_path):
        if not os.path.exists(json_path):
            print(f"❌ JSON文件不存在：{json_path}")
            return False

        # 读取JSON数据
        with open(json_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        # 逐个迁移数据
        # 1. 迁移设备数据
        if "equipment" in json_data:
            for eq in json_data["equipment"]:
                self.save_data("equipment", eq, where={"id": eq.get("id")})
        # 2. 迁移物料数据
        if "material" in json_data:
            for mat in json_data["material"]:
                self.save_data("material", mat, where={"material_name": mat.get("material_name")})
        # 3. 迁移MSDS数据
        if "msds" in json_data:
            for msds in json_data["msds"]:
                self.save_data("msds", msds, where={"material_id": msds.get("material_id")})
        # 4. 迁移流程图数据
        if "process_flow" in json_data:
            for flow in json_data["process_flow"]:
                self.save_data("process_flow", flow, where={"id": flow.get("id")})
        # 5. 迁移质量平衡数据
        if "mass_balance" in json_data:
            for mb in json_data["mass_balance"]:
                self.save_data("mass_balance", mb, where={"id": mb.get("id")})

        print("✅ JSON数据迁移到SQLite完成！")
        return True