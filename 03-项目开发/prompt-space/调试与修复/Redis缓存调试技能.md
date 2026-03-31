# 🛠️ Claude Code Skill: Redis 连接与缓存调试 (通用版)

**适用场景**：任何 Spring Boot/Java 项目的 Redis 连接失败、缓存问题、序列化异常

---

## 1. 快速开始

**如果你的项目遇到以下错误，立即使用此 Skill：**
- `Unable to connect to Redis at localhost:6379`
- `WRONGPASS invalid username-password pair`
- `Cannot serialize` 序列化异常
- `NullPointerException` 缓存获取为 null

**执行指令：**
> 请执行 **Redis调试技能**，诊断并修复 Redis 问题

---

## 2. 第一步：环境探测 (AI 自动执行)

### 2.1 检测构建工具和依赖

```bash
# 检测项目类型
# ============================================

# Maven 项目 (pom.xml)
ls -la pom.xml
grep -E "spring-boot-starter-data-redis|redis" pom.xml

# Gradle 项目 (build.gradle)
ls -la build.gradle
grep -E "spring-boot-starter-data-redis|redis" build.gradle

# 报告：确认使用的是什么 Redis 客户端
```

### 2.2 读取配置文件

```bash
# 检测配置文件位置
find . -name "application*.yml" -o -name "application*.properties" | head -5
```

**AI 需要读取以下配置文件：**

```yaml
# application.yml (Spring Boot 风格)
spring:
  data:
    redis:
      host: ${REDIS_HOST:localhost}     # Redis 地址
      port: ${REDIS_PORT:6379}          # 端口
      password: ${REDIS_PASSWORD:}      # 密码(可能为空)
      database: ${REDIS_DATABASE:0}     # 数据库编号
      timeout: 10000ms                   # 连接超时
      lettuce:
        pool:
          enabled: true
          max-active: 20
          max-idle: 10
          min-idle: 5
          max-wait: -1ms
```

```properties
# application.properties (Spring Boot 风格)
spring.data.redis.host=localhost
spring.data.redis.port=6379
spring.data.redis.password=
spring.data.redis.database=0
```

```yaml
# application.yml (Spring Boot 2.x 旧版)
spring:
  redis:
    host: localhost
    port: 6379
    password:
    database: 0
```

### 2.3 检测 Redis 服务状态

```bash
# 本地测试 Redis 连接
redis-cli ping

# 带认证测试
redis-cli -h <host> -p <port> -a <password> ping

# 查看占用端口
netstat -tlnp | grep 6379
# 或
lsof -i :6379
```

---

## 3. 第二步：连接测试 (根据配置类型选择)

### 3.1 Spring Boot 项目 (自动配置)

**无需编写代码，直接测试连接：**

```bash
# 使用 redis-cli 测试
redis-cli -h ${spring.data.redis.host:localhost} -p ${spring.data.redis.port:6379} -a ${spring.data.redis.password:} ping
```

**期望输出：** `PONG`

### 3.2 非 Spring Boot 项目 (原生 Java)

**创建测试类：**

```java
// RedisConnectionTest.java
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

public class RedisConnectionTest {

    // 从配置文件读取
    private static final String HOST = System.getProperty("redis.host", "localhost");
    private static final int PORT = Integer.parseInt(System.getProperty("redis.port", "6379"));
    private static final String PASSWORD = System.getProperty("redis.password", "");

    public static void main(String[] args) {
        Jedis jedis = null;
        try {
            jedis = new Jedis(HOST, PORT);
            if (PASSWORD != null && !PASSWORD.isEmpty()) {
                jedis.auth(PASSWORD);
            }

            // 测试连接
            String result = jedis.ping();
            System.out.println("Redis 连接成功: " + result);

            // 测试读写
            jedis.set("test:key", "Hello Redis");
            String value = jedis.get("test:key");
            System.out.println("读取值: " + value);

            // 清理测试数据
            jedis.del("test:key");
            System.out.println("测试通过!");

        } catch (Exception e) {
            System.err.println("Redis 连接失败: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (jedis != null) {
                jedis.close();
            }
        }
    }
}
```

### 3.3 Spring Boot + Lettuce (推荐)

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.redis.core.RedisTemplate;
import org.junit.jupiter.api.Test;
import java.time.Duration;

@SpringBootTest
class RedisConnectionTest {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    @Test
    void testRedisConnection() {
        // 测试连接
        redisTemplate.opsForValue().set("test:connection", "OK", Duration.ofSeconds(60));

        Object result = redisTemplate.opsForValue().get("test:connection");
        System.out.println("Redis 连接测试: " + result);

        // 清理
        redisTemplate.delete("test:connection");
        System.out.println("Redis 连接正常!");
    }
}
```

---

## 4. 第三步：常见问题诊断与修复

### 4.1 问题分类速查表

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `Unable to connect to localhost:6379` | Redis 未启动/地址错误 | 启动 Redis 或检查 host 配置 |
| `Connection refused` | 端口错误/防火墙 | 检查 port 和防火墙设置 |
| `WRONGPASS invalid username-password pair` | 密码错误 | 检查 password 配置 |
| `Cannot serialize` | 对象未序列化 | 使用 JSON 序列化器 |
| `JedisConnectionException` | 连接池耗尽 | 配置连接池参数 |
| `OOM command not allowed` | 内存不足 | 清理数据或增加内存 |

### 4.2 连接问题修复

**问题：使用默认 localhost，实际需要远程地址**

```yaml
# 解决方案：修改 application.yml
spring:
  data:
    redis:
      host: ${REDIS_HOST:192.168.80.6}  # 实际 Redis 地址
      port: ${REDIS_PORT:6379}
      password: ${REDIS_PASSWORD:123456}
```

**问题：密码认证失败**

```java
// Jedis 方式
Jedis jedis = new Jedis(host, port);
jedis.auth(password);  // 如果密码为空则不调用

// Spring Boot 方式 (自动处理)
spring:
  data:
    redis:
      password: "正确的密码"  # 或留空
```

### 4.3 序列化问题修复

**问题：`Cannot serialize` 异常**

```java
// 解决方案：配置 Jackson2JsonRedisSerializer
@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);

        // Key 使用 String 序列化
        template.setKeySerializer(new StringRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());

        // Value 使用 JSON 序列化
        Jackson2JsonRedisSerializer<Object> jsonSerializer =
            new Jackson2JsonRedisSerializer<>(Object.class);
        template.setValueSerializer(jsonSerializer);
        template.setHashValueSerializer(jsonSerializer);

        template.afterPropertiesSet();
        return template;
    }
}

// 对于存储 Java 对象，确保实现 Serializable
@Data
public class User implements Serializable {
    private Long id;
    private String username;
}
```

### 4.4 连接池配置

```yaml
spring:
  data:
    redis:
      host: localhost
      port: 6379
      lettuce:
        pool:
          enabled: true
          max-active: 16        # 最大连接数
          max-idle: 8           # 最大空闲连接
          min-idle: 4          # 最小空闲连接
          max-wait: -1ms       # 最大等待时间
```

---

## 5. 第四步：多环境配置支持

### 5.1 环境变量覆盖

```yaml
# application.yml (基础配置)
spring:
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: ${REDIS_PORT:6379}
      password: ${REDIS_PASSWORD:}
```

```bash
# Linux/Mac 环境变量
export REDIS_HOST=192.168.80.6
export REDIS_PASSWORD=123456

# Windows
set REDIS_HOST=192.168.80.6
set REDIS_PASSWORD=123456
```

### 5.2 多环境配置文件

```
src/main/resources/
├── application.yml              # 默认配置
├── application-dev.yml         # 开发环境
├── application-test.yml        # 测试环境
├── application-prod.yml        # 生产环境
```

```yaml
# application-dev.yml (开发环境)
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password:
```

```yaml
# application-prod.yml (生产环境)
spring:
  data:
    redis:
      host: ${REDIS_HOST}
      port: ${REDIS_PORT}
      password: ${REDIS_PASSWORD}
```

---

## 6. 第五步：验证清单

执行完成后，逐项检查：

- [ ] **连接测试通过**：`redis-cli ping` 返回 `PONG`
- [ ] **应用启动正常**：无 Redis 相关启动错误
- [ ] **读写测试通过**：能够正确存取数据
- [ ] **序列化正常**：对象能够正确序列化和反序列化
- [ ] **连接池正常**：在高并发下无连接超时
- [ ] **环境变量生效**：生产环境配置正确覆盖

---

## 7. 附录：Redis 客户端对比

| 客户端 | 特点 | 适用场景 |
|--------|------|----------|
| **Jedis** | 传统同步客户端，线程不安全 | 需要连接池管理 |
| **Lettuce** | Netty 异步客户端，线程安全 | Spring Boot 默认 |
| **Redisson** | 支持分布式锁、集合等高级功能 | 需要分布式特性 |

**Spring Boot 2.x 之前使用 Jedis，2.x 之后默认使用 Lettuce**

---

## 执行指令

> 请执行 **Redis调试技能**，按照以下步骤操作：
> 1. 检测项目类型和依赖
> 2. 读取 Redis 配置文件
> 3. 测试 Redis 连接
> 4. 诊断并修复问题：{具体错误描述}

---

## AI 执行要点

作为 AI，你需要：

1. **先探测后修改**：先读取项目配置，不要猜测
2. **根据项目类型选择**：Maven/Gradle、Spring Boot/原生 Java
3. **提供可运行的测试代码**：让用户验证修复效果
4. **解释原因**：告诉用户为什么会出现这个问题
5. **提供最佳实践**：如生产环境配置建议
