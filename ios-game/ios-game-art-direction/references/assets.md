# Sourcing and generating game assets

Read this before adding any image, sprite, model, texture, font or environment map to a game.

## Licenses

- Apple requires that the developer holds the rights to all content in the app. Every asset gets a line in `CREDITS.md`: file, source URL, author, license.
- **CC0** (public domain dedication): use freely, commercial use allowed, no attribution required. Prefer it.
  - Kenney (kenney.nl): large, consistent 2D and 3D packs, all CC0.
  - Poly Haven (polyhaven.com): CC0 HDRIs, textures and models. The HDRIs make excellent image-based lighting for RealityKit.
  - Quaternius (quaternius.com): CC0 low-poly 3D models.
- **CC-BY:** allowed with credit in the game. **CC-BY-SA, GPL, LGPL:** may conflict with App Store terms; avoid them or get the author's written permission. **Non-commercial licenses:** not usable in a game on the App Store.
- Fonts: SIL Open Font License fonts (for example from Google Fonts) may be bundled; include the license file and list the font in `UIAppFonts`.
- Never imitate another game's characters, logos or distinctive art.

## Generating 2D assets in code

- **Vector art as SVG:** write SVG files by hand (simple shapes, palette colors, consistent stroke width) and add them to the asset catalog; SpriteKit loads them by name. A sprite texture is a bitmap made once, so set each SVG's canvas to the largest size it appears on screen (in points); the catalog rasterizes it for @2x and @3x. Never scale a sprite above that size.
- **Rendered textures:** draw shapes, gradients and noise with `UIGraphicsImageRenderer` or SwiftUI `ImageRenderer` at load time, then wrap the image in `SKTexture(image:)`. Render once and reuse; never per frame.
- **Pixel art:** describe each sprite as a small grid of palette indices in data and rasterize it to a texture; draw at an integer scale with `.nearest` filtering.
- **Shader backgrounds:** animated gradients, stars or water as a fragment shader on one full-screen sprite (`ios-game-spritekit` references) or as a Shader Graph material.
- **Particles** replace much hand-drawn effect art: sparks, dust, smoke and trails are emitter settings plus one small soft-dot texture.
- Bake text-free assets only; all text is rendered at runtime so it can be localized.

## 3D assets

- Start from primitives (`MeshResource.generateBox`, spheres, cylinders with corner radius) or CC0 models; one consistent poly density and palette.
- Good lighting makes simple geometry convincing: one directional light with shadows, an HDRI as image-based light, and slightly rough PBR materials. Flat, unlit primitives on a black background look unfinished.
- Export from Blender to USDZ (see the `ios-game-realitykit` skill for units, axes and texture budgets).

## Generated images

- Apple's Image Playground is a feature for players, not an art pipeline: its output varies per run and per user, it needs Apple Intelligence hardware, and the programmatic `ImageCreator` API is deprecated in iOS 27. Do not use it for shipping art.
- External image generators: check the tool's terms for commercial rights, keep the prompts and outputs, regenerate in one consistent style, and clean up the results to match the palette. Never prompt for other games' characters or styles by name.

## App icon

Build the app icon in Icon Composer as layered artwork (1024 × 1024 canvas, vector layers preferred, no text) so it renders correctly in the iOS 26 light, dark, clear and tinted appearances. SF Symbols may not be used in app icons.
