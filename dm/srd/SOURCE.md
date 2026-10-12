# Source of this data

The JSON files here are copied unchanged from the 5e-bits project:
https://github.com/5e-bits/5e-srd-api, commit `ecfddae2f1738d7f917154a81fbce04aca56cdd1`,
path `packages/5e-database/src/2014/en`. The project's code is under the MIT licence (`LICENSE-5e-bits.md`).

The content is the System Reference Document 5.1:

This work includes material taken from the System Reference Document 5.1 ("SRD 5.1") by Wizards of the Coast
LLC and available at https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1 is licensed
under the Creative Commons Attribution 4.0 International License available at
https://creativecommons.org/licenses/by/4.0/legalcode.

Known gap: the Acolyte's prayer book (or prayer wheel), 5 sticks of incense and vestments are missing from its
starting equipment. `dm/create.py` adds them (`ACOLYTE_PRAYER`, `ACOLYTE_ITEMS`); the data here stays unchanged.

Gap-fill: `dm/srd/gapfill/5e-SRD-Rules.json` holds rules sections the dataset lacks, taken word for word from the
official SRD 5.1 PDF (`SRD_CC_v5.1.pdf`, https://dnd.wizards.com/resources/systems-reference-document), with only
the PDF's text-extraction artefacts (spacing, split words, broken hyphens, ligatures) repaired. `dm/srd.py` `table()`
adds these entries to the dataset's (an index that is already in the dataset raises). Each entry has a `source` field.
- Beyond 1st Level, with the Character Advancement table (p.56)
The SRD's Multiclassing (pp.56-58) and Feats (p.75) sections are left out on purpose: the game doesn't use those
optional rules (owner, 2026-10-11), and the DM's prompt says so.

The gap-fill is under the same licence and attribution as the rest of the SRD content here. The PDF's legal page asks
for this attribution statement:

This work includes material taken from the System Reference Document 5.1 ("SRD 5.1") by Wizards of the Coast
LLC and available at https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1 is licensed
under the Creative Commons Attribution 4.0 International License available at
https://creativecommons.org/licenses/by/4.0/legalcode.
