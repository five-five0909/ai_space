# npm/yarn/pnpm 淘宝镜像源配置

**最新镜像地址**：`https://registry.npmmirror.com`

> 旧域名 `registry.npm.taobao.org` 已废弃，请使用新域名。

## 配置命令

| 包管理器 | 设置镜像源 | 查看当前源 |
|---------|-----------|----------|
| npm | `npm config set registry https://registry.npmmirror.com` | `npm config get registry` |
| yarn | `yarn config set registry https://registry.npmmirror.com` | `yarn config get registry` |
| pnpm | `pnpm config set registry https://registry.npmmirror.com` | `pnpm config get registry` |

## 一键设置脚本

```bash
# 设置所有包管理器
npm config set registry https://registry.npmmirror.com
yarn config set registry https://registry.npmmirror.com
pnpm config set registry https://registry.npmmirror.com
```

## 恢复官方源

```bash
npm config set registry https://registry.npmjs.org
yarn config set registry https://registry.npmjs.org
pnpm config set registry https://registry.npmjs.org
```

---

*更新时间：2026年1月*