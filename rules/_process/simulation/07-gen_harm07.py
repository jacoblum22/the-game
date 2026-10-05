# 07-gen_harm07.py -- second half of 07-gen_data07.py (exec'd by it): data/harm.yaml, file writing, validation.
# Not run on its own.

B = lambda *xs: list(xs)


def clock(id_, name, kind, segments, visibility, tick_sources, auto_ticks, omens, on_complete, basis, **extra):
    c = {'id': id_, 'name': name, 'kind': kind, 'owner': '07', 'segments': segments, 'visibility': visibility,
         'direction': 'fill', 'tick_sources': tick_sources, 'auto_ticks': auto_ticks, 'decay': [], 'omens': omens,
         'on_complete': on_complete, 'races_with': None, 'links': []}
    c.update(extra)
    c['lifecycle'] = 'provisional'
    c['basis'] = basis
    return c


HARM = {
    'schema_version': 1,
    'vitality': {
        'meaning': 'wind, luck and guard: the margin by which a blow fails to be telling (07.1.1)',
        'max_formula': 'base + 2 * (power_band - 1) + effects(eff.max_modify) - wound penalties',
        'base': {'owner': '02', 'envelope': [10, 16], 'reference': 12, 'evaluated_on': 'current attributes'},
        'band_growth_per_band': 2, 'by_band_at_reference': [12, 14, 16, 18, 20],
        'cap': 24, 'floor': 'ceil((base + band growth) / 2)',
        'recompute_handler': 'h.07.vitality_max',
        'on_band_rise': 'current rises by the same amount', 'on_fall': 'current is clamped to the new maximum',
        'basis': B('07.1.2', '00.3.12', 'DL-00-04', 'DL-07-18')},
    'descriptors': [
        {'id': 'fresh', 'when': 'vitality.current == vitality.max', 'words': ['steady', 'untouched', 'breathing easy']},
        {'id': 'worn', 'when': 'vitality.current * 2 > vitality.max and vitality.current < vitality.max',
         'words': ['scraped', 'breathing hard', 'a step slower']},
        {'id': 'bloodied', 'when': '0 < vitality.current and vitality.current * 2 <= vitality.max',
         'words': ['bleeding from small cuts', 'battered', 'every movement costs']},
        {'id': 'staggered', 'when': 'harm_state == staggered', 'words': ['reeling', 'on a knee', 'guard gone', 'the world narrowing']},
        {'id': 'dying', 'when': 'harm_state == dying',
         'words': ['on the ground', 'the cold coming up', 'sound going far away', 'one thing left in you']},
        {'id': 'down', 'when': 'down == true', 'words': ['out', 'the dark closes', 'nothing, and then waking']},
        {'id': 'shaken', 'when': 'dread.current * 2 >= dread.threshold', 'words': ['hands not quite steady', 'jumping at small sounds']},
    ],
    'harm_states': [
        {'id': 'harm_state.active', 'name': 'Active', 'tags': [], 'entry': 'vitality.current > 0',
         'exit': 'vitality reaches 0 -> harm_state.staggered', 'actions': 3, 'lifecycle': 'provisional', 'basis': B('07.1.3')},
        {'id': 'harm_state.staggered', 'name': 'Staggered', 'tags': [],
         'entry': 'vitality reaches 0 by any harm; the excess of that harm is discarded (07.2.3)',
         'exit': 'vitality restored above 0 -> active | wound_load >= 3 under a lethal event -> dying at min(3, 1 + brink) | wound_load >= 3 under a non-lethal event -> down',
         'actions': 3, 'every_harm_event_is_a_wound': True, 'raises': ['trg.exits'], 'lifecycle': 'provisional',
         'basis': B('07.1.3', '07.2.3', '07.2.6', 'R6 C-R2')},
        {'id': 'harm_state.dying', 'name': 'Dying', 'tags': [],
         'entry': "a Staggered PC or companion's wound_load reaches 3 under a lethal harm event",
         'exit': 'step 0 or any Vitality restored -> stabilized (staggered or active, one inj.the_brink) | step would pass 3 -> the Threshold (last_chance.yaml)',
         'actions': 1, 'reactions': 0, 'conditions': ['cond.prone'], 'raises': ['trg.exits', 'on_dying'],
         'not_defeated': True, 'lifecycle': 'provisional', 'basis': B('07.1.3', '07.2.7', 'R: https://2e.aonprd.com/Rules.aspx?ID=2319')},
        {'id': 'harm_state.dead', 'name': 'Dead', 'tags': [], 'entry': 'only by two_key (07.3.1)', 'exit': 'none',
         'lifecycle': 'provisional', 'basis': B('07.3.1', 'INV-6')},
    ],
    'defeated': {'flag': 'defeated', 'manners_pc': ['down', 'yielded', 'captured', 'fled', 'dead'],
                 'manners_others': ['dead', 'dying', 'unconscious', 'yielded', 'driven_off', 'fled'],
                 'note': 'A Dying PC is not defeated: it has one action and a voice (07.1.3).'},
    'wounds': {
        'severity_track': [
            {'final_amount': '1-2', 'severity': 'S1', 'load': 1}, {'final_amount': '3-4', 'severity': 'S2', 'load': 1},
            {'final_amount': '5-7', 'severity': 'S3', 'load': 2}, {'final_amount': '8-11', 'severity': 'S4', 'load': 3},
            {'final_amount': '12+', 'severity': 'S5', 'load': 4}],
        'record_created_when': 'the harm event is not periodic',
        'periodic_events': 'add load, create no record',
        'site': {'order': ["the called shot's site (06.4.10)", "the attack's listed site (09)", 'tbl.wound_site'],
                 'sites': ['arm', 'leg', 'body', 'head']},
        'entry_key': 'injuries.yaml: inj.w.<family>.<site>.<severity>; S1: inj.w.<family>.light',
        'max_vitality_penalty': {'S3': 2, 'S4': 3, 'S5': 4},
        'status_penalty': {'S1': 0, 'S2': -1, 'S3': -2, 'S4': -2, 'S5': -3},
        'grit': 'a push (05.6.7, 1 Focus) may be declared as grit: the beat ignores status penalties from wounds and gains no reach',
        'load_limit': 3, 'load_cleared_at': ['scene_end', 'any rest completion', 'a last-chance outcome that says so'],
        'basis': B('07.2.4', '07.2.5', '07.2.6', 'DL-07-03', 'DL-07-04')},
    'dying': {
        'steps': 3, 'entry_step': 'min(3, 1 + brink)',
        'check': {'verb': 'verb.endure', 'attribute': 'endurance', 'modifier': 'attribute + competence + edge',
                  'levers': 'none', 'snags': 'none', 'status': 'none', 'at': "the character's turn_end; outside a conflict, each round",
                  'fate_reroll': True, 'handler': 'h.07.dying_check'},
        'stabilize_dc': [{'step': 1, 'tier': 'easy', 'dc': 10}, {'step': 2, 'tier': 'moderate', 'dc': 15},
                         {'step': 3, 'tier': 'hard', 'dc': 20}],
        'results': {'critical_success': 'stabilized', 'success': 'one step down (from step 1: stabilized)',
                    'failure_within_3': 'holds', 'failure': 'one step up', 'critical_failure': 'two steps up'},
        'lethal_harm': {'S1': 1, 'S2': 1, 'S3': 1, 'S4': 2, 'S5': 2}, 'non_lethal_harm': 'no step',
        'first_aid': {'verb': 'verb.handle', 'by': 'another character engaged with the Dying one', 'cost': '1 action',
                      'dc': 'the stabilize DC of the current step', 'kit': 'a Precision lever', 'success': 'stabilized',
                      'failure': 'no change', 'self': 'not allowed'},
        'restoring_vitality': 'stabilizes at once, then restores',
        'time': 'rounds, while anyone is Dying',
        'past_step_3': 'the Threshold: last_chance.yaml',
        'basis': B('07.2.7', 'R: https://2e.aonprd.com/Rules.aspx?ID=2319', 'DL-07-04')},
    'brink': {'wound': 'inj.the_brink', 'gained': 'each time a character is stabilized from Dying, except by lc.reprieve or a critical Gamble',
              'value': 'the count of unhealed inj.the_brink wounds', 'effect': 'the next fall enters Dying at 1 + brink (maximum 3)',
              'heals': 'clk.back_from_the_brink, one brink wound at a time', 'basis': B('07.2.8')},
    'stabilized': {'definition': 'dying_step 0; harm state Staggered (Vitality 0) or active if Vitality was restored; conscious; prone; on_stabilize fires; one inj.the_brink',
                   'effect': 'eff.07.stabilize', 'basis': B('07.2.8', "05's request (ab.breath_of_life)")},
    'down': {'definition': 'down: true; defeated {manner: down}; cond.unconscious and cond.prone; harm state stays Staggered; the ladder is frozen',
             'entered': ['wound_load >= 3 under a non-lethal event', 'a mode: nonlethal attack brings the target to 0 Vitality',
                         'collapse from lack of sleep or want (07.8.10)'],
             'wakes': 'when the disposition says, or after one interval', 'basis': B('07.2.9', 'INV-6')},
    'others': {'adversary_at_0': {'lethal': {'walk-on': 'dead', 'recurring': 'dying: dies at scene_end unless stabilized or finished',
                                             'principal': 'dying: dies at scene_end unless stabilized or finished'},
                                  'nonlethal': 'cond.unconscious for the scene'},
               'basis': B('07.2.10', '06.13.3', '06.4.8')},
    'reduction_cap': 4,
    'reduction_sources': [
        {'source': 'worn armor', 'amount': {'light': 1, 'medium': 2, 'heavy': 3}, 'applies_to': 'harm.physical from attacks and shaped effects'},
        {'source': 'natural armor (09)', 'amount': '0-3', 'applies_to': 'as the template says', 'no_gaps': True},
        {'source': 'eff.harm_reduction', 'amount': '1-4', 'applies_to': 'the listed harm tags, with cascade'},
        {'source': 'a shield', 'amount': 0, 'applies_to': 'nothing (it adds to Guard)'}],
    'no_reduction': ['cond.bleeding', 'cond.choking', 'affliction stage harm', 'overdraw and Backlash (05.6.6)',
                     'falls', 'being crushed by mass (a collapse, deep water)', 'starvation, thirst and lack of sleep'],
    'inheritance': {'periodic_events_take_lethal_from': 'the frame or exposure that started them, re-tested at each tick (07.2.11)',
                    'non_lethal_cap': 'Vitality, Stagger, wounds, Down; never Dying, never a dying step, never the Threshold'},
    'lethal_warning': {
        'trigger': [
            {'cause': 'advisory', 'when': 'threat_advisory(encounter, pc) == lethal at framing, or when it becomes lethal', 'from': '09'},
            {'cause': 'archetype', 'when': 'a hostile adversary with lethal_context: true is perceived or turns hostile', 'from': '09'},
            {'cause': 'disposition', 'when': "a side's defeat_disposition is or becomes kill toward the PC", 'from': '09, 06.13.2'},
            {'cause': 'severity', 'when': 'a source able to deliver S4 or S5 harm to the PC comes within reach (a hazard or trap perceived, a height of 40 ft or more, an attack listed at S4+)', 'from': '10, 06.5.8, 09'},
            {'cause': 'windup', 'when': 'an adversary begins a Windup for a heavy blow (06.9.5)', 'from': '06'},
            {'cause': 'clock', 'when': 'a sensed or hidden clock reaches imminent and its on_complete would expose the PC to lethal harm', 'from': '00.8.4, PR-00-3'},
            {'cause': 'hazard', 'when': 'the PC is about to enter or is in a hazard with lethal_context: true', 'from': '10'},
            {'cause': 'affliction', 'when': 'an affliction the PC carries reaches its warn_stage', 'from': '07.9.5'},
            {'cause': 'deprivation', 'when': 'three stacks of cond.exhausted while starving, parched or sleepless', 'from': '07.8.10, 10'},
            {'cause': 'chosen', 'when': "the player declares an act whose stated outcome is the character's death", 'from': '07.5.13'}],
        'writes': {'lethal_context': {'id': 'lc.<scene>.<source>', 'source': 'id', 'cause': 'enum', 'sign': 'str',
                                      'warned_at': 'time', 'effective_from': 'beat', 'shown': True,
                                      'ends': 'scene_end | source_gone | cured'}},
        'delivery': ['one perceivable sign in fiction (a tell, an omen, the plain sight of the thing)',
                     'the [WARNING] block in plain words, with the exits and current fate'],
        'effective': "from the end of the player's next declaration, or the PC's next turn, after the warning was shown",
        'block': "[WARNING] THIS CAN KILL YOU - <source as perceived>. <cause line> From your next action on, falling here can mean Dying. Fate: <n>. Exits now: Yield - <...> . Retreat - <...>",
        'cause_lines': {'advisory': 'As things stand you are unlikely to win this.', 'archetype': 'It means to kill.',
                        'disposition': 'It means to kill.', 'severity': 'A <Grievous | Catastrophic> danger.',
                        'hazard': 'A <Grievous | Catastrophic> danger.', 'windup': 'It is winding up <the attack named>.',
                        'clock': 'The signs say something deadly is very close.',
                        'affliction': 'Untreated, <affliction> will put your life at risk at its next stage.',
                        'deprivation': 'Your body is failing.', 'chosen': 'You have chosen this.'},
        'danger_notice': {'when': 'threat_advisory == hard and no lethal-warning row is true', 'writes': 'no lethal context',
                          'block': '[WARNING] A hard fight - you may well lose this. Losing here means <disposition in words>.'},
        'handler': 'h.07.lethal_scan', 'basis': B('07.3.2', '07.3.3', '07.3.4', '07.3.5', '07.3.8', 'R4 6.2 item 4', 'DL-07-02')},
    'two_key': {
        'keys': [
            {'key': 1, 'name': 'declared lethality',
             'holds_when': 'the harm event or chosen act belongs to a lethal frame: a lethal context for its source was recorded, shown and effective before the declaration (07.3.6)'},
            {'key': 2, 'name': "the brink, and the player's hand",
             'holds_when': ['the Threshold was reached and the player chose lc.last_stand',
                            'the Threshold was reached, the player chose lc.gamble, and the check failed',
                            'the player declared and confirmed a voluntary last stand in a lethal context (07.5.13)',
                            "a Death's Bargain was forfeited, returning the character to the Threshold, where one of the first two then applied"]}],
        'writes_dead_only_when': 'both keys hold; the engine refuses the write otherwise (INV-6)',
        'lethal_frame': ['a lethal context for the source exists and is effective',
                         'the producing frame is: a PC-actor frame at Dire with lethal: true (01.6.9) | an adversary-actor frame with mode lethal | a lethal hazard exposure or affliction stage | a periodic tick inheriting from one of these',
                         'the target is a PC or a companion'],
        'basis': B('07.3.1', '07.3.6', 'INV-6', 'R6 C.3 C-R1', 'DL-07-01')},
    'exits': {'trigger': 'trg.exits', 'raised_when': ['the PC becomes Staggered', 'the PC enters Dying'],
              'staggered_block': '[STATUS] STAGGERED - blows now wound you; at wound load 3 you <fall to Dying | go Down>. Load <n>/3. Exits: Yield - <...> . Retreat - <...> . or fight on.',
              'dying_block': '[STATUS] DYING <n> of 3 - one action a turn; a check each turn (you need <d> or better; <odds>). A blow adds a step. Past 3 you choose from the last-chance menu. Exits: Yield - <...>.',
              'basis': B('07.3.7', 'R6 C-R1, C-R4')},
    'yield': {
        'verb': 'verb.talk', 'cost': 'free', 'legal': 'always, including while Dying',
        'accepted_by': {'capture': True, 'ransom': True, 'rob': True, 'drive_off': True, 'leave': True, 'kill': False,
                        'drag_to_lair': False},
        'unless': "a refusing side's leader holds a recorded want the PC can meet: the answer names it",
        'terms': [
            {'id': 'no_further_harm', 'name': 'No further harm', 'always': True, 'text': 'the side that accepted applies no more harm; the PC stays conscious and sees where it is taken'},
            {'id': 'parole', 'name': 'Parole', 'allowed_for': ['capture', 'ransom'], 'text': 'not bound; breaking parole is a conduct.honesty event (03)'},
            {'id': 'keep_one_thing', 'name': 'Keep one thing', 'allowed_for': ['capture', 'ransom', 'rob'], 'text': 'one named item is not taken'},
            {'id': 'spare_another', 'name': 'Spare another', 'allowed_for': ['capture', 'ransom', 'rob', 'drive_off'], 'text': 'a named companion or bystander goes free'},
            {'id': 'send_word', 'name': 'Send word', 'allowed_for': ['capture', 'ransom'], 'text': 'a message goes to a named NPC or faction; the rescue or ransom lead starts with one tick'},
            {'id': 'an_audience', 'name': 'An audience', 'allowed_for': ['capture', 'ransom', 'drive_off'], 'text': "the PC is brought before the side's leader instead of to a cell"}],
        'terms_per_yield': 1, 'while_dying': 'no term beyond being stabilized', 'fate_gain': 0,
        'basis': B('07.4.1', '07.4.2', '06.11.7', 'R6 C-15', 'DL-07-08')},
    'retreat': {
        'verb': 'verb.move', 'illegal_when': ['flag.cornered', 'cond.restrained', 'cond.pinned', 'Dying', 'Down', 'no route (07.4.3 decision 1)'],
        'pursuit_test': {'willing': "the pursuer's side objective is kill, capture or rob toward the PC and the side is not broken",
                         'able': "the pursuer's pace is at least the PC's and it is not held or prone"},
        'clean': {'when': 'no pursuer is both willing and able', 'certain': True, 'price': ['parting_blow', 'left_behind']},
        'contested': {'when': 'some pursuer is willing and able', 'player_picks': ['run_for_it', 'rout']},
        'run_for_it': {'resolved_by': '06.12 (clk.escape 6 against clk.pursuit 8)', 'certain': False, 'price': 'none stated'},
        'rout': {'certain': True, 'price': ['parting_blow', 'left_behind', 'world_cost'], 'world_cost_ticks': 'U(S3) = 2',
                 'at_the_threshold': 'U(S4) = 3 (lc.rout)',
                 'clock_candidates': ["the opposing side's faction goal clock (11)", "an active danger or countdown clock of the scene owned by that side",
                                      'the opposing clock of the thread the scene served', 'else create clk.grudge'],
                 'setback': 'setback.retreated {severity: S3}'},
        'parting_blow': {'when': 'the PC is engaged at the declaration', 'severity': "the heaviest engaged enemy's ordinary attack severity, one rung lighter",
                         'lethal': False, 'times': 1},
        'left_behind': ['objective_lost', 'items not on the person or in hand', 'a Down or Dying companion not carried', 'a mount not ridden'],
        'carrying': 'one body per carrier; the carrier\'s pace is one lower',
        'basis': B('07.4.3', '07.4.4', '06.12.1', 'R6 C-16', 'DL-07-09')},
    'dispositions': [
        {'id': 'capture', 'name': 'Capture', 'tags': [], 'accepts_yield': True, 'if_dying': 'the captors stabilize the PC',
         'defeated': ['cond.restrained until_cleansed', 'moved to the holding place; time advanced by the journey', 'all carried items to a cache',
                      'clk.captors_intent', 'three openings (tbl.captivity_openings)', 'thr.captivity with clk.out_of_their_hands', 'setback.captured'],
         'yielded': ['as defeated, with the chosen term', 'the PC saw the route (a knowledge fact)'], 'lifecycle': 'provisional', 'basis': B('T-07-11', '07.6.3')},
        {'id': 'ransom', 'name': 'Ransom', 'tags': [], 'accepts_yield': True, 'if_dying': 'the captors stabilize the PC',
         'defeated': ['as capture', 'a demand sent to the NPC or faction of highest standing toward the PC', 'a price (08)', 'clk.captors_intent named for the deadline'],
         'yielded': ["as capture's yielded column", 'the PC may name who is asked'], 'lifecycle': 'provisional', 'basis': B('T-07-11')},
        {'id': 'rob', 'name': 'Rob', 'tags': [], 'accepts_yield': True, 'if_dying': 'they take what they came for and go; the dying checks run out alone',
         'defeated': ["all carried coin and every item above worn clothing, one weapon and one day's supply to a cache", 'left where it fell; wakes after one interval', 'setback.defeated'],
         'yielded': ['coin and valuables only', 'the PC keeps weapons and gear and is free to go', 'keep_one_thing protects one valuable'],
         'lifecycle': 'provisional', 'basis': B('T-07-11', '07.6.4')},
        {'id': 'drive_off', 'name': 'Drive off', 'tags': [], 'accepts_yield': True, 'if_dying': 'they leave the PC to its checks and hold their ground',
         'defeated': ['moved to the adjacent place on the way it came', 'barred_to_pc on the place while that side holds it', 'nothing taken', 'objective_lost', 'setback.defeated'],
         'yielded': ['the PC walks out under its own power', 'the same facts'], 'lifecycle': 'provisional', 'basis': B('T-07-11')},
        {'id': 'drag_to_lair', 'name': 'Drag to lair', 'tags': [], 'accepts_yield': False,
         'if_dying': 'nothing stabilizes the PC; the dying checks run during the drag; at the Threshold lc.captured is available',
         'defeated': ['wakes in the lair (a place with at least one recorded exit)', 'nothing taken; what was in hand lies at the place of the fight',
                      'clk.larder', 'three openings', 'setback.captured'],
         'yielded': ['not accepted'], 'lifecycle': 'provisional', 'basis': B('T-07-11')},
        {'id': 'leave', 'name': 'Leave', 'tags': [], 'accepts_yield': True, 'if_dying': 'they leave; the checks run out alone',
         'defeated': ['wakes after one interval where it fell', 'objective_lost', 'setback.defeated'], 'yielded': ['the same; a duel\'s terms (15) are honored'],
         'lifecycle': 'provisional', 'basis': B('T-07-11')},
        {'id': 'kill', 'name': 'Kill', 'tags': [], 'accepts_yield': False, 'if_dying': 'it goes on attacking',
         'defeated': ['with an effective lethal context this row is not reached (the PC falls to Dying and the Threshold)',
                      'without one: the victor leaves the PC for dead: lc.left_for_dead writes without a brink wound or mark; the belief pc.dead on the victor'],
         'yielded': ['not accepted'], 'lifecycle': 'provisional', 'basis': B('T-07-11', '07.3.5')},
    ],
    'defeat_always_writes': ['victory_over_pc {victor, scene, manner}', 'a reputation packet to 11 scoped to the witnesses',
                             'a setback fact (setback.defeated | .yielded | .captured | .dying_entered | .threshold | .retreated {severity} | .companion_dead)',
                             'at least one actionable lead (P16): PR-07-7 refuses to finish without one'],
    'captivity': {
        'holding_place_order': ["the victor's recorded objective, if it names a place", "the victor faction's nearest hold (11, 13)", "the victor's lair", 'a camp created at the nearest suitable place'],
        'fates': {'default_by_org': {'org.crown': 'trial', 'org.faith': 'trial', 'org.order': 'interrogation', 'org.guild': 'ransom',
                                     'org.company': 'ransom', 'org.clan': 'labor', 'org.outlaw': 'ransom', 'org.cult': 'sacrifice'},
                  'closed_list': ['trial', 'sale', 'sacrifice', 'interrogation', 'ransom', 'labor', 'the larder'],
                  'lethal_on_completion': ['sacrifice', 'the larder']},
        'openings_drawn': 3, 'openings_table': 'tbl.captivity_openings',
        'thread': {'id': 'thr.captivity', 'kind': 'situation', 'progress_clock': 'clk.out_of_their_hands', 'races_with': 'clk.captors_intent'},
        'time': 'advanced through the journey to the first moment the PC can act; never past the first tick of the captors\' clock',
        'basis': B('07.6.3', 'C:P16', 'R1 07')},
    'caches': {'record': 'cache.<n> {holder, place, items, taken_at}', 'clock': 'clk.cache',
               'on_dispersal': {'mundane_items': 'sold or used: gone', 'items_with_a_signature_or_bound_ability': 'pass to a named holder; a rumor points to the holder'},
               'never_deleted': 'an item with a signature property or an item-bound ability', 'basis': B('07.6.4', 'R1 07', 'R6 C-20')},
    'rests': [
        {'id': 'breather', 'name': 'Breather', 'tags': ['situation.rest'], 'duration': 'intervals:1', 'needs': ['no conflict in progress', 'not Dying'],
         'restores': {'vitality': {'full': '+2', 'partial': '+2', 'interrupted': '0'}, 'limit': 'the first 2 between short rests restore Vitality',
                      'wound_load': 'cleared', 'light_wounds': 'healed', 'moderate_wounds': 'only if treated during it'},
         'interrupted_by': ['conflict_start with the rester as participant', 'the rester takes harm or a condition of S2 or heavier',
                            'the rester makes a rolled beat, uses an active ability, labors or travels', 'the rester is moved against its will'],
         'resumable': 'never',
         'quality_rules': ['interrupted: broken beyond the allowance', 'partial: any quality cap holds (rough site; no food or water today; weather S2+ without shelter; an affliction at stage 2+; a haunt that says so)', 'full: otherwise'],
         'lifecycle': 'provisional', 'basis': B('07.8.1', '07.8.3', '07.8.4', 'T-07-14', '00.7.2')},
        {'id': 'rest_short', 'name': 'Short rest', 'tags': ['situation.rest'], 'duration': 'hours:1', 'needs': ['a place to stop', 'not Dying'],
         'restores': {'vitality': {'full': '+ceil(max / 2)', 'partial': '+ceil(max / 4)', 'interrupted': '+2'},
                      'limit': 'the first 2 of a day restore this much; later ones restore as a breather',
                      'wound_load': 'cleared', 'light_wounds': 'healed', 'moderate_wounds': 'only if treated during it'},
         'interrupted_by': 'as breather', 'resumable': 'one interruption of at most 1 interval',
         'quality_rules': 'as breather; a resumed rest is partial', 'lifecycle': 'provisional', 'basis': B('07.8.1', '07.8.3', '07.8.4', 'T-07-14')},
        {'id': 'rest_long', 'name': 'Long rest', 'tags': ['situation.rest'], 'duration': 'watches:1', 'max_per_day': 1,
         'needs': ['a rest site (haven, camp or rough)', 'at least 4 hours asleep', 'not Dying'],
         'restores': {'vitality': {'full': 'to max', 'partial': 'to ceil(3 * max / 4), never lowering', 'interrupted': 'as a partial short rest'},
                      'wound_load': 'cleared', 'light_wounds': 'healed', 'moderate_wounds': 'healed (full or partial)',
                      'exhausted': {'full': -1, 'partial': -1, 'full_in_haven': -2, 'interrupted': 0, 'none_while': 'its cause continues'},
                      'dread': {'full': -1}, 'sets': 'rested_today (full or partial)',
                      'afflictions': 'at full quality the next stage check holds a Precision lever', 'watches_awake': 'reset to 0 (interrupted: 2)'},
         'interrupted_by': 'as breather', 'resumable': 'one interruption of at most 1 hour, with at least 4 hours of sleep served in all',
         'quality_rules': 'as breather; also partial if slept in medium or heavy armor; a resumed rest is partial',
         'lifecycle': 'provisional', 'basis': B('07.8.1', '07.8.3', '07.8.4', 'T-07-14', '00.17.1 Q1, Q16')},
    ],
    'rest_sites': [
        {'id': 'haven', 'anchor': 'others keep the door: paid lodging, a guarded hold, a tended shrine, a friend\'s house', 'encounter_checks': False, 'bed_rest': True},
        {'id': 'camp', 'anchor': 'a made camp or a secured room: shelter or fire, defensible, nothing hostile known within reach', 'encounter_checks': True, 'bed_rest': False},
        {'id': 'rough', 'anchor': 'no shelter and no fire, or inside a hostile site\'s active area, or on the march', 'encounter_checks': True, 'bed_rest': False, 'quality_cap': 'partial'}],
    'rest_event_payload': {'quality': 'full | partial | interrupted', 'site': 'haven | camp | rough', 'treated': 'bool'},
    'recovery': {
        'clocks': {'S3': 'clk.wound_heavy', 'S4': 'clk.wound_grievous', 'S5': 'clk.wound_catastrophic', 'brink': 'clk.back_from_the_brink'},
        'ticks_per_day': {'rested_today': {'S3': 1, 'brink': 1, 'S4': 0, 'S5': 0}, 'treated_today': {'S3': 1, 'brink': 1, 'S4': 1, 'S5': 1},
                          'bed_rest_today': {'S3': 1, 'brink': 1, 'S4': 1, 'S5': 1}},
        'days_to_heal': {'road_untreated': {'S3': 4, 'S4': 'never', 'S5': 'never'}, 'road_treated': {'S3': 2, 'S4': 6, 'S5': 12},
                         'haven_bed_rest_treated': {'S3': 2, 'S4': 3, 'S5': 6}},
        'catastrophic': {'needs': 'surgery (Treat at very_hard) before its clock exists', 'unoperated': 'days:7 -> a maim (07.7.4)'},
        'grievous_untended': 'days:7 with no tick -> an exposure to aff.wound_rot',
        'on_heal': 'the wound and its carrier end; h.07.vitality_max runs; S4 and S5 leave inj.scar.<family>',
        'recovery_step': 'one "recovery step" in an ability or rite = 7 ticks on one wound\'s clock; for S5 it also counts as the surgery',
        'convalesce': {'per_day': ['bed_rest_today', 'treated_today if a tender with the license is present', 'cond.exhausted -1'],
                       'per_week': ['dread to 0', 'eff.07.affliction_shift -1 on any disease']},
        'handler': 'h.07.natural_recovery', 'basis': B('07.8.6', '07.8.7', '07.8.11', 'T-07-15', 'DL-07-13')},
    'treatment': {
        'license': 'lic.training.lore_medicine', 'crude_fallback': 'verb.handle: first aid (stabilize; staunch bleeding), reach capped limited',
        'attribute': 'intellect (agility for first aid in a conflict)', 'deed_tag': 'deed.lore.medicine',
        'dc_tier': {'S2': 'easy', 'S3': 'moderate', 'S4': 'hard', 'S5': 'very_hard (surgery; grade expert or better)', 'affliction': 'its virulence', 'dying': 'the stabilize DC'},
        'time': {'wounds': 'intervals:1', 'surgery': 'hours:1', 'first_aid': '1 action'}, 'per_patient_per_day': 1,
        'kit': 'item.tool.kit (healer\'s): a Precision lever; one use', 'self': 'a Precision snag; never surgery; never while Dying',
        'reach_wounds': {1: 'the worst wound is treated_today', 2: 'every wound at or below the framed tier is treated_today; S2 wounds heal now; bleeding ends',
                         3: 'as 2, and each of those recovery clocks gains 1 tick now', 4: 'as 3, and the patient\'s next dying or stage check holds a Precision lever'},
        'reach_affliction': {1: "the patient's next stage check holds a Precision lever", 2: 'as 1', 3: 'as 1, and the affliction falls one stage now', 4: 'as 3'},
        'stakes': {'S2': 'safe', 'S3': 'safe', 'affliction': 'safe', 'S4': 'risky', 'S5': 'risky'},
        'threatened_cost': 'cost.harm to the patient (lethal: false, no reduction)', 'alternate_cost': 'cost.time',
        'surgery_critical_failure': 'cost.closed_door: this tender may not operate on this wound again',
        'restores_vitality': False, 'counts_toward_healing_cap': False, 'basis': B('07.8.8', '07.8.9', '05.7.8', 'DL-07-13')},
    'fatigue': {
        'counter': 'watches_awake', 'reset_by': 'a long rest of partial or full quality (interrupted: set to 2)',
        'thresholds': [{'watches_awake': 4, 'effect': '+1 cond.exhausted'}, {'watches_awake': 6, 'effect': '+1 cond.exhausted'},
                       {'watches_awake': 8, 'effect': '+1 cond.exhausted'},
                       {'watches_awake': 'each beyond 8', 'effect': 'apply_harm S2, lethal: false, no_reduction: true; at 0 Vitality: Down (asleep)'}],
        'push_on': {'verb': 'verb.endure', 'attribute': 'endurance', 'dc_tier': ['moderate', 'hard (one stack held)', 'very_hard (two stacks held)'],
                    'result': 'the stack is deferred by delivered reach watches (01.18.15)'},
        'want': {'applied_by': 'h.10.supply: one stack per day without food or water', 'at_three_stacks': 'the deprivation warning fires (07.3.3)',
                 'beyond_three': 'each further stack is S3 harm, no reduction, lethal once the warning is effective'},
        'exhausted_confirmed': {'stacking': 'intensify', 'max_stacks': 3, 'per_stack': '-1 status on all checks', 'at_three': 'cond.slowed',
                                'also_added_by': '05.6.6 overdraw'},
        'handler': 'h.07.fatigue', 'basis': B('07.8.10', 'R5 HR-07', '06 T-06-10', '05.6.6')},
    'hazard_bands': [
        {'severity': 'S1', 'harm': 1, 'effect_dc': 'easy', 'examples': ['nettles', 'a slap of hot wax', 'a tumble of a few feet'], 'boundary': 'a short fall onto stone (S1) / a 10-ft fall (S2)'},
        {'severity': 'S2', 'harm': 3, 'effect_dc': 'moderate', 'examples': ['a 10-ft fall', "a campfire's flames", 'a kick from a horse', 'a minute in freezing water'], 'boundary': 'a burning brand (S2) / a burning room (S3)'},
        {'severity': 'S3', 'harm': 5, 'effect_dc': 'hard', 'examples': ['a 20-ft fall', 'a burning room', 'a river in spate', 'a night in a blizzard without shelter'], 'boundary': 'a rockfall at its edge (S3) / under it (S4)'},
        {'severity': 'S4', 'harm': 8, 'effect_dc': 'very_hard', 'examples': ['a 40-ft fall', 'a collapsing roof', 'a lightning strike', 'boiling oil'], 'boundary': 'a 40-ft fall (S4) / an 80-ft fall (S5)', 'raises_warning': 'severity'},
        {'severity': 'S5', 'harm': 12, 'effect_dc': 'legendary', 'examples': ['an 80-ft fall', 'the heart of a great fire', 'a falling gate', 'a flow of molten rock'], 'raises_warning': 'severity'}],
    'falls': {'heights_ft': {10: 'S2', 20: 'S3', 40: 'S4', 80: 'S5'}, 'harm_tags': ['harm.physical.crush'], 'no_reduction': True, 'owner_of_heights': '06.5.8'},
    'breath': {'held_rounds': '6 + 2 * endurance (minimum 2) + marks', 'then': 'cond.choking; at each turn_end an Endure check against moderate, hard, very_hard (one tier harder each round); a failure adds 1 more harm that turn',
               'ticks': 'periodic: at 0 Vitality each adds wound load', 'basis': B('07.10.4', '06 T-06-10 (cond.choking)')},
    'dread': {
        'quantity': 'dread {current, threshold}', 'visibility': 'shown', 'threshold': '8 + resolve + deltas of marks and haunts (minimum 4)',
        'sources': [
            {'id': 'dying_entered', 'units': 1, 'check': False}, {'id': 'threshold_reached', 'units': 2, 'check': False},
            {'id': 'companion_or_bond_dies_in_presence', 'severity': 'S3', 'check': True},
            {'id': 'first_sight_of_a_dread_adversary', 'severity': "the template's dread: S1..S4 (09)", 'check': True, 'per': 'scene'},
            {'id': 'captivity', 'severity': 'S2', 'check': True, 'per': 'week'},
            {'id': 'place_or_hazard_tagged_harm_mind_strain', 'severity': 'as listed (10)', 'check': True, 'per': 'its cadence'},
            {'id': 'effect', 'effect': 'eff.07.dread', 'check': 'as the effect states'}],
        'check': {'verb': 'verb.endure', 'attribute': 'resolve', 'dc': 'the tier matching the severity',
                  'critical_success': 'no dread; inured to that source kind until the season ends', 'success': 'no dread',
                  'failure': '+U(severity)', 'critical_failure': '+U(one rung heavier)'},
        'shaken': {'when': 'dread.current * 2 >= dread.threshold', 'effect': 'cond.frightened applied to the character is one rung heavier (to S3)'},
        'break': {'when': 'dread.current >= dread.threshold', 'test': {'verb': 'verb.endure', 'attribute': 'resolve', 'dc_tier': 'hard'},
                  'steeled': 'dread = floor(threshold / 2); cond.heartened S2 for the scene',
                  'haunt': 'the player picks one of three drawn kind: haunt entries; dread = 0; cond.frightened S2 toward the source for the scene'},
        'haunts_max': 3, 'fourth_break': 'career_end: the retirement procedure of ch.11 at the next scene_end; the character lives',
        'easing': {'long_rest_full': -1, 'solace_activity': -2, 'thread_completed_or_vow_kept': -2, 'week_of_downtime_in_a_haven': 'to 0'},
        'never': ['kills', 'takes control of the character', 'is moved by conduct strain (03) or by harm.mind.strain Vitality harm (05.6.6)'],
        'basis': B('07.11', '00.4.4', 'R6 C-R7', 'R5 HR-06', 'R: https://darkestdungeon.wiki.gg/wiki/Stress', 'R: https://cubicle7games.com/en_US/blog/the-one-ring-the-shadow', 'DL-07-15')},
    'companions': {
        'at_0_vitality': {'non_lethal_event': 'Down: unconscious for the scene, alive', 'lethal_event': 'bleeding out: clk.bleeding_out'},
        'stabilize': 'first aid against moderate (a kit: a Precision lever), or any Vitality-restoring effect',
        'after_down': 'wakes at scene_end at Vitality 1 with cond.wound_body S2',
        'after_bleeding_out': 'wakes after a long rest with cond.wound_body S3 on clk.wound_heavy; no attack-trait commands until healed',
        'wounds_carried': 1, 'marks': False, 'dread': False, 'last_chance_menu': False,
        'on_death': ['setback.companion_dead', 'the PC makes a dread check at S3', 'the opposing morale clock ticks -1 (06.11.3)', 'a chronicle line'],
        'left_behind': {'capture': 'a prisoner (a rescue lead)', 'ransom': 'a prisoner', 'rob': 'a prisoner', 'drag_to_lair': 'a prisoner', 'drive_off': 'left where it lies',
                        'leave': 'left where it lies', 'kill': 'dead with an effective lethal context; left for dead without'},
        'summoned_and_made': 'no ladder: at 0 Vitality it ends, as its working says',
        'basis': B('07.12', '00.17.1 Q8', 'R6 C-11')},
    'clock_templates': [
        clock('clk.wound_heavy', 'A Heavy wound mends', 'project', 4, 'public', [{'on': 'treat reach 3+ (07.8.8)', 'ticks': 1, 'condition': None}],
              [{'boundary': 'day', 'ticks': 'T-07-15', 'condition': 'rested_today / treated_today / bed_rest_today'}], None,
              {'effects': [E('eff.cleanse', condition_or_category='the wound\'s carrier', target='the bearer')], 'interrupting': False, 'then': 'close'},
              B('07.8.6', '07.8.7')),
        clock('clk.wound_grievous', 'A Grievous wound mends', 'project', 6, 'public', [{'on': 'treat reach 3+ (07.8.8)', 'ticks': 1, 'condition': None}],
              [{'boundary': 'day', 'ticks': 'T-07-15', 'condition': 'treated_today / bed_rest_today'}], None,
              {'effects': [E('eff.cleanse', condition_or_category='the wound\'s carrier', target='the bearer'),
                           E('eff.write_fact', subject='pc', predicate='marks', value='inj.scar.<family>')], 'interrupting': False, 'then': 'close'},
              B('07.8.6', '07.8.7')),
        clock('clk.wound_catastrophic', 'A Catastrophic wound mends', 'project', 12, 'public', [{'on': 'treat reach 3+ (07.8.8)', 'ticks': 1, 'condition': None}],
              [{'boundary': 'day', 'ticks': 'T-07-15', 'condition': 'treated_today / bed_rest_today; exists only after surgery'}], None,
              {'effects': [E('eff.cleanse', condition_or_category='the wound\'s carrier', target='the bearer'),
                           E('eff.write_fact', subject='pc', predicate='marks', value='inj.scar.<family>')], 'interrupting': False, 'then': 'close'},
              B('07.8.6', '07.8.7')),
        clock('clk.back_from_the_brink', 'Back from the brink', 'project', 4, 'public', [],
              [{'boundary': 'day', 'ticks': 'T-07-15 (as a Heavy wound)', 'condition': 'the oldest unhealed inj.the_brink only'}], None,
              {'effects': [E('eff.write_fact', subject='pc', predicate='wounds', value='remove one inj.the_brink')], 'interrupting': False, 'then': 'close'},
              B('07.2.8', '07.8.6')),
        clock('clk.bleeding_out', 'Bleeding out', 'countdown', 4, 'public', [{'on': 'a lethal harm event on the companion', 'ticks': 1, 'condition': None}],
              [{'boundary': 'round', 'ticks': 1, 'condition': None}], None,
              {'effects': [E('eff.write_fact', subject='the companion', predicate='exists', value='dead')], 'interrupting': False, 'then': 'close'},
              B('07.12.1', 'R6 C-11'), voided_by='stabilization'),
        clock('clk.captors_intent', "The captors' intent", 'countdown', 6, 'sensed', [],
              [{'boundary': 'day', 'ticks': 1, 'condition': 'the PC is held'}],
              {'stirring': ['the guards talk about someone who is coming', 'a meal better than a prisoner should get, or none at all'],
               'building': ['a clerk comes to look you over and writes something down', 'they move you to a cell nearer the door'],
               'imminent': ['irons are brought, and a cart is being harnessed', 'your name is called down the corridor']},
              {'effects': [E('eff.write_fact', subject='pc', predicate='captive_fate', value='carried out: trial | sale | sacrifice | interrogation | ransom | labor | the larder')],
               'interrupting': True, 'then': 'close'},
              B('07.6.3'), races_with='clk.out_of_their_hands'),
        clock('clk.larder', 'The larder', 'countdown', 4, 'sensed', [], [{'boundary': 'watch', 'ticks': 1, 'condition': 'the PC is in the lair'}],
              {'stirring': ['it sleeps, and you can hear it breathe', 'old bones, cracked for marrow'],
               'building': ['it wakes and noses among what it has stored', 'the young are restless'],
               'imminent': ['it comes to where you lie', 'it is hungry, and it is looking at you']},
              {'effects': [E('eff.deal_harm', severity='S4', harm_tags=['harm.physical'], target='the PC')], 'interrupting': True, 'then': 'reset'},
              B('T-07-11', '07.3.3'), lethal_on_complete=True),
        clock('clk.out_of_their_hands', 'Out of their hands', 'progress', 6, 'public',
              [{'on': 'a resolved beat that works an opening', 'ticks': 'delivered_reach', 'condition': None}], [], None,
              {'effects': [E('eff.write_fact', subject='pc', predicate='defeated.manner', value='none (free)')], 'interrupting': False, 'then': 'close'},
              B('07.6.3'), races_with='clk.captors_intent'),
        clock('clk.cache', 'What was taken', 'countdown', 6, 'hidden', [], [{'boundary': 'week', 'ticks': 1, 'condition': None}],
              {'stirring': ['a rumor: one of your things was seen', 'the taker is wearing or carrying something of yours'],
               'building': ['a rumor: a buyer has been asking', 'part of it has been moved'],
               'imminent': ['a rumor: it goes to market at the week\'s end', 'a rumor: a stranger has paid for the best of it']},
              {'effects': [E('eff.write_fact', subject='cache', predicate='dispersed', value='mundane items gone; signature items to named holders, each with a rumor')],
               'interrupting': False, 'then': 'close'},
              B('07.6.4')),
        clock('clk.deaths_debt', 'The debt comes due', 'countdown', 8, 'public', [], [{'boundary': 'week', 'ticks': 1, 'condition': 'the vow is unfulfilled'}], None,
              {'effects': [E('eff.07.affliction_shift', affliction='aff.deaths_debt', stages=1, target='the PC')], 'interrupting': False, 'then': 'reset'},
              B('07.5.5'), voided_by='the vow fulfilled'),
        clock('clk.grudge', 'They are not finished with you', 'danger', 6, 'hidden',
              [{'on': 'a rout from this victor', 'ticks': 'U(severity)', 'condition': None}], [{'boundary': 'week', 'ticks': 1, 'condition': None}],
              {'stirring': ['a rumor: they have been asking after you', 'tracks that are not yours, on your road'],
               'building': ['someone watches where you sleep', 'a warning left where you would find it'],
               'imminent': ['they are in the same town tonight', 'the way ahead is already held']},
              {'effects': [E('eff.summon', template="the victor's side, as an encounter", location="the PC's place", duration='scene')],
               'interrupting': True, 'then': 'close'},
              B('07.4.3'), starts_filled=2),
    ],
    'tables': [
        {'id': 'tbl.wound_site', 'name': 'Wound site', 'tags': [], 'die': 'd12', 'recency': False,
         'results': [{'range': '1-3', 'result': 'arm'}, {'range': '4-6', 'result': 'leg'}, {'range': '7-10', 'result': 'body'}, {'range': '11-12', 'result': 'head'}],
         'lifecycle': 'provisional', 'basis': B('07.2.4')},
        {'id': 'tbl.captivity_openings', 'name': 'Openings in captivity', 'tags': [], 'die': 'd8', 'recency': True, 'draw': '3 without repeats',
         'results': [{'range': '1', 'result': 'a careless or bribable guard (a named walk-on with a want)'},
                     {'range': '2', 'result': 'a bond or bar that can be worked (an obstacle with a stored tier)'},
                     {'range': '3', 'result': 'an ally or rival of the captors who wants the PC free (a named NPC who will come)'},
                     {'range': '4', 'result': 'a fellow prisoner who knows the place (a named NPC; a map in words)'},
                     {'range': '5', 'result': 'a leader who wants to talk (an audience at the next tick)'},
                     {'range': '6', 'result': "a transfer or change of the watch on the clock's next tick"},
                     {'range': '7', 'result': "something overlooked in the search (one concealable item of the PC's choice, if it held one)"},
                     {'range': '8', 'result': 'a noise outside: someone has come (11 supplies who)'}],
         'needs_no_roll_to_find': 'at least one of the three', 'lifecycle': 'provisional', 'basis': B('07.6.3', 'C:P16')},
        {'id': 'tbl.bargain_asks', 'name': "What the bargainer asks", 'tags': [], 'die': 'd6', 'recency': True,
         'results': [{'range': '1', 'result': 'return what was taken from it'}, {'range': '2', 'result': 'bring it a named person or thing'},
                     {'range': '3', 'result': 'end a named enemy of it'}, {'range': '4', 'result': 'serve it one season in four for a year'},
                     {'range': '5', 'result': 'carry its sign and its message to a named place'},
                     {'range': '6', 'result': 'give up a named bond or possession'}],
         'used_when': 'the bargainer has no recorded want the PC could fulfil', 'lifecycle': 'provisional', 'basis': B('07.5.5', 'R6 C-14')},
    ],
    'simulation_targets': {
        'script': 'rules/_process/simulation/07-harm-sim.py', 'writeup': 'rules/_process/simulation/07-harm-sim.md',
        'targets': ['one harm event from any Vitality above 0 ends at Staggered (exact)',
                    'fair fights against foes that kill, fighting to the end: the menu in <= 6 of 100; with an exit at Staggered <= 3',
                    'hard fights: <= 30 of 100 fighting on; <= 12 with an exit',
                    'a first fall left alone stabilizes >= 80%; a third <= 15%',
                    'Dying to full: median <= 2 days in a haven with a healer; <= 4 on the road alone'],
        'results': {'fair': {'dying': 7.1, 'menu': 5.0, 'menu_with_exit': 2.3}, 'hard': {'dying': 32.1, 'menu': 25.6, 'menu_with_exit': 10.5},
                    'lethal': {'dying': 83.5, 'menu': 80.0, 'menu_with_exit': 34.3}, 'first_fall_stabilizes': 85, 'third_fall_stabilizes': 11,
                    'recovery_median_days': {'haven': 2, 'road_treated': 2, 'road_untreated': 4}}},
}

HARM_HEADER = """# data/harm.yaml
# Purpose: chapter 07's ladder and procedures as data: Vitality, the harm states, wounds and wound load, Dying and the
#   stabilize DCs, brink, Down, the reduction cap, the Two-Key rule, the lethal-warning trigger and its plain words, the
#   exits card, Yield and Retreat, defeat dispositions and captivity, caches, the three rests and their quality, wound
#   recovery, treatment, fatigue, hazard bands, breath, dread, companion harm, clock templates and three tables.
# Owner: 07-harm-recovery-death. Schema: data/SCHEMAS.md#harmyaml (required keys: harm_states, dying, wounds,
#   reduction_cap, rests, lethal_warning, two_key). Optional keys added by ch.07 (documented in 07 Tables): vitality,
#   descriptors, defeated, brink, stabilized, down, others, reduction_sources, no_reduction, inheritance, exits, yield,
#   retreat, dispositions, defeat_always_writes, captivity, caches, rest_sites, rest_event_payload, recovery,
#   treatment, fatigue, hazard_bands, falls, breath, dread, companions, clock_templates, tables, simulation_targets.
# Numbers here are canonical for ch.07 (00.1.4 line 5). Generated and validated by
#   rules/_process/simulation/07-gen_data07.py.
# Basis: [07.1]-[07.12] [00.3.11-00.3.14] [INV-6] [00.17.1 Q1, Q8, Q9, Q15, Q16, Q18] [R6 C] [R4 6] [DL-07-01..18]
"""

# ----------------------------------------------------------------------------------------------- write
inj = wound_entries() + marks() + maims() + haunts()
write(os.path.join(D, 'injuries.yaml'), INJ_HEADER, '\n'.join(line(e) for e in inj) + '\n')
write(os.path.join(D, 'afflictions.yaml'), AFF_HEADER.rstrip('\n'), block(afflictions()))
write(os.path.join(D, 'last_chance.yaml'), LC_HEADER.rstrip('\n'), block(options()))
write(os.path.join(D, 'harm.yaml'), HARM_HEADER, block(HARM))
write(os.path.join(C, 'conditions.07.yaml'), COND_HEADER,
      '\n'.join('  ' + ln for ln in block(wound_conditions()).splitlines()) + '\n')
write(os.path.join(C, 'effects.07.yaml'), EFF_HEADER, '\n'.join('  ' + ln for ln in block(EFFECTS).splitlines()) + '\n')
hs = [{'id': h[0], 'boundary': h[1], 'phase': h[2], 'interrupting': h[3], 'effect': h[4], 'rule_id': h[5], 'status': h[6]} for h in HANDLERS]
hs[4]['before'] = ['h.05.focus_recover', 'h.05.rest_recharge']
write(os.path.join(C, 'boundaries.07.yaml'), BND_HEADER, '\n'.join('  ' + ln for ln in block(hs).splitlines()) + '\n')

# ----------------------------------------------------------------------------------------------- validate
L = lambda p: yaml.safe_load(io.open(p, encoding='utf-8'))
sub = L(os.path.join(D, 'substrate.yaml'))
eff_ids = {e['id'] for e in L(os.path.join(D, 'effects.yaml'))['core']}
for fn in os.listdir(C):
    if fn.startswith('effects.'):
        for b in L(os.path.join(C, fn))['blocks']:
            eff_ids |= {e['id'] for e in b['entries']}
cond_ids = {c['id'] for c in L(os.path.join(D, 'conditions.yaml'))['conditions']}
cond_ids |= {c['id'] for b in L(os.path.join(C, 'conditions.07.yaml'))['blocks'] for c in b['entries']}
ops = {o['id'] for o in sub['operations']}
tags = set()
tg = L(os.path.join(D, 'tags.yaml'))
for t in tg['tags']:
    tags.add(t['id'])
for f_ in tg['facets']:
    tags.add(f_['id'])
errors = []
seen = set()


def walk(o, where):
    if isinstance(o, dict):
        if 'effect_id' in o:
            if o['effect_id'] not in eff_ids:
                errors.append('%s: unknown effect %s' % (where, o['effect_id']))
            c = o.get('params', {}).get('condition')
            if c and c not in cond_ids:
                errors.append('%s: unknown condition %s' % (where, c))
        for v in o.values():
            walk(v, where)
    elif isinstance(o, list):
        for v in o:
            walk(v, where)


def check_entries(entries, where, need=('id', 'name', 'tags', 'lifecycle', 'basis')):
    for e in entries:
        for k in need:
            if k not in e:
                errors.append('%s %s: missing %s' % (where, e.get('id'), k))
        if e['id'] in seen:
            errors.append('duplicate id ' + e['id'])
        seen.add(e['id'])
        for t in e.get('tags', []) + e.get('harm_tags', []):
            if t not in tags:
                errors.append('%s %s: unknown tag %s' % (where, e['id'], t))
        for t in e.get('gate_tags', []):
            if t not in tags and t not in ('any', 'bargain'):
                errors.append('%s %s: unknown gate tag %s' % (where, e['id'], t))
        walk(e, '%s %s' % (where, e['id']))


inj_l = L(os.path.join(D, 'injuries.yaml'))['injuries']
check_entries(inj_l, 'injuries')
aff_l = L(os.path.join(D, 'afflictions.yaml'))['afflictions']
check_entries(aff_l, 'afflictions')
for a in aff_l:
    for s in a['stages']:
        if s['condition'] not in cond_ids:
            errors.append('%s stage %s: unknown carrier %s' % (a['id'], s['stage'], s['condition']))
    if a['lethal'] and not a['warn_stage']:
        errors.append('%s: lethal without warn_stage' % a['id'])
lc = L(os.path.join(D, 'last_chance.yaml'))
check_entries(lc['options'], 'last_chance')
alive_always = [o for o in lc['options'] if o.get('always_available') and o['death'] is False]
if len([o for o in lc['options'] if o.get('always_available')]) < 3 or not alive_always:
    errors.append('last_chance: the always-available set does not guarantee three options with one survival')
hm = L(os.path.join(D, 'harm.yaml'))
for k in ('harm_states', 'dying', 'wounds', 'reduction_cap', 'rests', 'lethal_warning', 'two_key'):
    if k not in hm:
        errors.append('harm.yaml: missing required key ' + k)
check_entries(hm['harm_states'], 'harm_states')
check_entries(hm['rests'], 'rests')
check_entries(hm['dispositions'], 'dispositions')
check_entries(hm['clock_templates'], 'clock_templates', need=('id', 'name', 'kind', 'segments', 'visibility', 'lifecycle', 'basis'))
check_entries(hm['tables'], 'tables')
for c in hm['clock_templates']:
    if c['segments'] not in (4, 6, 8, 12):
        errors.append('%s: bad clock size' % c['id'])
    if c['kind'] not in sub['reserved_ids']['clock_kinds']:
        errors.append('%s: bad clock kind' % c['id'])
    if c['visibility'] != 'public':
        for stg in ('stirring', 'building', 'imminent'):
            if not c['omens'] or len(c['omens'].get(stg, [])) < 2:
                errors.append('%s: fewer than two omens for %s' % (c['id'], stg))
if not 0 <= hm['reduction_cap'] <= 4:
    errors.append('reduction cap outside envelope')
if not 2 <= hm['dying']['steps'] <= 4:
    errors.append('dying steps outside envelope')
for b in L(os.path.join(C, 'conditions.07.yaml'))['blocks']:
    for c in b['entries']:
        if c['stacking'] not in [s['id'] for s in sub['condition_stacking']]:
            errors.append('%s: bad stacking' % c['id'])
        if c['category'] not in sub['condition_categories']:
            errors.append('%s: bad category' % c['id'])
        walk(c, c['id'])
for b in L(os.path.join(C, 'effects.07.yaml'))['blocks']:
    for e in b['entries']:
        if e['op'] not in ops:
            errors.append('%s: op %s not in the closed list' % (e['id'], e['op']))
bd = L(os.path.join(D, 'boundaries.yaml'))['boundaries']
allb = set(bd['time']) | set(bd['event'])
for b in L(os.path.join(C, 'boundaries.07.yaml'))['blocks']:
    for h in b['handlers']:
        bs = h['boundary'] if isinstance(h['boundary'], list) else [h['boundary']]
        for x in bs:
            if x not in allb:
                errors.append('%s: unknown boundary %s' % (h['id'], x))
        if not 1 <= h['phase'] <= 9:
            errors.append('%s: bad phase' % h['id'])

kinds = {}
for e in inj_l:
    kinds[e['kind']] = kinds.get(e['kind'], 0) + 1
print('injuries.yaml      :', len(inj_l), 'entries', kinds)
print('afflictions.yaml   :', len(aff_l), 'entries',
      {k: sum(1 for a in aff_l if a['kind'] == k) for k in ('poison', 'disease', 'curse')},
      'lethal:', sum(1 for a in aff_l if a['lethal']))
print('last_chance.yaml   :', len(lc['options']), 'options; always available:',
      [o['id'] for o in lc['options'] if o.get('always_available')])
print('harm.yaml          :', len(hm), 'keys;', len(hm['clock_templates']), 'clock templates;', len(hm['tables']), 'tables;',
      len(hm['dispositions']), 'dispositions')
print('contrib            : 6 conditions, %d effects, %d handlers' % (len(EFFECTS), len(HANDLERS)))
print('errors             :', len(errors))
for x in errors:
    print('  -', x)
