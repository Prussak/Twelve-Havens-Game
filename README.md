# Twelve Heavens

> *"In a world of twelve sacred powers, you may carry the wisdom of two. Choose wisely. Change carefully. There is always a cost."*

A top-down exploration RPG inspired by the Chinese Zodiac, built in Python + Pygame. Travel across twelve sacred regions, absorb Zodiac Wisdoms from ancient temples, and make decisions that permanently shape the world around you.

<img width="1376" height="768" alt="Twelve Haven Art" src="https://github.com/user-attachments/assets/f006dce0-8ca5-4b2b-b404-175a438ef0d4" />

---

## Table of Contents

- [Demo](#demo)
- [Installation](#installation)
- [Controls](#controls)
- [Core Concept](#core-concept)
- [The Two-Wisdom Rule](#the-two-wisdom-rule)
- [The Zodiac System](#the-zodiac-system)
- [Synergies](#synergies)
- [The Ritual System](#the-ritual-system)
- [Combat](#combat)
- [World Design](#world-design)
- [Quest System](#quest-system)
- [Bosses](#bosses)
- [Progression & Replayability](#progression--replayability)
- [Art Style & Tone](#art-style--tone)
- [Roadmap](#roadmap)

---

## Demo

The current build is a playable vertical slice featuring:

- 10×10 tile map with grass, walls, cobblestone paths, a village, and a temple
- Player movement with smooth interpolation and idle animation
- Village Elder NPC with a 3-stage quest
- 2 enemies with HP bars and bump-attack combat
- Tiger Wisdom — doubles ATK, enables a ranged power strike, adds a visible aura
- HUD with HP bar, ATK stat, Wisdom slot, and flash message system
- Win / death screens with restart

```
python twelve_heavens_demo.py
```

![demo screenshot placeholder](docs/screenshot.png)
<img width="1376" height="768" alt="twelve havens gameplayscenario" src="https://github.com/user-attachments/assets/27f03928-ef0b-44e0-9025-da6492970986" />

---

## Installation

**Requirements:** Python 3.8+ and Pygame

```bash
# Clone the repository
git clone https://github.com/yourname/twelve-heavens.git
cd twelve-heavens

# Install dependency
pip install pygame

# Run the demo
python twelve_heavens_demo.py
```

---

## Controls

| Key | Action |
|-----|--------|
| Arrow keys | Move / bump-attack adjacent enemies |
| `E` | Interact with NPC or temple |
| `SPACE` | Activate Tiger Wisdom strike (once acquired) |
| `R` | Restart |
| `ESC` | Quit |

---

## Core Concept

Twelve Heavens is set in a mythologized ancient world divided into twelve sacred regions, each shaped by one of the Chinese Zodiac animals. The player is a **Wanderer** — a figure of unknown origin who can absorb the spiritual essence of Zodiac Temples.

The central emotional question is not *"how powerful can I become?"* but rather *"who do I want to be right now — and what am I willing to give up?"*

### Design Pillars

- **Constraint as creativity** — limiting players to two powers forces genuine decision-making rather than unlimited accumulation
- **World as consequence** — villages remember, enemies adapt, NPCs hold grudges or offer gratitude
- **Depth without complexity** — systems are layered but never opaque; a new player grasps the loop in minutes
- **Story through action** — narrative emerges from how you play, not just from cutscenes

---

## The Two-Wisdom Rule

Each temple grants a **Zodiac Wisdom** — a special power that changes how you interact with the world in and out of combat.

**You may only hold two Wisdoms at the same time.**

Wanting a third means abandoning one you already carry. This decision is never trivial.

```
Current Wisdoms:  [ Tiger ]  [ Rabbit ]
                       ↑
           To take Snake, you must release one.
```

Powers are not merely stat bonuses — they alter available combat actions, NPC dialogue trees, puzzle solutions, and environmental traversal.

---

## The Zodiac System

| Animal | Role | Ability |
|--------|------|---------|
| 🐭 Rat | Strategist · Shadow | Read enemy intent ahead of time. Unlock hidden routes. Steal items without combat. |
| 🐂 Ox | Juggernaut · Anchor | Massive damage absorption. Carry heavy objects. Cannot be stunned or knocked back. |
| 🐯 Tiger | Predator · Fury | Damage builds Fury stacks. At max Fury, enter a devastating burst state. Frightens weaker enemies. |
| 🐰 Rabbit | Phantom · Evader | Perfect dodge window resets cooldowns. Move freely during enemy turns. |
| 🐲 Dragon | Sovereign · Gambit | Catastrophic power — but each use costs a permanent fragment of max health. |
| 🐍 Snake | Controller · Venom | Long-duration poison and paralysis. Extract information from NPCs through coercion. |
| 🐴 Horse | Wanderer · Swift | Traverse regions at double speed. Escape any combat without penalty. Discover hidden shortcuts. |
| 🐑 Goat | Shepherd · Mender | Heal self and NPCs. Wounded enemies become pacified rather than slain. |
| 🐒 Monkey | Trickster · Chaos | Swap enemy positions. Clone yourself as a decoy. Interact with the environment mid-combat. |
| 🐓 Rooster | Duelist · Precise | Timed actions deal critical damage. Perfect blocks reflect 50% damage back. |
| 🐕 Dog | Guardian · Faithful | Protect companions from damage. Sense hidden traps. Gain a loyal NPC follower per region. |
| 🐷 Pig | Survivor · Abundant | Passive health regeneration. Consume items for temporary buffs. Impossible to starve or exhaust. |

Each Wisdom also carries a **passive world effect**. Carrying Tiger wisdom means timid NPCs react with fear. Carrying Goat wisdom means wounded travelers approach you, triggering hidden quests.

---

## Synergies

Holding two Wisdoms simultaneously can trigger a named **Synergy Effect** — an additional ability available only while both are held. These are discovered through experimentation.

| Pairing | Synergy | Effect |
|---------|---------|--------|
| Tiger + Rabbit | **Burning Wind** | Perfect dodges during Fury reset the timer and add a free strike |
| Rat + Snake | **Hollow Court** | Stolen items are auto-poisoned; poisoned enemies reveal secrets |
| Dragon + Pig | **Undying Flame** | Pig's regeneration offsets Dragon's health cost over time |
| Ox + Dog | **Iron Hearth** | NPC follower gains your full damage absorption |
| Monkey + Rooster | **Stage Play** | Position swaps create a free Rooster critical hit window |
| Goat + Horse | **Open Road** | Healed NPCs reveal shortcuts only Horse can use |
| Snake + Rabbit | **Glass Viper** | Dodging through an enemy applies poison; poison slows attack speed |
| Dragon + Rat | **Hidden Throne** | Dragon's aura is concealed until the moment of activation |

There are 66 possible pairings. Not all produce a named effect, but all create meaningfully distinct playstyles.

---

## The Ritual System

Replacing a Wisdom requires performing the **Rite of Exchange** at a temple altar. It is never instant and never free.

### Sequence

1. Declare which Wisdom you are surrendering and which you are receiving
2. A contemplation phase displays the departing power's history — enemies defeated, quests completed, synergies enabled
3. The surrendered Wisdom crystallizes into a **Shard** — a passive memory item that grants a small permanent bonus
4. A cost is applied based on how long the power was held
5. The new Wisdom enters a **Tempering Phase** — partially available until used three times in meaningful ways

### Ritual Costs

| Hold Duration | Cost |
|---------------|------|
| Short (1–2 regions) | Brief vulnerability window — reduced defense for one region |
| Medium (3–5 regions) | Loss of accumulated Resonance energy |
| Long (6+ regions) | A permanent **Scar** — a minor persistent debuff visible on your character |

> Scars are not purely negative. Some quests, NPCs, and secret areas respond uniquely to specific Scars, treating them as marks of experience. A player bearing the Scar of Tiger speaks a language some war-torn regions understand.

### The Wanderer's Codex

Every ritual, every Wisdom held, and every Shard collected is recorded in the **Wanderer's Codex** — an in-world journal that becomes a unique record of that playthrough. In New Game+, the Codex from a previous run appears as a ghost record, silently narrating the choices of who you used to be.

---

## Combat

Combat is **turn-based with a momentum layer** — a hybrid that feels fluid rather than static.

- Each turn the player has **3 Action Points**: basic actions cost 1, Zodiac power activations cost 2
- The **momentum bar** fills as actions chain without taking damage; high momentum unlocks bonus moves
- Each Wisdom contributes a **Wisdom Wheel** of 3–4 abilities: one active, one reactive, one passive
- Enemies telegraph intent via visual symbols (Rat Wisdom lets you see two moves ahead)
- **Resonance** — the special energy resource — is built faster by actions that align with your current Wisdoms

### Non-Combat Resolutions

Many encounters can be resolved without fighting — bandits can be bribed (Pig), frightened (Tiger), tricked (Monkey), or simply bypassed (Horse). Non-lethal approaches are tracked and rewarded in specific quests.

---

## World Design

The world map is divided into twelve regions arranged in a wheel — six inner, six outer — mirroring the cyclical nature of the Zodiac itself.

### Each Region Contains

- A central **village** with unique culture and quests
- A **temple** set apart, guarded by a Corrupted Guardian
- Wilderness paths with enemies, puzzles, and side content
- At least one **secret location** accessible only with a specific Wisdom

### The Celestial Road

A recurring landmark in each region is a segment of the **Celestial Road** — a partially ruined ancient path. When all twelve segments are discovered and restored, the final region opens: the **Thirteenth Heaven**, where the true ending awaits.

---

## Quest System

Quests are short, layered, and consequence-laden. There are no quest markers — NPCs describe situations and the player navigates using observation and Wisdom-specific perception.

| Tier | Description |
|------|-------------|
| **Temple Quests** | One per region. Multi-stage, culminating in the guardian encounter. Choices permanently alter that region. |
| **Village Quests** | 2–3 per region. Relationship-focused. Completing them unlocks alternative temple paths. |
| **Wisdom Quests** | Appear only when holding a specific Zodiac Wisdom. Unique to your current identity. |
| **Echo Quests** | New Game+ exclusive. Ghosts of your previous character's choices appear as quests. |

### The Ripple System

Major quest decisions become **Ripples** — up to 8 active at once. Later regions surface these: an NPC you saved has traveled ahead and offers information; a village you abandoned is now hostile. The world has been paying attention.

---

## Bosses

Each temple is guarded by a **Corrupted Guardian** — a being whose Zodiac Wisdom has been twisted to excess.

| Guardian | Corruption | Challenge |
|----------|-----------|-----------|
| The Drowned Ox | Sorrow | Cannot be staggered; only rhythm disruption defeats it |
| The Thousand-Coil Serpent | Paranoia | Fills the arena with fog; an information vs. misdirection chess match |
| The Hollow Dragon | Pride | Grows stronger from damage taken; must be starved, not fought |
| The Shattered Rooster | Obsession | A perfectly looping attack pattern that subtly shifts each cycle |
| The Pale Horse | Flight | Never stays still; uniquely resolvable without combat via Goat or Snake |
| The Twin-Faced Monkey | Chaos | Clones itself constantly; the only boss the player can make fight itself |

---

## Progression & Replayability

Growth is **qualitative, not quantitative**. Holding a Wisdom longer deepens Resonance — unlocking more powerful versions of its abilities, but only while it is held.

Permanent progression comes through:
- **Shards** — remnants of surrendered Wisdoms, carried across runs
- **Celestial Road** — segments unlock passive world knowledge that persists into New Game+
- **Scars** — each Scar opens unique quest branches unavailable to unscarred Wanderers

### Replayability Systems

- **Shard Builds** — Shards from previous runs create new starting loadouts in subsequent playthroughs
- **Divergent Paths** — Many quest resolutions are locked behind specific Wisdoms; full completion requires multiple runs
- **Codex Challenges** — Hidden conditions revealed post-game: finish holding Dragon the entire time; never use the same Wisdom twice; reach the end with six Scars
- **Echo Mode (NG+)** — Ghost records of your previous run overlay the world; NPCs reference your old choices

---

## Art Style & Tone

The visual direction draws from two traditions:

- **Chinese ink painting (水墨画)** for environments — loose, atmospheric, with ink washes that suggest more than they define
- **Ukiyo-e woodblock prints** for characters and bosses — bold, flat, graphic

Each Zodiac Wisdom has its own visual signature: active powers release that region's color into the air as temporary calligraphy strokes. The color palette shifts by region — the Rat region is midnight blue and silver; the Tiger region is volcanic amber and deep shadow; the Goat region is soft spring green and white mist.

The tone is **contemplative and mythic** — the feeling of a fable that knows it is teaching you something important but trusts you to find it yourself.

The soundtrack uses erhu, guqin, shakuhachi, and sparse percussion. Each Wisdom subtly modifies the ambient music — Tiger adds low rhythmic drums; Goat adds a soft vocal hum.

---

## Roadmap

- [x] Tile map renderer
- [x] Player movement + smooth interpolation
- [x] Bump-attack combat
- [x] NPC with 3-stage quest
- [x] Tiger Wisdom (ATK buff + power strike)
- [x] HUD (HP bar, Wisdom slot, flash messages)
- [ ] All 12 Zodiac Wisdoms
- [ ] Two-Wisdom slot system + Ritual swap UI
- [ ] Synergy detection and Synergy Effects
- [ ] Turn-based combat engine with Action Points
- [ ] Enemy intent system
- [ ] Full 12-region world map
- [ ] Temple Guardian boss fights
- [ ] Quest Ripple system
- [ ] Wanderer's Codex
- [ ] New Game+ / Echo Mode
- [ ] Sound design

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<<<<<<< HEAD
*Twelve Heavens is a solo project in active development. Contributions, feedback, and ideas are welcome.*
=======
*Twelve Heavens is a solo project in active development. 
>>>>>>> b1f1de2f02a188cf155f638c02b7df901bf17b3f
