---
name: ios-game-ui-design
description: Designs the interface of an iOS game - HUD, menus, pause and settings screens, on-screen touch-control layout, how much information the player gets and in what form, text sizes, safe areas, aspect ratios, Liquid Glass versus custom game UI, and accessibility of the interface. Use when designing or fixing a HUD, menu, control layout, or any screen the player reads or taps.
license: MIT
---

# Game UI design

Game UI is how the player interacts with the game and how the game answers: menus, HUD, prompts and controls. It is part of the mechanics: deciding how much the player is told, and how, shapes what they know about the world and how the game feels. A game UI does not have to be effortless; players accept a richer interface when what it gives them is worth it. It must always be clear.

## Steps

1. List in the **UI** section of `GAME_DESIGN.md` every piece of information the player needs, when they need it, and where it lives:
   - **diegetic** (inside the world: a character's glowing health bar on their back),
   - **spatial** (in world space but outside the fiction: an outline through walls),
   - **screen** (classic HUD),
   - **meta** (screen effects: a red vignette when hurt).
   Clarity beats immersion: move information to the screen if players miss it in the world.
2. Lay out the HUD in groups anchored to screen edges and corners, each at a fixed size and offset, inside the safe area. Never scale one 16:9 layout uniformly.
3. Lay out touch controls (rules below) and implement them with the `ios-game-controller` skill.
4. Build menus, pause and settings.
5. Check every screen at 4:3 and about 1.43:1 (iPads), 16:9 (iPhone SE) and 19.5:9 (current iPhones), in each supported orientation, at the largest text size, with VoiceOver on and with Reduce Motion on. Done when nothing is clipped, overlapping, unreadable or unreachable in any of these.

## Sizes and layout

- Text: 17 pt default, never below 11 pt; thin or decorative fonts need larger sizes. Let text grow to at least 200% (Dynamic Type or an in-game text-size setting), and scroll rather than shrink when it overflows.
- Tap targets: 44 × 44 pt for frequent controls, at least 28 × 28 pt for minor ones.
- The game world fills the whole screen; safe areas apply to UI only. Keep HUD and controls clear of rounded corners, the Dynamic Island and the Home indicator.
- If the camera crops important content on some aspect ratio, adjust the camera before letterboxing.
- Contrast at least 4.5:1 for text up to 17 pt, 3:1 for larger or bold text. Never carry meaning with color alone.

## Touch controls

- Prefer tapping or dragging world objects directly over on-screen buttons.
- Movement on the left with a floating stick that appears where the thumb lands; camera by dragging on the right; frequent actions under the right thumb; rare ones (menu, map) along the top.
- Keep the screen center clear so the character stays visible.
- Icons show the action (a sword, an arrow up), not controller letters, and change with context. Hide controls whose action is unavailable.
- Fold multi-button combinations into one control: tap versus hold, drag to aim and release to fire, stick tilt for walk versus run.
- Every press shows a pressed state that is visible around the finger, and plays a sound or haptic.
- Hide virtual controls while a menu is open; menus respond to touch directly.

## Menus, pause and settings

- The game is playable within seconds of first launch. Defaults come from the device (controllers connected, accessibility settings), not from questions.
- Pause automatically when the app leaves the foreground or the Game Center overlay opens; resume exactly where the player was.
- Few settings, for things players change rarely: music and effects volume, haptics on/off, text size, control layout, motion intensity. Do not duplicate system accessibility settings.
- Show the Game Center access point only on menus (`ios-game-gamekit`).
- With a controller connected, A confirms, B goes back, Menu pauses; show the connected controller's own button symbols.

## Liquid Glass or custom

- In-play HUD and touch controls are part of the game's content: draw them in the game's own art style in the renderer, without glass.
- The out-of-play shell (settings, store, account, system sheets) may use standard SwiftUI components, which render as Liquid Glass when built with Xcode 27. Do not stack glass on glass, and test glass over bright, busy game frames.
- A fully custom themed menu is fine if it meets the sizes above, works by touch and is labeled for VoiceOver.
- SF Symbols suit interface glyphs and button icons; they are not the game's art style and may not be used in the app icon.

## Related skills

Implementing controls: `ios-game-controller`. Visual style of HUD art: `ios-game-art-direction`. Onboarding and accessibility of play: `ios-game-ux-design`. HUD in code: `ios-game-spritekit` (camera children) or `ios-game-realitykit` (SwiftUI overlay).
