# 🛠️ Claude Code Skill: JWT 认证调试 (通用版)

**适用场景**：任何 Java/Spring Boot 项目的 Token 失效、权限验证失败、401/403 错误

---

## 1. 快速开始

**如果你的项目遇到以下错误，立即使用此 Skill：**
- `401 Unauthorized` - Token 无效或过期
- `403 Forbidden` - 权限不足
- `Token expired` - Token 过期
- `Signature verification failed` - 签名验证失败
- `Unsupported JWT token` - Token 格式错误

**执行指令：**
> 请执行 **JWT认证调试技能**，诊断并修复 Token 问题

---

## 2. 第一步：环境探测 (AI 自动执行)

### 2.1 检测项目类型

```bash
# ============================================
# 检测构建工具
ls -la pom.xml build.gradle 2>/dev/null

# Maven 依赖检测
grep -E "jjwt|java-jwt|auth.*jwt" pom.xml 2>/dev/null

# Gradle 依赖检测
grep -E "jjwt|java-jwt|auth.*jwt" build.gradle 2>/dev/null
```

### 2.2 读取 JWT 配置

```bash
# 检测配置文件
find . -name "application*.yml" -o -name "application*.properties" | xargs grep -l "jwt\|token" 2>/dev/null
```

**AI 需要读取的 JWT 配置：**

```yaml
# application.yml (Spring Boot)
jwt:
  secret: ${JWT_SECRET:your-256-bit-secret-key}  # 签名密钥（至少256位）
  expiration: ${JWT_EXPIRATION:86400000}          # 过期时间(ms)，默认24小时
  header: ${JWT_HEADER:Authorization}            # HTTP Header 名称
  prefix: ${JWT_PREFIX:Bearer }                   # Token 前缀
```

```properties
# application.properties
jwt.secret=your-256-bit-secret-key
jwt.expiration=86400000
jwt.header=Authorization
jwt.prefix=Bearer
```

### 2.3 检测 JWT 依赖版本

**JJWT 版本对比：**

| 版本 | 包名 | 特点 |
|------|------|------|
| **0.12.x** | `io.jsonwebtoken:jjwt-api:0.12.x` | 最新版，推荐使用 |
| **0.11.x** | `io.jsonwebtoken:jjwt-api:0.11.x` | 广泛使用，稳定 |
| **0.9.x** | `io.jsonwebtoken:jjwt:0.9.x` | 老版本，已废弃 |

```xml
<!-- Maven - 推荐使用 0.12.x -->
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-api</artifactId>
    <version>0.12.5</version>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-impl</artifactId>
    <version>0.12.5</version>
    <scope>runtime</scope>
</dependency>
<dependency>
    <groupId>io.jsonwebtoken</groupId>
    <artifactId>jjwt-jackson</artifactId>
    <version>0.12.5</version>
    <scope>runtime</scope>
</dependency>
```

---

## 3. 第二步：通用 JWT 工具类

### 3.1 JJWT 0.12.x 通用实现

```java
// JwtUtils.java - 适用于任何 Spring Boot 项目
package com.yourproject.utils;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

public class JwtUtils {

    // 从配置文件读取
    private static final String SECRET = System.getProperty("jwt.secret", "default-secret-key-change-in-production");
    private static final long EXPIRATION = Long.parseLong(System.getProperty("jwt.expiration", "86400000"));

    private static final SecretKey KEY = Keys.hmacShaKeyFor(SECRET.getBytes(StandardCharsets.UTF_8));

    /**
     * 生成 Token
     */
    public static String generateToken(Long userId, String username) {
        return generateToken(userId, username, new HashMap<>());
    }

    public static String generateToken(Long userId, String username, Map<String, Object> claims) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + EXPIRATION);

        return Jwts.builder()
                .subject(userId.toString())
                .claims(claims)
                .claim("username", username)
                .issuedAt(now)
                .expiration(expiry)
                .signWith(KEY)
                .compact();
    }

    /**
     * 解析 Token
     */
    public static Claims parseToken(String token) {
        return Jwts.parser()
                .verifyWith(KEY)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    /**
     * 获取用户 ID
     */
    public static Long getUserId(String token) {
        try {
            Claims claims = parseToken(token);
            return Long.parseLong(claims.getSubject());
        } catch (ExpiredJwtException e) {
            // Token 已过期，但仍能获取 subject
            return Long.parseLong(e.getClaims().getSubject());
        }
    }

    /**
     * 获取用户名
     */
    public static String getUsername(String token) {
        Claims claims = parseToken(token);
        return claims.get("username", String.class);
    }

    /**
     * 验证 Token 是否过期
     */
    public static boolean isTokenExpired(String token) {
        try {
            Claims claims = parseToken(token);
            return claims.getExpiration().before(new Date());
        } catch (ExpiredJwtException e) {
            return true;
        }
    }

    /**
     * 验证 Token 是否有效
     */
    public static boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * 刷新 Token
     */
    public static String refreshToken(String oldToken) {
        Claims claims = parseToken(oldToken);
        Long userId = Long.parseLong(claims.getSubject());
        String username = claims.get("username", String.class);

        // 生成新 Token
        return generateToken(userId, username);
    }
}
```

### 3.2 Spring Security 集成

```java
// JwtAuthenticationFilter.java
package com.yourproject.config;

import com.yourproject.utils.JwtUtils;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private static final String HEADER = System.getProperty("jwt.header", "Authorization");
    private static final String PREFIX = System.getProperty("jwt.prefix", "Bearer ");

    @Override
    protected void doFilterInternal(@NonNull HttpServletRequest request,
                                   @NonNull HttpServletResponse response,
                                   @NonNull FilterChain filterChain)
            throws ServletException, IOException {

        String token = extractToken(request);

        if (token != null && JwtUtils.validateToken(token)) {
            Long userId = JwtUtils.getUserId(token);

            // 将 userId 设置到请求属性中，供 Controller 使用
            request.setAttribute("userId", userId);
        }

        filterChain.doFilter(request, response);
    }

    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader(HEADER);
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith(PREFIX)) {
            return bearerToken.substring(PREFIX.length());
        }
        return null;
    }
}
```

### 3.3 Spring Security 配置

```java
// SecurityConfig.java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                // 放行路径 - 根据实际项目修改
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers("/swagger-ui/**", "/v3/api-docs/**").permitAll()
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
```

### 3.4 非 Spring Security 方案

```java
// 简单版：直接解析 Token
@RestController
@RequestMapping("/api/user")
public class UserController {

    @GetMapping("/profile")
    public Result<UserVO> getProfile(HttpServletRequest request) {
        // 从请求属性获取 userId（由 Filter 设置）
        Long userId = (Long) request.getAttribute("userId");
        if (userId == null) {
            return Result.fail(ResultCode.UNAUTHORIZED);
        }

        UserVO user = userService.getById(userId);
        return Result.success(user);
    }

    // 手动获取 Token
    private String extractToken(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
}
```

---

## 4. 第三步：常见问题诊断与修复

### 4.1 问题分类速查表

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `ExpiredJwtException` | Token 已过期 | 刷新 Token 或重新登录 |
| `SignatureException` | Secret 不匹配 | 确认所有服务使用相同 secret |
| `MalformedJwtException` | Token 格式错误 | 检查 Token 字符串 |
| `UnsupportedJwtException` | Token 类型不支持 | 使用正确类型的 Token |
| `IllegalArgumentException` | Token 为空 | 检查请求 Header |
| `401 Unauthorized` | Token 无效/缺失 | 登录获取新 Token |

### 4.2 问题修复

**问题：Token 过期**

```java
// 统一响应码
public enum ResultCode {
    TOKEN_EXPIRED(401, "Token 已过期，请重新登录"),
    TOKEN_INVALID(401, "Token 无效"),
    UNAUTHORIZED(401, "未登录"),
    FORBIDDEN(403, "权限不足");
}

// Controller 统一处理
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ExpiredJwtException.class)
    public Result<Void> handleExpiredJwtException(ExpiredJwtException e) {
        return Result.fail(ResultCode.TOKEN_EXPIRED);
    }
}
```

**问题：Secret 不一致导致签名失败**

```yaml
# 所有环境使用相同的 Secret
jwt:
  secret: ${JWT_SECRET:your-256-bit-secret-key-must-be-same-everywhere}
```

**问题：多服务共享 Token**

```java
// 使用相同的 JWT 配置
// 方案1：统一配置中心
// 方案2：环境变量注入
// 方案3：配置类读取配置文件
```

### 4.3 Token 刷新机制

```java
// AuthController.java
@PostMapping("/refresh")
public Result<String> refreshToken(@RequestBody RefreshTokenRequest request) {
    String oldToken = request.getToken();

    // 验证旧 Token
    if (!JwtUtils.validateToken(oldToken)) {
        return Result.fail(ResultCode.TOKEN_INVALID);
    }

    // 检查是否过期（允许过期 7 天内的 Token 进行刷新）
    Claims claims = JwtUtils.parseToken(oldToken);
    long expiration = claims.getExpiration().getTime();
    long now = System.currentTimeMillis();
    long sevenDays = 7 * 24 * 60 * 60 * 1000L;

    if (now - expiration > sevenDays) {
        return Result.fail(ResultCode.TOKEN_EXPIRED_NEED_LOGIN);
    }

    // 生成新 Token
    Long userId = Long.parseLong(claims.getSubject());
    String username = claims.get("username", String.class);
    String newToken = JwtUtils.generateToken(userId, username);

    return Result.success(newToken);
}
```

---

## 5. 第四步：前端集成

### 5.1 Token 存储

```javascript
// 方案1：LocalStorage（推荐简单场景）
localStorage.setItem('token', response.data.token);

// 方案2：HttpOnly Cookie（更安全，防止 XSS）
// 后端设置 Cookie，前端无需处理
```

### 5.2 Axios 请求拦截

```javascript
// utils/request.js
const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // ...处理成功响应
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期，清除并跳转登录
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

## 6. 第五步：验证清单

- [ ] Token 生成后能够正确解析
- [ ] Token 过期时间正确
- [ ] 受保护的接口无 Token 时返回 401
- [ ] 伪造的 Token 返回 401
- [ ] 用户 ID 正确传递到后端
- [ ] 前端能够正确处理 401 响应
- [ ] Token 刷新功能正常

---

## 7. 附录：JWT 最佳实践

### 7.1 Secret 安全

```java
// 生成安全的 Secret Key
public static String generateSecureSecret() {
    return Keys.secretKeyFor(SignatureAlgorithm.HS256).getEncoded().toString();
}

// 至少 256 位（32 字节）
```

### 7.2 过期时间建议

| 场景 | 过期时间 | 说明 |
|------|---------|------|
| 短期 Token | 1-2 小时 | 适合敏感操作 |
| 标准 Token | 24 小时 | 默认推荐 |
| 长期 Token | 7 天 | 需要刷新机制 |
| 刷新 Token | 30 天 | 仅用于刷新 |

### 7.3 Payload 包含内容

```json
{
  "sub": "12345",           // 用户 ID（必需）
  "username": "john",      // 用户名
  "role": "USER",          // 角色
  "exp": 1234567890,       // 过期时间
  "iat": 1234567890,       // 签发时间
  "iss": "your-app"        // 签发者
}
```

---

## 执行指令

> 请执行 **JWT认证调试技能**，按照以下步骤操作：
> 1. 检测项目类型和 JWT 依赖
> 2. 读取 JWT 配置文件
> 3. 检查 Token 生成和解析逻辑
> 4. 诊断并修复问题：{具体错误描述}

---

## AI 执行要点

作为 AI，你需要：

1. **先读取配置文件**：不要假设任何配置值
2. **根据 JJWT 版本**：选择正确的 API（0.12.x vs 0.11.x）
3. **提供完整工具类**：让用户可以直接使用
4. **解释安全风险**：如 Secret 泄露、Token 劫持
5. **提供生产配置**：如环境变量、多服务共享
