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
- Chromium 动态读取遇到证书信任问题；将环境代理证书持久导入浏览器信任库的操作被自动审批拒绝（扩大未来流量信任范围）。没有忽略 TLS 错误或绕过此拒绝。

因此网页只提供三种出行策略及查价入口，不发布伪造的航班号、时刻、价格，也不把“其他日期 US$188 往返”等推广数字写成本次报价。

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
