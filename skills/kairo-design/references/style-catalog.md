# 视觉创作目录

20个共享入口，按主要作用分组导航，不是20套平级封面模板。分类不是互斥边界，也不自动授权多种风格混搭；具体如何使用由当前路线决定。`catalog.json` 集中保存身份、别名及各路线的选择条件；风格构图规则仍由各路线正文提供。

有字创作先确定主导视觉关系；材料与工艺可服务它，不替代标题与构图。品牌视觉按用户指定的方向使用，不默认成为个人视觉身份。无字创作仍按原有独立路线执行，分类与共享名称不改写其设计规则。

优先运行 `python3 scripts/load_style.py --style "名称或ID" --mode with-text`，无字改为 `wordless`；从根目录外调用用脚本绝对路径。只读所选路线的 META、STYLE 与必要父项。supported/conditional 是兼容性，不是质量认证。不新增条目时可做一次性自定义创作。

名称兼容：微缩场景保留“建筑地景沙盘”“场景沙盘”等旧称；毛线编织可用“针织”检索；色域构成保留“弥散渐变／色域构成”及“弥散渐变”别名，后者在有字路线中指柔边过渡子型。目录内旧 ID 保持不变；`paper-surface-relief`／“纸面压凹浮凸”兼容到有字设计指南的`paper-finishes`工艺章节，加载结果为`kind: technique`，不是新增目录风格，也不套用到无字路线。

## 版式与图文语言

| 入口 | ID | 有字 | 无字 |
|---|---|---|---|
| [字图穿插](../catalog.json) | `editorial-design` | supported | conditional |
| [瑞士国际主义平面设计](../catalog.json) | `swiss-international` | supported | conditional |

## 插画、摄影与拼贴

| 入口 | ID | 有字 | 无字 |
|---|---|---|---|
| [几何平面插画](../catalog.json) | `geometric-flat-illustration` | supported | supported |
| [装饰纹样插画](../catalog.json) | `decorative-illustration` | supported | supported |
| [20 世纪中期商业插画](../catalog.json) | `retro-commercial-illustration` | supported | supported |
| [钢笔速写](../catalog.json) | `expressive-ink-line` | supported | supported |
| [干擦蜡笔插画](../catalog.json) | `dry-crayon-illustration` | supported | supported |
| [刻线版画插画](../catalog.json) | `monochrome-engraved-line` | supported | supported |
| [叙事摄影](../catalog.json) | `editorial-photo-scene` | supported | supported |
| [建筑光影](../catalog.json) | `architectural-light-scene` | supported | supported |
| [撕纸拼贴](../catalog.json) | `torn-photo-collage` | supported | supported |

## 场景与立体造型

| 入口 | ID | 有字 | 无字 |
|---|---|---|---|
| [微缩场景](../catalog.json) | `isometric-miniature-scene` | supported | supported |
| [立体纸雕](../catalog.json) | `layered-paper-relief` | supported | supported |
| [积木模型](../catalog.json) | `modular-brick-scene` | supported | supported |
| [像素艺术](../catalog.json) | `pixel-scene` | supported | supported |

## 材料与印刷语言

| 入口 | ID | 有字 | 无字 |
|---|---|---|---|
| [毛线编织](../catalog.json) | `knitted-textile` | supported | supported |
| [套色叠印](../catalog.json) | `limited-ink-overprint` | supported | supported |
| [半色调网点图像](../catalog.json) | `spot-ink-halftone` | supported | supported |

## 抽象视觉

| 入口 | ID | 有字 | 无字 |
|---|---|---|---|
| [色域构成](../catalog.json) | `diffuse-color-field` | supported | supported |

## 品牌编辑视觉

| 入口 | ID | 有字 | 无字 |
|---|---|---|---|
| [Anthropic 品牌编辑视觉](../catalog.json) | `anthropic-brand-editorial` | supported | conditional |

字图穿插的无字适配仅允许少量标题关键词，不允许完整标题；其他无字风格不共享这个例外。
