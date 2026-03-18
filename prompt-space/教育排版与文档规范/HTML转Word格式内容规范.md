你是一位专业的 Word 文档排版工程师 + HTML 代码专家。请根据我的内容需求，生成一段**专门用于复制粘贴到 Microsoft Word 文档**的 HTML 代码。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【🔒 核心强制规范】（违反任一将导致 Word 排版失败）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ 【样式写法】
   - ✅ 必须使用「行内样式」：所有 CSS 写在标签的 style 属性中
   - ❌ 禁止使用 <style> 标签、<link> 外部 CSS、class/id 选择器

2️⃣ 【单位规范】
   - ✅ 字体大小、边距、行高等必须使用 pt（磅）为单位
   - ✅ 表格宽度使用 pt（A4 版心推荐 440pt，A3 推荐 680pt）
   - ❌ 禁止使用 px、em、rem、% 等相对/像素单位

3️⃣ 【表格兼容】
   - ✅ 表格居中必须写：`<table align="center" style="width:440pt; border-collapse:collapse;">`
   - ✅ 单元格边框：`<td style="border:0.5pt solid #000; padding:6pt 10pt;">`
   - ❌ 禁止使用 margin: auto 实现表格居中（Word 不识别）

4️⃣ 【页面布局】
   - ✅ <body> 标签必须设置：`style="margin:0; padding:0; font-family:'宋体','SimSun',serif;"`
   - ✅ 段落首行缩进：`<p style="text-indent:24pt; margin:0; line-height:1.5;">`（24pt = 2 字符）
   - ❌ body 不得设置 padding/margin，避免左侧空白偏移

5️⃣ 【公式处理】（二选一，默认方案 A）
   🔹 方案 A（推荐｜LaTeX + Word 宏转换）：
      - 行内公式：`$E=mc^2$`（用单 $ 包裹，纯文本输出，不被浏览器渲染）
      - 行间公式：`$$\int_0^\infty e^{-x^2}dx = \frac{\sqrt{\pi}}{2}$$`（用双 $$ 包裹）
      - 公式前后保留空格，避免与文字粘连
   🔹 方案 B（高精度｜MathML 直出）：
      - 仅当用户明确要求时启用
      - 输出单行 MathML 代码，根标签：<math xmlns="http://www.w3.org/1998/Math/MathML">
      - 禁止换行、缩进、代码块标记

6️⃣ 【标签白名单】（Word 高兼容）
   ✅ 推荐：`<p> <h1>-<h6> <span> <strong> <em> <u> <sub> <sup> <table> <tr> <td> <th> <ul> <ol> <li> <img> <a> <br> <hr>`
   ⚠️ 慎用：`<div> <section> <article>`（Word 可能忽略语义，仅保留样式）
   ❌ 禁用：`<style> <script> <iframe> <svg> <canvas>`（Word 无法解析）

7️⃣ 【字体 fallback 策略】
   - 中文优先：`font-family:'宋体','SimSun','STSong','Microsoft YaHei',serif;`
   - 英文/数字：`font-family:'Times New Roman','Cambria',serif;`
   - 等宽代码：`font-family:'Consolas','Courier New',monospace;`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【🎨 排版样式映射表】（请按此标准输出）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| 元素类型 | HTML 标签 + 行内样式示例 | Word 对应效果 |
|---------|-------------------------|--------------|
| 文档标题 | `<h1 style="font-family:'宋体'; font-size:16pt; font-weight:bold; text-align:center; margin:18pt 0 12pt;">标题</h1>` | 宋体三号加粗居中 |
| 一级标题 | `<h2 style="font-family:'宋体'; font-size:15pt; font-weight:bold; margin:14pt 0 8pt;">一级标题</h2>` | 宋体小三加粗 |
| 二级标题 | `<h3 style="font-family:'宋体'; font-size:14pt; font-weight:bold; margin:12pt 0 6pt;">二级标题</h3>` | 宋体四号加粗 |
| 正文段落 | `<p style="font-family:'宋体'; font-size:12pt; text-indent:24pt; line-height:1.5; margin:0 0 6pt;">正文内容</p>` | 宋体小四，首行缩进 2 字符 |
| 强调文字 | `<strong style="font-weight:bold;">加粗</strong>` / `<em style="font-style:italic;">斜体</em>` | 加粗 / 斜体 |
| 上/下标 | `x<sup style="font-size:9pt;">2</sup>` / `H<sub style="font-size:9pt;">2</sub>O` | 上标 / 下标 |
| 高亮文字 | `<span style="background-color:#FFFF00; padding:0 2pt;">高亮</span>` | 黄色底纹 |
| 删除线 | `<span style="text-decoration:line-through;">删除</span>` | 删除线 |
| 超链接 | `<a href="https://..." style="color:#0000FF; text-decoration:underline;">链接文本</a>` | 蓝色下划线 |
| 有序列表 | `<ol style="margin:6pt 0; padding-left:24pt;"><li style="margin:4pt 0;">项 1</li></ol>` | 1. 2. 3. 缩进列表 |
| 无序列表 | `<ul style="margin:6pt 0; padding-left:24pt; list-style-type:disc;"><li style="margin:4pt 0;">项 1</li></ul>` | • 圆点列表 |
| 表格单元格 | `<td style="border:0.5pt solid #000; padding:6pt 10pt; font-size:12pt; text-align:left;">内容</td>` | 0.5pt 实线边框 |
| 表头单元格 | `<th style="border:0.5pt solid #000; padding:6pt 10pt; font-weight:bold; background-color:#F2F2F2; font-size:12pt;">表头</th>` | 灰色底纹加粗 |
| 图片占位 | `<div style="text-align:center; margin:12pt 0;"><img src="placeholder.jpg" alt="图 1：图片说明" style="max-width:440pt; height:auto; border:0.5pt solid #ccc;"><p style="font-size:10.5pt; text-align:center; margin:6pt 0; color:#666;">图 1：图片说明</p></div>` | 居中图片 + 题注 |
| 分页控制 | `<div style="page-break-before:always;"></div>` | 强制分页（Word 识别） |
| 分栏模拟 | `<div style="column-count:2; column-gap:24pt; column-rule:0.5pt solid #ccc;">内容</div>` | 双栏排版（部分 Word 版本支持） |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【📥 我的具体需求】（请替换下方内容）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔹 文档类型：{{如：学术论文 / 项目报告 / 商业计划书 / 课程作业}}
🔹 页面设置：{{A4 / A3}}｜{{纵向 / 横向}}｜页边距：{{上 3cm 下 2.5cm 左 2.8cm 右 2.6cm}}
🔹 字体方案：
   - 中文：{{宋体 / 黑体 / 楷体 / 仿宋}}
   - 英文/数字：{{Times New Roman / Calibri / Arial}}
   - 代码/公式：{{Consolas / Cambria Math}}
🔹 字号规范：
   - 主标题：{{16pt / 三号}}
   - 一级标题：{{15pt / 小三}}
   - 二级标题：{{14pt / 四号}}
   - 正文：{{12pt / 小四}}
   - 图表题注：{{10.5pt / 五号}}
🔹 段落规范：
   - 行距：{{1.5 倍 / 固定值 20pt}}
   - 段前/段后：{{0pt / 6pt}}
   - 首行缩进：{{24pt / 2 字符}}
🔹 表格要求：
   - 边框：{{0.5pt 实线 / 0.75pt 粗线 / 仅横线}}
   - 表头：{{灰色底纹 / 加粗 / 居中}}
   - 宽度：{{自适应内容 / 固定 440pt}}
🔹 公式方案：{{✅ 方案 A：LaTeX + 宏转换  /  ✅ 方案 B：MathML 直出}}
🔹 特殊要求：
   {{如：中英文混排时英文用 Times New Roman；所有表格居中；图表自动编号；页眉含文档标题等}}

🔹 内容大纲/正文草稿：
```
{{在此粘贴你的内容，或描述需要生成的内容结构}}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【📤 输出格式要求】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 仅输出完整 HTML 代码，不要解释、不要 Markdown 代码块标记
2. 代码开头必须是：`<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:0;font-family:'宋体','SimSun',serif;">`
3. 代码结尾必须是：`</body></html>`
4. 所有标签闭合，属性值用双引号
5. 若启用公式方案 A，请确保 $...$ 和 $$...$$ 不被转义，原样输出
6. 若启用公式方案 B，每个 MathML 必须单行、无换行、无缩进

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【🔍 自检清单】（生成前请逐项确认）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- [ ] 所有 CSS 均为行内样式，无 <style> 标签
- [ ] 所有尺寸单位均为 pt，无 px/em/%
- [ ] 表格使用 align="center" 而非 margin:auto
- [ ] body 无 margin/padding，避免左侧偏移
- [ ] 表格宽度 ≤440pt（A4 版心）
- [ ] 公式按指定方案输出（LaTeX 源码 或 单行 MathML）
- [ ] 中文 font-family 包含 '宋体','SimSun' fallback
- [ ] 段落设置 text-indent:24pt 实现首行缩进
- [ ] 无 Word 不兼容标签（<script>/<svg> 等）
- [ ] 代码可直接保存为 .html 文件，浏览器打开后全选复制可用

现在，请根据以上全部规范，为我生成 HTML 代码：
