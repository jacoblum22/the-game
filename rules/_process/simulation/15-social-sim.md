# 15 — Social calibration simulation

Script: `15-social-sim.py` (output: `15-social-sim-output.txt`). Method: exhaustive enumeration of the d20
under 01.8.1 (critical bands ±10, natural 20/1 one-step shift, near miss = failure with margin ≥ −3) for
the DC grid; Monte Carlo (40,000 seeded runs per cell) for persuasion campaigns.

Inputs (15.1.2, 15.3.2, 15.8.1): standing DC mods +5/+3/+1/0/−1/−3/−5; request mods R1 +0, R2 +2,
R3 +5, R4 +8, R5 +10. The script's `CEIL` table matches T-15-1, writing Hostile's "R1 only with a term" as 0 (so R1 is starred).
The first campaign block is a discarded draft (beat DC at R2 for every standing);
"Campaign v2" is the shipped rule (beat DC at the rung below the target, clocks 4/4/6/8 and patience
4/6/6/8).

Used in the chapter: T-15-3 (at-ceiling requests DC 11–15 for a defense of 10); 15.8.1's calibration line
(a P1 talker, +5, against defense 10 wins 98–100% with 7–30% of wins carrying a compromise; against
defense 16, 39–89% with 37–76% compromises; an untrained PC, +1, against defense 13, 27–83%).

```
T-15 grid: DC for defense 10 (commoner) at each standing x request (ceiling marked), success-or-better % at +1/+5/+9
Hostile    R1*:15(35/55/75)  R2*:17(25/45/65)  R3*:20(10/30/50)  R4*:23(5/15/35)  R5*:25(5/5/25)
Unfriendly R1:13(45/65/85)  R2*:15(35/55/75)  R3*:18(20/40/60)  R4*:21(5/25/45)  R5*:23(5/15/35)
Wary       R1:11(55/75/95)  R2*:13(45/65/85)  R3*:16(30/50/70)  R4*:19(15/35/55)  R5*:21(5/25/45)
Neutral    R1:10(60/80/95)  R2:12(50/70/90)  R3*:15(35/55/75)  R4*:18(20/40/60)  R5*:20(10/30/50)
Warm       R1:9(65/85/95)  R2:11(55/75/95)  R3:14(40/60/80)  R4*:17(25/45/65)  R5*:19(15/35/55)
Friendly   R1:7(75/95/95)  R2:9(65/85/95)  R3:12(50/70/90)  R4:15(35/55/75)  R5*:17(25/45/65)
Devoted    R1:5(85/95/95)  R2:7(75/95/95)  R3:10(60/80/95)  R4:13(45/65/85)  R5:15(35/55/75)

Persuasion campaign (defense 10/13/16), win% / compromise share / mean beats
Wary 4 clk 4 d10+1:82/44/3.0 d10+5:97/23/2.5 d10+9:99/10/2.1 d13+1:55/58/3.1 d13+5:90/39/2.9 d13+9:98/19/2.3 d16+1:28/71/3.0 d16+5:65/54/3.0 d16+9:93/33/2.7
Wary 4 clk 6 d10+1:66/60/4.0 d10+5:92/36/3.6 d10+9:99/15/3.0 d13+1:33/71/3.8 d13+5:77/55/4.1 d13+9:95/30/3.4 d16+1:10/81/3.3 d16+5:43/67/3.9 d16+9:84/49/3.9
Wary 4 clk 8 d10+1:49/70/4.8 d10+5:86/46/4.6 d10+9:98/20/3.8 d13+1:17/80/4.1 d13+5:63/66/5.0 d13+9:91/38/4.4 d16+1:4/86/3.4 d16+5:26/77/4.4 d16+9:72/61/4.9
Neutral 6 clk 4 d10+1:98/23/3.0 d10+5:100/7/2.3 d10+9:100/2/2.1 d13+1:83/44/3.6 d13+5:99/18/2.8 d13+9:100/5/2.2 d16+1:55/60/3.9 d16+5:89/37/3.4 d16+9:99/14/2.7
Neutral 6 clk 6 d10+1:93/38/4.5 d10+5:99/14/3.5 d10+9:100/3/3.0 d13+1:65/60/4.8 d13+5:96/32/4.2 d13+9:100/10/3.2 d16+1:30/74/4.8 d16+5:76/54/4.8 d16+9:98/25/3.9
Neutral 6 clk 8 d10+1:86/53/5.8 d10+5:99/22/4.5 d10+9:100/5/3.8 d13+1:48/72/5.8 d13+5:91/45/5.5 d13+9:99/15/4.2 d16+1:15/82/5.2 d16+5:60/66/5.8 d16+9:95/37/5.2
Warm 6 clk 4 d10+1:99/18/2.8 d10+5:100/5/2.2 d10+9:100/1/2.1 d13+1:89/37/3.4 d13+5:99/14/2.7 d13+9:100/3/2.1 d16+1:65/54/3.8 d16+5:94/30/3.2 d16+9:100/10/2.5
Warm 6 clk 6 d10+1:96/32/4.2 d10+5:100/10/3.2 d10+9:100/1/2.9 d13+1:76/54/4.8 d13+5:98/25/3.9 d13+9:100/7/3.0 d16+1:42/69/4.8 d16+5:85/47/4.6 d16+9:99/19/3.7
Warm 6 clk 8 d10+1:91/45/5.5 d10+5:99/15/4.2 d10+9:100/2/3.7 d13+1:60/66/5.8 d13+5:95/37/5.2 d13+9:100/10/4.0 d16+1:24/79/5.4 d16+5:74/60/5.9 d16+9:97/29/4.8
Friendly 8 clk 4 d10+1:100/4/2.5 d10+5:100/1/2.1 d10+9:100/0/2.0 d13+1:99/12/3.1 d13+5:100/3/2.4 d13+9:100/1/2.1 d16+1:92/34/3.8 d16+5:100/9/2.9 d16+9:100/2/2.2
Friendly 8 clk 6 d10+1:100/9/3.7 d10+5:100/2/3.0 d10+9:100/0/2.7 d13+1:98/25/4.6 d13+5:100/6/3.5 d13+9:100/1/3.0 d16+1:80/51/5.4 d16+5:99/19/4.3 d16+9:100/4/3.2
Friendly 8 clk 8 d10+1:99/16/4.9 d10+5:100/3/3.9 d10+9:100/0/3.4 d13+1:95/38/6.0 d13+5:100/10/4.5 d13+9:100/2/3.8 d16+1:66/65/6.7 d16+5:98/30/5.6 d16+9:100/7/4.2

Campaign v2: beat DC = defense + standing + REQ[ceiling]; clock by target rung (R2 4, R3 4, R4 6, R5 8); patience Wary4 Neutral6 Warm6 Friendly8
Wary ->R2 d10(DC11)+1:93/33/2.7 d10(DC11)+5:99/15/2.2 d10(DC11)+9:99/9/2.1 d13(DC14)+1:74/49/3.0 d13(DC14)+5:95/28/2.6 d13(DC14)+9:99/11/2.1 d16(DC17)+1:46/62/3.0 d16(DC17)+5:82/44/2.9 d16(DC17)+9:97/23/2.5
Neutral ->R3 d10(DC12)+1:98/23/3.0 d10(DC12)+5:100/7/2.3 d10(DC12)+9:100/2/2.1 d13(DC15)+1:83/43/3.5 d13(DC15)+5:99/18/2.8 d13(DC15)+9:100/5/2.2 d16(DC18)+1:55/59/3.9 d16(DC18)+5:89/37/3.4 d16(DC18)+9:99/14/2.7
Warm ->R4 d10(DC14)+1:76/54/4.8 d10(DC14)+5:98/25/3.9 d10(DC14)+9:100/7/3.0 d13(DC17)+1:42/70/4.8 d13(DC17)+5:86/47/4.6 d13(DC17)+9:99/19/3.7 d16(DC20)+1:13/81/4.5 d16(DC20)+5:54/65/4.9 d16(DC20)+9:93/39/4.5
Friendly ->R5 d10(DC15)+1:66/65/6.7 d10(DC15)+5:98/30/5.6 d10(DC15)+9:100/6/4.2 d13(DC18)+1:27/80/6.5 d13(DC18)+5:79/57/6.5 d13(DC18)+9:99/22/5.2 d16(DC21)+1:5/87/5.7 d16(DC21)+5:39/76/6.7 d16(DC21)+9:88/49/6.3
```
