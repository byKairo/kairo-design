# Kairo Design

[简体中文](./README.md) | English

Kairo Design is a visual design Skill for AI agents. Turn articles, ideas, and source material into covers, article illustrations, or posters, with separate workflows for images with text and wordless images, 20 visual styles, and image editing.

> [!IMPORTANT]
> Free for personal, non-commercial use. Commercial use requires prior written permission. See [License](./LICENSE).

## Installation

Send this request to an AI agent that supports Skills:

```text
Please install the design Skill from this repository:
https://github.com/byKairo/kairo-design
```

Or install it from your terminal:

```bash
npx -y skills add byKairo/kairo-design -g --skill kairo-design
```

## Available Skill

| Skill | Purpose |
| --- | --- |
| `kairo-design` | Create covers, illustrations, and posters from articles, themes, or source material; supports images with text, wordless images, series, and image editing |

## kairo-design

Provide an article or theme, specify whether the image should contain text, and name the platform and intended use. If you specify a style, the agent uses it directly. Otherwise, it recommends three options, or you can let it choose. A theme alone is enough to start; a full article is optional.

Images with text preserve your complete title by default and use typography and layout to accommodate its length. Wordless images receive their own composition. Multiple images and platform versions are composed separately and delivered as individual files.

The Skill's detailed instructions and reference files are currently written in Chinese. You can make requests in English and explicitly specify the language of the response and any text that should appear in the image. Use the stable style IDs below to select a style unambiguously.

### Platforms and aspect ratios

Built-in presets cover WeChat Official Account articles, Xiaohongshu / RED, X, WeChat picture messages, and general illustrations. Custom aspect ratios are also supported.

Presets guide the composition. They do not require mathematically exact pixel ratios by default. If the image tool does not support the requested ratio, the agent selects the nearest available format and briefly explains the substitution. For example, a WeChat cover requested at `2.35:1` can use `21:9`. The default check allows up to 2% relative deviation from the selected generation ratio, preserves the full image, and records its actual dimensions. This tolerance is a Skill production rule, not an official platform specification.

Strict checks apply only when you explicitly require exact pixels or an exact ratio, or when a platform's hard requirements have been verified. Images are not cropped or stretched by default, and small rounding differences should not repeatedly interrupt delivery.

### Usage examples

Create a WeChat cover with an English title:

```text
Use $kairo-design to create a cover with text for a WeChat Official Account article.
Title: Build Your Own AI Studio with Claude
Use the exact English title above and respond in English.
Please recommend suitable styles.
```

Choose a style for a wordless cover:

```text
Use $kairo-design to create a wordless WeChat article cover.
Style ID: layered-paper-relief
Theme: Build your own AI studio with Claude.
Respond in English.
```

Create several styles for the same theme:

```text
Use $kairo-design for the theme “Build Your Own AI Studio with Claude.”
Create WeChat covers in knitted-textile, pixel-scene, and torn-photo-collage.
For each style, make one image with the exact English title above and one wordless image.
Deliver six individual images. Respond in English.
```

Let the agent make the design decisions:

```text
Use $kairo-design to create a cover for this article.
Choose whether it needs text, the platform format, and the style, then complete the image.
Respond in English. If the image contains text, use English.
Paste the full article here.
```

Request only a prompt:

```text
Use $kairo-design to write an image-generation prompt only, without generating an image.
Create a wordless WeChat article cover in architectural-light-scene style.
Respond in English.
Paste the article here.
```

Edit an existing image:

```text
Use $kairo-design to edit the attached image.
Preserve its title and main subject. Change the background to warm gray.
Keep the original image dimensions. Respond in English.
```

### Available styles

The 20 visual approaches span layout, photography, illustration, scenes, and material techniques. Each has separate rules for images with text and wordless images. They are not fixed layout templates. See the [style catalog](./skills/kairo-design/references/style-catalog.md) for detailed selection criteria in Chinese.

| Style | Style ID | Suitable themes or visual directions |
| --- | --- | --- |
| Anthropic Brand Editorial | `anthropic-brand-editorial` | Reflective viewpoints, conceptual imagery with editorial structure, research and thoughtful reading |
| Architectural Light | `architectural-light-scene` | Boundaries and entry, scale and distance, quiet and solitude |
| Decorative Illustration | `decorative-illustration` | Celebration, abundance, group activities |
| Color Field Composition | `diffuse-color-field` | Emotional transitions, tension, openness |
| Dry Crayon Illustration | `dry-crayon-illustration` | Everyday observations, action and expression, relationships and emotions |
| Interwoven Type and Image | `editorial-design` | Viewpoints, people, space |
| Narrative Photography | `editorial-photo-scene` | Human situations, everyday observations, solitude |
| Expressive Ink Drawing | `expressive-ink-line` | Cities, crowds, thoughts |
| Geometric Flat Illustration | `geometric-flat-illustration` | Relationships, action, methods |
| Miniature Scenes | `isometric-miniature-scene` | People and objects, everyday or conceptual scenes, nature and activities |
| Knitted Textile | `knitted-textile` | Translating forms into textile, connection and tension, contrasting textures |
| Layered Paper Relief | `layered-paper-relief` | Layers, revelation, protection |
| Limited-Ink Overprint | `limited-ink-overprint` | Spatial depth and rhythm through overlapping color layers, visible print textures |
| Modular Brick Models | `modular-brick-scene` | Building, collaboration, trial and error |
| Engraved-Line Illustration | `monochrome-engraved-line` | Inner conflict and attention, patient observation, complex mechanisms |
| Pixel Art | `pixel-scene` | Processes, exploration, building |
| Mid-Century Commercial Illustration | `retro-commercial-illustration` | Communication, everyday roles, travel |
| Halftone Imagery | `spot-ink-halftone` | News-like imagery, public topics, retro expression |
| Swiss International Graphic Design | `swiss-international` | Information hierarchy, clear comparisons, rational arguments |
| Torn Photo Collage | `torn-photo-collage` | Rupture, conflict, recombination |

In the wordless workflow, Interwoven Type and Image may retain a few title keywords only with the user's agreement; this example set retains `AI`. Wordless adaptations of the Anthropic and Swiss approaches retain aspects of their visual language and do not claim to define official standards.

### Style examples

These 40 examples share the theme “Build Your Own AI Studio with Claude,” with 20 images with text and 20 wordless images. Each version has its own composition. The examples with text use Chinese titles. The Torn Photo Collage example with text is the image selected and supplied by the author; its title translates to “Build Your Own AI Product Studio with Claude.”

All images retain their actual output dimensions. Click an image to open the original. These examples show the results of this project; they do not establish that every theme or platform has been tested.

| Style | With text | Wordless |
| --- | :---: | :---: |
| Anthropic Brand Editorial | ![Anthropic Brand Editorial: with text](./screenshots/kairo-design/anthropic-brand-editorial-with-text.png) | ![Anthropic Brand Editorial: wordless](./screenshots/kairo-design/anthropic-brand-editorial-wordless.png) |
| Architectural Light | ![Architectural Light: with text](./screenshots/kairo-design/architectural-light-scene-with-text.png) | ![Architectural Light: wordless](./screenshots/kairo-design/architectural-light-scene-wordless.png) |
| Decorative Illustration | ![Decorative Illustration: with text](./screenshots/kairo-design/decorative-illustration-with-text.png) | ![Decorative Illustration: wordless](./screenshots/kairo-design/decorative-illustration-wordless.png) |
| Color Field Composition | ![Color Field Composition: with text](./screenshots/kairo-design/diffuse-color-field-with-text.png) | ![Color Field Composition: wordless](./screenshots/kairo-design/diffuse-color-field-wordless.png) |
| Dry Crayon Illustration | ![Dry Crayon Illustration: with text](./screenshots/kairo-design/dry-crayon-illustration-with-text.png) | ![Dry Crayon Illustration: wordless](./screenshots/kairo-design/dry-crayon-illustration-wordless.png) |
| Interwoven Type and Image | ![Interwoven Type and Image: with text](./screenshots/kairo-design/editorial-design-with-text.png) | ![Interwoven Type and Image: wordless](./screenshots/kairo-design/editorial-design-wordless.png) |
| Narrative Photography | ![Narrative Photography: with text](./screenshots/kairo-design/editorial-photo-scene-with-text.png) | ![Narrative Photography: wordless](./screenshots/kairo-design/editorial-photo-scene-wordless.png) |
| Expressive Ink Drawing | ![Expressive Ink Drawing: with text](./screenshots/kairo-design/expressive-ink-line-with-text.png) | ![Expressive Ink Drawing: wordless](./screenshots/kairo-design/expressive-ink-line-wordless.png) |
| Geometric Flat Illustration | ![Geometric Flat Illustration: with text](./screenshots/kairo-design/geometric-flat-illustration-with-text.png) | ![Geometric Flat Illustration: wordless](./screenshots/kairo-design/geometric-flat-illustration-wordless.png) |
| Miniature Scenes | ![Miniature Scenes: with text](./screenshots/kairo-design/isometric-miniature-scene-with-text.png) | ![Miniature Scenes: wordless](./screenshots/kairo-design/isometric-miniature-scene-wordless.png) |
| Knitted Textile | ![Knitted Textile: with text](./screenshots/kairo-design/knitted-textile-with-text.png) | ![Knitted Textile: wordless](./screenshots/kairo-design/knitted-textile-wordless.png) |
| Layered Paper Relief | ![Layered Paper Relief: with text](./screenshots/kairo-design/layered-paper-relief-with-text.png) | ![Layered Paper Relief: wordless](./screenshots/kairo-design/layered-paper-relief-wordless.png) |
| Limited-Ink Overprint | ![Limited-Ink Overprint: with text](./screenshots/kairo-design/limited-ink-overprint-with-text.png) | ![Limited-Ink Overprint: wordless](./screenshots/kairo-design/limited-ink-overprint-wordless.png) |
| Modular Brick Models | ![Modular Brick Models: with text](./screenshots/kairo-design/modular-brick-scene-with-text.png) | ![Modular Brick Models: wordless](./screenshots/kairo-design/modular-brick-scene-wordless.png) |
| Engraved-Line Illustration | ![Engraved-Line Illustration: with text](./screenshots/kairo-design/monochrome-engraved-line-with-text.png) | ![Engraved-Line Illustration: wordless](./screenshots/kairo-design/monochrome-engraved-line-wordless.png) |
| Pixel Art | ![Pixel Art: with text](./screenshots/kairo-design/pixel-scene-with-text.png) | ![Pixel Art: wordless](./screenshots/kairo-design/pixel-scene-wordless.png) |
| Mid-Century Commercial Illustration | ![Mid-Century Commercial Illustration: with text](./screenshots/kairo-design/retro-commercial-illustration-with-text.png) | ![Mid-Century Commercial Illustration: wordless](./screenshots/kairo-design/retro-commercial-illustration-wordless.png) |
| Halftone Imagery | ![Halftone Imagery: with text](./screenshots/kairo-design/spot-ink-halftone-with-text.png) | ![Halftone Imagery: wordless](./screenshots/kairo-design/spot-ink-halftone-wordless.png) |
| Swiss International Graphic Design | ![Swiss International Graphic Design: with text](./screenshots/kairo-design/swiss-international-with-text.png) | ![Swiss International Graphic Design: wordless](./screenshots/kairo-design/swiss-international-wordless.png) |
| Torn Photo Collage | ![Torn Photo Collage: with text](./screenshots/kairo-design/torn-photo-collage-with-text.png) | ![Torn Photo Collage: wordless](./screenshots/kairo-design/torn-photo-collage-wordless.png) |

## Tools and environment

You need an AI agent that supports Skills and has access to an image generation or editing tool. This Skill does not include a model, generation credits, or a standalone image service. Generation capabilities and available aspect ratios depend on the host tool.

Python 3 is used for loading styles and validating deliveries. Image inspection and format export require Pillow. If you use the included typesetting script, supply fonts suitable for the text and your environment. Generated images still need visual review of the text, subject, style, and composition; scripts cannot establish aesthetic quality.

## Repository structure

```text
skills/kairo-design/     Complete installable Skill
  SKILL.md              Entry point and interaction rules
  routes/               Workflows for images with text and wordless images
  styles/               Separate workflow rules for 20 styles
  references/           Style index, platform presets, and delivery guidance
  scripts/              Loading, validation, and export tools
screenshots/            40 original example images
```

## License

Free for personal, non-commercial use. Commercial use, including commercial content, marketing, paid services, team business activities, and client projects, requires prior written permission. Contact the author through [GitHub Issues](https://github.com/byKairo/kairo-design/issues); do not post private business material publicly. See [LICENSE](./LICENSE) for the full terms in Chinese. This English summary does not replace or expand those terms.

Third-party brands, fonts, and materials receive no additional permissions under this repository's license. Brand-inspired examples do not imply official endorsement. See [third-party notices](./THIRD_PARTY_NOTICES.md) in Chinese.

## Credits

- Design and maintenance: [@byKairo](https://github.com/byKairo)
