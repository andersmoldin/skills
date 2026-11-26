---
name: ios-game-art-direction
description: Directs the look of an iOS game so it reads as a finished game - visual style, palette, shape language, readability, sourcing or generating 2D and 3D assets with clean licenses, and juice (particles, screen shake, easing, hit-stop, flashes, lighting). Use before making any game asset, when a game looks like placeholder art or programmer graphics, or when actions lack impact.
license: MIT
---

# Game art direction

A game looks finished when every asset follows one style and every action answers with visible feedback. Agent-built games most often fail on both: mixed or primitive graphics, and silent, linear motion. This skill sets the style before assets exist and adds juice once the core loop works.

## Steps

1. Pick a style the project can produce consistently (table below) and write the **Art direction** section of `GAME_DESIGN.md` as a style guide:
   - palette: 5 to 8 colors with roles (background, midground, player, interactable, danger, interface accent), stored as named colors in the asset catalog;
   - value range: backgrounds low-contrast and darker or lighter than the gameplay layer;
   - shape language: round for friendly, angular for dangerous, and an outline rule (all outlined or none);
   - scale: pixel size or texture density, and the camera's view size in world units;
   - light direction and the font (bundled with its license).
   Done when an asset can be checked against the guide with yes or no answers.
2. Source or generate assets following [references/assets.md](references/assets.md). Record source, author and license of every file in `CREDITS.md`.
3. Check readability (below) on screenshots: `xcrun simctl io booted screenshot shot.png`, then look at the image in color and in grayscale.
4. After the core loop feels right (`ios-game-ux-design`), add juice with [references/juice.md](references/juice.md).
5. Compare screenshots against the finished-look checklist (below). Done when every item passes.

## Choose a producible style

| Style | Produced by | Fits |
|---|---|---|
| One CC0 asset family (for example a single Kenney pack series) | Download | Fastest consistent result, 2D or 3D |
| Flat vector shapes with a strict palette | SVG written as text, imported into the asset catalog as vector images | Puzzle, casual, minimalist |
| Pixel art at a fixed low resolution | Small sprites drawn as data or sourced, `.nearest` filtering | Retro action, platformers |
| Procedural textures and shader backgrounds | Core Graphics or shaders at load time | Abstract, space, ambient games |
| Low-poly 3D with flat colors and good lighting | Primitive or CC0 meshes, `PhysicallyBasedMaterial`, image-based light | 3D games without an art team |

Never mix asset families with different line weights, perspectives or palettes in one game; recolor to the palette instead.

## Readability

- Every gameplay-relevant thing has a distinct silhouette: fill the screenshot's sprites with solid black and check that each is still recognizable.
- Gameplay layer: higher contrast and saturation than the background. Background: calmer, less detail.
- Reserve the accent colors: interactables and danger use colors nothing else uses.
- Check in grayscale (values must still separate) and with a color-blindness simulation; pair color with shape or icon.
- Shade from warm to cool instead of toward black; a rim highlight separates characters from the background.
- Direct the eye with light: brightest and most saturated where the player should look, darker toward the edges.

## Finished-look checklist

- No `SKShapeNode` or untextured primitives left as final art; no system default fonts in the game world.
- Backgrounds have depth: at least two layers, with parallax in 2D or atmospheric fog and lighting in 3D.
- Characters and pickups never stand perfectly still: idle bob, breathing scale or blinking.
- Characters have a ground shadow (a soft ellipse in 2D, `GroundingShadowComponent` or a shadow-casting light in 3D).
- Every motion is eased; nothing moves linearly except projectiles and conveyor belts.
- Every player action and every hit produces at least two kinds of feedback (motion, particles, flash, sound, haptic).
- The palette in the style guide is the only palette on screen.

## Related skills

Implementing effects: `ios-game-spritekit` (emitters, shaders, lights) or `ios-game-realitykit` (particles, materials, lights, post-processing). Feel and timing: `ios-game-ux-design`. HUD style: `ios-game-ui-design`. Mood of places: `ios-game-level-design`.
