# 🛠️ Claude Code Skill: 集成企业级日志系统 (通用版)

**适用场景**：任何 Spring Boot 项目的日志配置、企业级日志追踪

---

## 1. 快速开始

**如果你的项目需要以下功能，立即使用此 Skill：**
- 彩色控制台日志输出
- 按日期分目录存储日志
- 日志文件自动滚动 (Rolling)
- 异步输出提高性能
- 链路追踪 TraceID

**执行指令：**
> 请执行 **日志集成技能**，为项目配置企业级日志系统

---

## 2. 第一步：环境探测 (AI 自动执行)

### 2.1 检测项目配置

```bash
# 检测构建工具
ls -la pom.xml build.gradle 2>/dev/null

# 检测是否已有 Lombok
grep -E "lombok" pom.xml 2>/dev/null

# 检测是否已有 AOP
grep -E "spring-boot-starter-aop" pom.xml 2>/dev/null
```

### 2.2 读取现有日志配置

```bash
# 检测现有日志文件
find . -name "logback*.xml" -o -name "logging*.yml" -o -name "logging*.properties" 2>/dev/null
```

---

## 3. 第二步：添加依赖 (如需)

### 3.1 Maven 项目

```xml
<!-- Spring Boot 已默认包含 logback，无需额外依赖 -->
<!-- 如需 AOP (用于请求日志切面) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
```

### 3.2 Gradle 项目

```groovy
// Spring Boot 已默认包含
// 如需 AOP
implementation 'org.springframework.boot:spring-boot-starter-aop'
```

---

## 4. 第三步：生成 Logback 配置

### 4.1 通用配置模板

在 `src/main/resources/` 下创建 `logback-spring.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <!-- ==================== 属性定义 ==================== -->
    <property name="LOG_PATH" value="${LOG_PATH:-logs/${APP_NAME:-app}}"/>
    <property name="APP_NAME" value="${APP_NAME:-myapp}"/>
    <property name="LOG_PATTERN" value="%d{yyyy-MM-dd HH:mm:ss.SSS} %highlight(%-5level) [%green(%thread)] %magenta([%X{traceId:-}]) %cyan(%logger{50}) - %msg%n"/>

    <!-- ==================== 控制台输出 ==================== -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
    </appender>

    <!-- ==================== INFO 文件输出 ==================== -->
    <appender name="FILE_INFO" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/info.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_PATH}/info.%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>INFO</level>
        </filter>
    </appender>

    <!-- ==================== ERROR 文件输出 ==================== -->
    <appender name="FILE_ERROR" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/error.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_PATH}/error.%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>ERROR</level>
        </filter>
    </appender>

    <!-- ==================== 异步输出 (提高性能) ==================== -->
    <appender name="ASYNC_INFO" class="ch.qos.logback.classic.AsyncAppender">
        <appender-ref ref="FILE_INFO"/>
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
    </appender>

    <appender name="ASYNC_ERROR" class="ch.qos.logback.classic.AsyncAppender">
        <appender-ref ref="FILE_ERROR"/>
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
    </appender>

    <!-- ==================== 日志级别控制 ==================== -->
    <logger name="org.springframework" level="INFO"/>
    <logger name="org.mybatis" level="INFO"/>
    <logger name="com.yourpackage" level="DEBUG"/> <!-- 替换为实际包名 -->

    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="ASYNC_INFO"/>
        <appender-ref ref="ASYNC_ERROR"/>
    </root>
</configuration>
```

### 4.2 日志文件结构

执行后，日志将按以下结构存储：

```
logs/myapp/
├── info.log
├── error.log
├── info.2024-01-15.0.log
├── info.2024-01-15.1.log
├── error.2024-01-15.0.log
└── ...
```

---

## 5. 第四步：创建 TraceId 过滤器

### 5.1 TraceIdFilter.java

```java
// TraceIdFilter.java - 通用链路追踪过滤器
package com.yourpackage.common.filter;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import java.io.IOException;
import java.util.UUID;

public class TraceIdFilter implements Filter {

    private static final String TRACE_ID = "traceId";

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest httpRequest = (HttpServletRequest) request;
        String traceId = httpRequest.getHeader(TRACE_ID);

        if (traceId == null || traceId.isEmpty()) {
            traceId = UUID.randomUUID().toString().replace("-", "");
        }

        try {
            org.slf4j.MDC.put(TRACE_ID, traceId);
            chain.doFilter(request, response);
        } finally {
            org.slf4j.MDC.clear();
        }
    }
}
```

### 5.2 注册过滤器 (如使用原生 Servlet)

```java
// WebConfig.java
@Configuration
public class WebConfig {

    @Bean
    public FilterRegistrationBean<TraceIdFilter> traceIdFilter() {
        FilterRegistrationBean<TraceIdFilter> bean = new FilterRegistrationBean<>();
        bean.setFilter(new TraceIdFilter());
        bean.addUrlPatterns("/*");
        bean.setOrder(1);
        return bean;
    }
}
```

---

## 6. 第五步：创建统一请求日志切面

### 6.1 WebLogAspect.java

```java
// WebLogAspect.java - 统一请求日志切面
package com.yourpackage.common.aspect;

import jakarta.servlet.http.*;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.*;
import org.slf4j.*;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.*;

import java.util.*;

@Aspect
@Component
public class WebLogAspect {

    private static final Logger log = LoggerFactory.getLogger(WebLogAspect.class);

    @Pointcut("execution(* com.yourpackage..controller.*.*(..))")
    public void controllerPointcut() {}

    @Around("controllerPointcut()")
    public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
        // 获取请求信息
        RequestAttributes attributes = RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = (HttpServletRequest) attributes.resolveReference(RequestAttributes.REFERENCE_REQUEST);

        String method = request.getMethod();
        String url = request.getRequestURL().toString();
        String ip = getClientIp(request);
        String classMethod = joinPoint.getSignature().getDeclaringTypeName() + "." +
                             joinPoint.getSignature().getName();
        Object[] args = joinPoint.getArgs();

        // 过滤敏感参数 (如密码)
        Object[] filteredArgs = filterSensitiveArgs(args);

        long startTime = System.currentTimeMillis();

        log.info("=== REQUEST ===");
        log.info("URL: {} {}", method, url);
        log.info("IP: {}", ip);
        log.info("Method: {}", classMethod);
        log.info("Args: {}", Arrays.toString(filteredArgs));

        // 执行目标方法
        Object result = joinPoint.proceed();

        long timeCost = System.currentTimeMillis() - startTime;

        log.info("=== RESPONSE ===");
        log.info("Result: {}", result != null ? result.toString().substring(0, 500) : "null");
        log.info("Time-Cost: {}ms", timeCost);

        return result;
    }

    private String getClientIp(HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("WL-Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        return ip;
    }

    private Object[] filterSensitiveArgs(Object[] args) {
        return Arrays.stream(args).map(arg -> {
            if (arg == null) return null;
            if (arg instanceof HttpServletRequest || arg instanceof HttpServletResponse) {
                return "[" + arg.getClass().getSimpleName() + "]";
            }
            if (arg instanceof org.springframework.web.multipart.MultipartFile) {
                return "[MultipartFile]";
            }
            return arg;
        }).toArray();
    }
}
```

---

## 7. 第六步：application.yml 配置

```yaml
spring:
  config:
    activate:
      on-profile: dev

logging:
  level:
    root: INFO
    com.yourpackage: DEBUG  # 替换为实际包名
  file:
    path: logs/myapp
    name: logs/myapp/info.log
```

---

## 8. 常见问题

### Q1: 日志文件路径如何自定义？

```bash
# 通过环境变量自定义
export LOG_PATH=/var/log/myapp
export APP_NAME=myapp
```

### Q2: 如何只输出到控制台（开发环境）？

```xml
<!-- logback-dev.xml -->
<configuration>
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <root level="DEBUG">
        <appender-ref ref="CONSOLE"/>
    </root>
</configuration>
```

### Q3: TraceID 不显示？

确保：
1. MDC.put() 在请求开始时调用
2. MDC.clear() 在 finally 块中调用
3. 日志 Pattern 中包含 `%X{traceId}`

---

## 9. 验证清单

- [ ] 控制台输出彩色日志
- [ ] 日志按日期分目录存储
- [ ] info.log 和 error.log 分开输出
- [ ] TraceID 在日志中显示
- [ ] 异步输出正常工作

---

## 10. 附录：完整配置示例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration scan="true" scanPeriod="30 seconds">
    <!-- 属性 -->
    <property name="LOG_PATH" value="logs/${APP_NAME:-app}"/>
    <property name="APP_NAME" value="${APP_NAME:-app}"/>
    <property name="MAX_FILE_SIZE" value="100MB"/>
    <property name="MAX_HISTORY" value="30"/>

    <!-- 彩色格式 -->
    <property name="LOG_PATTERN" value="%d{yyyy-MM-dd HH:mm:ss.SSS} %highlight(%-5level) [%green(%thread)] %magenta([%X{traceId:-}]) %cyan(%logger{50}) - %msg%n"/>

    <!-- 控制台 -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
    </appender>

    <!-- 文件输出 -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/app.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_PATH}/app.%d{yyyy-MM-dd}.%i.log</fileNamePattern>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>${MAX_FILE_SIZE}</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
            <maxHistory>${MAX_HISTORY}</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>${LOG_PATTERN}</pattern>
        </encoder>
    </appender>

    <!-- 异步包装 -->
    <appender name="ASYNC_FILE" class="ch.qos.logback.classic.AsyncAppender">
        <appender-ref ref="FILE"/>
        <queueSize>512</queueSize>
        <discardingThreshold>0</discardingThreshold>
    </appender>

    <!-- 输出 -->
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="ASYNC_FILE"/>
    </root>
</configuration>
```

---

## 执行指令

> 请执行 **日志集成技能**，按照以下步骤操作：
> 1. 检测项目配置
> 2. 生成 logback-spring.xml
> 3. 创建 TraceId 过滤器
> 4. 创建请求日志切面
> 5. 验证日志输出

---

## AI 执行要点

作为 AI，你需要：

1. **先探测后修改**：先读取项目现有配置，不要直接生成
2. **根据环境选择配置**：开发环境简化配置，生产环境完整配置
3. **提供环境变量支持**：让用户可以通过环境变量自定义路径
4. **说明性能影响**：异步输出 vs 同步输出的区别
5. **提供最佳实践**：如日志级别选择、文件大小限制
