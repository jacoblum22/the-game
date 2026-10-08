# Contract: the OFFER block and the pause menu (12.15.2, 14.2.7)

The text below is what a player sees. Line order is fixed; a line with nothing to say is omitted.

```
[OFFER] <the beat as restated>
  <mode line, when stretched / emulated / a crude fallback>
  Chance: <word> — <N>%   (<Attribute> <±n>, <competence name> <±n>, a help +2, a hindrance −2, ...)
  If it works: <reach words>.   Very well (<N>%): more than you asked.
  If it fails: [Danger: ]<cost clause> — <severity word>.   Badly (<N>%): <cost clause> — <severity word>.
  THIS CAN KILL YOU — <source> (warned <when>)            (lethal frames)
  Close call (<N>%): get it anyway and pay <alternate clause>, or fail.
  Takes: <method consequences> · fate <n>
  Another way: <alternative> (<N>%) · ...
```

Variants: secret (`Chance: you can't judge how hard this is.`, no Close call), long shot (`Chance: long shot —
N% (failing badly is likelier: M%)`, Another way first), natural 20 only (`Chance: only by luck — 5%, and at best
what you wanted`), auto (`[OFFER — auto]`, no menu).

Never in the block: `S1`–`S5`, `DC`, `verb.`, `anchor`, `Mode:`.

## Menu (play-phase pauses)
```
[Enter] Do it   [b] Go big   [s] Play it safe   [c] Another way   [w] Back off   [?] Explain
```
- Enter is always printed. On a Dire, lethal or long-shot OFFER and on other waiting pauses it is
  `[Enter] Show this again` and committing is `[d] Do it`.
- `?` lists the glossary (14.2.7); `? <word>` explains one word.
- A digit still picks the n-th choice.
