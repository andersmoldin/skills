---
name: ios-game-audio-design
description: Designs everything an iOS game sounds like - sound effects, music, voice, title and menu themes, jingles, adaptive music, the mix, behavior with the Silent switch and the player's own music, and legal sourcing of audio. Use when deciding what sounds a game needs, how music reacts to play, or why the game sounds flat, tiring or confusing.
license: MIT
---

# Game audio design

Audio design creates or selects every sound in the game: music, sound effects and voice, including the title theme and the jingles in menus. Implement it with the `ios-game-audio-engine` skill.

## Steps

1. Write the **Audio** section of `GAME_DESIGN.md`: the musical style in one line with two reference moods (not specific tracks to copy), whether the player's own music should keep playing (default yes, see below), and the mix buses (music, effects, interface, voice).
2. Make a sound list: one row per player action and game event, with its weight (light, medium, heavy), whether it exists in the game world (diegetic) or belongs to the interface or score, and the visual and haptic that accompany it. Done when every input the player can make and every state change they must notice has a row.
3. Source or create each sound (below) and record its source, author and license in `CREDITS.md`.
4. Plan the music: which tracks play where, and how they react to play (adaptive music, below).
5. Listen on the iPhone speaker, on earbuds and muted. Done when the game is fully playable muted and nothing is harsh or buried on the speaker.

## Principles

- **Playable muted.** Many players have sound off. Every essential cue also has a visual or haptic form.
- **Every action answers.** Each meaningful action has a sound whose size matches its weight; a heavy hit sounds heavier than a light one.
- **Vary repetition.** Randomize pitch slightly (about ±1 semitone) and volume on sounds that repeat often, and keep two to four variants of the most frequent ones.
- **The player's music comes first.** Default to the ambient session behavior: the game mixes with whatever the player is listening to and goes quiet with the Silent switch, and game music steps aside while other audio plays. Replace the player's music only when the soundtrack is central to the experience, and decide that explicitly in the doc.
- **Respect the system.** Never change the system volume; balance levels in your own mix and offer separate music and effects sliders.
- **Clear mix.** Interface and critical warnings sit on top; music sits under effects. Reduce music briefly (ducking) for important voice lines and big moments.
- **Consistent haptics.** Each haptic pattern has one meaning, matches the strength of its sound and animation, and can be switched off.
- **Handle interruptions gracefully.** Calls and alarms pause the game; play resumes with sound restored.

## Adaptive music

- **Vertical layering:** one track split into stems (drums, bass, melody) that fade in and out with intensity. Reacts instantly without cutting the music; the default choice.
- **Horizontal resequencing:** music made of segments, with the next one chosen by game state and switched on a bar or beat boundary. Use when the structure must change (exploration to combat to victory).
- **Stingers:** short musical phrases for events (pickup, level complete), started on the next beat so they sit in the music.

## Sourcing

- Retro and synthesized effects can be generated with sfxr-style tools (jsfxr) and edited.
- Licenses follow the same rules as art (`ios-game-art-direction`): CC0 freely, CC-BY with credit in the game, CC-BY-SA and GPL only with the author's written permission, non-commercial licenses never on the App Store.
- Never copy recognizable music or sounds from other games.
- Loudness target for handheld play: about −18 LUFS integrated, so the game is neither quieter nor louder than other apps.

## Related skills

Implementation: `ios-game-audio-engine`. Haptics: `ios-game-controller`. Feel of feedback timing: `ios-game-ux-design`.
