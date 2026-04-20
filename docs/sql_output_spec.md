# SQL 输出规格

## 1. 输出接口

模型输出必须是：

- 单条 SQL
- SQLite 方言
- 只读 `SELECT`

不允许：

- 自然语言解释
- Markdown 代码块
- 多语句
- `INSERT / UPDATE / DELETE / DROP / ALTER`

## 2. 格式要求

### 合法示例

```sql
SELECT department_name, COUNT(*) AS employee_count
FROM departments
GROUP BY department_name
ORDER BY employee_count DESC;
```

### 非法示例

```text
下面是 SQL：
SELECT * FROM departments;
```

```sql
SELECT * FROM departments;
SELECT * FROM employees;
```

```sql
DROP TABLE departments;
```

## 3. 清洗规则

为了做自动评测，推理后会执行一层轻量清洗：

- 去掉代码块围栏
- 去掉前缀 `SQL:`
- 提取首条 SQL 语句

但训练目标仍然是让模型原生只输出 SQL，而不是依赖后处理兜底。

## 4. 设计原因

第一版把接口收紧到“只输出 SQL”，有三个好处：

1. 评测简单
2. DPO 偏好标准清晰
3. 后续如果接 agent，可以直接把 SQL 生成能力作为底层工具接口复用
