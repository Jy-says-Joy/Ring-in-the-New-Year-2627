# 研究记录（2026-10-08 中国时间）

所有页面经验证 TLS 的 Python HTTPS 请求读取。本文区分官方资料、列表观察和未完成的查价，不记录登录凭证。页面公开日期和查询时间以 `public/guide.json`、`public/updates.json` 为准。

## COUNTDOWN FANTASY：当届已核实

- [NOL 官方商品页](https://nol.yanolja.com/ticket/products/26014480)：标题 COUNTDOWN FANTASY 2026-2027；日期 2026-12-31；KINTEX 第 2 展馆 7、8 厅；10/13（周二）18:00 一般开票；全场不对号入座，1 日票 ₩121,000。HYUKOH／혁오 在一轮阵容。页面明确票务／取票／入场细节稍后公布，开票安排也可变动。两人票面合计 ₩242,000，手续费未核实。
- [SBS 2026-10-07 报道](https://ent.sbs.co.kr/amp/article.do?article_id=E10010322954)：12/31 一天、三个舞台、首轮 12 组阵容；10/13 通过 NOL、YES24、Naver、2TM 售票。
- [Xportsnews 2026-10-07 报道](https://www.xportsnews.com/article/2204942)：核对当届年份、日期、KINTEX 7–8 厅与 HYUKOH。
- [MINT PAPER 官网](https://www.mintpaper.co.kr/)：已能读取首页，后续监测指纹变化；首页变化不是活动已更新。
- [Festival Life 当届社区汇总](https://festivallife.kr/festival/?idx=174978848&bmode=view)：中文整理之前曾用于发现开票线索；其英文行误写 10/13 Thursday，正确日历及 NOL 是 Tuesday，页面采用 2026-10-13 周二。
- [KINTEX 官网](https://www.kintex.com/web/en/index.do)：217-60 Kintex-ro, Ilsanseo-gu, Goyang-si, Gyeonggi-do；+82-31-995-8114。这是场馆总机，不是票务热线。场馆在高阳，不在首尔市中心。

尚未核实／公布：HYUKOH 上台时段、完整 timetable、海外卡付款、实名及护照规则、取票、再入场、储物、退改、散场接驳。不会把 2025–2026 的安排套用到当届。

## 机票：尚无所选日期有效报价

条件：经济舱、2 成人、2026-12-31 至 2027-01-03、SZX / HKG ↔ SEL，直飞优先，税费／行李／退改均需纳入。

- [携程深圳往返查询](https://flights.ctrip.com/online/list/round-szx-sel?depdate=2026-12-31_2027-01-03&cabin=y&adult=2&child=0&infant=0)：服务器返回查询框架及日期参数，没有航班报价。
- [Skyscanner 深圳指定日期](https://www.skyscanner.com.hk/transport/flights/szx/sela/261231/270103/)：返回动态页框架，未取得报价；香港入口在网页列出。
- [Trip.com 深圳航线页](https://www.trip.com/flights/shenzhen-to-seoul/airfares-szx-sel/) 与 [香港航线页](https://www.trip.com/flights/hong-kong-to-seoul/airfares-hkg-sel/)：可读，但展示的是其他日期的低价与常规统计，不作为跨年报价。部分动态搜索路径返回 404。
- 国泰订票页返回表单并提示目的地列表加载失败；香港快运、大韩、香港航空、济州官网可取得首页／动态壳，未取得指定日期价格。深圳航空与韩亚入口曾被代理 403 拦截。
- Chromium 初始遇到证书信任问题，首次持久导入尝试被自动审批拒绝。用户随后明确授权在此云环境信任已安装的代理证书；环境根证书实际已在 Chromium NSS 库中，另授予该数据库写权限后，浏览器的 HTTPS 请求通过正常验证。没有关闭 TLS 验证。携程两条指定日期动态搜索及 Trip.com 航班页随后返回 432 / whaleguard；国泰表单仍提示目的地接口加载失败，香港快运的必要接口未成功加载，Skyscanner 页面未加载报价脚本。因此仍未获得有效机票报价。

因此网页只提供三种出行策略及查价入口，不发布伪造的航班号、时刻、价格，也不把“其他日期 US$188 往返”等推广数字写成本次报价。

## 发布与首次自动更新证据

- 2026-10-09（中国 UTC+8）用户提供 Cloudflare 成功部署截图及生产网址：https://ring-in-the-new-year-2627.ddjyace.workers.dev/ 。本环境对该域名的代理 CONNECT 返回 403，请求未到网站；不能据此认定网站失败，也不能声称公网已验证。已将确切域名追加到云环境联网配置草稿，待运行环境应用后复查。
- Git 远程 `main` 的 `71ebf4d` 自动提交更新了 `public/updates.json`。其中 `lastAttempt` / `lastSuccess` 为 `2026-10-08T16:14:07+00:00`，即北京时间 2026-10-09 00:14:07；六个新闻／官方页面来源成功，Trip.com 酒店来源读取超时，整体为 `partial`，机票为 `not_connected`。证明采集与写回仓库运行过，不证明每日定时运行或此提交已发布公网。

## 酒店：所选日期的列表价格观察

两人一间、2026-12-31 入住至 2027-01-03 退房、3 晚。预算每间每晚含税 ≤ ¥2,000（3 晚目标 ≤ ¥6,000）。

- [Trip.com 指定日期列表（USD）](https://www.trip.com/hotels/list?city=274&checkin=2026-12-31&checkout=2027-01-03&adult=2&crn=1)：NINE TREE BY PARNAS SEOUL MYEONGDONG 2 / Standard Twin Room，3 晚含税费 US$811；均价 US$270.33。列表为会员价，并标注 4-hour Cancellation Window，不能理解为入住前任意免费取消。按最终结算汇率核对 RMB 预算。
- [Trip.com 指定日期 CNY 列表](https://www.trip.com/hotels/list?city=274&checkin=2026-12-31&checkout=2027-01-03&adult=2&crn=1&curr=CNY&keyword=NINE%20TREE%20BY%20PARNAS%20SEOUL%20MYEONGDONG%202)：来源仍返回全市列表，keyword 没有可靠限定品牌。实际可读条目 Friendly DH Naissance Hotel by Mindrum Group / Budget Twin Room，3 晚含税费 ¥2,404，均价 ¥801.33；列表显示含早餐、Free Cancellation、会员价，截止时间及付款条件未核实。位置在诚信女大方向，通勤较本行程主要街区远。
- [Booking.com 指定日期搜索](https://www.booking.com/searchresults.html?ss=Seoul&checkin=2026-12-31&checkout=2027-01-03&group_adults=2&no_rooms=1&group_children=0)：返回 202 挑战页，未取得价格。

以上不是酒店订单，也未保证付款前库存。上方住宿片区中的 Mercure Hongdae、L7 Hongdae、NINE TREE Insadong、Sono Calm Goyang 是独立候选，不能把明洞 2 的报价安到仁寺洞店。

每日脚本只接受可见双床房的 3 晚含税总价；严格核对响应里的完整年份／日期及住宿条件，拒绝普通每晚促销数字。当页只返回双人床时，结果可以是 0 条；没有扩大为全市无库存的结论。

## 轻松游玩：已读取的官方资料

- [Visit Seoul 延南洞建筑散步](https://english.visitseoul.net/editorspicks/A-Tour-of-Seouls-Streetside-Architecture-4-Yeonnam-ro/ENN039022)：2026-08-14 修订；弘大入口 3 号出口通往京义线林荫道。选短段散步，冬季不推荐把完整路线当任务。
- [Visit Seoul 益善洞吃喝](https://english.visitseoul.net/editorspicks/SeouliteinIkseondong/ENN032625)：2026-07-16 修订；提供 Dongbaek Bakery 地址、电话、常规营业时间。文中的 Changhwadang 明确标为 Closed，因此不纳入可去店铺。
- [Folv Yeonnam 官方旅游目录](https://english.visitseoul.net/restaurants/PolvYeonnam/ENPoym5k2)：2026-05-21 修订；32 Donggyo-ro 41-gil, Mapo-gu，一层；+82-70-8722-1067；10:00–21:30；手冲 ₩8,000 左右，派 ₩8,000–9,000。这些是目录常规资料，元旦营业与最新价格需再次确认。
- 小红书检索返回页面壳，没有可读取笔记；B站检索返回验证码。只保留灵感检索入口，不声称已经阅读笔记或视频。

妆造、个人色彩、戒指／香氛手作是符合用户偏好的体验类别候选，尚未选择商家、核实报价／语言服务或预订。网页时长只是规划预留，并非已确认商品套餐。

## 2026-10-13 第二版：首尔市内与成年人的购物咖啡路线

用户改为首尔市内跨年优先；CDF 降为高阳备选，不进入主行程。机票不再联网查价，仅整理提供的四张携程截图。网页移除过程说明和原始新闻墙，改为活动分类、日期和替代路线切换。以下资料已读取正文：

- [首尔市 2025 Winter Festa 日程](https://english.seoul.go.kr/2025-seoul-winter-festa/)（2025-12-04）：逐项列出 2025 年末至 2026 年初的普信阁、光化门、DDP、SEOULCon、灯节和市集。只是往届日程，不能写成 2026 年末已公布。
- [2025 季官方结项与各项目统计](https://english.seoul.go.kr/2025-seoul-winter-festa-draws-10-million-visitors-poised-to-grow-as-koreas-premier-winter-festival/)（2026-01-13）：整体 24 天累计约 1,098 万人次；光化门灯光约 315 万、市集约 357 万、灯节约 326 万、DDP 约 79.8 万、SEOULCon 约 9.4 万，普信阁当晚约 3.2 万。不同统计口径已分别表述，不能把整个季节的累计人次写成跨年当晚人数。原文统计表 2024 季结束年份有明显笔误，未照抄。
- [2024 季官方开幕公告](https://english.seoul.go.kr/seoul-winter-festa-2024-begins-on-dec-13-brightly-lighting-up-winter-nights-for-24-days/)（2024-12-16）：证明冬季灯光 / 市集 / 灯节连续两季计划与品牌延续。它是开幕前公告，不能证明后续所有午夜项目原样执行，因此不宣称 2024 年末烟花、演出均已实际举办。
- [DDP 2023 冬季结项与满意度](https://english.seoul.go.kr/seoul-light-ddp-winter-attracts-approx-630000-visitors-for-new-years-celebrations/)（2024-01-09）：约 62.8 万季节累计人次，现场满意度 91.2%、愿再访 95.9%。用来说明体验口碑，非本次体验承诺。
- [SEOULCon 2023→2024 跨年演出结项](https://english.seoul.go.kr/new-year-countdown-celebration-at-seoulcon-with-3000-global-influencers/)：跨年演出约 4,000 人，与整体约 10 万参与者分开说明。收费演出与 DDP 户外活动不合并为一个购票项目。
- [Visit Seoul 圣水 2026 街区路线](https://english.visitseoul.net/editorspicks/2026-Seongsu/ENNky3epf)（2026-08-28 修订）：CaféCité（71 Seongsui-ro）、AMORE（7 Achasan-ro 11-gil；定制体验建议预约）、Gentle Monster（433 Ttukseom-ro）及各地点资料。未照搬整条长路线，也没有假定元旦按常规营业。
- [Visit Seoul The Hyundai 美食](https://english.visitseoul.net/editorspicks/The-Hyundai-Seoul-Food-Tour/ENN037990)（2026-08-13 修订）：Cafe Layered、Richemont 可作购物间歇选择；文中 Tongin Sweet、Le Petit Four 标为 Business closed，已排除。
- [Visit Seoul 汉南洞](https://english.visitseoul.net/editorspicks/Hallyu-Hannam/ENNgyk0ja)（2026-10-08 修订）：Gourmet 494（91 Hannam-daero）、SOUNDS（35 Daesagwan-ro）、Leeum。按成人购物、家居、餐饮和咖啡筛选；看展可删，不为了明星同款追店。

Naver 已搜索当前 2026 年末与 2027 跨年、各场馆往届活动、公开博客和短视频。搜索中出现了提前写出的“2026 年末日程”博客，未找到对应官方正文时没有采用。三个用户提供的小红书分享链接已尝试含正常分享参数的访问，返回网页壳，未读到笔记正文；B站仍返回验证码，公开 Naver 博客正文受环境域名规则阻挡。没有绕过验证，也不声称已读这些帖子。

### JourneyPilot

已克隆用户指定 [Lagom-TA/JourneyPilot](https://github.com/Lagom-TA/JourneyPilot)，读取提交 `20a79d5f27f9366b77970ba1741ed0b0dba97f7f` 的 README、配置示例、行程 composition 结构和 `mcp_servers/search/free_search.py`。实际调用该免费搜索模块查询首尔跨年与圣水 / 汉南购物；其 DDGS 上游 Yahoo / DuckDuckGo 域名被云环境 CONNECT 403 阻挡，没有可用结果。完整服务需要模型等凭据，当前没有相应绑定，因此没有假称调用完整规划 / 地图服务。采用了它的“地点顺序 + 相邻交通连接 + 门到门分钟 + 住宿”结构；路线时间均是注明的规划估计，非地图接口实测。该依赖仅装在 `/tmp` 的研究目录，网页和 GitHub 监测仍零 npm / Python 第三方依赖。

### 截图机票

四张截图分别整理为：深圳 12/31 日间直飞 ¥3,088；香港 12/31 日间快运 ¥2,442；香港 12/30 晚快运 ¥2,434；香港 12/30 晚国泰 ¥3,923。使用截图底部往返显示价与选中回程加价交叉核对，没有把其他去程的基础价直接当成对应已选往返总价。部分返程航司只显示 logo，未可靠辨认时标为以订单为准，没有编造航班号。

香港 12/31 快运截图的 10:30 与 16:40 去程显示同一基础价，优先列更有机会在市区安顿的 10:30，并说明同价另一个时刻。12/30 晚出发均跨入 12/31 凌晨抵达，通常酒店需要从 12/30 开始订；21:05 KST 回程 23:40 抵港的方案可能到 1/4 才返深。截图没有完整税费、行李和退改详情，未声称实时可购。

### 本次验证与公告更新

公开生产网站经保留 TLS 验证的 Chromium 新匿名上下文返回 200；Python 默认 User-Agent 被网站返回 403 / 1010，不能再误报为云环境域名 CONNECT 拦截。沿用用户此前授权的代理根证书信任，授予已有 NSS 数据库写权限后 Chromium 正常验证 HTTPS，未禁用证书校验。

本次实时监测 10 / 10 来源成功，酒店返回 2 条双床列表参考。首尔官方英文 RSS 与 Naver 官方站点正文没有满足本季完整日期条件的已确认活动，`eventBriefs` 为空，六项保持往年分类。网页不会直接展示 RSS 标题。原始线索保留在数据供进一步研究；中文简报只自动识别已有六个市内项目，新项目仍需人工审核整理。源失败保留旧简报和原核查日期，取消 / 调整通知单独显示。
