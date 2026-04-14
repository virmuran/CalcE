# CalcE - 化工工程师桌面工具

基于 **PySide6** 的桌面应用，面向化工工程师，提供专业工程计算和单位换算功能。

---

## 功能模块

### 工程计算（38+ 计算器）

| 类别 | 计算器 |
|------|--------|
| 管道 | 管径计算、管道压降、管道壁厚、管道跨距、管道间距、管道补偿 |
| 流体设备 | 离心泵功率、NPSHa 汽蚀余量、风机功率 |
| 换热 | 换热器面积、换热器计算、隔热层厚度、蒸汽管径流量、长距离蒸汽管 |
| 热工/制冷 | 制冷循环、蒸汽性质、气体状态转换、湿空气 |
| 容器/结构 | 容器体积计算、罐体重量、篮式过滤器设计 |
| 安全/消防 | 安全阀计算、安全泄放面积、消火栓计算、危化品查询、腐蚀数据查询 |
| 热力学 | 状态方程(EOS)、纯物质性质、气体混合物性质、固体溶解度、汽液平衡(VLE)、混合液闪点 |
| 其他 | 法兰尺寸、压力管道定义、压力管道压缩流压降、制冷剂性质 |

### 单位换算器

支持长度、重量、温度、压力、体积、面积、能量、功率、速度、力等多类换算。

### 计算历史

每次工程计算自动记录到 SQLite 数据库，支持按计算器类型筛选和关键词搜索，可查看历史输入输出详情，逐条删除。

### 倒计时

多事件倒计时，自定义名称和目标时间，实时更新。

---

## 技术栈

- **GUI**：Python 3.8+ / PySide6 6.5+
- **科学计算**：NumPy、SciPy
- **PDF 导出**：ReportLab
- **日志**：Loguru
- **数据存储**：本地 JSON（AppData/CalcE） + SQLite（计算历史）
- **计算基础**：流体力学、制冷热力学、IAPWS-IF97 水蒸气公式、离心泵理论等

---

## 运行

```bash
pip install -r requirements.txt
python main.py
```

---

## 目录结构

```
CalcE/
├── main.py
├── data_manager.py           # 数据管理（JSON 单例）
├── theme_manager.py          # 主题管理
├── module_loader.py          # 模块动态加载器
├── base_module.py            # 模块基类
├── resource_helper.py        # 资源路径
├── history_db.py             # 历史记录 SQLite 数据库
├── requirements.txt
└── modules/
    ├── history_viewer.py     # 计算历史查看器
    ├── chemical_calculations/
    │   ├── calculators/       # 38+ 计算器实现
    │   └── chemical_calculations_widget.py
    ├── converter/             # 单位换算器
    └── countdowns.py          # 倒计时
```

---

## 免责声明

计算结果仅供工程参考，实际应用请由专业工程师审核确认。
