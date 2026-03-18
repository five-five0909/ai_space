# 🛠️ Claude Code Skill: 自动集成 Knife4j (Auto-Integrate Knife4j)

**Context:** 我需要给当前 Java Spring Boot 项目集成 Knife4j 接口文档/调试工具。
**Requirement:** 请遵循以下标准工作流（SOP）进行操作。

## Step 1: 环境探测 (Environment Detection)
请执行以下操作，不要猜测，必须基于文件内容：
1.  **读取构建文件**：查找并读取根目录下的 `pom.xml` (Maven) 或 `build.gradle` (Gradle)。
2.  **分析 Spring Boot 版本**：
    *   检查 `<parent>` 标签或 dependency management 中的 `spring-boot-starter-parent` 版本。
    *   **判定逻辑**：
        *   如果版本号 `>= 3.0.0` (如 3.1.x, 3.2.x)：标记环境为 **[SB3]**。
        *   如果版本号 `< 3.0.0` (如 2.7.x, 2.6.x)：标记环境为 **[SB2]**。
3.  **报告环境**：告诉我你检测到的 Spring Boot 版本以及你将采用哪种集成方案。

## Step 2: 添加依赖 (Add Dependencies)
根据 Step 1 的判定结果，修改构建文件：

### 🟢 如果是 [SB3] (Spring Boot 3.x + JDK 17+):
请添加以下 Maven 依赖（如果是 Gradle 请自动转换）：
```xml
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
    <version>4.5.0</version>
</dependency>
```

### 🔵 如果是 [SB2] (Spring Boot 2.x + JDK 8/11):
请添加以下 Maven 依赖：
```xml
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-openapi2-spring-boot-starter</artifactId>
    <version>4.5.0</version>
</dependency>
```

## Step 3: 创建配置类 (Create Configuration)
在项目的 `config` 包下（如果没有则创建 `src/main/java/.../config`）新建 `Knife4jConfig.java`。
*请务必根据包结构自动调整 package 声明。*

### 🟢 [SB3] 配置模板 (OpenAPI 3):
```java
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class Knife4jConfig {
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("API 接口文档")
                        .version("1.0")
                        .description("基于 Knife4j + OpenAPI3 构建")
                        .contact(new Contact().name("Backend Team")));
    }
}
```

### 🔵 [SB2] 配置模板 (Swagger 2):
```java
import com.github.xiaoymin.knife4j.spring.annotations.EnableKnife4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import springfox.documentation.builders.ApiInfoBuilder;
import springfox.documentation.builders.PathSelectors;
import springfox.documentation.builders.RequestHandlerSelectors;
import springfox.documentation.spi.DocumentationType;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger2.annotations.EnableSwagger2WebMvc;

@Configuration
@EnableKnife4j
@EnableSwagger2WebMvc
public class Knife4jConfig {
    @Bean
    public Docket defaultApi() {
        return new Docket(DocumentationType.SWAGGER_2)
                .apiInfo(new ApiInfoBuilder()
                        .title("API 接口文档")
                        .description("基于 Knife4j + Swagger2 构建")
                        .version("1.0")
                        .build())
                .select()
                // ⚠️ 注意：这里让 AI 自动识别 Controller 所在的包路径填入 basePackage
                .apis(RequestHandlerSelectors.basePackage("${自动检测到的Controller包路径}"))
                .paths(PathSelectors.any())
                .build();
    }
}
```

## Step 4: 修改配置文件 (Update Application Config)
读取 `src/main/resources/application.yml` (或 properties)。
如果文件存在，追加以下配置；如果不存在，询问是否创建。

```yaml
knife4j:
  enable: true
  setting:
    language: zh_cn
```

## Execution Trigger
现在，请开始执行 Step 1，先读取我的项目依赖文件，并告诉我你的分析结果。然后执行基于我本地项目的正确的 Knife4j 依赖和配置代码