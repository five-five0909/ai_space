# 🛠️ Claude Code Skill: MySQL 数据库调试 (通用版)

**适用场景**：任何 Java 项目的 MySQL 连接失败、查询慢、死锁、数据不一致

---

## 1. 快速开始

**如果你的项目遇到以下错误，立即使用此 Skill：**
- `Access denied for user` - MySQL 连接被拒绝
- `Connection refused` - MySQL 端口不通
- `Communications link failure` - 连接超时
- `Lock wait timeout exceeded` - 死锁/锁等待
- `Table 'xxx' doesn't exist` - 表不存在

**执行指令：**
> 请执行 **MySQL调试技能**，诊断并修复数据库问题

---

## 2. 第一步：环境探测 (AI 自动执行)

### 2.1 检测项目配置

```bash
# 检测构建工具
ls -la pom.xml build.gradle 2>/dev/null

# 检测数据库连接池
grep -E "druid|hikari|c3p0|dbcp" pom.xml 2>/dev/null | head -5

# 检测配置文件
find . -name "application*.yml" -o -name "application*.properties" | xargs grep -l "datasource\|jdbc\|mysql" 2>/dev/null
```

**AI 需要读取的数据库配置：**

```yaml
# application.yml (Spring Boot + HikariCP)
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://${DB_HOST:localhost}:${DB_PORT:3306}/${DB_NAME}?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true
    username: ${DB_USERNAME:root}
    password: ${DB_PASSWORD:}
    hikari:
      minimum-idle: 5
      maximum-pool-size: 20
      idle-timeout: 30000
      max-lifetime: 1800000
      connection-timeout: 30000
      pool-name: HikariPool-${DB_NAME}
```

```properties
# application.properties
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.datasource.url=jdbc:mysql://localhost:3306/db_name?useUnicode=true&characterEncoding=UTF-8
spring.datasource.username=root
spring.datasource.password=password
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.maximum-pool-size=20
```

### 2.2 检测 MySQL 服务状态

```bash
# MySQL 服务状态
systemctl status mysql    # Linux
net start mysql          # Windows

# MySQL 端口检测
netstat -tlnp | grep 3306
lsof -i :3306

# MySQL 连接测试
mysql -h ${DB_HOST:localhost} -P ${DB_PORT:3306} -u ${DB_USERNAME:root} -p${DB_PASSWORD:}
```

---

## 3. 第二步：连接测试

### 3.1 命令行测试

```bash
# 本地连接
mysql -u root -p

# 远程连接
mysql -h 192.168.1.100 -P 3306 -u root -p

# 测试连接并执行查询
mysql -h localhost -u root -p -e "SHOW DATABASES; SELECT 1;"
```

### 3.2 Java 连接测试

```java
// ConnectionTest.java - 通用连接测试
import java.sql.*;

public class ConnectionTest {

    // 从配置读取
    private static final String URL = System.getProperty("db.url",
        "jdbc:mysql://localhost:3306/db_name?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai");
    private static final String USER = System.getProperty("db.username", "root");
    private static final String PASSWORD = System.getProperty("db.password", "");

    public static void main(String[] args) {
        try {
            // 加载驱动
            Class.forName("com.mysql.cj.jdbc.Driver");

            // 获取连接
            try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
                System.out.println("数据库连接成功!");

                // 测试查询
                try (Statement stmt = conn.createStatement();
                     ResultSet rs = stmt.executeQuery("SELECT 1 AS test")) {
                    if (rs.next()) {
                        System.out.println("查询测试通过: " + rs.getInt("test"));
                    }
                }
            }

        } catch (ClassNotFoundException e) {
            System.err.println("MySQL 驱动未找到: " + e.getMessage());
        } catch (SQLException e) {
            System.err.println("数据库连接失败: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
```

### 3.3 Spring Boot 测试

```java
// DataSourceConfigTest.java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;
import javax.sql.DataSource;
import java.sql.Connection;

@SpringBootTest
@TestPropertySource(properties = {
    "spring.datasource.url=jdbc:mysql://localhost:3306/test_db",
    "spring.datasource.username=root",
    "spring.datasource.password=password"
})
class DataSourceTest {

    @Autowired
    private DataSource dataSource;

    @Test
    void testConnection() throws SQLException {
        try (Connection conn = dataSource.getConnection()) {
            System.out.println("连接成功: " + conn.getMetaData().getURL());
            System.out.println("数据库: " + conn.getCatalog());
        }
    }
}
```

---

## 4. 第三步：常见问题诊断与修复

### 4.1 问题分类速查表

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `Access denied` | 用户名/密码错误 | 检查凭据 |
| `Connection refused` | MySQL 未启动/端口错误 | 启动 MySQL，检查端口 |
| `Unknown database` | 数据库不存在 | 创建数据库 |
| `Table doesn't exist` | 表未创建 | 执行建表脚本 |
| `Lock wait timeout` | 事务锁等待 | 优化事务，减少持有时间 |
| `Too many connections` | 连接池耗尽 | 增加池大小或优化连接使用 |
| `Packet too large` | 查询结果过大 | 增加 max_allowed_packet |

### 4.2 问题修复

**问题：连接池耗尽**

```yaml
# 解决方案：增加连接池配置
spring:
  datasource:
    hikari:
      minimum-idle: 5
      maximum-pool-size: 50          # 增加最大连接数
      idle-timeout: 30000
      max-lifetime: 1800000
      connection-timeout: 30000
```

**问题：连接超时**

```yaml
spring:
  datasource:
    hikari:
      connection-timeout: 60000       # 增加连接超时
      validation-timeout: 5000        # 验证超时
```

**问题：SSL 连接错误**

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/db_name?useSSL=false&serverTimezone=Asia/Shanghai
```

### 4.3 Druid 连接池配置

```yaml
# 如果使用 Alibaba Druid
spring:
  datasource:
    type: com.alibaba.druid.pool.DruidDataSource
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/db_name?useUnicode=true
    username: root
    password: password
    druid:
      initial-size: 5
      min-idle: 5
      max-active: 20
      max-wait: 60000
      time-between-eviction-runs-millis: 60000
      min-evictable-idle-time-millis: 300000
      validation-query: SELECT 1
      test-while-idle: true
      test-on-borrow: false
      test-on-return: false
```

---

## 5. 第四步：查询性能优化

### 5.1 慢查询检测

```sql
-- 查看慢查询配置
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;  # 超过2秒记录

-- 查看慢查询日志位置
SHOW VARIABLES LIKE 'slow_query_log_file';
```

### 5.2 执行计划分析

```sql
-- 分析查询计划
EXPLAIN SELECT * FROM users WHERE username = 'john';

-- 分析更新计划
EXPLAIN UPDATE users SET status = 1 WHERE id = 1;

-- 查看索引使用情况
SHOW INDEX FROM users;
```

### 5.3 索引优化建议

```sql
-- 为高频查询字段添加索引
ALTER TABLE users ADD INDEX idx_username (username);
ALTER TABLE orders ADD INDEX idx_user_time (user_id, created_at DESC);

-- 查看索引基数
SHOW INDEX FROM table_name;

-- 删除无用索引
ALTER TABLE table_name DROP INDEX index_name;
```

---

## 6. 第五步：锁问题诊断

### 6.1 查看锁状态

```sql
-- 查看当前锁
SHOW ENGINE INNODB STATUS;

-- 查看锁等待
SELECT * FROM information_schema.INNODB_LOCK_WAITS;

-- 查看进程
SHOW PROCESSLIST;
-- 或
SELECT * FROM information_schema.processlist;
```

### 6.2 死锁处理

```sql
-- 查看最近死锁
SHOW ENGINE INNODB STATUS\G

-- 自动处理：增加锁等待超时
SET GLOBAL innodb_lock_wait_timeout = 120;
```

---

## 7. 第六步：验证清单

- [ ] MySQL 服务正常运行
- [ ] 应用能够成功连接数据库
- [ ] 无连接超时错误
- [ ] 慢查询时间 < 1s
- [ ] 无死锁
- [ ] 数据一致无重复
- [ ] 索引被正确使用

---

## 7. 附录：常用 SQL 速查

```sql
-- 查看数据库大小
SELECT table_schema,
       ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
GROUP BY table_schema;

-- 查看表大小
SELECT table_name,
       ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'db_name';

-- 查看表行数
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema = 'db_name';

-- 优化表（定期执行）
OPTIMIZE TABLE table_name;

-- 修复表
REPAIR TABLE table_name;
```

---

## 执行指令

> 请执行 **MySQL调试技能**，按照以下步骤操作：
> 1. 检测项目数据库配置
> 2. 测试 MySQL 连接
> 3. 诊断并修复连接问题
> 4. 优化查询性能
> 5. 诊断并修复问题：{具体错误描述}

---

## AI 执行要点

作为 AI，你需要：

1. **先读取配置**：不要假设数据库地址和凭据
2. **根据连接池类型**：选择正确的配置（HikariCP vs Druid）
3. **提供可运行的测试代码**：让用户验证连接
4. **提供性能优化建议**：如索引、慢查询
5. **说明安全风险**：如 SQL 注入、数据泄露
