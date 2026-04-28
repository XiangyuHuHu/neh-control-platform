# Python 模型服务

当前目录已收纳以下两套模型源码：

- `smart-density`
- `smart-reagent`

源码来源：

- `卓朗2/密控系统算法包-20250926/智能密控系统算法包/Archive/project`
- `卓朗2/加药系统算法包-20250926/智能加药系统算法包/Archive/project`

## 当前策略

当前仅完成：

1. 源码并入当前仓库
2. Dockerfile 与依赖文件补齐
3. 供当前管控平台通过 HTTP 代理调用

当前未做：

1. 现场点位映射
2. 模型精调
3. 真实 PLC / OPC 回写联调

## 启动说明

### 本地 Python 直接运行

进入对应目录后执行：

```powershell
python main.py
```

默认端口：

- 智能密控：`6789`
- 智能加药：`6788`

### Docker Compose 可选启动

主项目 `docker-compose.yml` 已预留 `models` profile。

```powershell
docker compose --profile models up -d smart-density smart-reagent
```

如果要让当前 Java 后端直接调用容器内模型服务，需要同时配置：

```env
SMART_DENSITY_ENABLED=true
SMART_DENSITY_BASE_URL=http://smart-density:6789

SMART_REAGENT_ENABLED=true
SMART_REAGENT_BASE_URL=http://smart-reagent:6788
```

## 说明

这两套模型依赖较重，包含 TensorFlow、cvxpy 等组件。
当前仓库已经具备容器化骨架，但在没有现场数据联调前，不建议把模型镜像作为默认启动项。
