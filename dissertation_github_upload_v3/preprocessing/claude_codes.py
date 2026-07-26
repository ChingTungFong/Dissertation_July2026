"""
Claude's independent coding of the 200 validation comments.
Format: comment_index -> (benign_envy, malicious_envy, psi, purchase_intent)
"""
CLAUDE_CODES = {
    # 0-9
    0: (0, 0, 0, 0),   # name list
    1: (0, 0, 0, 0),   # "loving this" — too vague for PSI
    2: (0, 0, 0, 0),   # recommendation, not personal closeness
    3: (0, 1, 0, 0),   # "PR lessons from Jaclyn Hill" — sarcastic
    4: (0, 0, 0, 0),   # recommendation
    5: (0, 0, 0, 0),   # name list
    6: (0, 0, 0, 0),   # product list
    7: (0, 0, 0, 0),   # neutral reference
    8: (0, 0, 1, 0),   # "She is great! ❤️" — affection with heart
    9: (0, 0, 0, 0),   # learned tip, neutral
    # 10-19
    10: (0, 0, 0, 0),  # hostility is at the brand/Mikayla, not Jackie Aina
    11: (0, 0, 0, 0),  # product list
    12: (0, 0, 0, 0),  # positive about her work, not parasocial
    13: (0, 0, 0, 0),  # criticism is at Sara, not Kelly
    14: (0, 0, 0, 0),  # "all time fave" is about palette
    15: (0, 0, 1, 0),  # "I adore Lauren Mae, Julia Adams, and Amanda Z"
    16: (0, 0, 0, 0),  # recommendation
    17: (0, 0, 0, 0),  # tangential mention
    18: (0, 0, 0, 0),  # product list
    19: (0, 1, 0, 0),  # critical of Theresa's "I HAVE to buy it" attitude
    # 20-29
    20: (0, 0, 0, 0),  # product compliment
    21: (0, 0, 0, 0),  # neutral
    22: (0, 0, 0, 0),  # mild negative, not malicious
    23: (0, 0, 1, 0),  # "She was so fun" + "I miss her" — personal connection
    24: (0, 0, 0, 1),  # "I get the urge to try them"
    25: (0, 0, 0, 0),  # nostalgia, mild
    26: (0, 0, 0, 0),  # recommendation
    27: (1, 0, 0, 0),  # "I'm like Nikkie Tutorials" — identification/aspiration
    28: (0, 0, 0, 0),  # product list
    29: (0, 0, 0, 0),  # product mention
    # 30-39
    30: (0, 0, 0, 0),  # critique of recommendation videos, mild
    31: (0, 1, 0, 0),  # sarcastic critique of Jaclyn
    32: (0, 0, 0, 0),  # critique of trend, mild
    33: (0, 1, 0, 0),  # "gave me the ick"
    34: (0, 0, 0, 0),  # recommendation
    35: (0, 0, 0, 0),  # name list
    36: (0, 0, 0, 0),  # playful, not hostile
    37: (0, 0, 0, 0),  # recommendation
    38: (0, 0, 0, 0),  # name list
    39: (0, 0, 0, 0),  # criticism is at Jen, not Jaclyn
    # 40-49
    40: (0, 0, 0, 0),  # speculation, analytical
    41: (0, 0, 0, 0),  # product list
    42: (0, 0, 1, 0),  # "Jackie Aina has literally never lead me astray" — personal trust
    43: (0, 0, 0, 0),  # mild critique
    44: (0, 0, 0, 0),  # dismissive but neutral
    45: (0, 0, 0, 1),  # "she damn near sold me" — purchase pull
    46: (0, 0, 0, 0),  # product list
    47: (1, 0, 1, 0),  # "I love HLP in so many ways" — affection + admiration
    48: (0, 0, 1, 0),  # "I hope she's doing well" — personal concern
    49: (0, 0, 0, 0),  # disappointment in brand, not Jackie
    # 50-59
    50: (0, 1, 0, 0),  # "left Jaclyn Hill in 2019" — sarcastic dismissal
    51: (1, 0, 1, 0),  # "channels that feel like a big sister" + identifies with Julia/Emily etc
    52: (0, 0, 0, 0),  # product list
    53: (0, 0, 0, 0),  # neutral tutorial mention
    54: (0, 0, 0, 0),  # about another creator
    55: (0, 0, 1, 0),  # "Sad when that happens... with jaclyn hill and me" — personal
    56: (0, 0, 0, 0),  # factual reference
    57: (0, 0, 0, 0),  # product list
    58: (0, 0, 0, 0),  # name list
    59: (0, 0, 0, 0),  # critique is of retailers, brief Jaclyn mention
    # 60-69
    60: (0, 0, 0, 0),  # already purchased, no present urgency
    61: (0, 0, 0, 0),  # mild recognition
    62: (0, 0, 0, 0),  # product reference
    63: (0, 0, 1, 0),  # "Lauren Mae 🥲" — emotional emoji of affection
    64: (0, 0, 0, 0),  # praise of skill, not personal closeness
    65: (1, 0, 1, 0),  # "I LOVE Lauren Mae" + magic — strong affection + admiration
    66: (0, 0, 0, 0),  # product mention
    67: (0, 0, 0, 0),  # name list
    68: (0, 0, 0, 0),  # recommendation
    69: (0, 0, 0, 0),  # neutral
    # 70-79
    70: (0, 0, 0, 0),  # learned from her
    71: (0, 0, 1, 0),  # "she's easy to like"
    72: (0, 0, 0, 0),  # name list
    73: (0, 0, 0, 0),  # positive about content
    74: (0, 1, 0, 0),  # "Jaclyn deserves all the criticism"
    75: (0, 0, 0, 0),  # product brand list
    76: (0, 0, 0, 0),  # name list
    77: (0, 1, 0, 0),  # "browser extension to block Jaclyn Hill"
    78: (0, 0, 1, 0),  # "sweetest ones on YouTube" + nightly searching
    79: (0, 0, 1, 0),  # "really like her attitude"
    # 80-89
    80: (0, 0, 0, 0),  # neutral review compilation
    81: (0, 1, 0, 0),  # "Jaclyn Hill 2.0 with all her bullshit"
    82: (0, 0, 0, 0),  # "not a fan" mild
    83: (0, 0, 0, 0),  # positive about HLP's role
    84: (0, 0, 0, 0),  # product recommendation
    85: (0, 1, 0, 0),  # "had to stop following her" — dismissive
    86: (0, 0, 0, 0),  # product list
    87: (0, 0, 0, 0),  # critical concern, not affectionate
    88: (0, 0, 0, 0),  # product enthusiasm only
    89: (0, 0, 0, 0),  # curiosity
    # 90-99
    90: (0, 0, 0, 0),  # factual observation
    91: (0, 0, 0, 0),  # comparison
    92: (0, 0, 0, 0),  # neutral observation
    93: (0, 1, 0, 0),  # "shady things" critique of Jaclyn
    94: (0, 0, 1, 0),  # "great sense of humour" — personal warmth
    95: (0, 0, 0, 0),  # finds products via her, mild
    96: (0, 0, 0, 0),  # neutral mention
    97: (0, 0, 0, 0),  # reference
    98: (0, 0, 0, 0),  # critique of content style, mild
    99: (0, 0, 0, 0),  # names
    # 100-109
    100: (0, 0, 0, 0), # name list
    101: (0, 0, 0, 0), # name list
    102: (0, 0, 0, 0), # name list of brands boycotted, mild
    103: (0, 0, 0, 0), # praises review style
    104: (0, 0, 0, 0), # "not a fan of Jaclyn" but neutral here
    105: (0, 0, 0, 0), # critique of era style, mild
    106: (0, 0, 0, 0), # product review
    107: (0, 0, 0, 0), # nostalgia about palette
    108: (0, 0, 0, 0), # positive about content
    109: (0, 0, 0, 0), # neutral mention
    # 110-119
    110: (0, 0, 1, 1), # engaged with her content + likely purchase
    111: (0, 0, 0, 0), # product reference
    112: (0, 0, 1, 0), # "love her down to earth" + Julia Adams "gorgeous"
    113: (0, 0, 0, 0), # factual review reference
    114: (0, 0, 0, 0), # neutral viewing habits
    115: (0, 0, 1, 0), # defends Jackie ("just because she included his makeup")
    116: (0, 0, 1, 0), # defending Jackie from accusations
    117: (0, 0, 1, 0), # "I miss the old tutorials... I liked her a lot"
    118: (0, 0, 0, 0), # general advice
    119: (0, 0, 0, 0), # product list
    # 120-129
    120: (0, 0, 0, 0), # general recommendation
    121: (0, 1, 0, 0), # "how many awful people are in the beauty industry"
    122: (0, 0, 0, 0), # critical reference, mild
    123: (0, 0, 0, 0), # positive about her work, not parasocial
    124: (0, 0, 0, 0), # factual mention of Jaclyn lipsticks
    125: (0, 0, 0, 0), # name list
    126: (0, 0, 1, 0), # "really like YouTuber Hannah Louise Poston because of her stance"
    127: (0, 0, 0, 0), # recommendation
    128: (0, 0, 0, 0), # past use reference
    129: (0, 0, 0, 0), # name list
    # 130-139
    130: (0, 0, 0, 0), # similar undertones, mild identification
    131: (0, 0, 1, 0), # playful familiarity ("I'm always like 'please be the last'")
    132: (0, 0, 0, 0), # name only
    133: (1, 0, 0, 0), # "drawn to her style" — aspiration
    134: (0, 0, 0, 0), # palette critique
    135: (0, 1, 0, 0), # "didn't support her for a multitude of reasons" — critical
    136: (0, 0, 0, 0), # list of blue checks
    137: (0, 0, 1, 0), # "all amazing" — warmth
    138: (0, 0, 0, 0), # factual ("Kelly Gooch loves it")
    139: (0, 0, 0, 0), # product list
    # 140-149
    140: (0, 0, 1, 0), # "Julia Adams MUA is great!"
    141: (0, 1, 0, 0), # mild critique of her review style
    142: (0, 0, 0, 0), # factual
    143: (0, 0, 0, 0), # checks with her for reviews
    144: (0, 0, 0, 0), # product list
    145: (0, 1, 0, 0), # "Even Jackie Aina... is doing this shit"
    146: (0, 0, 0, 0), # name list
    147: (0, 0, 0, 0), # analytical about commenters
    148: (0, 0, 0, 0), # name list
    149: (0, 0, 0, 0), # general recommendation
    # 150-159
    150: (0, 0, 0, 0), # mild dismissive
    151: (0, 0, 0, 0), # recommendation list
    152: (0, 0, 1, 0), # "hilarious"
    153: (0, 0, 0, 0), # comparison about industry response
    154: (0, 0, 0, 0), # personal mention, mild
    155: (0, 0, 0, 0), # factual reference
    156: (0, 0, 0, 0), # advice about glasses, not Kackie
    157: (0, 0, 0, 0), # factual reference
    158: (0, 0, 0, 0), # past mention
    159: (0, 0, 0, 0), # name only
    # 160-169
    160: (0, 0, 0, 0), # historical reference list
    161: (0, 0, 0, 0), # fragment
    162: (0, 0, 0, 0), # nostalgic ASMR memory
    163: (0, 1, 0, 0), # "Karma for Morphe... Jaclyn turning into what she is now"
    164: (0, 1, 0, 0), # "full of herself it's shocking"
    165: (0, 0, 1, 0), # "I like her a lot"
    166: (0, 0, 0, 0), # foundation recommendation reference
    167: (0, 0, 0, 0), # name only
    168: (0, 0, 0, 0), # nostalgia
    169: (0, 0, 1, 0), # praise of past skills, personal
    # 170-179
    170: (0, 1, 0, 0), # "Too bad how she turned out"
    171: (0, 0, 0, 0), # thanks for tip
    172: (0, 0, 0, 0), # comparison
    173: (0, 0, 1, 0), # re-followed HLP, "a lot funner to watch"
    174: (0, 0, 0, 0), # analytical critique, mild
    175: (0, 0, 0, 0), # product review
    176: (0, 0, 0, 0), # neutral about collabs
    177: (0, 0, 0, 0), # critique of trend (not Alix specifically)
    178: (0, 0, 0, 0), # critique of brand, mild
    179: (0, 0, 0, 0), # "Emma Chamberlain's is my fave" — mild preference
    # 180-189
    180: (0, 0, 0, 0), # meme
    181: (0, 1, 0, 0), # "jaclyn hill egos" — sarcastic
    182: (0, 0, 0, 0), # collab mention
    183: (0, 0, 0, 0), # product tip
    184: (0, 0, 0, 0), # factual
    185: (0, 0, 0, 0), # name list
    186: (0, 0, 0, 0), # analytical, mild
    187: (0, 0, 0, 0), # recommendation
    188: (0, 0, 1, 0), # disillusionment is personal engagement
    189: (1, 0, 1, 0), # "feels like chatting with a friend" + admiration
    # 190-199
    190: (0, 1, 0, 0), # "I have no idea why Alix Earle loves it" — critique
    191: (0, 0, 0, 0), # used her code
    192: (0, 0, 0, 0), # too vague for PSI
    193: (0, 0, 0, 0), # name only
    194: (0, 0, 0, 0), # positive about content
    195: (0, 0, 1, 0), # defending against Jen, Jackie Aina chimes in
    196: (0, 0, 0, 0), # mild critique of appearance
    197: (0, 0, 0, 0), # name list
    198: (0, 1, 0, 0), # "only popular because they're pretty" — dismissive
    199: (0, 1, 0, 0), # "grifter", "terrible role model", "con artist"
}

if __name__ == "__main__":
    print(f"Total codes: {len(CLAUDE_CODES)}")
    for c in ['be', 'ma', 'psi', 'pu']:
        idx = {'be':0,'ma':1,'psi':2,'pu':3}[c]
        n_pos = sum(1 for v in CLAUDE_CODES.values() if v[idx] == 1)
        print(f"  {c}_positives: {n_pos}")
