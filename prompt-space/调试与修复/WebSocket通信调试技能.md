# 🛠️ Claude Code Skill: WebSocket 即时通讯调试 (通用版)

**适用场景**：任何 Java/Spring Boot 项目的 WebSocket 连接失败、消息收发异常

---

## 1. 快速开始

**如果你的项目遇到以下错误，立即使用此 Skill：**
- `404 Not Found` - WebSocket 端点未找到
- `Connection failed` - WebSocket 连接失败
- `WebSocket handshake failed` - 握手失败
- 消息无法送达
- 心跳检测失败

**执行指令：**
> 请执行 **WebSocket调试技能**，诊断并修复 WebSocket 问题

---

## 2. 第一步：环境探测 (AI 自动执行)

### 2.1 检测项目类型

```bash
# 检测构建工具和依赖
ls -la pom.xml build.gradle 2>/dev/null

# 检测 WebSocket 依赖
grep -E "websocket|spring-boot-starter-websocket" pom.xml 2>/dev/null

# 检测 Spring Boot 版本
grep -E "spring-boot-starter-parent" pom.xml | head -1
```

### 2.2 检测 WebSocket 配置

```bash
# 查找 WebSocket 相关文件
find . -name "*WebSocket*.java" -o -name "*SocketHandler*.java" 2>/dev/null | head -10
find . -name "*SocketConfig*.java" 2>/dev/null | head -5
```

---

## 3. 第二步：通用 WebSocket 实现

### 3.1 Spring Boot WebSocket 依赖

```xml
<!-- Spring Boot 3.x -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-websocket</artifactId>
</dependency>

<!-- 或使用 Spring WebSocket (非 Spring Boot) -->
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-websocket</artifactId>
    <version>6.1.0</version>
</dependency>
```

### 3.2 WebSocket 配置类

```java
// WebSocketConfig.java - 适用于任何 Spring Boot 项目
package com.yourproject.websocket;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    // WebSocket 端点路径
    private static final String WS_ENDPOINT = "/ws";
    private static final String WS_ENDPOINT_CHAT = "/ws/chat";
    private static final String ALLOWED_ORIGINS = "*";  // 根据实际需求修改

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry
            .addHandler(new YourWebSocketHandler(), WS_ENDPOINT_CHAT + "/{userId}")
            .setAllowedOrigins(ALLOWED_ORIGINS.split(","));
    }
}
```

### 3.3 WebSocket 处理器

```java
// YourWebSocketHandler.java - 通用处理器
package com.yourproject.websocket;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.lang.NonNull;
import org.springframework.web.socket.*;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class YourWebSocketHandler extends TextWebSocketHandler {

    // 存储用户连接会话
    private static final Map<Long, WebSocketSession> SESSIONS = new ConcurrentHashMap<>();
    private static final Map<String, Long> SESSION_TO_USER = new ConcurrentHashMap<>();

    private final ObjectMapper objectMapper = new ObjectMapper();

    // 连接建立
    @Override
    public void afterConnectionEstablished(@NonNull WebSocketSession session) throws Exception {
        // 从路径参数获取 userId
        String path = session.getUri().getPath();
        Long userId = extractUserId(path);

        if (userId != null) {
            SESSIONS.put(userId, session);
            SESSION_TO_USER.put(session.getId(), userId);
            System.out.println("用户 " + userId + " WebSocket 连接成功");
        }
    }

    // 接收消息
    @Override
    protected void handleTextMessage(@NonNull WebSocketSession session, @NonNull TextMessage message) throws Exception {
        Long userId = SESSION_TO_USER.get(session.getId());
        String payload = message.getPayload();

        System.out.println("收到用户 " + userId + " 的消息: " + payload);

        // 解析消息
        @SuppressWarnings("unchecked")
        Map<String, Object> data = objectMapper.readValue(payload, Map.class);
        String type = (String) data.get("type");

        // 根据消息类型处理
        switch (type) {
            case "CHAT":
                handleChatMessage(userId, data);
                break;
            case "PING":
                sendMessage(session, Map.of("type", "PONG", "timestamp", System.currentTimeMillis()));
                break;
            default:
                System.out.println("未知消息类型: " + type);
        }
    }

    // 连接关闭
    @Override
    public void afterConnectionClosed(@NonNull WebSocketSession session, @NonNull CloseStatus status) throws Exception {
        Long userId = SESSION_TO_USER.get(session.getId());
        if (userId != null) {
            SESSIONS.remove(userId);
            SESSION_TO_USER.remove(session.getId());
            System.out.println("用户 " + userId + " WebSocket 已断开: " + status);
        }
    }

    // 错误处理
    @Override
    public void handleTransportError(@NonNull WebSocketSession session, @NonNull Throwable exception) throws Exception {
        System.err.println("WebSocket 传输错误: " + exception.getMessage());
        session.close(CloseStatus.SERVER_ERROR);
    }

    // ========== 辅助方法 ==========

    private Long extractUserId(String path) {
        try {
            String[] parts = path.split("/");
            String userIdStr = parts[parts.length - 1];
            return Long.parseLong(userIdStr);
        } catch (Exception e) {
            return null;
        }
    }

    // 发送消息给指定用户
    public static void sendMessageToUser(Long userId, Object message) {
        WebSocketSession session = SESSIONS.get(userId);
        if (session != null && session.isOpen()) {
            try {
                String json = new ObjectMapper().writeValueAsString(message);
                session.sendMessage(new TextMessage(json));
            } catch (IOException e) {
                System.err.println("发送消息给用户 " + userId + " 失败: " + e.getMessage());
            }
        }
    }

    // 发送消息
    private void sendMessage(WebSocketSession session, Object message) throws IOException {
        String json = objectMapper.writeValueAsString(message);
        session.sendMessage(new TextMessage(json));
    }

    // 广播消息给所有用户
    public static void broadcast(Object message) {
        SESSIONS.forEach((userId, session) -> {
            if (session.isOpen()) {
                sendMessageToUser(userId, message);
            }
        });
    }

    // 获取在线用户数
    public static int getOnlineCount() {
        return SESSIONS.size();
    }
}
```

### 3.4 STOMP 协议支持 (可选)

```java
// StompWebSocketConfig.java - 如果需要 STOMP 协议
@Configuration
@EnableWebSocketMessageBroker
public class StompWebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // 启用简单 broker，用于广播
        registry.enableSimpleBroker("/topic", "/queue");
        // 应用目的地前缀
        registry.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
                .setAllowedOrigins("*")
                .withSockJS();
    }
}
```

---

## 4. 第三步：前端集成

### 4.1 原生 WebSocket 连接

```javascript
// websocket.js - 通用 WebSocket 客户端
class WebSocketClient {
  constructor(url, userId, options = {}) {
    this.url = url;
    this.userId = userId;
    this.options = options;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.heartbeatTimer = null;
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.socket = new WebSocket(
          `${this.url}/${this.userId}${this.getAuthParams()}`
        );

        this.socket.onopen = () => {
          console.log('WebSocket 连接成功');
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          resolve();
        };

        this.socket.onclose = (e) => {
          console.log('WebSocket 连接关闭:', e.code, e.reason);
          this.stopHeartbeat();
          this.attemptReconnect();
        };

        this.socket.onerror = (error) => {
          console.error('WebSocket 错误:', error);
          reject(error);
        };

        this.socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  getAuthParams() {
    const token = localStorage.getItem('token');
    return token ? `?token=${encodeURIComponent(token)}` : '';
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket 未连接，消息未发送');
    }
  }

  // 发送聊天消息
  sendChatMessage(content, receiverId, bizType, bizId) {
    this.send({
      type: 'CHAT',
      content,
      receiverId,
      bizType,
      bizId,
      timestamp: Date.now()
    });
  }

  handleMessage(data) {
    switch (data.type) {
      case 'CHAT':
        // 处理聊天消息
        this.onChatMessage?.(data);
        break;
      case 'NOTIFICATION':
        // 处理通知
        this.onNotification?.(data);
        break;
      case 'PONG':
        // 心跳响应
        break;
    }
  }

  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'PING', timestamp: Date.now() });
    }, 30000);
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`尝试重新连接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => this.connect(), 5000);
    } else {
      console.error('已达到最大重连次数');
    }
  }

  disconnect() {
    this.stopHeartbeat();
    if (this.socket) {
      this.socket.close(1000, '客户端主动断开');
    }
  }

  // 回调函数
  onChatMessage = null;
  onNotification = null;
}

// 使用示例
const wsClient = new WebSocketClient(
  'ws://localhost:8080/ws/chat',
  currentUserId
);

wsClient.onChatMessage = (data) => {
  console.log('收到新消息:', data);
};

wsClient.connect();
```

---

## 5. 第四步：常见问题修复

### 5.1 问题分类速查表

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `404 Not Found` | 端点路径错误 | 检查 @ServerEndpoint 路径 |
| `Connection refused` | 服务未启动 | 启动 WebSocket 服务 |
| `WebSocket handshake failed` | 跨域/CORS 配置 | 配置 allowed origins |
| `Session is null` | 并发问题 | 使用 Map 存储 Session |
| 消息丢失 | 心跳超时 | 添加心跳检测 |
| 无法广播 | Session 已关闭 | 检查 Session.isOpen() |

### 5.2 问题修复

**问题：跨域配置**

```java
// 方案1：设置允许的来源
registry.addHandler(handler, "/ws/{userId}")
        .setAllowedOrigins("http://localhost:3000", "http://localhost:5173");

// 方案2：允许所有来源（开发环境）
.setAllowedOrigins("*");
```

**问题：Spring Security 拦截**

```java
// WebSocket 配置
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry
            .addHandler(new ChatWebSocketHandler(), "/ws/chat/{userId}")
            .addInterceptors(new HttpSessionHandshakeInterceptor())
            .setAllowedOrigins("*");
    }
}
```

**问题：Session 存储**

```java
// 使用 ConcurrentHashMap 保证线程安全
public class ChatWebSocketHandler extends TextWebSocketHandler {

    // 线程安全的 Session 存储
    private static final Map<Long, WebSocketSession> SESSIONS = new ConcurrentHashMap<>();
    private static final Map<String, Long> SESSION_TO_USER = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        Long userId = extractUserId(session);
        SESSIONS.put(userId, session);
        SESSION_TO_USER.put(session.getId(), userId);
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        Long userId = SESSION_TO_USER.get(session.getId());
        SESSIONS.remove(userId);
        SESSION_TO_USER.remove(session.getId());
    }
}
```

---

## 6. 第五步：验证清单

- [ ] WebSocket 端点可访问
- [ ] 连接建立成功
- [ ] 消息能够双向传递
- [ ] 断线后自动重连
- [ ] 心跳检测正常工作
- [ ] 多用户能够互相通信
- [ ] 无跨域问题

---

## 7. 附录：WebSocket 状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 1000 | 正常关闭 | 连接成功完成 |
| 1001 | 端点离开 | 页面关闭或跳转 |
| 1002 | 协议错误 | 协议错误 |
| 1003 | 数据类型错误 | 不支持的数据类型 |
| 1008 | 策略违规 | 策略检查失败 |
| 1011 | 服务器错误 | 服务器异常 |
| 1012 | 服务重启 | 服务正在重启 |

---

## 执行指令

> 请执行 **WebSocket调试技能**，按照以下步骤操作：
> 1. 检测项目 WebSocket 依赖和配置
> 2. 检查 WebSocket 端点和处理器
> 3. 配置跨域和认证
> 4. 诊断并修复问题：{具体错误描述}

---

## AI 执行要点

作为 AI，你需要：

1. **先读取配置**：不要假设端点路径和端口
2. **根据 Spring 版本**：选择正确的 API（WebFlux vs MVC）
3. **提供完整实现**：包括 Session 存储和消息处理
4. **说明安全风险**：如跨站 WebSocket 劫持
5. **提供生产配置**：如心跳间隔、重连策略
