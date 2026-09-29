# AI RPG Tools Landscape: A Survey of Interactive Fiction & Game Master Engines

**Date**: September 2026  
**Focus**: Tools for building choose-your-own-adventure and D&D-style interactive games, with emphasis on architecture, strengths, weaknesses, and the tension between free-form narrative and structured rules.

---

## Table of Contents

1. [Non-AI Branching Narrative Tools](#non-ai-branching-narrative-tools)
2. [AI-Driven Interactive Fiction Platforms](#ai-driven-interactive-fiction-platforms)
3. [Community-Oriented Roleplay Platforms](#community-oriented-roleplay-platforms)
4. [Open-Source AI Dungeon Master Projects](#open-source-ai-dungeon-master-projects)
5. [Supporting Infrastructure & Engines](#supporting-infrastructure--engines)
6. [Technical Approaches to Bounded AI Narration](#technical-approaches-to-bounded-ai-narration)
7. [Design Tensions & Failure Modes](#design-tensions--failure-modes)
8. [Key Architectural Patterns](#key-architectural-patterns)

---

## Non-AI Branching Narrative Tools

These tools solve the problem of managing complex branching narratives WITHOUT AI generation. They excel at state management, variable tracking, and enabling writers to author rich, choice-driven stories.

### Ink (by Inkle Studios)

**What it is**: An open-source, script-based narrative language created by Inkle (makers of *80 Days*). Ink is not a flowchart tool—it's entirely script-driven, designed for writers to quickly author heavily branching narrative that flows naturally from beginning to end.

**Architecture**:
- **Core language**: Markup-style syntax where text comes first and logic is embedded inline
- **State management**: Variables (prefixed with `$`) store numbers, strings, or booleans. The Dialogue Presenter's Variable Storage component handles persistence
- **Flow control**: Nodes, Lines, Options, and Jumps structure dialogue. Diverts (branching) are seamlessly woven into text
- **Advanced features**: Parallel, shared-state story flows allow switching between simultaneous conversations (e.g., NPCs) while enabling one conversation to affect another
- **Serialization**: Stories serialize to JSON via Story.ToJson() for save/load functionality

**Editor**: **Inky** - an IDE that allows play-as-you-write, with error detection, fast-forward replay, and hyperlinked divert navigation.

**Strengths**:
- Excellent for complex state tracking and large narrative projects
- Clean separation of constants, state variables, and operations
- Seamless integration with Unity and Unreal Engine
- Mature ecosystem with extensive documentation

**Weaknesses**:
- Steeper learning curve than visual tools (requires understanding the scripting language)
- Flowchart lovers must adjust to text-first approach
- Can be overkill for simple branching stories

**Key insight**: Ink proves that text-first, code-like approaches scale well for managing narrative state without sacrificing writerly expressiveness.

---

### Yarn Spinner

**What it is**: A dialogue scripting language designed for game developers, with seamless integration into game engines (Unity, Godot, Unreal, Bevy). Yarn Spinner treats dialogue as first-class narrative content, separate from but coordinated with game logic.

**Architecture**:
- **Core language**: Simple, human-readable scripting language designed for writers without programming experience
- **Variables**: Stored in a Variable Storage component, supporting numbers, strings, and booleans
- **State management**: The Dialogue Runner bridges written Yarn scripts to game components. Variable values persist across sessions via the Variable Storage system
- **Script structure**: Nodes, Lines, Options, Jumps, Detours, and Flow Control (conditions, loops)
- **Integration**: Dialogue Runner component loads, runs, and manages Yarn Projects, delivering content to game UI and systems

**Strengths**:
- Approachable syntax for non-programmers
- Strong integration with popular game engines
- Good documentation and growing community
- Lightweight and performant

**Weaknesses**:
- Less powerful for very complex state management than Ink
- Smaller ecosystem than Ink
- Variable naming convention (`$`) can feel limiting

**Key insight**: Yarn Spinner demonstrates that a simpler scripting language can be effective when designed with writers (not programmers) as the primary user.

---

### Twine

**What it is**: An open-source, browser-based tool for authoring interactive, nonlinear stories and hypertext fiction. Twine compiles to standalone HTML, playable in any web browser.

**Architecture**:
- **Editor model**: Node-based visual editor where passages (scenes) are boxes connected via hyperlinks
- **Story formats**: Pluggable engines (Harlowe, SugarCube, etc.) that handle rendering, state management, and logic
- **State management**: Variables and conditional logic supported via story format macros
- **Integration**: Outputs plain HTML; no engine dependencies
- **Flexibility**: SugarCube allows JavaScript macros, CSS styling, and complex programming; Harlowe avoids explicit code with markup-based scripting

**Strengths**:
- Lowest barrier to entry; no programming required for simple stories
- Visual editor makes structure immediately apparent
- Modular story format system enables flexibility without forking Twine itself
- Perfect for prototyping, classroom projects, and fast experiments
- Active community with plugins and extensions

**Weaknesses**:
- Visual clutter in the editor for large branching graphs (can become hard to navigate)
- Less refined state management than Ink for complex projects
- Story formats vary in power and maturity
- HTML output means less integration with custom engines

**Key insight**: Twine proves that visual authoring can be extremely accessible, but visual graphs have scalability limits for dense branching.

---

### ChoiceScript (Choice of Games LLC)

**What it is**: A scripting language specifically for writing stat-based interactive novels. Choice of Games LLC publishes interactive fiction commercially and licenses ChoiceScript to authors, with a 75/25 revenue split.

**Architecture**:
- **Language**: Simple programming language focused on storytelling, not technical programming
- **Variables**: Central to ChoiceScript design; stat-tracking enables complex branching based on accumulated character attributes
- **State management**: *creation, *set, *if, *else, *goto for branching logic
- **Publishing**: Choice of Games provides hosting, marketing, and App Store distribution

**Strengths**:
- Explicit support for stats-driven narrative (perfect for RPG-like progression)
- Proven commercial model with revenue sharing
- Simplicity makes it accessible to writers
- Built for text-heavy, stat-focused games (matching the Choice of Games library)

**Weaknesses**:
- Less flexible than Ink or Yarn Spinner for advanced features
- Designed narrowly for stat-based interactive fiction, not dialogue-heavy games
- Community smaller than Twine or Ink

**Key insight**: ChoiceScript shows that designing explicitly for a specific narrative pattern (stat-driven stories) can result in elegant, focused tooling.

---

### NarrativeFlow

**What it is**: A modern, visual branching dialogue tool for game developers. Designed to solve the "branching narrative nightmare" by providing visual node-and-link editing without requiring code.

**Architecture**:
- **Visual node editor**: Dialogue nodes, choice nodes, conditional branches, variable operations
- **Variable system**: Tracks player decisions and state without scripting
- **Export**: Multi-engine support (Unity, Unreal, Godot) via standardized exports
- **Features**: Search and filtering, localization, version control, error checking

**Strengths**:
- Modern UI, designed for game developers not writers
- Visual + logic hybrid (variables and conditions without code)
- Strong export pipeline to game engines
- Scalable for large dialogue graphs with built-in search/filter

**Weaknesses**:
- Younger project than Ink or Twine; smaller community
- Less mature ecosystem compared to established tools
- May be overkill for simple projects

**Key insight**: NarrativeFlow represents the evolution of branching dialogue tools toward game-engine-first design, prioritizing integration over pure authorship experience.

---

## AI-Driven Interactive Fiction Platforms

These platforms generate narrative dynamically using LLMs, enabling open-ended storytelling while attempting to manage the tension between free-form creativity and narrative coherence.

### NovelAI

**What it is**: A subscription-based, cloud-hosted platform for long-form narrative fiction and interactive storytelling. Positioned as a successor to AI Dungeon with stronger narrative fidelity.

**Architecture**:
- **Backend**: Custom fine-tuned models (not off-the-shelf GPT)
- **Features**: Lorebook system for world-building and character tracking, Custom AI modules for genre-specific writing styles, Image generation integration
- **Privacy**: End-to-end encryption of stories; no prompt logging

**Narrative strengths**:
- Lorebook enables persistent world state and character knowledge
- Genre-specific modules produce more coherent narratives within their domain
- Encryption and privacy-first approach appeals to authors

**Limitations**:
- Still suffers from context window limitations in long campaigns
- Free-form generation can drift off-track after extended play
- Subscription required for full functionality

**Best for**: Long-form fiction writing and character exploration, rather than rules-bound RPGs.

**Key insight**: NovelAI's Lorebook demonstrates that persistent external knowledge (structured world state) significantly improves narrative coherence compared to context-window-only approaches.

---

### KoboldAI

**What it is**: An open-source, browser-based front-end for AI-assisted writing with multiple inference backends (local models, cloud APIs). Includes Adventure Mode for text adventure RPG gameplay.

**Architecture**:
- **Backend flexibility**: Supports any OpenAI-compatible LLM or local Ollama model
- **State management**: Python Flask backend with koboldai_vars class as single source of truth; __setattr__ interception broadcasts changes to connected clients via SocketIO
- **Story management**: KoboldStoryRegister manages story actions with undo/redo and branching support
- **Modes**: Story (novel), Adventure (text adventure), Chat (dialogue), Instruct (ChatGPT-style tasks)
- **Extensibility**: Model backends implement common InferenceModel interface; discovered and loaded at startup

**Strengths**:
- Completely free and open-source with no subscription
- Adventure Mode provides RPG-like gameplay
- Local execution option (privacy-focused)
- Supports Stable Diffusion integration for character art generation
- Active community with many forks and variants

**Weaknesses**:
- Adventure Mode state management remains problematic (drifting narratives, context window issues)
- Setup complexity higher than cloud platforms
- Requires understanding of different inference backends
- Still subject to all the narrative drift problems of free-form LLM generation

**Technical insight**: KoboldAI's SocketIO-based state broadcasting shows how to synchronize game state across multiple clients in real-time, but doesn't solve the core problem of keeping narrative coherent over long sessions.

**Best for**: Writers exploring local LLM inference, developers building custom AI writing tools, RPG enthusiasts building custom Adventures.

---

### DreamGen & SpicyChat

**What it is**: Commercial, cloud-hosted platforms for uncensored long-form roleplay and interactive fiction with fine-tuned models.

**DreamGen specifics**:
- **Turn-based roleplay**: One-on-one character interaction
- **Story editor**: Collaborative long-fiction writing mode
- **Multi-character scenes**: Support for 3-4 distinct characters in same scene with separate voices and motivations
- **World-building**: Rich character, location, lore, and artifact definitions

**SpicyChat specifics**:
- **Uncensored dialogue**: Direct entry into explicit content without euphemism
- **Character library**: Browse and chat with pre-made characters
- **No explicit content restrictions**: Policy allows fantasy/roleplay content that mainstream services block

**Strengths**:
- Designed explicitly for roleplay, not general fiction
- Multiple characters per scene (DreamGen unique feature)
- Privacy-respecting (no conversation logging)

**Weaknesses**:
- Subscription-based business model
- Still vulnerable to context window limitations in long campaigns
- Less integrated with game mechanics or rules engines than other platforms
- Narrative drift remains unsolved

**Best for**: Uncensored roleplay, collaborative storytelling, character interaction exploration.

---

## Community-Oriented Roleplay Platforms

These platforms prioritize user control, customization, and freedom over content guardrails. They sit at the intersection of AI infrastructure and narrative.

### SillyTavern

**What it is**: Free, open-source, locally-installed client for AI roleplay. A "power tool" interface that does NOT include an AI model—users connect their own.

**Philosophy**:
- **User control**: Total control over model selection, inference parameters, character definitions
- **Privacy**: Everything runs locally by default; no cloud dependency option
- **Customization**: Extensive character card support, lorebook integration, advanced prompt engineering

**Architecture**:
- **Frontend**: React-based UI treating chat like an IDE for writers
- **Model-agnostic**: Works with any OpenAI-compatible API or local Ollama
- **Character system**: Complex character definitions with detailed personality, examples, and behavior vectors
- **Lorebook**: Retrieval-augmented generation of context; supports tags and dynamic insertion

**Strengths**:
- Completely free and open-source
- Extreme customization and control
- Strong community with active development
- Powerful character definition and world-building
- Local-first architecture for privacy

**Weaknesses**:
- Steeper learning curve than hosted services
- Requires understanding of LLM inference, parameters, and character engineering
- Still subject to narrative drift and context window limitations
- No built-in rules engine or game mechanics system

**Best for**: Experienced users, developers, writers who want total control; roleplay enthusiasts who don't want guardrails or content restrictions.

**Key insight**: SillyTavern's popularity demonstrates that users value control and customization over convenience, and that the "IDE for writers" metaphor resonates strongly with the roleplay community.

---

### Janitor AI

**What it is**: All-in-one, cloud-hosted platform combining character directory, chat interface, and proprietary LLM backend (JanitorLLM/JLLM).

**Strengths**:
- Easy entry point; no setup required
- Character discovery through directory
- Uncensored roleplay allowed (within legal bounds)
- Great characters and active user community

**Weaknesses**:
- Less customization than SillyTavern
- Proprietary backend limits model flexibility
- Still vulnerable to narrative drift in long campaigns
- Less suitable for game mechanics integration

**Best for**: Casual roleplay enthusiasts, social discovery of characters and stories.

---

### Character.AI (Historical Note)

**What it was**: Early pioneer in conversational AI for roleplay; focused on character consistency and dialogue quality.

**Why it fell short**:
- Heavy safety guardrails that destroyed immersion for many users
- Memory resets after dozens of messages, breaking narrative continuity
- Restrictive content policies

**Legacy**: Character.AI demonstrated both the appeal of character-driven AI interaction AND the user backlash against overly restrictive content moderation. Its limitations directly motivated the creation of less-restricted alternatives.

---

## Open-Source AI Dungeon Master Projects

These projects attempt to build full RPG experiences with automated game masters. They represent active research into combining free-form LLM narration with structured game mechanics.

### NarrativeEngine (Multiple Variants: -P, -Argent, etc.)

**What it is**: Self-hosted TTRPG engine for extended, multi-session campaigns with persistent memory, living NPCs, and any OpenAI-compatible LLM.

**Core Architecture**:
- **Problem it solves**: "Long campaigns usually collapse when the LLM runs out of context. This engine keeps campaigns coherent across sessions."
- **Memory strategy**: Separates persistent character/location data from dynamic world state
  - Character and location chunks seed "ledgers" (retrieval-augmented context for people/places)
  - Factions, power systems, economy, and events stay in RAG (~1200 tokens/turn)
  - This dual approach avoids polluting the context window with static data

**NPC System**:
- NPCs are simulated with psychology, goals, and relationships
- Values shape how NPCs speak, react, and make decisions
- NPC characteristics drift naturally as they experience events
- Allows complex NPC intrigues and relationships that evolve over time

**State Management**:
- Sessions are stored persistently
- Campaign state is versioned
- Supports rollback and multiple parallel story branches

**Strengths**:
- Explicitly addresses the context window problem (the #1 killer of long AI campaigns)
- Smart memory architecture separates persistent from ephemeral state
- NPC systems add depth beyond simple narration
- Fully open-source and self-hosted

**Weaknesses**:
- Requires LLM access (API key or local model)
- Setup complexity moderate-to-high
- Still relies on unstructured LLM generation; narrative can still drift without careful prompting
- Limited enforcement of game rules or mechanics

**Best for**: Campaign-focused GMs who want persistent NPCs, world state, and multi-session memory without cloud dependency.

**Key architectural insight**: The two-tier memory system (ledgers for static knowledge, RAG for dynamic events) is a practical pattern for managing limited context windows in long campaigns.

---

### GameMasterAI

**What it is**: Web-based AI DM system built by Cole Porter (Deck of DM Things), powered by GPT-3.5-turbo or GPT-4.

**Architecture**:
- Web UI for single-player TTRPG experience
- Story tracking and branching
- Designed for accessible, guided gameplay

**Status**: Community-driven (originated from Patreon support); represents a more polished but less flexible alternative to NarrativeEngine variants.

---

### Open Dungeon

**What it is**: AI-driven Zork-style text adventure where narration is LLM-powered BUT game state is 100% deterministic and engine-owned.

**Key principle**: Inverts the typical approach—free-form narration overlays structured, rules-bound game state rather than narrative driving state.

**Strengths**:
- Game state integrity is guaranteed (no narrative can break rules)
- Predictable, testable game mechanics
- Players understand the rule boundaries

**Weaknesses**:
- Narration is constrained to describe game state, limiting creative freedom
- Requires translating all game mechanics to deterministic rules

**Architectural insight**: "Engine-owned state" is the opposite extreme from "narrative-driven state," and both extremes have tradeoffs.

---

### Other Notable Projects

- **Dungeon Master AI Project** (Python): State machine + map system, D&D 5e-inspired mechanics, modular NPC and item systems
- **Voice-Based Dungeon Master** (Discord integration): Speech-to-text → LLM → TTS pipeline, system-agnostic rule support
- **LOTM-GAME**: Self-hosted campaign engine with RAG-indexed world markdown
- **Grimoire**: TTRPG content organizer with campaign management

---

## Supporting Infrastructure & Engines

### Foundry Virtual Tabletop (VTT)

**What it is**: Commercial, self-hosted virtual tabletop for TTRPGs with rich automation and extensibility. Not an AI tool, but critical infrastructure for managing game mechanics in digital play.

**Architecture**:
- **Game systems**: Community-maintained rule systems (D&D 5e bundled)
- **State management**: Dynamic Active Effects (DAE), Midi-QOL for automated resolution
- **Extensibility**: Module ecosystem allows community automation of rules
- **Integration**: Automation modules handle dice rolls, damage, spell effects, resource tracking

**Relevance to AI GM design**: Foundry VTT shows how rich, automated rule systems can be built and how to separate visual presentation from mechanical resolution. Potential integration point for AI GMs (some experimental modules exist).

---

### SRD Rules Engine

**What it is**: Community-driven D&D 5.2 rules engine treating game mechanics as structured, composable data.

**Architecture**:
- **Data-driven**: Classes, feats, items, prerequisites, effects defined as reusable data
- **Entity-Component System**: Flexible framework for complex mechanics
- **Authority boundary**: Rules engine owns outcome authority; LLM narrates results but cannot invent them

**Architectural principle**: Separates "narration of what happened" from "calculation of what happens." Rules engine is law; narration is flavor.

**Best for**: Projects prioritizing rule integrity over narrative freedom.

---

### Procedural Content Generation (PCG)

**What it is**: Algorithmic generation of game content (levels, items, encounters, NPCs, etc.).

**Approaches**:
- **Traditional**: Perlin noise, cellular automata, rule-based systems for landscapes/dungeons
- **AI-driven**: GANs, diffusion models for more creative, learned-pattern-based generation
- **Recent advances**: 40% increase in environmental diversity with 28% computational overhead reduction

**Game applications**: No Man's Sky (billions of unique planets), Hades/Spelunky (dungeon layouts).

**Relevance to AI GMs**: Procedural generation complements LLM narration—NPCs, encounters, loot, world details can be procedurally seeded, reducing context window load and improving consistency.

---

## Technical Approaches to Bounded AI Narration

### Function Calling / Tool Use

**Research**: "You Have Thirteen Hours in Which to Solve the Labyrinth" (Song, Zhu, Callison-Burch; arXiv:2409.06949)

**Core insight**: Game masters need to read and write game state. Function calling is the mechanism by which LLMs accomplish this.

**Pattern**:
```
LLM receives:
  - Current game state (JSON)
  - Available functions (schema)
  - Player action / prompt

LLM outputs:
  - Narration (free text)
  - Function calls (structured: UpdateEnemyHP, AwardXP, etc.)

Engine processes function calls to update state before next turn.
```

**Benefits**:
- Narration remains creative (free text)
- State updates are deterministic and validated
- Player cannot exploit narrative to break rules

**Limitations**:
- Requires carefully designed function schema
- LLM must learn when to call which functions
- Complex rules may require many functions, increasing schema size

**Best for**: Turn-based TTRPGs where state changes are discrete and well-defined.

---

### Retrieval-Augmented Generation (RAG)

**Concept**: External knowledge retrieval supplements the LLM's limited context window.

**Game application**:
- World markdown is indexed (NPC descriptions, location details, faction info, past events)
- At each turn, relevant chunks are retrieved and injected into context
- Enables persistent world knowledge without overwhelming context window

**Example**: LOTM-GAME uses RAG with ~1200 tokens/turn of retrieved context alongside character/location ledgers.

**Tradeoff**: Retrieved context is fixed-size and curated; deeper, more nuanced world knowledge still requires manual curation.

---

### Constrained Decoding / Structured Output

**Technique**: Force LLM output to conform to a JSON schema, preventing invalid outputs.

**How it works**:
- Model cannot emit tokens that violate schema (with strict: true in Claude, OpenAI)
- Physical constraint, not post-hoc validation
- Allows reliable extraction of game state updates

**Limitation**: Constraints must be representable in schema. Complex conditional logic ("if player is below 10 HP, monsters gain advantage") is better expressed as rules than as output schema.

**Best for**: Ensuring structured game data is always valid.

---

### Guardrails & Prompt Engineering

**7 guardrail strategies**:
1. **Schemas**: Structured output format
2. **Retrieval**: Inject relevant context
3. **Tool use**: Function calls for state changes
4. **Verification**: Post-hoc validation of outputs
5. **Decoding constraints**: Token-level schema enforcement
6. **Policy gates**: Conditional logic for sensitive outputs
7. **Observability**: Logging and monitoring

**Empirical finding**: Character persona constraints reduce hallucinations by ~45%; combining with output length limits and stop-sequence tuning improves further.

**Design tension**: Increasing constraints beyond a point reduces narrative coherence and creativity.

---

## Design Tensions & Failure Modes

### The Fundamental Conflict

**The problem**: AI excels at open-ended narration. RPGs require deterministic rule enforcement. These are in tension.

**ChatGPT has no character system**—it has a conversation history with no structured data like strength scores. Rules buried in the middle of a dense prompt get overshadowed by recency effects from conversation history.

### Universal Failure Mode: Campaign Collapse

**What happens**:
- Sessions 1-10 go well; narration is engaging, rules mostly honored
- Sessions 10-50: Context window fills, older decisions are summarized, LLM begins drifting
- Sessions 50+: Campaign incoherent; story threads forgotten, rules increasingly violated, encounters feel disconnected

**Root cause**: Context window limitations. As conversation history grows, earlier plot seeds fall out of context or are compressed into vague summaries.

**Documented in**: Multiple dev blogs, the "Thirteen Hours" paper, and community discussions on r/aidungeon and r/aiRPG.

### Narrative Drift

**Symptoms**:
- Story elements introduced early are forgotten or contradicted
- Encounters feel cosmetically related but narratively pointless
- Player goals diverge from game world coherence
- Tone shifts unexpectedly (comic relief to grimdark)

**Causes**:
- Limited context window
- No persistent memory of world state beyond current message
- Narrative inertia (narration follows player momentum rather than authored plot)

### State Tracking Failure

**The problem**: Without structured state, "game state" is implicit in narration.

**Example failure**:
```
Turn 1: "You are at the tavern. You have 10 gold."
Turn 50: (in summarized context) "You're an adventurer with gold."
Turn 51: Player: "I spend my gold on a horse"
LLM: "You now have 5 gold left"
(LLM hallucinated—no one knows if player had 10, 5, or 50 gold)
```

**Solution**: Explicit, structured state tracking separate from narration.

### Rules Enforcement Paradox

**The tension**:
- More rules constraints → more coherent rule application, but less narrative flexibility
- Fewer constraints → more narrative freedom, but rule violations and player frustration

**Evidence**: "Increasing prompt complexity and constraint specificity beyond a certain point reduces narrative coherence and creativity."

### Content Guardrail Backlash

**Issue**: Safety constraints imposed by OpenAI/Claude can destroy game immersion.

**Example**: Villain must behave non-antagonistically due to safety guardrails, breaking their narrative role.

**Community response**: Led to explosion of fine-tuned models (KoboldAI, DreamGen) that relax safety constraints, prioritizing narrative freedom for consenting adults.

---

## Key Architectural Patterns

### Pattern 1: Ledgers + RAG Memory

**Used by**: NarrativeEngine variants, LOTM-GAME

**Structure**:
```
Persistent Knowledge (Ledgers):
  - Character facts (name, motivation, appearance)
  - Location descriptions
  - Historical events (immutable log)

Dynamic State (RAG):
  - Current NPC positions
  - Active quests
  - Recent events
  - Environmental conditions
```

**Advantage**: Keeps context window focused on present while maintaining long-term consistency.

---

### Pattern 2: Engine-Owned State

**Used by**: Open Dungeon, traditional VTT + AI narration hybrid

**Structure**:
```
Authoritative Engine State:
  - HP, XP, inventory (structured data)
  - Turn order, spell effects
  - Map and collision

LLM Narration Layer:
  - Describes game state
  - Interprets player intent
  - Cannot invent results
```

**Advantage**: Rules are inviolable; player trust is preserved.
**Disadvantage**: Narration must be retrofitted to fixed state, limiting creative freedom.

---

### Pattern 3: Function Calling + Narration

**Used by**: "Thirteen Hours" paper approach, experimental modern GMs

**Structure**:
```
Per turn:
  1. LLM receives state + functions + player action
  2. LLM generates:
     - Narration (free text)
     - Function calls (UpdateState, RollCheck, etc.)
  3. Engine validates and applies functions
  4. Loop with updated state
```

**Advantage**: Narrative and mechanics both guided by LLM, but mechanics are deterministic.
**Disadvantage**: Requires good function schema design; complex rules become unwieldy.

---

### Pattern 4: Layered Prompting

**Principle**: Different types of guidance for different game states.

**Structure**:
```
Top of context (most important):
  - Core rules (cannot be violated)
  - Current turn mechanics

Middle of context:
  - Character descriptions
  - Recent events

Bottom/separate injection:
  - World lore (only injected when not in combat)
  - Creative voice guidance
```

**Empirical improvement**: Separating combat rules from narrative craft guidance improves adherence without losing narrative quality.

---

### Pattern 5: Character Definition + Lorebook

**Used by**: SillyTavern, NovelAI, DreamGen

**Structure**:
```
Character Card:
  - Name, description, personality
  - Speech examples (few-shot)
  - Goals, relationships, secrets

Lorebook:
  - World-building entries (indexed)
  - Tag-based retrieval
  - Entries injected when tags match context
```

**Advantage**: Rich character behavior, persistent world knowledge without context overload.
**Disadvantage**: Still subject to context window limits in very long sessions.

---

## Synthesis: Designing an AI RPG

Based on the landscape survey, here are design principles that emerge across successful tools:

### 1. **Separate Narration from State**
Non-negotiable. Never store game state implicitly in narration.

### 2. **Use External Memory for World Knowledge**
RAG, ledgers, or indexed markdown. Don't rely on context window for facts.

### 3. **Enforce Rules Explicitly**
Via function calls, structured output validation, or a rules engine. Narration interprets; rules decide.

### 4. **Design Character Definition for Few-Shot Learning**
Character cards with examples teach voice more reliably than lengthy prose descriptions.

### 5. **Tier Prompt Guidance by Importance**
Rules first (inviolable). Recent events next. Lore and flavor last (can be pruned).

### 6. **Embrace Branching Narrative Tools' Lessons**
Even if your game is AI-driven, study how Ink, Yarn Spinner, and ChoiceScript structure state. These patterns transfer.

### 7. **Plan for Campaign Longevity Early**
Assume your game will run 100+ turns. Design memory, state persistence, and summarization from day one.

### 8. **Test Guardrails Empirically**
Don't over-constrain; measure narrative coherence vs. rule adherence and iterate.

---

## Comparative Summary Table

| Tool | Type | State Management | Narrative Freedom | Complexity | Best For |
|------|------|------------------|-------------------|-----------|----------|
| **Ink** | Script (non-AI) | Strong (variables, JSON save) | High (writer-driven) | Medium | Complex branching stories, game integration |
| **Yarn Spinner** | Script (non-AI) | Good (variables) | High (writer-driven) | Low-Medium | Game dialogue, dialogue-heavy narratives |
| **Twine** | Visual (non-AI) | Fair (macros, story formats vary) | High | Low | Fast prototyping, learning, classroom |
| **ChoiceScript** | Script (non-AI) | Excellent (stat-based) | Medium (stat-driven) | Low | Stat-tracking interactive fiction |
| **NarrativeFlow** | Visual (non-AI) | Good (variables, conditions) | Medium-High | Medium | Game engine integration, dialogue trees |
| **NovelAI** | AI-driven | Lorebook + context | Very High (creative) | Medium | Long-form fiction, creative writing |
| **KoboldAI** | AI-driven | Adventure mode (limited) | Very High | Medium-High (setup) | Local LLM experimentation, custom tools |
| **SillyTavern** | AI-driven | Character cards + lorebook | Very High | High (requires model knowledge) | Roleplay, character interaction, customization |
| **NarrativeEngine** | AI + rules | Ledgers + RAG (excellent) | High (narration tier) | High (setup) | Long-form campaigns, persistent world |
| **Open Dungeon** | AI + rules | Engine-owned (perfect) | Medium (constrained by rules) | Medium | Deterministic game state with AI narration |

---

## References & Sources

### Tools & Platforms
- [Ink (inkle Studios)](https://www.inklestudios.com/ink/)
- [Yarn Spinner](https://yarnspinner.dev/)
- [Twine](https://twinery.org/)
- [ChoiceScript](https://www.choiceofgames.com/make-your-own-games/choicescript-intro/)
- [NovelAI](https://novelai.net/)
- [KoboldAI](https://github.com/KoboldAI/KoboldAI-Client)
- [SillyTavern](https://github.com/SillyTavern/SillyTavern)
- [DreamGen](https://dreamgen.com/)
- [NarrativeEngine-P](https://github.com/Sagesheep/NarrativeEngine-P)

### Research Papers
- Song, Zhu, Callison-Burch. "You Have Thirteen Hours in Which to Solve the Labyrinth: Enhancing AI Game Masters with Function Calling." arXiv:2409.06949 (Sept 2024)
- "Game Knowledge Management System: Schema-Governed LLM Pipeline for Executable Narrative Generation in RPGs" (MDPI, 2024)
- "Large Language Models and Games: A Survey and Roadmap" (arXiv, 2024)
- "Static Vs. Agentic Game Master AI for Facilitating Solo Role-Playing Experiences" (arXiv, 2025)

### Educational & Blog Resources
- [The GM's Guide to Advanced Foundry VTT Automation](https://nat20labs.com/blog/mastering-foundry-vtt-advanced-automation/)
- [Prompt Architecture for a Reliable AI Dungeon Master](https://dev.to/austin_amento_860aebb9f55/prompt-architecture-for-a-reliable-ai-dungeon-master-d99)
- [Context Window Management Strategies](https://www.getmaxim.ai/articles/context-window-management-strategies-for-long-context-ai-agents-and-chatbots/)
- [Guardrails for LLMs](https://medium.com/@Nexumo_/7-guardrails-that-reduce-llm-hallucinations-78facbb0d560)

---

**Document compiled**: September 28, 2026  
**Scope**: Tools and platforms for interactive fiction, RPG game masters, and D&D-style games, with emphasis on open-source and accessible options.
