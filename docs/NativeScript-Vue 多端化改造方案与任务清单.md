## 目标与范围

- 目标：在保留现有 Web 架构（Vue3 + Vite + Naive UI）的基础上，引入 NativeScript-Vue，提供 iOS/Android 原生应用，满足现场设备巡检、告警处理、扫码、离线、推送等移动场景。
- 范围：
  - 保留现有后端（FastAPI v2 标准化 API），不做接口协议变更；
  - 抽取可复用的业务层（types/api/utils/stores/i18n），Web 与 Mobile 共用；
  - 移动端 UI 使用 NativeScript 组件重写，遵循移动交互规范；
  - 先做 MVP（登录、健康检查、仪表盘/告警列表、设备明细只读），再逐步覆盖设备管理/维修记录等核心流程。

## 技术选型与基本原则

- 客户端：
  - NativeScript + Vue（与 Web 保持 Vue3 生态，使用 `@nativescript/vue`）
  - 状态管理：Pinia（仅承载业务状态与动作，禁止耦合 DOM/浏览器 API）
  - 网络：建议采用 `ofetch`（浏览器与原生统一）或自封装 adapter（Web 用 axios、Native 用 fetch）
  - 安全：Native 使用 Secure Storage 保存 token；全链路 HTTPS
  - WebSocket：使用标准 WebSocket（NativeScript 支持）
- 工程组织：
  - Monorepo（pnpm workspace）+ `packages/shared` 共享复用层
- 后端：
  - 无需变更；移动端不受 CORS 限制，但生产仍强制 HTTPS 与证书校验

## 架构与目录规划（建议）

```
DeviceMonitorV2/
├─ app/                               # 后端（保持不变）
├─ web/                               # Web 前端（Vue3 + Vite + Naive UI）
├─ mobile/                            # 新增：NativeScript-Vue 项目
│  ├─ app/
│  │  ├─ App.vue
│  │  ├─ main.ts
│  │  ├─ pages/                       # 移动端页面（重写）
│  │  ├─ components/
│  │  ├─ navigation/                  # 原生导航封装（Frame/Page）
│  │  ├─ plugins/                     # secure storage、push、camera 等
│  │  └─ stores/                      # 仅透传 shared 的 stores（必要时轻适配）
│  └─ nativescript.config.ts
├─ packages/
│  └─ shared/                         # 新增：共享层
│     ├─ api/                         # API 客户端（ofetch/adapter）
│     ├─ types/                       # TS 类型、枚举、常量
│     ├─ utils/                       # 业务工具函数、校验
│     ├─ i18n/                        # 词条与加载器
│     └─ stores/                      # Pinia（无 UI 依赖）
└─ docs/
   ├─ 系统优化建议与风险评估.md
   └─ NativeScript-Vue 多端化改造方案与任务清单.md  # 当前文档
```

## 详细落地计划（分阶段）

### Phase 0：准备与验证（1-2 天）
- 确认移动端需求优先级（扫码/推送/离线/蓝牙等）
- 锁定技术版本：
  - NativeScript 版本、`@nativescript/vue`（Vue3）、TypeScript 版本
  - Node、pnpm 版本
- 本地快速 POC：新建空的 NativeScript-Vue 项目，调用后端 `/api/v2/health` 成功返回
- 交付物：
  - 版本矩阵与安装说明
  - POC 工程（独立，不入主仓）

### Phase 1：共享层抽取（3-5 天）
- 从 `web/src` 抽离可复用代码到 `packages/shared`：
  - `types/` 业务类型定义
  - `utils/` 格式化、校验、权限判定等
  - `i18n/` 词条与加载
  - `stores/` Pinia 业务状态与动作（移除 DOM/组件依赖）
  - `api/` 客户端封装（建议改为 `ofetch`，或提供 axios/native adapter）
- 补充单元测试（关键函数）
- 交付物：
  - `packages/shared/*` 可在 Web 端正常引用并通过构建
  - Web 端切换为引用 shared，功能不回退

### Phase 2：Mobile 项目初始化（2-3 天）
- 新建 `mobile/` 项目，配置 pnpm workspace 与 TS 路径别名
- 挂载 shared：在移动端引入 `packages/shared` 模块
- 基础能力：
  - Secure Storage（保存/读取/清除 token）
  - API 基础拦截（携带 token、错误码映射、网络错误提示）
  - 原生导航与页面脚手架（Frame/Page/StackLayout 等）
- 交付物：
  - `mobile/` 能拉起并调用后端健康检查，打印/展示结果

### Phase 3：认证与基础框架（3-4 天）
- 登录页（账号/密码 + token 持久化 + 退出登录）
- 全局异常处理与错误页
- 配置环境区分（Dev/Prod API 基础地址、Android 模拟器 `10.0.2.2` 指南）
- 交付物：
- 登录/退出完整链路
- API 基础配置与环境切换说明

### Phase 4：MVP 页面（5-8 天）
- 仪表盘（精简版）：读取后端统计/健康信息
- 告警列表/详情（只读）
- 设备列表/详情（只读）
- 交付物：
  - 可安装/运行的最小可用移动端（Android 优先，iOS 可次阶段跟进）
  - 与 Web 一致的权限校验与数据呈现（只读）

### Phase 5：原生能力（可选，视需求 5-10 天）
- 相机/扫码（设备入库/盘点/绑定）
- 推送通知（告警推送与跳转）
- 文件选择/拍照上传（设备图片/附件）
- 离线缓存与网络切换（关键接口本地缓存、重试机制）
- 蓝牙/局域网直连（如需）
- 交付物：
  - 对应原生功能可用、权限申请正确、异常处理完善

### Phase 6：性能与稳定性（3-5 天）
- 首屏性能：资源裁剪、延迟加载、列表虚拟化
- 错误与崩溃上报（Sentry/自建）
- 指标埋点：接口耗时、失败率、冷启动时间
- 交付物：
  - 性能报告与阈值、监控告警接入

### Phase 7：发布与运维（3-5 天）
- 构建签名与配置（Android keystore、iOS 证书）
- 环境打包脚本与 CI（产出 Web 与 Mobile 的独立工件）
- 安装/升级指引、回滚说明
- 交付物：
  - 发布流水线、可安装包（.apk/.aab、.ipa）

## 关键实现要点与示例

### API 客户端（跨端 adapter 建议示例）

```ts
// packages/shared/api/client.ts
// 方案A：统一采用 ofetch（推荐）
import { ofetch } from 'ofetch';

export const api = ofetch.create({
  baseURL: process.env.VITE_BASE_API || '/api/v2',
  headers: () => {
    const token = getToken(); // from shared auth store or injected getter
    return token ? { Authorization: `Bearer ${token}` } : {};
  },
  // 可加拦截：onRequest, onResponse, onRequestError, onResponseError
});

// 方案B：自适配 axios/fetch（如保留 axios）
export async function request<T>(config: { url: string; method?: string; data?: any; params?: any }): Promise<T> {
  const isNative = typeof global !== 'undefined' && (global as any).__runtimeVersion; // 粗略判断
  const token = getToken();
  const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
  if (isNative) {
    const res = await fetch(`${BASE_URL}${config.url}`, {
      method: config.method || 'GET',
      headers: { 'Content-Type': 'application/json', ...headers },
      body: config.data ? JSON.stringify(config.data) : undefined,
    });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  } else {
    // axios 分支
    const { default: axios } = await import('axios');
    const r = await axios({ baseURL: BASE_URL, ...config, headers });
    return r.data;
  }
}
```

### Token 安全存储（Native）

```ts
// mobile/app/plugins/secure-storage.ts
import { SecureStorage } from '@nativescript/secure-storage';

const storage = new SecureStorage();

export async function setToken(token: string) {
  await storage.set({ key: 'token', value: token });
}
export async function getToken() {
  return (await storage.get({ key: 'token' })) || '';
}
export async function clearToken() {
  await storage.remove({ key: 'token' });
}
```

### 平台与开发地址配置

- Android 模拟器访问宿主机后端：`http://10.0.2.2:8001`
- iOS 模拟器通常可用 `http://127.0.0.1:8001`
- 通过环境变量或运行时配置切换 `BASE_URL`

## 任务清单（WBS）

- 准备阶段
  - [ ] 需求优先级与版本矩阵确认
  - [ ] NativeScript-Vue POC：调用 `/api/v2/health`
- 共享层抽取
  - [ ] 建立 `packages/shared` 与 workspace
  - [ ] 抽取 `types/`、`utils/`、`i18n/`、`stores/`、`api/`
  - [ ] Pinia 去 UI 化（剥离 DOM 依赖）
  - [ ] Web 端切换引用 shared 并通过构建
- Mobile 初始化
  - [ ] 创建 `mobile/` 工程与别名/TS 配置
  - [ ] 引入 shared 并跑通健康检查
  - [ ] 封装 Secure Storage 与 API 拦截
  - [ ] 导航骨架搭建
- 认证与基础
  - [ ] 登录/退出与 token 管理
  - [ ] 全局异常与错误页
  - [ ] 环境配置（dev/prod 与模拟器地址）
- MVP 页面
  - [ ] 仪表盘（精简）
  - [ ] 告警列表/详情（只读）
  - [ ] 设备列表/详情（只读）
- 原生能力（按需）
  - [ ] 相机/扫码
  - [ ] 推送通知（告警）
  - [ ] 上传/附件
  - [ ] 离线缓存与重试
  - [ ] 蓝牙/本地直连（如需）
- 性能与稳定性
  - [ ] 首屏/列表优化与懒加载
  - [ ] 崩溃与错误上报
  - [ ] 指标埋点
- 发布与运维
  - [ ] 打包签名与脚本
  - [ ] CI 产物（Web 与 Mobile）
  - [ ] 安装/升级/回滚指引

## 风险与缓解

- UI 重写工作量：通过优先级收敛范围，先做 MVP
- 生态与插件兼容：优先选官方与活跃维护的插件（secure-storage、push、camera）
- 逻辑分叉：强制“View 与业务”分层，业务统一在 shared，避免重复实现
- 测试成本：建立模拟器/真机回归清单与关键流程 E2E

## 时间与资源估算（参考）

- P0-P2（准备、共享层、移动端初始化）：约 1.5-2 周
- MVP：1-2 周（取决于页面复杂度）
- 原生能力：1-2 周（按需求拆分实施）
- 性能与发布：1 周

## 验收标准（MVP）

- 登录/退出正常；token 安全存储
- 仪表盘/告警/设备只读链路无报错，弱网下可用
- 日志与崩溃上报可用；接口错误率与耗时可观测
- 打包可安装；环境切换配置明确


