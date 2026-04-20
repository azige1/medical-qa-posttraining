# Preference 判优标准

## 1. 目标

构造 `chosen/rejected` 时，必须保证 preference 不是“SQL 看起来更顺眼”，而是能稳定解释为什么 `chosen` 更优。

本标准同时服务于：

- `DPO`
- `Reward Model`

也就是说，同一对样本既要能支撑“模型应该更偏好 chosen”，也要能支撑“reward 应该给 chosen 更高分”。

## 2. 判优优先级

对于同一 `schema_text + question_zh`，比较优先级固定如下：

1. 执行结果是否正确
2. 表列引用是否 grounded 到正确 schema
3. SQL 是否可执行
4. SQL 是否只读且安全
5. SQL 是否更简洁稳定

只要前面的层级已经分出胜负，后面的层级不再翻盘。

## 3. 直接判差条件

若 `rejected` 存在以下任一问题，即使写法更复杂，也应直接判差：

- 非 `SELECT`
- 多语句
- 引用了不存在的表或列
- 无法执行
- 执行结果错误
- 为了“像 SQL”输出了自然语言解释

## 4. rejected 的主要来源

### 4.1 模型生成错误

- base / SFT 模型实际生成但执行错误
- 这类 pair 最贴近真实推理错误分布

### 4.2 规则扰动错误

- 错表
- 错列
- 错过滤条件
- 错聚合函数
- 错排序 / LIMIT
- 错 join key

### 4.3 部分正确但不等价

- SQL 能执行，但结果不等价
- 例如漏掉分组条件、过滤条件过宽、聚合层级错误

## 5. 推荐标签

给每条 `rejected` 至少打一个错误标签，便于后续误差分析：

- `wrong_table`
- `wrong_column`
- `wrong_filter`
- `wrong_aggregation`
- `wrong_join`
- `wrong_order_limit`
- `schema_hallucination`
- `unsafe_sql`
- `execution_failure`
- `wrong_result`

## 6. 一个合格的判优解释应该长什么样

对于每条 pair，理想情况下都能补一句：

- “`chosen` 执行结果与 gold 一致；`rejected` 把 `orders.amount` 写成了 `products.unit_price`，虽然能执行，但结果不等价。”
- “`chosen` 正确引用了 `departments.department_name`；`rejected` 使用了不存在的列，属于 schema hallucination。”

如果一句话不能解释清楚，说明 pair 设计可能还不够稳定。
