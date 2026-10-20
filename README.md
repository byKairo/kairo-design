# Kairo Design

Kairo Design 是一个给 AI Agent 使用的视觉设计 Skill。把文章、想法和素材做成封面、正文配图或海报，支持有字与无字两条创作路线、20 种视觉风格和图片修改。

> [!IMPORTANT]
> 个人非商用免费；商业使用须事先取得书面授权。详见 [使用许可](./LICENSE)。

## 安装

把下面这段话发给支持 Skills 的 AI Agent：

```text
请安装这个仓库里的设计 Skill：https://github.com/byKairo/kairo-design
```

也可以在终端安装：

```bash
npx -y skills add byKairo/kairo-design -g --skill kairo-design
```

## 可用 Skill

| Skill | 用途 |
| --- | --- |
| `kairo-design` | 将文章、主题或素材做成封面、配图和海报；支持有字、无字、系列图及图片修改 |

## kairo-design

给出文章或主题，说明有字还是无字、平台与用途。指定风格会直接采用；未指定时推荐 3 种供选择，也可以授权 Agent 自行选择。主题本身即可开始，不要求补全文稿。

有字版默认完整保留用户标题，先通过排版解决长度；无字版重新设计画面，不是简单删掉文字。多张或多平台任务分别构图，交付独立图片。

### 平台与画幅

内置微信公众号、小红书、X、微信图片消息及普通配图等用途预设，也支持自定义画幅。

预设是构图方向，不是必须精确相等的像素门槛。工具不支持时自动选择最近的可用画幅，例如公众号 `2.35:1` 可采用 `21:9`，简短说明后继续。默认允许相对生成画幅不超过 2% 的比例偏差，保留原图并记录实际尺寸；这项容差是 Skill 的制作规则，不是平台官方尺寸标准。

只有明确要求精确像素、严格比例或已核实平台存在硬性约束时，才启用严格检查。默认不裁切、不拉伸，不会为了微小尾差反复询问或中断交付。

### 使用示例

用主题制作公众号有字封面：

```text
使用 $kairo-design，为微信公众号设计有字封面。
标题：用 Claude 建立你自己的 AI 工作室
请推荐适合的风格。
```

指定风格与无字路线：

```text
使用 $kairo-design，用「立体纸雕」风格制作公众号文章的无字封面。
主题：用 Claude 建立你自己的 AI 工作室
```

同主题制作多种风格：

```text
使用 $kairo-design，主题是「用 Claude 建立你自己的 AI 工作室」。
微信公众号封面，毛线编织、像素艺术、撕纸拼贴各做有字和无字版本，各一张。
```

让 Agent 自行决定：

```text
使用 $kairo-design，给这篇文章配一张封面。
有字或无字、平台画幅和风格都由你决定，直接完成。
这里粘贴文章全文。
```

只生成提示词：

```text
使用 $kairo-design，只为这篇文章写无字封面的生图提示词。
风格：建筑光影。用途：公众号文章封面。
这里粘贴文章内容。
```

修改已有图片：

```text
使用 $kairo-design，修改附图。
保留标题和主体，把背景改为暖灰色；保持原图尺寸。
```

### 可用风格

20 个视觉入口涵盖版式、摄影、插画、场景和材料工艺；每种都有独立的有字与无字规则，不是固定布局模板。完整选择条件见 [风格目录](./skills/kairo-design/references/style-catalog.md)。

| 风格 | Style ID | 适合内容或视觉方向 |
| --- | --- | --- |
| Anthropic 品牌编辑视觉 | `anthropic-brand-editorial` | 温和理性的观点与观察、需要概念图像与编辑秩序共同表达的内容、研究与思考的阅读气质 |
| 建筑光影 | `architectural-light-scene` | 边界与进入、尺度与距离、安静与独处 |
| 装饰纹样插画 | `decorative-illustration` | 节庆、丰盛、群体活动 |
| 色域构成 | `diffuse-color-field` | 情绪过渡、张力、开放 |
| 干擦蜡笔插画 | `dry-crayon-illustration` | 日常观察、行动与表达、关系与情绪 |
| 字图穿插 | `editorial-design` | 观点、人物、空间 |
| 叙事摄影 | `editorial-photo-scene` | 人物处境、日常观察、孤独 |
| 钢笔速写 | `expressive-ink-line` | 城市、人群、思绪 |
| 几何平面插画 | `geometric-flat-illustration` | 关系、行动、方法 |
| 微缩场景 | `isometric-miniature-scene` | 人物与物件关系、日常或概念场景、自然与活动 |
| 毛线编织 | `knitted-textile` | 已有主形的材料转译、连接与张力、触感反差 |
| 立体纸雕 | `layered-paper-relief` | 层次、显露、保护 |
| 套色叠印 | `limited-ink-overprint` | 用有限色版表现空间层次、以色层交叠组织形体与节奏、需要可见印刷质感的观点或情绪图 |
| 积木模型 | `modular-brick-scene` | 搭建、协作、试错 |
| 刻线版画插画 | `monochrome-engraved-line` | 内在冲突与注意力、耐心与细致观察、复杂机制 |
| 像素艺术 | `pixel-scene` | 过程、探索、搭建 |
| 20 世纪中期商业插画 | `retro-commercial-illustration` | 沟通、生活角色、旅行 |
| 半色调网点图像 | `spot-ink-halftone` | 新闻感、公共话题、复古 |
| 瑞士国际主义平面设计 | `swiss-international` | 信息秩序、清晰对照、理性主张 |
| 撕纸拼贴 | `torn-photo-collage` | 断裂、冲突、重组 |

无字路线中，「字图穿插」仅在用户同意时保留少量标题关键词；本组案例保留 `AI`。Anthropic 与瑞士入口的无字版属于相应视觉语言的条件适配，不宣称官方规范。

### 风格样例

这 40 张案例以「用 Claude 建立你自己的 AI 工作室」为共同主题，有字与无字各 20 张。两版分别构图。撕纸拼贴有字版采用作者提供的指定成图，图中标题为「用 Claude 建立你自己的 AI 产品工作室」。

所有图片保留实际输出尺寸；点击可查看原图。样例展示本次创作结果，不代表所有题材和平台都已验证。

| 风格 | 有字版 | 无字版 |
| --- | :---: | :---: |
| Anthropic 品牌编辑视觉 | ![Anthropic 品牌编辑视觉·有字](./screenshots/kairo-design/anthropic-brand-editorial-with-text.png) | ![Anthropic 品牌编辑视觉·无字](./screenshots/kairo-design/anthropic-brand-editorial-wordless.png) |
| 建筑光影 | ![建筑光影·有字](./screenshots/kairo-design/architectural-light-scene-with-text.png) | ![建筑光影·无字](./screenshots/kairo-design/architectural-light-scene-wordless.png) |
| 装饰纹样插画 | ![装饰纹样插画·有字](./screenshots/kairo-design/decorative-illustration-with-text.png) | ![装饰纹样插画·无字](./screenshots/kairo-design/decorative-illustration-wordless.png) |
| 色域构成 | ![色域构成·有字](./screenshots/kairo-design/diffuse-color-field-with-text.png) | ![色域构成·无字](./screenshots/kairo-design/diffuse-color-field-wordless.png) |
| 干擦蜡笔插画 | ![干擦蜡笔插画·有字](./screenshots/kairo-design/dry-crayon-illustration-with-text.png) | ![干擦蜡笔插画·无字](./screenshots/kairo-design/dry-crayon-illustration-wordless.png) |
| 字图穿插 | ![字图穿插·有字](./screenshots/kairo-design/editorial-design-with-text.png) | ![字图穿插·无字](./screenshots/kairo-design/editorial-design-wordless.png) |
| 叙事摄影 | ![叙事摄影·有字](./screenshots/kairo-design/editorial-photo-scene-with-text.png) | ![叙事摄影·无字](./screenshots/kairo-design/editorial-photo-scene-wordless.png) |
| 钢笔速写 | ![钢笔速写·有字](./screenshots/kairo-design/expressive-ink-line-with-text.png) | ![钢笔速写·无字](./screenshots/kairo-design/expressive-ink-line-wordless.png) |
| 几何平面插画 | ![几何平面插画·有字](./screenshots/kairo-design/geometric-flat-illustration-with-text.png) | ![几何平面插画·无字](./screenshots/kairo-design/geometric-flat-illustration-wordless.png) |
| 微缩场景 | ![微缩场景·有字](./screenshots/kairo-design/isometric-miniature-scene-with-text.png) | ![微缩场景·无字](./screenshots/kairo-design/isometric-miniature-scene-wordless.png) |
| 毛线编织 | ![毛线编织·有字](./screenshots/kairo-design/knitted-textile-with-text.png) | ![毛线编织·无字](./screenshots/kairo-design/knitted-textile-wordless.png) |
| 立体纸雕 | ![立体纸雕·有字](./screenshots/kairo-design/layered-paper-relief-with-text.png) | ![立体纸雕·无字](./screenshots/kairo-design/layered-paper-relief-wordless.png) |
| 套色叠印 | ![套色叠印·有字](./screenshots/kairo-design/limited-ink-overprint-with-text.png) | ![套色叠印·无字](./screenshots/kairo-design/limited-ink-overprint-wordless.png) |
| 积木模型 | ![积木模型·有字](./screenshots/kairo-design/modular-brick-scene-with-text.png) | ![积木模型·无字](./screenshots/kairo-design/modular-brick-scene-wordless.png) |
| 刻线版画插画 | ![刻线版画插画·有字](./screenshots/kairo-design/monochrome-engraved-line-with-text.png) | ![刻线版画插画·无字](./screenshots/kairo-design/monochrome-engraved-line-wordless.png) |
| 像素艺术 | ![像素艺术·有字](./screenshots/kairo-design/pixel-scene-with-text.png) | ![像素艺术·无字](./screenshots/kairo-design/pixel-scene-wordless.png) |
| 20 世纪中期商业插画 | ![20 世纪中期商业插画·有字](./screenshots/kairo-design/retro-commercial-illustration-with-text.png) | ![20 世纪中期商业插画·无字](./screenshots/kairo-design/retro-commercial-illustration-wordless.png) |
| 半色调网点图像 | ![半色调网点图像·有字](./screenshots/kairo-design/spot-ink-halftone-with-text.png) | ![半色调网点图像·无字](./screenshots/kairo-design/spot-ink-halftone-wordless.png) |
| 瑞士国际主义平面设计 | ![瑞士国际主义平面设计·有字](./screenshots/kairo-design/swiss-international-with-text.png) | ![瑞士国际主义平面设计·无字](./screenshots/kairo-design/swiss-international-wordless.png) |
| 撕纸拼贴 | ![撕纸拼贴·有字](./screenshots/kairo-design/torn-photo-collage-with-text.png) | ![撕纸拼贴·无字](./screenshots/kairo-design/torn-photo-collage-wordless.png) |

## 工具与环境

需要支持 Skill 的 AI Agent 及可用的图像生成／编辑工具；Skill 本身不提供模型、额度或独立生图服务。生成能力与实际支持的画幅由宿主工具决定。

Python 3 用于加载风格与检查交付；图像检查和格式导出需要 Pillow。附带的文字排版脚本使用时需按环境准备字体。生成后仍须目检文字、主体、风格和画面，脚本不能证明审美质量。

## 仓库结构

```text
skills/kairo-design/     可安装的完整 Skill
  SKILL.md              入口与交互规则
  routes/               有字与无字工作流
  styles/               20 种风格的独立路线规则
  references/           风格索引、平台与交付说明
  scripts/              加载、检查与导出工具
screenshots/            40 张案例原图
```

## 使用许可

个人非商用使用免费；商业使用，包括商业内容、营销、收费服务、团队业务和客户项目，须事先取得书面授权。请通过 [GitHub Issues](https://github.com/byKairo/kairo-design/issues) 联系作者，勿公开提交私密业务材料。完整条款见 [LICENSE](./LICENSE)。

第三方品牌、字体与素材不因本仓库的许可而获得额外授权；品牌视觉案例不表示官方背书。见 [第三方说明](./THIRD_PARTY_NOTICES.md)。

## 致谢

- 设计与维护：[@byKairo](https://github.com/byKairo)  
