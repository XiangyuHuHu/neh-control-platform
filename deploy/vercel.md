# Vercel 前端部署

仓库：`https://github.com/XiangyuHuHu/neh-control-platform`

## Vercel 项目设置（二选一）

### 推荐：Root Directory = `web`

| 项 | 值 |
|----|-----|
| Root Directory | `web` |
| Framework Preset | Vite |
| Build Command | `npm run build:vercel`（或留空，读 `web/vercel.json`） |
| Output Directory | `dist` |
| Install Command | `npm ci` |

### 备选：Root Directory = 仓库根目录 `.`

使用根目录的 `vercel.json`（已配置 `web` 子目录构建）。

## 环境变量（必配，否则登录/接口 502）

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `API_PROXY_TARGET` | 公网可访问的后端根地址（**不要**末尾 `/`） | `https://neh.你的域名.com` |

后端仍在现场 Ubuntu；需先用 **Cloudflare Tunnel** 或端口映射提供 HTTPS 公网地址，再填到 Vercel。

`192.168.3.238` 是内网 IP，**不能**填到 Vercel。

## 部署后验证

1. 打开 `https://你的项目.vercel.app/` 应出现登录页（不是 404）
2. 打开 `https://你的项目.vercel.app/api/dashboard/portal-metrics` 应返回 JSON（不是 502）
3. 用手机 4G 访问同上

## 常见问题

| 现象 | 处理 |
|------|------|
| Build 失败 `package.json not found` | Root Directory 改为 `web`，或保留根目录 `vercel.json` |
| 页面 404、刷新子路由 404 | 已配置 SPA rewrite；重新 Deploy |
| 接口 502 `API_PROXY_TARGET not configured` | 在 Vercel 添加环境变量并 Redeploy |
| 接口超时 | 检查 Cloudflare 隧道 / 后端是否在线 |
| 仅想看静态页、暂不连后端 | 仍会 502；需配 `API_PROXY_TARGET` |
