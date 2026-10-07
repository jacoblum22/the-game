# dsl05.py -- authoring vocabulary for data/abilities.yaml (chapter 05).
# Each effect constructor returns (effect_ref, effect_units). Effect units (EU) are the power-budget
# currency of rule 05.11; the table EU_TABLE below is rendered into the chapter as T-05-9.
# An ability row is individually authored; this module only removes repetition and lets the generator
# check ids, parameter ranges and budgets mechanically.

HARM_EU = {1: 1, 2: 2, 3: 3, 4: 5, 5: 7}
HEAL_EU = {1: 1, 3: 2, 5: 3, 8: 5}
COND_LIGHT = {'cond.off_balance', 'cond.distracted', 'cond.exposed', 'cond.slowed', 'cond.deafened', 'cond.chilled'}
COND_MID = {'cond.prone', 'cond.weakened', 'cond.frightened', 'cond.blinded', 'cond.grabbed',
            'cond.dazed', 'cond.choking', 'cond.poisoned', 'cond.exhausted'}
# Lingering harm: conditions whose whole effect is 1 Vitality per stack at the bearer's turn end, ended by one action
# of the bearer. Priced by 06-conflict-sim.py K1 (the bearer answering at its best) [revision: I-033].
COND_DOT = {'cond.burning', 'cond.bleeding'}
COND_HARD = {'cond.stunned', 'cond.restrained', 'cond.charmed', 'cond.unconscious', 'cond.pinned', 'cond.frozen'}
SHORT = ('beat', 'rounds:1', 'uses:1')

EU_TABLE = [
    ("Check edge +1 / +2 in a stated circumstance", "2 / 4", "eff.check_edge, eff.defense_edge, eff.effect_dc_edge"),
    ("Lever for one beat or one round", "1", "eff.grant_lever"),
    ("Lever that stands for a scene, or whenever a stated circumstance holds", "2", "eff.grant_lever"),
    ("Reach +1 rung; stakes -1 rung", "2 each", "eff.reach_step, eff.stakes_step"),
    ("Harm S1 / S2 / S3 / S4 / S5 to one target", "1 / 2 / 3 / 5 / 7", "eff.deal_harm"),
    ("Harm severity +1 rung on your own attack", "2", "eff.harm_severity_step"),
    ("Harm edge +1 / +2", "1 / 2", "eff.harm_edge"),
    ("Strike or spell delivery changed (harm type, form)", "1 (+ its harm edge)", "eff.strike_delivery, eff.05.spell_delivery"),
    ("Each target beyond the first (through a spread tag)", "1", "spread"),
    ("Condition, light group (off_balance, distracted, exposed, slowed, deafened, chilled)", "1 (+1 if it lasts beyond a round)", "eff.apply_condition"),
    ("Condition, middle group (prone, weakened, frightened, blinded, grabbed, dazed, choking, poisoned, exhausted)", "2 (+1 beyond a round)", "eff.apply_condition"),
    ("Condition, lingering harm (burning, bleeding: harm at the bearer's turn end, which one action of the bearer ends), per stack applied", "1, whatever its duration", "eff.apply_condition"),
    ("Condition, hard-control group (stunned, restrained, charmed, unconscious, pinned, frozen)", "4 (+1 beyond a round)", "eff.apply_condition"),
    ("Harm reduction 1 for one harm branch / for all physical harm or several branches", "1 / 2 per point", "eff.harm_reduction"),
    ("Resistance (halve) one harm branch", "3", "eff.harm_resistance"),
    ("Hazards of a kind count one rung lower", "2", "eff.hazard_step"),
    ("Negate one hit; negate one working", "4", "eff.prevent_hit, eff.05.counter_working"),
    ("Take a hit meant for another", "2", "eff.intercept"),
    ("End a condition; end a magical effect", "2 / 3", "eff.cleanse, eff.05.end_working"),
    ("Immunity to one named condition; a restriction placed on a target", "2", "eff.condition_immunity, eff.restrict"),
    ("Restore Vitality 1 / 3 / 5 / 8", "1 / 2 / 3 / 5", "eff.restore"),
    ("Restore or drain 1 Focus; return one use of an ability", "2", "eff.restore, eff.drain, eff.05.refresh_use"),
    ("Maximum Vitality or Focus +1", "2", "eff.max_modify"),
    ("Focus cost -1 in a stated circumstance", "2", "eff.focus_cost_step"),
    ("Move self or a target one band; add or clear one positional flag", "1 each", "eff.reposition"),
    ("Movement mode: climb or swim / burrow / fly", "2 / 3 / 4", "eff.movement_mode"),
    ("Another shape", "4", "eff.body_form"),
    ("One more reaction per round", "3", "eff.reaction_grant"),
    ("Tick a clock by 1 / by delivered reach", "1 / 2", "eff.tick_clock"),
    ("Reveal one sealed fact or tell", "2", "eff.reveal"),
    ("Bring a helper or object into being (threat band B)", "2 x B", "eff.summon"),
    ("Establish a fact (a mark, a sign, a bond)", "1", "eff.write_fact"),
    ("A temporary license for another, or a method beyond the basic verbs (ordinary / world-bending)", "2 / 4", "eff.grant_license, Permission scope"),
]


def _e(eid, eu, **params):
    return ({'effect_id': eid, 'params': params}, eu)


def edge(n, when):
    return _e('eff.check_edge', 2 * n, amount=n, applies_when=when)


def dedge(n, attr, when):
    return _e('eff.defense_edge', 2 * n, amount=n, attribute=attr, applies_when=when)


def dcedge(n, when):
    return _e('eff.effect_dc_edge', 2 * n, amount=n, applies_when=when)


def lev(typ, when, dur='beat', verbs=None, tags=None):
    p = dict(type=typ, duration=dur, applies_when=when)
    if verbs:
        p['for_verbs'] = verbs
    if tags:
        p['for_tags'] = tags
    return _e('eff.grant_lever', 1 if dur in SHORT else 2, **p)


def reach(when):
    return _e('eff.reach_step', 2, ladder='reach', steps=1, applies_when=when)


def stakes(when):
    return _e('eff.stakes_step', 2, ladder='stakes', steps=-1, applies_when=when)


def hedge(n, when):
    return _e('eff.harm_edge', n, amount=n, applies_when=when)


def sev(n, when):
    return _e('eff.harm_severity_step', 2 * abs(n), ladder='severity', steps=n, applies_when=when)


def harm(S, tags, target):
    return _e('eff.deal_harm', HARM_EU[S], severity='S%d' % S, harm_tags=tags, target=target)


def sdel(tags, he, dur, rank=10):
    return _e('eff.strike_delivery', 1 + he, priority_rank=rank, harm_tags=tags, harm_edge=he, duration=dur,
              cosmetic_merge=False)


def red(n, tags):
    broad = ('harm.physical' in tags) or len(tags) > 1
    return _e('eff.harm_reduction', n * (2 if broad else 1), amount=n, harm_tags=tags)


def resist(tags):
    return _e('eff.harm_resistance', 3, factor=0.5, harm_tags=tags)


def hazard(tags):
    return _e('eff.hazard_step', 2, ladder='severity', steps=-1, harm_tags=tags, applies_when='hazard')


def prevent(when, per=None, uses=1):
    p = dict(applies_when=when)
    if per:
        p['limits'] = {'per': per, 'uses': uses}
    return _e('eff.prevent_hit', 4, **p)


def intercept(when='an ally engaged with you is hit'):
    return _e('eff.intercept', 2, new_target='self', applies_when=when)


def cond(c, S, dur, target):
    if c in COND_DOT:                                   # lingering harm: 1 per stack, any duration [revision: I-033]
        return _e('eff.apply_condition', 1, condition=c, severity='S%d' % S, duration=dur, target=target)
    base = 1 if c in COND_LIGHT else 2 if c in COND_MID else 4
    return _e('eff.apply_condition', base + (0 if dur in SHORT else 1), condition=c, severity='S%d' % S,
              duration=dur, target=target)


def cleanse(what, target):
    return _e('eff.cleanse', 2, condition_or_category=what, target=target)


def immune(conds):
    return _e('eff.condition_immunity', 2 * len(conds), forbid={'conditions': conds}, target='self')


def restr(forbid, target, dur):
    return _e('eff.restrict', 2, forbid=forbid, target=target, duration=dur)


def heal(units, target):
    return _e('eff.restore', HEAL_EU[units], quantity='vitality', units=units, target=target)


def foc(units, target='self'):
    return _e('eff.restore', 2 * units, quantity='focus', units=units, target=target)


def drain(units, target):
    return _e('eff.drain', 2 * units, quantity='focus', units=units, target=target)


def maxm(q, n):
    return _e('eff.max_modify', 2 * n, quantity=q, amount=n)


def fstep(n, when):
    return _e('eff.focus_cost_step', 2 * abs(n), amount=n, applies_when=when)


def glic(lic, grade, dur, big=False):
    return _e('eff.grant_license', 4 if big else 2, license=lic, grade=grade, duration=dur)


def mode(m, dur, rank=10):
    return _e('eff.movement_mode', {'climb': 2, 'swim': 2, 'burrow': 3, 'fly': 4}[m], priority_rank=rank, mode=m,
              duration=dur)


def stance(form, inner, rank=10):
    return _e('eff.stance', sum(x[1] for x in inner), priority_rank=rank, form=form, effects=[x[0] for x in inner])


def aura(band, inner, rank=10):
    return _e('eff.aura', 1 + sum(x[1] for x in inner), priority_rank=rank, band=band, effects=[x[0] for x in inner])


def bform(template, dur, rank=10):
    return _e('eff.body_form', 4, priority_rank=rank, template=template, duration=dur)


def react(when):
    return _e('eff.reaction_grant', 3, reactions=1, applies_when=when)


def move(target, bands, add=None, rem=None):
    add = add or []
    rem = rem or []
    return _e('eff.reposition', abs(bands) + len(add) + len(rem), target=target, band_change=bands, flags_add=add,
              flags_remove=rem)


def tick(clock, ticks):
    return _e('eff.tick_clock', 1 if ticks == 1 else 2, clock=clock, ticks=ticks)


def rev(ref):
    return _e('eff.reveal', 2, sealed_ref=ref)


def summ(template, band, dur, location='within band.close of you'):
    return _e('eff.summon', 2 * band, template=template, location=location, duration=dur)


def fchk(verb, source='your effect DC', table='01.18.3'):
    return _e('eff.force_check', 0, verb=verb, effect_dc_source=source, degree_table=table)


def fact(s, p, v):
    return _e('eff.write_fact', 1, subject=s, predicate=p, value=v)


def spdel(form, dur='instant', rank=10):
    return _e('eff.05.spell_delivery', 1, priority_rank=rank, form=form, duration=dur, cosmetic_merge=False)


def dreact(form, inner, rank=10):
    return _e('eff.05.defense_reaction', sum(x[1] for x in inner), priority_rank=rank, form=form,
              effects=[x[0] for x in inner])


def refr(ability, uses=1):
    return _e('eff.05.refresh_use', 2 * uses, ability=ability, uses=uses)


def ctr(when):
    return _e('eff.05.counter_working', 4, applies_when=when)


def endw(target):
    return _e('eff.05.end_working', 3, target=target)


def perm(eu=2):
    """A Permission's scope itself: no effect reference; the method is licensed by the text."""
    return (None, eu)


def tgt(n):
    """n targets beyond the first, delivered by the ability's spread tag."""
    return (None, n)



def harmw(step, target):
    """The wielded weapon's own harm, shifted by `step` severity rungs (weapon base is S2 for costing)."""
    sevtxt = 'weapon base' if step == 0 else 'weapon base %+d rung%s' % (step, '' if abs(step) == 1 else 's')
    return _e('eff.deal_harm', {-1: 1, 0: 2, 1: 3, 2: 5}[step], severity=sevtxt, harm_tags=["the weapon's harm tags"], target=target)


def waive(what, when):
    """An Exception: one named snag, provoked reaction or restriction does not apply."""
    return _e('eff.05.waive', 2, event_kind=what, applies_when=when)


def rk(text, effects, f=0, per=None, uses=1):
    return dict(text=text, effects=effects, f=f, per=per, uses=uses)


ABILITIES = []


def ab(id, name, tag, mt, grp, form, timing, principle, limitation, ranks, **kw):
    d = dict(id=id, name=name, tag=tag, mt=mt, grp=grp, form=form, timing=timing, principle=principle,
             limitation=limitation, ranks=ranks)
    d.update(kw)
    ABILITIES.append(d)
    return d
