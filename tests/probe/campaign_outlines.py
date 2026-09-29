"""Three distinct, original campaign outlines for feature 002 (T011).

Original text, not adapted from copyrighted material, per research.md's decision -- we're
borrowing NCP-Bench's extraction *method*, not its specific source material (movie synopses).
Each is deliberately short; the pipeline expands it into a full trajectory/commitment/state set.
"""

OUTLINES: dict[str, str] = {
    "outpost": (
        "A small trading outpost has gone silent. A scout is sent to investigate, finds the "
        "outpost abandoned but for a locked storeroom, and discovers signs of a recent raid "
        "by bandits who fled north with stolen goods, leaving a surviving clerk trapped inside."
    ),
    "lighthouse": (
        "A keeper's apprentice arrives at a remote coastal lighthouse to begin their post, "
        "only to find the previous keeper missing and the light extinguished. Strange tide "
        "patterns suggest something is wrong offshore, and the apprentice must relight the "
        "lamp before a storm-bound ship wrecks on the rocks."
    ),
    "archive": (
        "A junior archivist is sent into a sealed underground library to retrieve a specific "
        "ledger before the vault reseals at dawn. The library's old cataloguing spirits are "
        "still active and will only cooperate with someone who follows the library's "
        "old-fashioned rules of conduct."
    ),
}
