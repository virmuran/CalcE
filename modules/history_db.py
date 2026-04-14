# CalcE/modules/history_db.py
"""计算历史记录 SQLite 数据库管理"""
import sqlite3
import json
import os
from datetime import datetime
from PySide6.QtCore import QObject, Signal


class HistoryDB(QObject):
    """历史记录数据库，支持单例和刷新信号"""
    record_added = Signal()  # 保存新记录后发送此信号

    _instance = None
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()  # 初始化 QObject
        self._initialized = True

        db_dir = os.path.join(os.path.expandvars("%APPDATA%"), "CalcE", "CalcE")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, "calc_history.db")

        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS calculation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calculator_id TEXT NOT NULL,
                calculator_name TEXT NOT NULL,
                calculator_category TEXT DEFAULT '',
                inputs TEXT NOT NULL DEFAULT '{}',
                outputs TEXT NOT NULL DEFAULT '{}',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_calculator_id
            ON calculation_history(calculator_id)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_category
            ON calculation_history(calculator_category)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON calculation_history(created_at DESC)
        """)
        conn.commit()
        conn.close()

    def save(self, calculator_id, calculator_name, calculator_category,
             inputs, outputs, notes=""):
        """保存一条计算历史"""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO calculation_history
                (calculator_id, calculator_name, calculator_category,
                 inputs, outputs, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            calculator_id,
            calculator_name,
            calculator_category,
            json.dumps(inputs, ensure_ascii=False),
            json.dumps(outputs, ensure_ascii=False),
            notes,
            datetime.now().isoformat()
        ))
        conn.commit()
        record_id = cur.lastrowid
        conn.close()
        self.record_added.emit()  # 通知界面刷新
        return record_id

    def get_all(self, calculator_id=None, keyword="", limit=100, offset=0):
        """查询历史记录，支持按计算器筛选和关键词搜索"""
        conn = self._get_conn()
        cur = conn.cursor()

        where_clauses = []
        params = []

        if calculator_id:
            where_clauses.append("calculator_id = ?")
            params.append(calculator_id)

        if keyword:
            where_clauses.append(
                "(calculator_name LIKE ? OR inputs LIKE ? OR outputs LIKE ? OR notes LIKE ?)"
            )
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw, kw])

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        sql = f"""
            SELECT id, calculator_id, calculator_name, calculator_category,
                   inputs, outputs, notes, created_at
            FROM calculation_history
            WHERE {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        cur.execute(sql, params)
        rows = cur.fetchall()

        records = []
        for row in rows:
            records.append({
                "id": row[0],
                "calculator_id": row[1],
                "calculator_name": row[2],
                "calculator_category": row[3],
                "inputs": json.loads(row[4]),
                "outputs": json.loads(row[5]),
                "notes": row[6],
                "created_at": row[7],
            })

        cur.execute(f"SELECT COUNT(*) FROM calculation_history WHERE {where_sql}", params[:-2])
        total = cur.fetchone()[0]
        conn.close()
        return records, total

    def get_categories(self):
        """获取所有分类列表"""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT calculator_category FROM calculation_history "
            "WHERE calculator_category != '' ORDER BY calculator_category"
        )
        categories = [r[0] for r in cur.fetchall()]
        conn.close()
        return categories

    def get_calculator_ids(self):
        """获取所有计算器ID和名称"""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT calculator_id, calculator_name "
            "FROM calculation_history ORDER BY calculator_name"
        )
        result = {r[0]: r[1] for r in cur.fetchall()}
        conn.close()
        return result

    def delete(self, record_id):
        """删除指定记录"""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM calculation_history WHERE id = ?", (record_id,))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        return affected > 0
