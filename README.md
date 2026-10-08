# SEOUL, slowly — 首尔跨年手册 2026 → 2027

深圳／香港出发，两位女生，2026-12-31 至 2027-01-03，经济舱、双床房，酒店每间每晚含税预算不超过人民币 2,000 元。

## 当前状态

手机优先的静态旅行手册已经完成。网页运行时没有第三方依赖，不用登录，无外部字体、脚本、图片、地图嵌入、追踪器或本地勾选状态。外部链接仅在点击后打开。支持系统自动深浅色、首尔时区秒级倒计时、SVG 示意图、逐日展开路线与 Google Maps 多点地址串联。

**研究进展：**已核对 NOL 当届票务页、SBS／Xportsnews 正文：CDF 于 2026-12-31 在高阳 KINTEX 第 2 展馆 7–8 厅举办，HYUKOH 在首轮阵容；2026-10-13 18:00 KST（中国 17:00）开票，一日票 ₩121,000。海外购票、取票细则与 timetable 尚未公布。已读取指定日期的 Trip.com 双床房列表含税总价、Visit Seoul 延南洞／益善洞／咖啡店资料，以及 KINTEX 官网地址电话。机票动态搜索未取得有效报价，航班卡片仍只是筛选方案和期望窗口；2027 元旦放假安排、签证和假期营业仍需核对。初始网络访问曾被代理 403 拦截，部分域名后续恢复。用户授权代理证书信任后，Chromium 的 HTTPS 已能正常读取部分动态页，全程保留证书验证；航班网站仍存在访问拦截或必要接口加载失败。详细证据见 RESEARCH.md。

**发布进展（2026-10-09，中国 UTC+8）：**用户提供的生产地址为 [打开旅行手册](https://ring-in-the-new-year-2627.ddjyace.workers.dev/)，Cloudflare 截图显示首次部署成功。云环境访问该域名的 CONNECT 请求仍被联网规则返回 403，尚未从本环境验证公网页面、匿名访问或是否发布最新提交；已把确切域名追加到环境配置草稿，草稿保存不等于运行环境已应用。

GitHub `main` 已收到首次 `Daily Seoul leads` 自动提交 `71ebf4d`，采集时间为北京时间 2026-10-09 00:14:07。六个活动新闻／官方页面来源成功，Trip.com 酒店来源读取超时，数据正确标为 `partial`；这验证了监测数据写回仓库，尚不能证明定时触发或 Cloudflare 自动发布已成功。机票自动报价仍未接通。

## 本地使用

预装 Node.js 24 与 Python 3.12 即可，无需 `npm install`：

```sh
cd /workspace/Ring-in-the-New-Year-2627
npm run check
npm start
```

这是内部验证服务。不要把本地地址当成公开分享网址。Cloudflare 的静态资源配置在 `wrangler.jsonc`。

## 一次性公开发布（推荐电脑操作）

浏览器登录不会传递到 Codex 的云机器。Cloudflare Git 连接完成后无需给 GitHub Actions 提供 Cloudflare API 密钥。以下使用 **Workers + Workers Builds**，不是 Pages 项目。

1. 在 GitHub 确认 `Jy-says-Joy/Ring-in-the-New-Year-2627` 的 `main` 分支有 `public/`、`wrangler.jsonc` 和 `.github/workflows/daily-monitor.yml`。
2. 打开 Cloudflare 控制台 → **Workers & Pages** → **Create application** → **Import a repository / Get started**。若界面文字变化，选择连接 GitHub 仓库的入口。
3. 连接 GitHub，授权 Cloudflare GitHub App 读取本仓库，选择上述仓库。
4. 填写以下设置并 **Save and Deploy**：

| 字段 | 值 |
| --- | --- |
| Worker 名称 | `seoul-new-year-2627`（必须与 `wrangler.jsonc` 一致） |
| 生产分支 | `main` |
| 根目录 | 仓库根目录（空或 `/`，不用填 `public`） |
| 构建命令 | `npm run check` |
| 部署命令 | `npx --yes wrangler@4.148.0 deploy` |
| Node.js | 24（环境允许时选择；Wrangler 需受支持的 Node.js） |

5. 等待部署成功。使用 Worker 页面给出的**生产 `workers.dev` URL**，不是需要令牌的预览 URL。用无痕窗口／未登录手机打开，确认页面和 `guide.json`、`updates.json` 能访问。
6. 若账户首次使用 Workers，按 Cloudflare 提示选账户的 `workers.dev` 子域；无需买域名。确认 `workers.dev` 已启用，且未对该网站添加 Cloudflare Access 登录规则。`workers_dev: true` 已写入配置。
7. GitHub → 本仓库 **Actions**。如果提示启用工作流，启用；选择 **Daily Seoul leads** → **Run workflow** → `main`。若写回遇到权限错误，检查 **Settings → Actions → General → Workflow permissions** 是否允许读写，及分支保护是否允许此自动化账号。不要为此关闭已有必要保护；保护阻止机器人写入时改为 PR 审核流程。
8. 任务完成后，核对 `public/updates.json` 的更新时间及 Cloudflare 自动构建日志。第一次推送与自动监测提交均需验证确实触发生产发布。

这些控制台步骤通常可以用手机浏览器完成，**没有技术上必须用电脑的步骤**；连接 GitHub、填写构建设置与查看日志建议用电脑。只有选择下方命令行备用方案才需要带终端的电脑。

Cloudflare 免费计划受其当期额度限制；这是小型静态站，不需要付费产品。GitHub 私有仓库 Actions 也可能受免费分钟额度限制。不在网页公开任何密钥或个人订单。

官方参考：[Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/) 与 [Wrangler 配置](https://developers.cloudflare.com/workers/wrangler/configuration/)。本次通过 Cloudflare 官方文档仓库核对了 Git 导入流程、名称必须匹配和纯静态资源 Worker 配置，并完成 Wrangler dry-run；用户随后在 Cloudflare 控制台完成首次成功部署，公网及后续自动发布仍待验证。

### Git 连接无法使用时的备用发布

在有终端的电脑、仓库目录内执行：

```sh
npx --yes wrangler@4.148.0 login
npm run check
npx --yes wrangler@4.148.0 deploy
```

登录会打开浏览器授权。这个备用方案需要每次手动部署，后续仍应回到 Worker 的 **Settings → Builds → Connect** 连接 GitHub，才能实现 push 自动上线。不要在聊天里发送 API token。

## 每日监测究竟做什么

GitHub Actions 计划在每日 UTC 01:00（中国 UTC+8 的 09:00，韩国 KST 的 10:00）运行 `scripts/monitor.py`，搜索 COUNTDOWN FANTASY、HYUKOH／혁오 和首尔城市跨年新闻，并监测 MINT PAPER、首尔市英文首页指纹变化；另外读取指定 3 晚／两人一间的 Trip.com 酒店列表，筛选双床房含税总价。只覆盖本次列表实际返回的条目，不是完整酒店市场。定时执行可能被 GitHub 延迟，并非准点 SLA。只在默认分支 `main` 运行。

任务把搜索结果写入 `public/updates.json`，标记“未核实”，然后只提交这个文件，由 Cloudflare Git 连接发布。所有来源失败时保留旧线索、记录本次失败并令工作流失败，不能以“0 条新消息”掩盖故障。网站首页变化不等于新增跨年公告；旧年份、同名活动和错误搜索结果需要人工复核。

**机票自动报价尚未实现。**动态航班搜索没有返回可验证的指定日期价格，新闻 RSS 不提供库存。酒店自动更新只记录可读取的列表快照；来源失败保留上次快照并显示原查询时间，来源本次未返回双床房时显示 0 条，不代表全市没有房源。`priceMonitoring.flights` 保持 `not_connected`，不能承诺机票每日实时报价或酒店最终订单可购性。小红书只返回搜索页壳，B站返回验证码，未绕过登录／验证。后续机票自动更新需可用的数据服务与授权，不能把搜索摘要、其他日期低价或促销起价当作本次报价。

GitHub 公共仓库长期没有活动时，定时工作流可能被自动停用（通常 60 天）。临近出发检查 Actions 最近运行时间，必要时重新启用。旅行结束后在 Actions 中停用这个工作流。

## 更新共享手册

- `public/guide.json`：已人工整理的候选行程、活动、酒店、实际报价及待办。办完事项后从 `todos` 移除／改文字，提交后所有人看到相同版本。
- `public/updates.json`：自动监测结果，不能提升为确认活动。不要放个人秘密。
- `public/index.html`、`style.css`、`app.js`：网页。

查询实际报价时必须记录来源链接、查询时刻及税费／行李／取消条款。`flightQuotes` 的每条结构：

```json
{
  "platform": "平台／航司名（真实查询后填写）",
  "url": "https://实际来源域名/",
  "price": "每人往返含税总价 + 币种（真实查询后填写）",
  "schedule": "实际航班号、日期、机场、起降时刻及每段时区",
  "conditions": "行李、退改与人数条件",
  "checkedAt": "带 Z 或时区偏移的真实 ISO 8601 查询时刻"
}
```

当前没有实际报价，不能直接复制示例文字冒充报价。时间必须带时区，日期用完整年份。示意图只表示街区关系；未确认的音乐节场馆不会出现在精确导航中。Google Maps 韩国导航可能受限，页面提供 Naver Map 备用入口。

## 检查与复现

```sh
npm run check
python3 -m unittest discover -s tests
npm run monitor
```

`npm run monitor` 会联网，网络未允许时返回失败并写入错误状态。执行前确认环境联网权限。当前实例另外通过 Chromium 验证手机排版、路线展开、多点导航参数、跨时区倒计时和自动深色主题；通过 Wrangler 本地服务验证静态资源、CSP 和 JSON 无缓存响应头，未知路径返回 404。这不是 Cloudflare 公网验证。

部署工具只用于发布，网页运行时没有 Wrangler 或 npm 依赖。当前固定部署工具版本为官方 npm 注册表查询到的 `4.148.0`。
