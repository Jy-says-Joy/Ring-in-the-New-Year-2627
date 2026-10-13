# SEOUL, slowly — 首尔跨年手册 2026 → 2027

公开手册：[ring-in-the-new-year-2627.ddjyace.workers.dev](https://ring-in-the-new-year-2627.ddjyace.workers.dev/)

手机优先、无需登录、运行时零外部依赖。没有外部字体、脚本、图片、嵌入地图、追踪器或本地待办勾选。Google / Naver 地图和购票平台只在用户点击后打开。

## 第二版：首尔市内跨年与轻松购物

- 跨年活动排在第一章，切换“已公布活动 / 往年活动”。六个有官方记录的往年项目：普信阁、光化门灯光、DDP、SEOULCon、清溪川灯节、光化门市集。午夜主场与晚间暖场分开说明，2026 年末日程未公布时不沿用往届时刻、烟花或阵容。高阳 COUNTDOWN FANTASY 只作周边备选。
- 每日先切换日期，再选路线：12/31 钟路 / 光化门 / DDP；1/1 汝矣岛商场 / 汉南洞；1/2 圣水 / 江南室内购物；1/3 午后 / 晚间返程。共九条替代路线，每条都有地点总览、交通方式、含步行等候的估计时长、地图和多点导航。不是地图 API 实测时间。
- 机票只整理用户提供的四张携程截图，区分 12/30 与 12/31 出发，不再联网查价。截图未给航班号、完整行李和退改规则，未补造。强调凌晨到达需多订一晚，以及 23:40 抵港后可能到 1/4 才回深圳。
- 主行程围绕购物、美食和咖啡；妆发与 AMORE 定制体验可选，不安排学生风打卡。三晚酒店优先钟路 / 明洞，保留双床房与取消条件建议；住宿金额和价格参考按用户要求移除。
- 新增 35 家具体餐饮店、40 条沿线吃喝选择，按正餐、咖啡甜点、小酌等筛选；新增 FAUST、Cakeshop、Charles H. 和 Jean Frigo 夜生活关注名单，常规去处不等于已公布跨年场次。
- 已移除研究过程说明和原始韩文新闻列表。系统自动切换深浅色，倒计时使用首尔午夜的绝对时刻。共享待办只由仓库更新。

## 开发与验证

预装 Node.js 24 与 Python 3.12 即可，无需 `npm install`。

```sh
cd /workspace/Ring-in-the-New-Year-2627
npm run check
python3 -m unittest discover -s tests
npm start
```

`npm start` 启动内部 HTTP 服务；不要把本地地址当成公开链接。端口已被以前的实例占用时，先检查实际响应，或用另一端口验证，不要停止未知进程。

本次验证覆盖：320 / 390 / 768 / 1440 像素宽度，活动、日期和路线切换、地图、导航、无横向溢出与 JS 错误；上海、首尔、洛杉矶时区的绝对倒计时；深色模式与来源失败回退。监测测试还覆盖往届年份、页脚年份、不可信来源、未来发布时间和单个活动取消。

## 每日中文活动简报：韩网、公开社交和夜生活

GitHub **Actions → Daily Seoul leads** 每日 UTC 01:00（北京时间 09:00、首尔 10:00）计划运行，支持手动触发。GitHub 可能延迟，不承诺准点。

```sh
npm run monitor
```

- Google News 公开 RSS 搜索市内活动、年末小型演出、夜店 / 酒吧派对和公开社交索引；Naver 每日搜索韩网、Instagram 公开索引和本地售票线索。原始结果保留未核实状态，不在网页展示。
- 首尔市官方英文 RSS 与 Naver 官方站点正文继续核对六个城市候选，只接受完整的本季日期，不用版权年份或往届迎新新闻确认本年活动。
- `scripts/activity_sources.py` 新增主办方及票务活动核实。候选不再限于六个大活动：RA / NOL / YES24 及登记的场地方 `Event` 结构化公告必须有明确本季日期、实际首尔场地和可信来源，才生成中文卡片。支持午夜后至 1/1 06:00 的跨年夜场次、公布票面价和阵容、取消及改期回退。不能仅靠搜索页或普通店铺介绍确认派对，不能把未知时段写成午夜。
- FAUST / Cakeshop 公开社交账号和 RA 首尔跨年夜目录纳入关注；需要登录、验证或只提供不可解析图片的内容不能自动核实，记录失败 / 待核实状态，保留原时间的已有卡片。系统不是任意社交帖的全文翻译器，不承诺覆盖所有公告；新来源可继续人工审核补充。
- 机票仍只用用户截图，不联网查价；住宿价格已不显示、不采集。原 `hotelQuotes`、`observedHotelRates` 和住宿预算字段从网页数据移除。

工作流运行监测测试与数据检查后，只提交 `public/updates.json`，由 Cloudflare Git 连接发布。取消 / 改期会退下已公布推荐并显示通知；来源失败不更新旧信息的核查日期，也不会伪称“没有新活动”。日志区分入口组成功与子渠道失败。GitHub 公共仓库长期无活动可能停用计划任务，临近出发检查最近运行记录，旅行后可停用。

## 发布与 Git 自动上线

现有 Cloudflare Worker 已成功部署，无需重新创建项目。仓库 `main` 的后续提交通过已有 Git 连接发布。Cloudflare **Deployments** 可查看构建是否成功及对应提交；**Domains** 中生产 `workers.dev` 地址为上面的分享链接。

已有项目建议构建命令 `npm run check`，根目录为仓库根目录，部署命令 `npx --yes wrangler@4.148.0 deploy`。静态资源目录 `./public` 已在 `wrangler.jsonc` 配置，不需要另外安装网页依赖或接入登录验证。保持正在工作的 Worker 名称与 Cloudflare 构建配置，不要为了文档示例重新创建。

新账户 / Git 连接尚未完成时，在 Cloudflare **Workers & Pages → Create application → Import a repository** 选择本仓库，生产分支 `main`，根目录 `/`，填写上述构建 / 部署命令。新 Worker 名称与 `wrangler.jsonc` 保持一致；生产 `workers.dev` 需启用。不要为旅行手册启用 Cloudflare Access 登录规则。

GitHub **Actions → Daily Seoul leads → Run workflow → main** 可验证写回；已成功运行的无需反复启用。若写回被分支保护阻挡，改为 PR 审核流程，不要关闭必要保护。浏览器登录不会把密钥交给云机器，Git 连接不需要在公开仓库添加 Cloudflare API token。

控制台步骤手机也能操作，连接仓库和查看日志建议电脑；没有技术上必须在电脑做的控制台步骤。终端备用部署才需要有终端的电脑：

```sh
npx --yes wrangler@4.148.0 login
npm run check
npx --yes wrangler@4.148.0 deploy
```

免费计划受 Cloudflare 与 GitHub 当期额度限制。官方文档：[Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/)、[Wrangler 配置](https://developers.cloudflare.com/workers/wrangler/configuration/)。

## 更新内容

- `public/guide.json`：活动、九条替代路线、截图机票、酒店和共享待办。办完后修改 `todos`，提交即可更新大家看到的同一份手册。
- `public/updates.json`：自动中文活动卡片、内部检索线索和渠道状态。`eventBriefs` 必须有当季、官方正文与原核查时间，不能从 RSS 标题直接确认。
- `public/index.html`、`style.css`、`app.js`：移动网页，所有菜单切换支持键盘。
- `RESEARCH.md`：资料来源、JourneyPilot 调用记录与查询边界，不把研究过程放到产品页面。

所有绝对时间使用 ISO 8601 时区偏移；行程时刻为 KST / UTC+9，截图香港 / 深圳时刻为 UTC+8。不要公开分享链接的访问 token、护照、订单和密钥。示意 SVG 不按比例，真实交通与营业情况以当天地图及商家公告为准。
