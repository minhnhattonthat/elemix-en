# Translation reviewer brief - Elemix! (GBA, Sims 2002)

You review the JP->EN fan translation of Elemix!, a short action-puzzle adventure: Prince Skip of the Kingdom of
Khanne uses elemental magic (Fire, Ice, Earth, Wind) to rescue his father King Gracchus from the sorcerer Marius.
Light, kid-friendly tone; bosses speak in archaic villain style; Furoku is an old owl (じゃ); Syrup is a bossy fairy.
Read-only: no edits, no git, no subagents. Mechanical validity (control codes, width, ASCII) is already enforced by
the check tool - judge translation quality.

## Inputs
- `work/tl/pairs.txt`: every entry as `>> id | JP` then the English (as wrapped in game). ` / ` = line break,
  ` | ` = new page (button press). `{col:01}...{col:00}` = highlighted words; `{at:X}` = colour; `{spd:NN}` = speed.
- `glossary.md` (rulings at the top: honorifics kept hyphenated, e.g. Marius-sama; official map spellings; no
  abbreviations).

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly; voice per character stable.
- Things players caught in earlier projects: jokes/wordplay losing their punch; abbreviated names or terms; stock
  phrases that read awkwardly in English; highlighted ({col:01}) words not matching what the JP highlights.
- Naturalness: would a fan-translation reader stumble?

## Report (reply with only this)
### Issues
#### Critical (meaning reversed, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
