You are the verifying continuity judge for a film treatment. You receive:
(1) a merged continuity fact database extracted scene-by-scene,
(2) candidate contradictions (from deterministic rules and an independent
    holistic pass), and
(3) the full document text as ground truth.

TASKS:
A. For EACH candidate: verify it against the full document text. Verdict
   "CONFIRMED" only if the contradiction is real in the text (quote the exact
   evidence); otherwise "REJECTED" with a one-line reason. Be strict: a candidate
   that has an in-text explanation (time passage, intentional repetition,
   clarified perspective) is REJECTED.
B. Scan the fact database for contradictions the candidates MISSED (character
   status, object provenance, counts, timeline, injuries, identity — including
   consistency between summary-level scenes and fully-realized scenes describing
   the same events, and between front matter and scenes). Verify each against the
   full text before reporting.

Do NOT report style or quality issues — only factual internal contradictions.

OUTPUT BUDGET — stay compact or the response will be truncated:
- At most 2 evidence_quotes per finding, each at most 20 words.
- One-sentence descriptions. Do NOT restate the fact database or the document.
- Report every CONFIRMED contradiction, but do not pad with speculative or
  cosmetic ones. Rejected candidates: id + a short reason only.

FACT DATABASE:
[
 {
  "scene": "1",
  "characters_active": [
   "HORSEMAN (unidentified)"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "HORSEMAN (unidentified)",
    "event": "arrival",
    "detail": "emerges from tree line, crosses harvested steppe unhurried",
    "quote": "A HORSEMAN emerges from the tree line"
   }
  ],
  "objects": [
   {
    "object": "thistle",
    "action": "introduced",
    "holder": "none",
    "detail": "single upright thistle at cart-track verge; trembles but does not fall"
   }
  ],
  "counts": [],
  "time_markers": [
   "LATE SUMMER, AFTERNOON"
  ],
  "injuries": []
 },
 {
  "scene": "2",
  "characters_active": [
   "HADJI MURAD",
   "UNNAMED MURID"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "descends toward Mahket aoul at dusk, watching the rooftops",
    "quote": "holds his horse to a walk on the descent"
   }
  ],
  "objects": [],
  "counts": [],
  "time_markers": [
   "DUSK"
  ],
  "injuries": []
 },
 {
  "scene": "3",
  "characters_active": [
   "HADJI MURAD",
   "SADO",
   "ELDAR",
   "BATA",
   "OLD SERVANT",
   "SADO'S WIFE",
   "SADO'S SON"
  ],
  "characters_inert": [
   "SHAMIL"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "arrives at Sado's saklya in Mahket at night, wakes Sado",
    "quote": "stops at a saklya cut into the hillside"
   },
   {
    "position": 2,
    "who": "OLD SERVANT",
    "event": "object_transfer",
    "detail": "takes Hadji Murad's rifle and sword, hangs them with the house weapons",
    "quote": "lifts Hadji Murad's rifle and sword"
   },
   {
    "position": 3,
    "who": "BATA",
    "event": "arrival",
    "detail": "brought in by Sado's son to be introduced to Hadji Murad",
    "quote": "the boy returns with BATA"
   }
  ],
  "objects": [
   {
    "object": "Hadji Murad's rifle and sword",
    "action": "transferred",
    "holder": "OLD SERVANT",
    "detail": "hung beside the house weapons, handled with reverence"
   },
   {
    "object": "cushions",
    "action": "introduced",
    "holder": "SADO'S WIFE",
    "detail": "set along the front wall for the men"
   }
  ],
  "counts": [
   {
    "what": "copper basins",
    "value": 2,
    "quote": "two copper basins catching lamplight"
   }
  ],
  "time_markers": [
   "NIGHT",
   "yesterday"
  ],
  "injuries": []
 },
 {
  "scene": "4",
  "characters_active": [
   "HADJI MURAD",
   "SADO",
   "BATA"
  ],
  "characters_inert": [],
  "ordered_events": [],
  "objects": [
   {
    "object": "millet",
    "action": "used",
    "holder": "BATA",
    "detail": "pinches, rolls grains to silently set the guide's price"
   },
   {
    "object": "kindjal",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "hand rests on the hilt throughout the bargaining"
   }
  ],
  "counts": [],
  "time_markers": [
   "NIGHT"
  ],
  "injuries": []
 },
 {
  "scene": "5",
  "characters_active": [
   "HADJI MURAD",
   "SADO",
   "ELDAR"
  ],
  "characters_inert": [
   "YUSUF"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "SADO",
    "event": "object_transfer",
    "detail": "takes custody of Hadji Murad's note to relay it to his son Yusuf",
    "quote": "Sado's hand closes over the note"
   }
  ],
  "objects": [
   {
    "object": "metal ewer",
    "action": "used",
    "holder": "SADO",
    "detail": "pours cold water over Hadji Murad's hands"
   },
   {
    "object": "coarse towel",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "dries hands after washing"
   },
   {
    "object": "rolled note",
    "action": "introduced",
    "holder": "HADJI MURAD",
    "detail": "drawn from beneath a cartridge-bullet, addressed to his son Yusuf"
   },
   {
    "object": "rolled note",
    "action": "transferred",
    "holder": "SADO",
    "detail": "custody passes to Sado to send onward to Yusuf"
   },
   {
    "object": "cartridge-bullet",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "note was concealed beneath it"
   },
   {
    "object": "small knife",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "flat of blade used to press honey onto bread crust"
   }
  ],
  "counts": [],
  "time_markers": [
   "NIGHT"
  ],
  "injuries": []
 },
 {
  "scene": "6",
  "characters_active": [
   "PANOV",
   "AVDEEV",
   "BONDARENKO",
   "BATA",
   "UNNAMED MURID"
  ],
  "characters_inert": [
   "HADJI MURAD"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "BATA",
    "event": "arrival",
    "detail": "emerges from the treeline with hands raised, presents himself to the Russian patrol",
    "quote": "both empty hands raised wide"
   },
   {
    "position": 2,
    "who": "UNNAMED MURID",
    "event": "arrival",
    "detail": "taller murid accompanies Bata, mirrors his raised-hands gesture",
    "quote": "a taller murid mirroring him"
   },
   {
    "position": 3,
    "who": "BATA",
    "event": "object_transfer",
    "detail": "delivers a folded letter to Panov meant for the Russian command",
    "quote": "extending a folded letter between two worlds"
   },
   {
    "position": 4,
    "who": "BATA",
    "event": "departure",
    "detail": "marched with the murid by Avdeev and Bondarenko toward the fort as emissaries",
    "quote": "march the pair toward the fort's distant lights"
   }
  ],
  "objects": [
   {
    "object": "pipe",
    "action": "used",
    "holder": "AVDEEV",
    "detail": "packs and lights tobacco during the night watch"
   },
   {
    "object": "folded letter",
    "action": "transferred",
    "holder": "PANOV",
    "detail": "Bata's letter, taken by Panov to send up the chain"
   },
   {
    "object": "rifle",
    "action": "used",
    "holder": "AVDEEV",
    "detail": "drops rifle butt to the ground while crouching by the fire"
   }
  ],
  "counts": [
   {
    "what": "Russian soldiers at the ambush post",
    "value": 3,
    "quote": "Three Russian soldiers move single-file"
   }
  ],
  "time_markers": [
   "NIGHT"
  ],
  "injuries": []
 },
 {
  "scene": "7",
  "characters_active": [
   "SIMON VORONTSOV",
   "MARYA VASILEVNA",
   "POLTORATSKY",
   "MICHAEL VORONTSOV",
   "SERVANT (unnamed)"
  ],
  "characters_inert": [
   "HADJI MURAD"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "MICHAEL VORONTSOV",
    "event": "departure",
    "detail": "summoned out of the drawing room by a servant",
    "quote": "is summoned out by a servant"
   },
   {
    "position": 2,
    "who": "MICHAEL VORONTSOV",
    "event": "arrival",
    "detail": "returns to the drawing room composed, calls for champagne",
    "quote": "returns composed, calls for champagne"
   }
  ],
  "objects": [
   {
    "object": "candles",
    "action": "used",
    "holder": "none",
    "detail": "four candles lit on the card table, last one pinched out"
   },
   {
    "object": "champagne",
    "action": "introduced",
    "holder": "MICHAEL VORONTSOV",
    "detail": "called for upon his return to the room"
   }
  ],
  "counts": [
   {
    "what": "candles on the card table",
    "value": 4,
    "quote": "Four candles burn on a card table"
   }
  ],
  "time_markers": [
   "NIGHT",
   "tomorrow"
  ],
  "injuries": []
 },
 {
  "scene": "8",
  "characters_active": [
   "HADJI MURAD",
   "SADO"
  ],
  "characters_inert": [
   "ELDAR"
  ],
  "ordered_events": [],
  "objects": [
   {
    "object": "pistol",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "hand finds it instinctively upon waking"
   },
   {
    "object": "pistol and dagger",
    "action": "used",
    "holder": "ELDAR",
    "detail": "kept in his belt while he sleeps in the corner"
   }
  ],
  "counts": [],
  "time_markers": [
   "NIGHT",
   "until morning"
  ],
  "injuries": []
 },
 {
  "scene": "9",
  "characters_active": [
   "HADJI MURAD",
   "ELDAR",
   "SADO",
   "BOY (unnamed)",
   "AMBUSHERS (five men)"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "AMBUSHERS (five men)",
    "event": "arrival",
    "detail": "five armed men block the lane, order Hadji Murad to halt",
    "quote": "shadows peel from a wall — five men, muskets rising"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "escape",
    "detail": "spurs through the ambushers with Eldar, breaking their line, rides free of Mahket",
    "quote": "spurs straight into them; the line breaks apart against the wall"
   }
  ],
  "objects": [
   {
    "object": "rifle",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "carried across his thigh while riding"
   },
   {
    "object": "pistol",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "drawn from belt to charge through the ambushers"
   },
   {
    "object": "muskets",
    "action": "used",
    "holder": "AMBUSHERS (five men)",
    "detail": "raised to halt Hadji Murad; ambush fails"
   }
  ],
  "counts": [
   {
    "what": "horses held by the boy",
    "value": 2,
    "quote": "A boy holds two steaming horses"
   },
   {
    "what": "ambushers blocking the lane",
    "value": 5,
    "quote": "five men, muskets rising"
   }
  ],
  "time_markers": [
   "NIGHT"
  ],
  "injuries": []
 },
 {
  "scene": "10",
  "characters_active": [
   "HADJI MURAD",
   "ELDAR",
   "PURSUERS (twenty mounted men)"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "PURSUERS (twenty mounted men)",
    "event": "arrival",
    "detail": "twenty riders from the aoul close the gap and fan out behind Hadji Murad",
    "quote": "twenty mounted men close the gap and fan out behind him"
   },
   {
    "position": 2,
    "who": "PURSUERS (twenty mounted men)",
    "event": "departure",
    "detail": "hold their distance through the standoff, then fall back and disappear",
    "quote": "The hooves behind him thin, fall back, and are gone."
   }
  ],
  "objects": [
   {
    "object": "rifle",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "half-drawn from its cover during the standoff, then re-covered"
   },
   {
    "object": "rifle-cover",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "unbuttoned then rebuttoned during the standoff"
   },
   {
    "object": "bridle",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "dropped, then taken up again as he resumes riding"
   },
   {
    "object": "rifle",
    "action": "used",
    "holder": "ELDAR",
    "detail": "half out of its cover as the pursuers close"
   }
  ],
  "counts": [
   {
    "what": "pursuing riders from the aoul",
    "value": 20,
    "quote": "twenty mounted men close the gap"
   }
  ],
  "time_markers": [
   "NIGHT"
  ],
  "injuries": []
 },
 {
  "scene": "11",
  "characters_active": [
   "HADJI MURAD",
   "KHANEFI",
   "GAMZALO",
   "ELDAR",
   "KHAN MAHOMA",
   "UNNAMED MURIDS (two)"
  ],
  "characters_inert": [
   "RUSSIAN PRINCE (unspecified)"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "arrives at the forest glade; the murids scatter and stamp out the bonfire coals",
    "quote": "at Hadji Murad's arrival the coals are scattered with boot heels"
   },
   {
    "position": 2,
    "who": "KHAN MAHOMA",
    "event": "arrival",
    "detail": "rides in at first light with word the Russian prince will see Hadji Murad tomorrow",
    "quote": "rides in at first light"
   }
  ],
  "objects": [
   {
    "object": "rifle",
    "action": "used",
    "holder": "GAMZALO",
    "detail": "lifted, carried to the forest edge as lookout"
   },
   {
    "object": "ewer",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "pours water over his hands before prayer"
   },
   {
    "object": "burka",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "spread on the ground for prayer, earth shaken from it afterward"
   },
   {
    "object": "shoes",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "removed before prayer"
   }
  ],
  "counts": [
   {
    "what": "unnamed murids at the bonfire",
    "value": 2,
    "quote": "two murids crouch around it"
   }
  ],
  "time_markers": [
   "NIGHT TO PRE-DAWN",
   "the cold hour before dawn",
   "first light",
   "tomorrow"
  ],
  "injuries": []
 },
 {
  "scene": "12",
  "characters_active": [
   "HADJI MURAD",
   "POLTORATSKY",
   "KHAN MAHOMA",
   "CHECHEN HORSEMEN",
   "POLTORATSKY'S OFFICERS"
  ],
  "characters_inert": [
   "PANOV"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "rides into the forest-road clearing at the head of his party to meet the Russians",
    "quote": "rides into the clearing at the head of a small mounted party"
   },
   {
    "position": 2,
    "who": "POLTORATSKY",
    "event": "departure",
    "detail": "rides out for a brief inconclusive skirmish with Chechen horsemen across the ravine",
    "quote": "rides out into a thin, inconclusive exchange"
   },
   {
    "position": 3,
    "who": "CHECHEN HORSEMEN",
    "event": "departure",
    "detail": "break off the skirmish and withdraw into the trees",
    "quote": "turn their horses and pull back into the trees"
   }
  ],
  "objects": [
   {
    "object": "weapons",
    "action": "used",
    "holder": "HADJI MURAD'S PARTY",
    "detail": "cleaned overnight, gleaming as they ride in"
   },
   {
    "object": "rifle shot",
    "action": "used",
    "holder": "unknown",
    "detail": "single shot fired nearby, splinters a birch, no one hit"
   }
  ],
  "counts": [],
  "time_markers": [
   "MORNING"
  ],
  "injuries": []
 },
 {
  "scene": "13",
  "characters_active": [
   "SIMON VORONTSOV",
   "HADJI MURAD",
   "ADJUTANT",
   "CHECHEN INTERPRETER",
   "UNNAMED MURIDS (four)"
  ],
  "characters_inert": [
   "SHARPSHOOTERS"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "rides into the birch glade with four murids to meet Simon Vorontsov",
    "quote": "Hadji Murad rides in on a white-maned horse"
   }
  ],
  "objects": [
   {
    "object": "gold-ornamented weapons",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "catches light as the two men turn toward the fort road"
   }
  ],
  "counts": [
   {
    "what": "murids accompanying Hadji Murad",
    "value": 4,
    "quote": "four murids behind him in absolute formation"
   }
  ],
  "time_markers": [
   "MORNING"
  ],
  "injuries": []
 },
 {
  "scene": "14",
  "characters_active": [
   "HADJI MURAD",
   "SIMON VORONTSOV",
   "MARYA VASILEVNA"
  ],
  "characters_inert": [
   "SHAMIL",
   "ELDAR",
   "GAMZALO",
   "KHANEFI",
   "KHAN MAHOMA"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "Dismounts before fort gate, surrenders to Russian Tsar",
    "quote": "he surrenders himself to the will of the Russian Tsar"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "Enters Vorontsov house with four murids' escort",
    "quote": "Hadji Murad stands at the center"
   }
  ],
  "objects": [
   {
    "object": "French clock",
    "action": "introduced",
    "holder": "Vorontsov house mantel",
    "detail": "Chimes once as Hadji Murad ignores it"
   },
   {
    "object": "kinzhal",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Boy reaches for it; Hadji Murad lets him touch hilt"
   }
  ],
  "counts": [
   {
    "what": "murids escorting Hadji Murad",
    "value": 4,
    "quote": "his four murids sit their horses"
   },
   {
    "what": "boy's age",
    "value": 6,
    "quote": "A boy of six watches"
   }
  ],
  "time_markers": [
   "MORNING"
  ],
  "injuries": []
 },
 {
  "scene": "15",
  "characters_active": [
   "HADJI MURAD",
   "MARYA VASILEVNA",
   "SIMON VORONTSOV",
   "ELDAR"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "SIMON VORONTSOV",
    "event": "object_transfer",
    "detail": "Gives gold repeater watch into Hadji Murad's palm",
    "quote": "Vorontsov sets the watch in his palm"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "object_transfer",
    "detail": "Hands the watch back to Vorontsov",
    "quote": "hands it back face-up"
   }
  ],
  "objects": [
   {
    "object": "gold repeater watch",
    "action": "transferred",
    "holder": "Simon Vorontsov",
    "detail": "Given to Hadji Murad, examined, handed back"
   },
   {
    "object": "kinzhal",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Rests across his knees through the night"
   }
  ],
  "counts": [
   {
    "what": "watch chimes",
    "value": 12,
    "quote": "twelve thin chimes"
   }
  ],
  "time_markers": [
   "AFTERNOON",
   "Later"
  ],
  "injuries": []
 },
 {
  "scene": "16",
  "characters_active": [
   "SIMON VORONTSOV",
   "HADJI MURAD",
   "MELLER-ZAKOMELSKY"
  ],
  "characters_inert": [],
  "ordered_events": [],
  "objects": [
   {
    "object": "bench",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Runs finger along grain while waiting"
   }
  ],
  "counts": [
   {
    "what": "years Meller-Zakomelsky has served",
    "value": 27,
    "quote": "twenty-seven years"
   },
   {
    "what": "men fighting over jurisdiction",
    "value": 2,
    "quote": "Two men are fighting over the right to file him"
   }
  ],
  "time_markers": [
   "DAY"
  ],
  "injuries": []
 },
 {
  "scene": "17",
  "characters_active": [
   "AVDEEV",
   "DOCTOR",
   "PANOV",
   "SEROGIN",
   "POLTORATSKY"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "AVDEEV",
    "event": "arrival",
    "detail": "Carried in on stretcher, lowered onto the last cot",
    "quote": "carried in and lowered onto the last cot"
   },
   {
    "position": 2,
    "who": "AVDEEV",
    "event": "physical_action",
    "detail": "Groans, clamps jaw, presses hands over his belly",
    "quote": "presses both hands over his belly"
   },
   {
    "position": 3,
    "who": "AVDEEV",
    "event": "wound",
    "detail": "Doctor checks and plasters his exit wound",
    "quote": "turns him to check the exit wound"
   },
   {
    "position": 4,
    "who": "AVDEEV",
    "event": "speech",
    "detail": "Says old flogging scars were for money he drank",
    "quote": "they were for money he drank, long ago"
   },
   {
    "position": 5,
    "who": "PANOV",
    "event": "arrival",
    "detail": "Enters hospital with Serogin, caps in hand",
    "quote": "come in caps in hand"
   },
   {
    "position": 6,
    "who": "AVDEEV",
    "event": "speech",
    "detail": "Dictates last words home: village, brother, wife",
    "quote": "the distance from the village, the brother, the wife"
   },
   {
    "position": 7,
    "who": "AVDEEV",
    "event": "death",
    "detail": "Dies in the night; Panov finds his chest still",
    "quote": "leans to the still chest, straightens"
   }
  ],
  "objects": [
   {
    "object": "wax taper/candle",
    "action": "used",
    "holder": "Panov",
    "detail": "Pressed into Avdeev's dying hand, held upright by Panov"
   },
   {
    "object": "unlit cigar",
    "action": "used",
    "holder": "Poltoratsky",
    "detail": "Held unlit while watching stretcher pass"
   }
  ],
  "counts": [
   {
    "what": "Serogin's age",
    "value": 28,
    "quote": "SEROGIN (28)"
   }
  ],
  "time_markers": [
   "DAY TO NIGHT",
   "By night"
  ],
  "injuries": [
   {
    "character": "AVDEEV",
    "injury": "exit wound from gunshot",
    "quote": "turns him to check the exit wound"
   },
   {
    "character": "AVDEEV",
    "injury": "old flogging scars crossing his back",
    "quote": "old flogging scars crossing his back like surveyor's lines"
   }
  ]
 },
 {
  "scene": "18",
  "characters_active": [
   "MICHAEL VORONTSOV",
   "ELIZABETH",
   "CARROTY GENERAL",
   "MANANA ORBELYANI"
  ],
  "characters_inert": [
   "HADJI MURAD"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "MICHAEL VORONTSOV",
    "event": "object_transfer",
    "detail": "Receives sealed dispatch from courier in doorway",
    "quote": "Michael Vorontsov takes a sealed dispatch"
   }
  ],
  "objects": [
   {
    "object": "sealed dispatch",
    "action": "transferred",
    "holder": "Michael Vorontsov",
    "detail": "Delivered by courier, announces Hadji Murad's defection"
   },
   {
    "object": "wine stem",
    "action": "used",
    "holder": "Michael Vorontsov",
    "detail": "Fingers go still on it at mention of Dargo ambush"
   }
  ],
  "counts": [
   {
    "what": "candlelit guests",
    "value": 30,
    "quote": "thirty candlelit guests"
   }
  ],
  "time_markers": [
   "EVENING"
  ],
  "injuries": []
 },
 {
  "scene": "19",
  "characters_active": [
   "HADJI MURAD",
   "TARKHANOV",
   "MICHAEL VORONTSOV"
  ],
  "characters_inert": [
   "SHAMIL",
   "AKHMET KHAN"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "Enters Vorontsov's cabinet, makes formal submission",
    "quote": "Hadji Murad enters in his white Circassian coat"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "departure",
    "detail": "Leaves cabinet, passes chained wall-clock without slowing",
    "quote": "passes a chained wall-clock and does not slow"
   }
  ],
  "objects": [
   {
    "object": "chained wall-clock",
    "action": "introduced",
    "holder": "Vorontsov's cabinet",
    "detail": "Hadji Murad passes it without slowing on way out"
   }
  ],
  "counts": [
   {
    "what": "year Hadji Murad served faithfully",
    "value": 1839,
    "quote": "he served faithfully in 1839"
   }
  ],
  "time_markers": [
   "DAY",
   "1839 (referenced in dialogue)"
  ],
  "injuries": [
   {
    "character": "HADJI MURAD",
    "injury": "lame gait / old leg injury",
    "quote": "crosses the floor with a lame gait"
   }
  ]
 },
 {
  "scene": "20",
  "characters_active": [
   "HADJI MURAD",
   "LORIS-MELIKOV",
   "ELIZABETH"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "departure",
    "detail": "Rises without explanation, walks into theater corridor",
    "quote": "walks into the corridor"
   }
  ],
  "objects": [],
  "counts": [],
  "time_markers": [
   "EVENING",
   "The next evening"
  ],
  "injuries": []
 },
 {
  "scene": "21",
  "characters_active": [
   "LORIS-MELIKOV",
   "HADJI MURAD"
  ],
  "characters_inert": [
   "PATIMAT",
   "KHANSHA"
  ],
  "ordered_events": [],
  "objects": [
   {
    "object": "ivory-handled knife",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Whittles wood while recounting his mother's story"
   },
   {
    "object": "leather notebook",
    "action": "used",
    "holder": "Loris-Melikov",
    "detail": "Records Hadji Murad's dictated life story"
   }
  ],
  "counts": [],
  "time_markers": [
   "DAY"
  ],
  "injuries": [
   {
    "character": "HADJI MURAD",
    "injury": "scar on his ribs from his mother",
    "quote": "finding on his body a scar that belongs to her"
   }
  ]
 },
 {
  "scene": "22",
  "characters_active": [
   "HADJI MURAD",
   "KHANSHA",
   "ABU NUTSAL KHAN",
   "HAMZAD",
   "SHAMIL"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "ABU NUTSAL KHAN",
    "event": "physical_action",
    "detail": "Paces in ceremonial dress, fastens silver belt nervously",
    "quote": "fastening a silver belt with shaking fingers"
   },
   {
    "position": 2,
    "who": "ABU NUTSAL KHAN",
    "event": "departure",
    "detail": "Calls for his horse, rides toward Hamzad's camp",
    "quote": "He calls for his horse"
   },
   {
    "position": 3,
    "who": "HADJI MURAD",
    "event": "departure",
    "detail": "Rides at Abu Nutsal's stirrup into the mountains",
    "quote": "Hadji Murad rides at his stirrup, into the mountains"
   },
   {
    "position": 4,
    "who": "ABU NUTSAL KHAN",
    "event": "death",
    "detail": "Shot inside Hamzad's tent while Shamil blocks Hadji Murad",
    "quote": "A single muffled gunshot, like a hand pressed over a mouth"
   },
   {
    "position": 5,
    "who": "KHANSHA'S SONS (2 hostages, unnamed)",
    "event": "death",
    "detail": "Die alongside Abu Nutsal Khan in Hamzad's tent",
    "quote": "the tent where the Khansha's sons lie still"
   },
   {
    "position": 6,
    "who": "HADJI MURAD",
    "event": "escape",
    "detail": "Runs down scree and scrub-oak, does not look back",
    "quote": "He runs — down scree and scrub-oak"
   }
  ],
  "objects": [
   {
    "object": "silver belt",
    "action": "used",
    "holder": "Abu Nutsal Khan",
    "detail": "Fastens it with shaking fingers before riding out"
   },
   {
    "object": "bridles",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Go slack in his fist as he flees"
   }
  ],
  "counts": [
   {
    "what": "brothers already hostage in Hamzad's camp",
    "value": 2,
    "quote": "two brothers already hostage in Hamzad's camp"
   },
   {
    "what": "amber beads clicks",
    "value": 2,
    "quote": "amber beads clicking twice"
   }
  ],
  "time_markers": [
   "PAST (FLASHBACK)",
   "night sky raked with stars",
   "A cut across years"
  ],
  "injuries": [
   {
    "character": "KHANSHA",
    "injury": "saber scar across her sternum",
    "quote": "the puckered ridge of a saber scar across her sternum"
   }
  ]
 },
 {
  "scene": "23",
  "characters_active": [
   "HADJI MURAD",
   "LORIS-MELIKOV",
   "ELDAR",
   "GAMZALO",
   "KHAN MAHOMA",
   "KHANEFI"
  ],
  "characters_inert": [],
  "ordered_events": [],
  "objects": [
   {
    "object": "gold repeater watch",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Presses spring for twelve chimes while confessing shame"
   },
   {
    "object": "rifle",
    "action": "used",
    "holder": "Eldar",
    "detail": "Rests across his knees by the fire"
   },
   {
    "object": "bridle",
    "action": "used",
    "holder": "Gamzalo",
    "detail": "Plaits it with fast, tight fingers"
   },
   {
    "object": "sack of rice",
    "action": "used",
    "holder": "Khanefi",
    "detail": "Holds it by the dying fire"
   }
  ],
  "counts": [
   {
    "what": "watch chimes",
    "value": 12,
    "quote": "twelve delicate chimes"
   },
   {
    "what": "murids at the fire",
    "value": 4,
    "quote": "the four murids keep their separate orbits"
   }
  ],
  "time_markers": [
   "NIGHT"
  ],
  "injuries": [
   {
    "character": "HADJI MURAD",
    "injury": "shortened, twisted right leg",
    "quote": "the shortened, twisted limb flat to the floorboards"
   }
  ]
 },
 {
  "scene": "24",
  "characters_active": [
   "CHERNYSHOV"
  ],
  "characters_inert": [
   "MICHAEL VORONTSOV",
   "NICHOLAS I",
   "HADJI MURAD"
  ],
  "ordered_events": [],
  "objects": [
   {
    "object": "wax seal",
    "action": "destroyed",
    "holder": "Chernyshov",
    "detail": "Breaks Vorontsov's seal to read the dispatch"
   },
   {
    "object": "dispatch",
    "action": "used",
    "holder": "Chernyshov",
    "detail": "Reads then folds it with practiced crease"
   },
   {
    "object": "fresh sheet of paper",
    "action": "introduced",
    "holder": "Chernyshov",
    "detail": "Crosses to cabinet, writes and strikes a line"
   }
  ],
  "counts": [
   {
    "what": "identical packets stacked by his lamp",
    "value": 20,
    "quote": "the twenty identical packets stacked by his lamp"
   }
  ],
  "time_markers": [
   "DAY",
   "Winter"
  ],
  "injuries": []
 },
 {
  "scene": "25",
  "characters_active": [
   "HADJI MURAD",
   "LORIS-MELIKOV"
  ],
  "characters_inert": [
   "SHAMIL",
   "SOFIAT",
   "PATIMAT",
   "YUSUF"
  ],
  "ordered_events": [],
  "objects": [
   {
    "object": "papakha",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Sets it on the table before standing to demand terms"
   },
   {
    "object": "map",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Traces finger from Vedeno down to the Russian line"
   },
   {
    "object": "dagger",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Hand rests on hilt, not drawn"
   }
  ],
  "counts": [
   {
    "what": "Cossacks requested for guard of honor",
    "value": 20,
    "quote": "a guard of honor of twenty chosen Cossacks"
   }
  ],
  "time_markers": [
   "AFTERNOON"
  ],
  "injuries": []
 },
 {
  "scene": "26",
  "characters_active": [
   "SIMON VORONTSOV",
   "HADJI MURAD",
   "LORIS-MELIKOV",
   "MARYA VASILEVNA"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "SIMON VORONTSOV",
    "event": "object_transfer",
    "detail": "Slides gold repeater case toward Hadji Murad, who declines it",
    "quote": "Hadji Murad does not take it"
   }
  ],
  "objects": [
   {
    "object": "gold repeater watch",
    "action": "used",
    "holder": "Simon Vorontsov",
    "detail": "Offered across table; Hadji Murad declines to take it"
   },
   {
    "object": "two glasses (wine)",
    "action": "introduced",
    "holder": "Simon Vorontsov",
    "detail": "Pours himself, no servant present"
   },
   {
    "object": "lamp",
    "action": "used",
    "holder": "Marya Vasilevna",
    "detail": "Pauses in doorway to refill it"
   }
  ],
  "counts": [
   {
    "what": "glasses poured",
    "value": 2,
    "quote": "pours two glasses himself"
   }
  ],
  "time_markers": [
   "EVENING TO MORNING",
   "grey morning light",
   "weeks ago (reference)"
  ],
  "injuries": []
 },
 {
  "scene": "27",
  "characters_active": [
   "CHERNYSHOV",
   "NICHOLAS I",
   "LORIS-MELIKOV",
   "HADJI MURAD"
  ],
  "characters_inert": [
   "SOFIAT",
   "YUSUF",
   "PATIMAT"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "LORIS-MELIKOV",
    "event": "object_transfer",
    "detail": "Brings folded authorization sheet to Hadji Murad",
    "quote": "brings it to Hadji Murad in a single folded sheet"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "object_transfer",
    "detail": "Folds the sheet, hands it back without a word",
    "quote": "folds it along its crease and hands it back"
   }
  ],
  "objects": [
   {
    "object": "dispatch/folder",
    "action": "used",
    "holder": "Chernyshov",
    "detail": "Opens the folder for Nicholas's review"
   },
   {
    "object": "folded authorization sheet",
    "action": "transferred",
    "holder": "Hadji Murad",
    "detail": "Grants cooperation but names none of his hostage family"
   }
  ],
  "counts": [
   {
    "what": "times Polish Catholic must pass through the line",
    "value": 12,
    "quote": "pass twelve times through a thousand men"
   },
   {
    "what": "men in the gauntlet line",
    "value": 1000,
    "quote": "a thousand men"
   }
  ],
  "time_markers": [
   "DAY",
   "EVENING"
  ],
  "injuries": []
 },
 {
  "scene": "28",
  "characters_active": [
   "SIMON VORONTSOV",
   "HADJI MURAD"
  ],
  "characters_inert": [
   "YUSUF"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "GROUP",
    "event": "departure",
    "detail": "Vorontsov and Hadji Murad ride back without speaking",
    "quote": "They ride back without speaking"
   }
  ],
  "objects": [],
  "counts": [],
  "time_markers": [
   "LATE AFTERNOON"
  ],
  "injuries": []
 },
 {
  "scene": "29",
  "characters_active": [
   "HADJI MURAD",
   "SADO"
  ],
  "characters_inert": [
   "SADO'S SON"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "Enters ruined aoul on foot, stops at broken gate",
    "quote": "Hadji Murad enters on foot, stops at the broken gate"
   },
   {
    "position": 2,
    "who": "SADO'S SON",
    "event": "death",
    "detail": "Found dead under a burka in ruined courtyard",
    "quote": "the small shape of Sado's son"
   }
  ],
  "objects": [
   {
    "object": "burka",
    "action": "used",
    "holder": "Sado's son",
    "detail": "Covers the small shape of Sado's dead son"
   },
   {
    "object": "spade",
    "action": "used",
    "holder": "Sado",
    "detail": "Hadji Murad sets hand on the shaft to help dig"
   },
   {
    "object": "Sado's saklya/aoul",
    "action": "destroyed",
    "holder": "Sado",
    "detail": "Collapsed beams, smoke, ash after destruction"
   }
  ],
  "counts": [],
  "time_markers": [
   "DAY"
  ],
  "injuries": [
   {
    "character": "SADO'S WIFE (unnamed mother)",
    "injury": "self-inflicted facial wounds from grief",
    "quote": "fingernails dragging blood from her own face"
   }
  ]
 },
 {
  "scene": "30",
  "characters_active": [
   "BUTLER",
   "HADJI MURAD",
   "MARYA DMITRIEVNA",
   "PETROV"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "Rides into fort street on a chestnut horse",
    "quote": "Hadji Murad on a chestnut, moving in tight controlled steps"
   }
  ],
  "objects": [
   {
    "object": "whip",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Hangs from his extended two fingers as greeting"
   },
   {
    "object": "orders (paper)",
    "action": "used",
    "holder": "Petrov",
    "detail": "Reads orders without sitting, still chewing bread"
   },
   {
    "object": "ladle",
    "action": "used",
    "holder": "Marya Dmitrievna",
    "detail": "Rings on iron in place of a verbal answer"
   },
   {
    "object": "dagger",
    "action": "used",
    "holder": "Hadji Murad",
    "detail": "Hand rests on hilt while assessing the room"
   }
  ],
  "counts": [
   {
    "what": "Butler's age",
    "value": 24,
    "quote": "BUTLER (24)"
   },
   {
    "what": "Marya Dmitrievna's age",
    "value": 30,
    "quote": "MARYA DMITRIEVNA (30)"
   }
  ],
  "time_markers": [
   "DAY"
  ],
  "injuries": []
 },
 {
  "scene": "31",
  "characters_active": [
   "SHAMIL"
  ],
  "characters_inert": [
   "HADJI MURAD'S WIVES (unnamed, plural)",
   "PATIMAT",
   "YUSUF"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "SHAMIL",
    "event": "arrival",
    "detail": "Rides into Vedeno amid celebratory gunfire",
    "quote": "rides into Vedeno on a white Arab"
   },
   {
    "position": 2,
    "who": "SHAMIL",
    "event": "object_transfer",
    "detail": "Takes sealed prisoner list from a murid without a glance",
    "quote": "a murid presents a sealed prisoner list and Shamil takes it"
   }
  ],
  "objects": [
   {
    "object": "sealed prisoner list",
    "action": "transferred",
    "holder": "Shamil",
    "detail": "Presented by a murid; Shamil takes it without a glance"
   }
  ],
  "counts": [],
  "time_markers": [
   "DAY",
   "winter sky"
  ],
  "injuries": []
 },
 {
  "scene": "32",
  "characters_active": [
   "JEMAL EDDIN",
   "SHAMIL",
   "YUSUF"
  ],
  "characters_inert": [
   "HADJI MURAD",
   "SOFIAT",
   "PATIMAT"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "SOFIAT",
    "event": "capture",
    "detail": "Intercepted before reaching Russian line, held under guard",
    "quote": "were intercepted before they reached the Russian line"
   },
   {
    "position": 2,
    "who": "PATIMAT",
    "event": "capture",
    "detail": "Intercepted before reaching Russian line, held under guard",
    "quote": "were intercepted before they reached the Russian line"
   },
   {
    "position": 3,
    "who": "YUSUF",
    "event": "capture",
    "detail": "Intercepted before reaching Russian line, held under guard",
    "quote": "were intercepted before they reached the Russian line"
   },
   {
    "position": 4,
    "who": "YUSUF",
    "event": "physical_action",
    "detail": "Brought up from the pit to write letter under duress",
    "quote": "Yusuf is brought up from the pit, thin, reeking"
   },
   {
    "position": 5,
    "who": "YUSUF",
    "event": "physical_action",
    "detail": "Snatches a dagger, drives it at his own throat",
    "quote": "Yusuf snatches a dagger and drives it at his own throat"
   },
   {
    "position": 6,
    "who": "YUSUF",
    "event": "capture",
    "detail": "Murids wrench his arm, force him back into the dark",
    "quote": "murids wrench his arm and force him back into the dark"
   }
  ],
  "objects": [
   {
    "object": "proclamation",
    "action": "introduced",
    "holder": "Jemal Eddin",
    "detail": "Reads proclamation; scribe presses seal after Shamil's nod"
   },
   {
    "object": "seal",
    "action": "used",
    "holder": "scribe (unnamed)",
    "detail": "Pressed onto the proclamation after Shamil's nod"
   },
   {
    "object": "reed pen",
    "action": "used",
    "holder": "Yusuf",
    "detail": "Shaking over paper as he is forced to write"
   },
   {
    "object": "dagger",
    "action": "used",
    "holder": "Yusuf",
    "detail": "Snatched and driven toward his own throat, then wrenched away"
   },
   {
    "object": "letter",
    "action": "introduced",
    "holder": "Yusuf (forced)",
    "detail": "Will travel to the Russian fort like a blade"
   }
  ],
  "counts": [
   {
    "what": "family members intercepted",
    "value": 3,
    "quote": "all three now held under guard in Vedeno"
   },
   {
    "what": "Jemal Eddin's age",
    "value": 30,
    "quote": "JEMAL EDDIN (30)"
   }
  ],
  "time_markers": [
   "DAY"
  ],
  "injuries": []
 },
 {
  "scene": "33",
  "characters_active": [
   "KHANEFI",
   "MARYA DMITRIEVNA",
   "ELDAR",
   "HADJI MURAD",
   "BUTLER"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "ELDAR",
    "event": "object_transfer",
    "detail": "Carries Hadji Murad's tray through the house",
    "quote": "Eldar carries Hadji Murad's tray through"
   }
  ],
  "objects": [
   {
    "object": "copper bowl",
    "action": "used",
    "holder": "Khanefi",
    "detail": "Holds it in kitchen doorway, directed to water"
   },
   {
    "object": "tray",
    "action": "used",
    "holder": "Eldar",
    "detail": "Carries Hadji Murad's tray through the house"
   }
  ],
  "counts": [
   {
    "what": "words in Hadji Murad's praise of the song",
    "value": 4,
    "quote": "four words from a man who has recognized his own obituary"
   }
  ],
  "time_markers": [
   "EVENING"
  ],
  "injuries": []
 },
 {
  "scene": "34",
  "characters_active": [
   "HADJI MURAD",
   "ELDAR",
   "MARYA DMITRIEVNA",
   "PETROV",
   "BUTLER"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "object_transfer",
    "detail": "Gives white burka to Marya Dmitrievna with both hands",
    "quote": "holds it out with both hands"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "object_transfer",
    "detail": "Gives the Gurda sword to Major Petrov",
    "quote": "The Gurda sword goes to Petrov"
   },
   {
    "position": 3,
    "who": "HADJI MURAD",
    "event": "departure",
    "detail": "Mounts and rides away from the fort with his men",
    "quote": "The riders dwindle"
   }
  ],
  "objects": [
   {
    "object": "white burka",
    "action": "transferred",
    "holder": "Marya Dmitrievna",
    "detail": "Given by Hadji Murad via Eldar as a parting gift"
   },
   {
    "object": "Gurda sword",
    "action": "transferred",
    "holder": "Petrov",
    "detail": "Given by Hadji Murad as a parting gift"
   }
  ],
  "counts": [],
  "time_markers": [
   "MORNING",
   "On the morning of departure"
  ],
  "injuries": [
   {
    "character": "HADJI MURAD",
    "injury": "limp (old leg injury)",
    "quote": "Hadji Murad limps to Marya Dmitrievna"
   }
  ]
 },
 {
  "scene": "35",
  "characters_active": [
   "HADJI MURAD",
   "LORIS-MELIKOV"
  ],
  "characters_inert": [
   "ARGUTINSKI",
   "SOFIAT",
   "PATIMAT",
   "YUSUF"
  ],
  "ordered_events": [],
  "objects": [],
  "counts": [],
  "time_markers": [
   "DAY",
   "next week (referenced, future)"
  ],
  "injuries": []
 },
 {
  "scene": "36",
  "characters_active": [
   "HADJI MURAD",
   "KIRILLOV"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "arrival",
    "detail": "Enters his Nukha reception room in riding dress, does not sit",
    "quote": "Hadji Murad enters in riding dress, dust on his boots"
   },
   {
    "position": 2,
    "who": "KIRILLOV",
    "event": "object_transfer",
    "detail": "Counts seven piles of ten gold coins onto the table",
    "quote": "counts seven piles of ten gold coins onto the table"
   },
   {
    "position": 3,
    "who": "HADJI MURAD",
    "event": "object_transfer",
    "detail": "Sweeps the gold coins into his sleeve in one motion",
    "quote": "sweeps them into his sleeve in one motion"
   },
   {
    "position": 4,
    "who": "HADJI MURAD",
    "event": "departure",
    "detail": "Slaps Kirillov's bald pate and walks out of the room",
    "quote": "slaps Kirillov's bald pate with the flat of his hand"
   }
  ],
  "objects": [
   {
    "object": "spy's report",
    "action": "introduced",
    "holder": "HADJI MURAD",
    "detail": "Folded, set on the table between the two men"
   },
   {
    "object": "sealed dispatch",
    "action": "introduced",
    "holder": "KIRILLOV",
    "detail": "Extended toward Hadji Murad, who refuses to take it"
   },
   {
    "object": "gold coins",
    "action": "transferred",
    "holder": "HADJI MURAD",
    "detail": "Seven piles of ten swept into his sleeve"
   },
   {
    "object": "leather satchel",
    "action": "introduced",
    "holder": "KIRILLOV",
    "detail": "Kirillov arrives carrying the satchel"
   }
  ],
  "counts": [
   {
    "what": "gold coin piles",
    "value": 7,
    "quote": "seven piles of ten gold coins"
   },
   {
    "what": "coins per pile",
    "value": 10,
    "quote": "seven piles of ten gold coins"
   }
  ],
  "time_markers": [
   "DAY"
  ],
  "injuries": []
 },
 {
  "scene": "37",
  "characters_active": [
   "HADJI MURAD",
   "ELDAR",
   "SPIES",
   "MESSENGERS"
  ],
  "characters_inert": [
   "SHAMIL",
   "YUSUF"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "SPIES",
    "event": "arrival",
    "detail": "Two hooded spies enter Hadji Murad's quarters at dusk",
    "quote": "Two SPIES enter hooded"
   },
   {
    "position": 2,
    "who": "MESSENGERS",
    "event": "arrival",
    "detail": "Two road-dusted messengers report Shamil's watchers everywhere",
    "quote": "Two road-dusted messengers add that Shamil's watchers are on every road"
   },
   {
    "position": 3,
    "who": "HADJI MURAD",
    "event": "object_transfer",
    "detail": "Slides a gold coin across the carpet to each man",
    "quote": "slides a gold coin across the carpet to each man"
   },
   {
    "position": 4,
    "who": "HADJI MURAD",
    "event": "departure",
    "detail": "Rises, prepares gear, orders Eldar to saddle two horses",
    "quote": "tells Eldar to saddle the bay and the second horse"
   }
  ],
  "objects": [
   {
    "object": "gold coins",
    "action": "transferred",
    "holder": "SPIES/MESSENGERS",
    "detail": "One coin slid to each of the four visitors"
   },
   {
    "object": "silver coin (Yusuf's token)",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "On leather thong at throat, closed in his hand"
   },
   {
    "object": "saddle blanket",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "Lifted down, folded once, set beside his sword"
   },
   {
    "object": "sword",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "Set beside the folded saddle blanket"
   }
  ],
  "counts": [
   {
    "what": "hooded spies",
    "value": 2,
    "quote": "Two SPIES enter hooded"
   },
   {
    "what": "road-dusted messengers",
    "value": 2,
    "quote": "Two road-dusted messengers"
   }
  ],
  "time_markers": [
   "DUSK TO NIGHT",
   "Grey-blue dusk",
   "Hours later"
  ],
  "injuries": []
 },
 {
  "scene": "38",
  "characters_active": [
   "KHANEFI",
   "BATA",
   "GAMZALO"
  ],
  "characters_inert": [],
  "ordered_events": [],
  "objects": [],
  "counts": [],
  "time_markers": [
   "BEFORE FIRST LIGHT"
  ],
  "injuries": []
 },
 {
  "scene": "39",
  "characters_active": [
   "HADJI MURAD",
   "COSSACKS"
  ],
  "characters_inert": [
   "ELDAR"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "COSSACKS",
    "event": "arrival",
    "detail": "Cossacks approach fast on the ridge at first light",
    "quote": "Hoofbeats on the ridge — Cossacks, coming fast"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "departure",
    "detail": "Swings into the saddle with dagger drawn, rides out at dawn",
    "quote": "He swings into the saddle, dagger already drawn"
   }
  ],
  "objects": [
   {
    "object": "dagger",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "Already drawn as he mounts"
   }
  ],
  "counts": [
   {
    "what": "horses",
    "value": 5,
    "quote": "Five horses in frost-burned scrub"
   }
  ],
  "time_markers": [
   "FIRST GREY LIGHT",
   "dawn"
  ],
  "injuries": []
 },
 {
  "scene": "40",
  "characters_active": [
   "HADJI MURAD",
   "NAZAROV",
   "GAMZALO",
   "COSSACKS"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "NAZAROV",
    "event": "arrival",
    "detail": "Rides at Hadji Murad's stirrup with the escort",
    "quote": "NAZAROV (28) rides at his stirrup"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Veers toward the ridge a mile out, draws pistol",
    "quote": "A pistol clears the burka"
   },
   {
    "position": 3,
    "who": "COSSACKS",
    "event": "death",
    "detail": "Four escorting Cossacks shot down in three heartbeats",
    "quote": "four Cossacks down in the dust"
   },
   {
    "position": 4,
    "who": "COSSACKS",
    "event": "escape",
    "detail": "The fifth Cossack rides hard for the watchtower",
    "quote": "the fifth bent low over his horse's neck, riding hard"
   }
  ],
  "objects": [
   {
    "object": "pistol",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "Cleared from the burka, kills four Cossacks"
   }
  ],
  "counts": [
   {
    "what": "Cossack mounts flanking",
    "value": 5,
    "quote": "five Cossack mounts flanking close"
   },
   {
    "what": "Cossacks down",
    "value": 4,
    "quote": "four Cossacks down in the dust"
   },
   {
    "what": "Cossack escaped",
    "value": 1,
    "quote": "the fifth bent low over his horse's neck"
   },
   {
    "what": "distance before veer",
    "value": 1,
    "quote": "A mile out, Hadji Murad veers toward the ridge"
   }
  ],
  "time_markers": [
   "MORNING"
  ],
  "injuries": [
   {
    "character": "COSSACKS (four of the escort)",
    "injury": "shot dead by Hadji Murad's pistol",
    "quote": "four Cossacks down in the dust"
   }
  ]
 },
 {
  "scene": "41",
  "characters_active": [
   "HADJI MURAD",
   "ELDAR",
   "MURIDS"
  ],
  "characters_inert": [
   "HAMZAD"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Turns left toward the flooded rice-fields against instinct",
    "quote": "Hadji Murad turns left"
   },
   {
    "position": 2,
    "who": "PURSUERS",
    "event": "arrival",
    "detail": "Many horses heard approaching the night camp",
    "quote": "horses, many of them"
   }
  ],
  "objects": [
   {
    "object": "burkas",
    "action": "used",
    "holder": "MURIDS",
    "detail": "Spread like dark altars on the only dry ground"
   }
  ],
  "counts": [],
  "time_markers": [
   "DAY TO DEEP NIGHT",
   "Deep night now",
   "last night"
  ],
  "injuries": []
 },
 {
  "scene": "42",
  "characters_active": [
   "HADJI MURAD",
   "KARGANOV",
   "MURIDS"
  ],
  "characters_inert": [
   "ELDAR"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "MURIDS",
    "event": "physical_action",
    "detail": "Six men cut branches and throw earth onto a low bank",
    "quote": "Six men cut branches with daggers, throw earth onto a low bank"
   },
   {
    "position": 2,
    "who": "KARGANOV",
    "event": "arrival",
    "detail": "His surrender call drifts across the shrubs",
    "quote": "KARGANOV's (~40) surrender call drifts across the shrubs"
   }
  ],
  "objects": [
   {
    "object": "daggers",
    "action": "used",
    "holder": "MURIDS",
    "detail": "Used to cut branches for the earth bank"
   }
  ],
  "counts": [
   {
    "what": "men digging in",
    "value": 6,
    "quote": "Six men cut branches with daggers"
   }
  ],
  "time_markers": [
   "PRE-DAWN"
  ],
  "injuries": []
 },
 {
  "scene": "43",
  "characters_active": [
   "HADJI AGA",
   "HADJI MURAD",
   "ELDAR",
   "BATA",
   "KHAN MAHOMA",
   "KHANEFI"
  ],
  "characters_inert": [],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI AGA",
    "event": "arrival",
    "detail": "Reins in twenty paces off with two hundred riders, calls out",
    "quote": "reins in twenty paces off, two hundred riders behind him"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Lowers rifle, recalls Hadji Aga once ate from his dish",
    "quote": "once Hadji Aga ate from his dish"
   },
   {
    "position": 3,
    "who": "HADJI MURAD",
    "event": "wound",
    "detail": "Wedged behind bank, beshmet torn, cotton wool in wound",
    "quote": "beshmet torn, blackened cotton wool in the wound"
   },
   {
    "position": 4,
    "who": "ELDAR",
    "event": "death",
    "detail": "A bullet takes him as he leans past the bank, falls onto Hadji Murad's leg",
    "quote": "a bullet takes him; he reels back onto Hadji Murad's leg"
   },
   {
    "position": 5,
    "who": "BATA",
    "event": "death",
    "detail": "Sits hard in dirt, throat ragged, spits red, goes still",
    "quote": "throat ragged, spits red, goes still"
   }
  ],
  "objects": [
   {
    "object": "rifle",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "Passed by Khanefi; he sights without hurry"
   },
   {
    "object": "powder flask",
    "action": "used",
    "holder": "KHANEFI",
    "detail": "Last flask set within reach at the bank wall"
   },
   {
    "object": "dagger",
    "action": "used",
    "holder": "ELDAR",
    "detail": "Drawn as he half-rises and leans past the bank"
   }
  ],
  "counts": [
   {
    "what": "riders behind Hadji Aga",
    "value": 200,
    "quote": "two hundred riders behind him"
   },
   {
    "what": "distance Hadji Aga reins in",
    "value": 20,
    "quote": "reins in twenty paces off"
   },
   {
    "what": "open road offered",
    "value": 1,
    "quote": "the road back open for one hour"
   }
  ],
  "time_markers": [
   "CONTINUOUS",
   "Spring greens",
   "today"
  ],
  "injuries": [
   {
    "character": "HADJI MURAD",
    "injury": "gunshot wound packed with blackened cotton wool",
    "quote": "beshmet torn, blackened cotton wool in the wound"
   },
   {
    "character": "ELDAR",
    "injury": "shot dead, falls onto Hadji Murad's leg",
    "quote": "a bullet takes him; he reels back onto Hadji Murad's leg"
   },
   {
    "character": "BATA",
    "injury": "throat wound, spits red and dies",
    "quote": "throat ragged, spits red, goes still"
   }
  ]
 },
 {
  "scene": "44",
  "characters_active": [
   "MICHAEL VORONTSOV",
   "SHAMIL",
   "YUSUF"
  ],
  "characters_inert": [
   "HADJI MURAD"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "MICHAEL VORONTSOV",
    "event": "speech",
    "detail": "Dictates that the dispatch say Hadji Murad fell bravely, refusing surrender",
    "quote": "Hadji Murad fell bravely, surrounded, refusing surrender"
   },
   {
    "position": 2,
    "who": "COURIER",
    "event": "object_transfer",
    "detail": "Kneels before Shamil with a cloth bundle on the carpet",
    "quote": "a courier kneels with a cloth bundle on the carpet"
   },
   {
    "position": 3,
    "who": "SHAMIL",
    "event": "physical_action",
    "detail": "Does not look up, strokes his beard once, turns a Quran page",
    "quote": "does not look up, strokes his beard once, turns a page"
   },
   {
    "position": 4,
    "who": "YUSUF",
    "event": "physical_action",
    "detail": "Presses ear to cold stone, then turns his face to the wall",
    "quote": "Yusuf presses his ear to cold stone and listens upward"
   }
  ],
  "objects": [
   {
    "object": "folded telegram",
    "action": "used",
    "holder": "MICHAEL VORONTSOV",
    "detail": "Read before dictating the official dispatch"
   },
   {
    "object": "cloth bundle (severed head)",
    "action": "transferred",
    "holder": "SHAMIL",
    "detail": "Delivered by kneeling courier onto the carpet"
   },
   {
    "object": "Quran",
    "action": "used",
    "holder": "SHAMIL",
    "detail": "Across his knees; he turns a page"
   },
   {
    "object": "untouched bowl",
    "action": "introduced",
    "holder": "YUSUF",
    "detail": "Sits beside Yusuf in the pit"
   }
  ],
  "counts": [],
  "time_markers": [
   "CONTINUOUS"
  ],
  "injuries": []
 },
 {
  "scene": "45",
  "characters_active": [
   "HADJI MURAD",
   "HADJI AGA",
   "YOUNG RIDER"
  ],
  "characters_inert": [
   "KHANEFI",
   "KHAN MAHOMA",
   "GAMZALO"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Drags himself out, fires pistol once, walks forward on broken leg",
    "quote": "walks forward on the broken leg — dagger in hand, straight at the guns"
   },
   {
    "position": 2,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Speaks his son's name once into the open air",
    "quote": "speaks his son's name once into the open air"
   },
   {
    "position": 3,
    "who": "HADJI MURAD",
    "event": "death",
    "detail": "Second volley takes him against a young tree's trunk",
    "quote": "before the second volley takes him"
   },
   {
    "position": 4,
    "who": "HADJI AGA",
    "event": "object_transfer",
    "detail": "Kneels, takes the head with two clean strokes, rolls it away",
    "quote": "Two clean strokes, eyes on the middle distance, and the head comes free"
   },
   {
    "position": 5,
    "who": "KHANEFI",
    "event": "capture",
    "detail": "Stands bound with Khan Mahoma and Gamzalo, watching",
    "quote": "stand bound, watching, naming nothing"
   },
   {
    "position": 6,
    "who": "KHAN MAHOMA",
    "event": "capture",
    "detail": "Stands bound with Khanefi and Gamzalo, watching",
    "quote": "stand bound, watching, naming nothing"
   },
   {
    "position": 7,
    "who": "GAMZALO",
    "event": "capture",
    "detail": "Stands bound with Khanefi and Khan Mahoma, watching",
    "quote": "stand bound, watching, naming nothing"
   }
  ],
  "objects": [
   {
    "object": "pistol",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "Fired once as he drags himself from the bank"
   },
   {
    "object": "dagger",
    "action": "used",
    "holder": "HADJI AGA",
    "detail": "Two clean strokes take the head free"
   },
   {
    "object": "severed head",
    "action": "transferred",
    "holder": "HADJI AGA",
    "detail": "Rolled away with the side of his foot"
   }
  ],
  "counts": [
   {
    "what": "clean strokes to take the head",
    "value": 2,
    "quote": "Two clean strokes, eyes on the middle distance"
   }
  ],
  "time_markers": [
   "DAY"
  ],
  "injuries": [
   {
    "character": "HADJI MURAD",
    "injury": "shot by rifles then killed by second volley, decapitated",
    "quote": "blood at his side and shoulder and face"
   }
  ]
 },
 {
  "scene": "46",
  "characters_active": [
   "KAMENEV",
   "BUTLER",
   "MARYA DMITRIEVNA",
   "PETROV",
   "COSSACK",
   "CORPORAL"
  ],
  "characters_inert": [
   "AVDEEV"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "KAMENEV",
    "event": "arrival",
    "detail": "Dismounts in moonlit yard, lifts a heavy linen sack",
    "quote": "KAMENEV (~40) dismounts in the moonlit yard"
   },
   {
    "position": 2,
    "who": "KAMENEV",
    "event": "object_transfer",
    "detail": "Hauls out the severed head by the shaven skull",
    "quote": "He hauls out the head by the shaven skull"
   },
   {
    "position": 3,
    "who": "CORPORAL",
    "event": "object_transfer",
    "detail": "Seals Avdeev's death notice packet for the post",
    "quote": "a corporal seals a thin packet for the post"
   },
   {
    "position": 4,
    "who": "PETROV",
    "event": "physical_action",
    "detail": "Sways toward the head, presses his mouth to the dead forehead",
    "quote": "presses his mouth to the dead forehead"
   }
  ],
  "objects": [
   {
    "object": "linen sack",
    "action": "used",
    "holder": "KAMENEV",
    "detail": "Lifted from saddle-bag, holds the severed head"
   },
   {
    "object": "severed head",
    "action": "used",
    "holder": "KAMENEV",
    "detail": "Hauled out by skull, later slid back into canvas by Cossack"
   },
   {
    "object": "Avdeev death notice packet",
    "action": "introduced",
    "holder": "CORPORAL",
    "detail": "Sealed for the post, addressed to a snow-covered village"
   }
  ],
  "counts": [],
  "time_markers": [
   "NIGHT",
   "moonlit",
   "At the same dim hour"
  ],
  "injuries": []
 },
 {
  "scene": "47",
  "characters_active": [
   "MARYA DMITRIEVNA",
   "BUTLER"
  ],
  "characters_inert": [
   "KAMENEV",
   "PETROV"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "BUTLER",
    "event": "arrival",
    "detail": "Steps out onto the porch and reaches for a word",
    "quote": "Butler steps out and reaches for a word"
   },
   {
    "position": 2,
    "who": "MARYA DMITRIEVNA",
    "event": "speech",
    "detail": "Says they are all cut-throats; a head belongs in the earth",
    "quote": "They are all cut-throats, she says, flat and final"
   },
   {
    "position": 3,
    "who": "MARYA DMITRIEVNA",
    "event": "departure",
    "detail": "Stands, descends the last step, walks toward the dark",
    "quote": "walks toward the dark without looking back"
   }
  ],
  "objects": [
   {
    "object": "white burka",
    "action": "used",
    "holder": "MARYA DMITRIEVNA",
    "detail": "Carried out, laid across her knees, smoothed once by hand"
   }
  ],
  "counts": [],
  "time_markers": [
   "NIGHT"
  ],
  "injuries": []
 },
 {
  "scene": "48",
  "characters_active": [],
  "characters_inert": [],
  "ordered_events": [],
  "objects": [
   {
    "object": "thistle",
    "action": "introduced",
    "holder": "none",
    "detail": "Bent and bloodied at ditch edge, then upright and flowering"
   }
  ],
  "counts": [],
  "time_markers": [
   "DAY",
   "midsummer light"
  ],
  "injuries": []
 },
 {
  "scene": "KEY_SCENE",
  "characters_active": [
   "HADJI MURAD",
   "BATA",
   "GAMZALO",
   "KHANEFI",
   "HADJI AGA",
   "KHAN MAHOMA",
   "ELDAR"
  ],
  "characters_inert": [
   "KARGANOV",
   "AKHMET KHAN",
   "YUSUF",
   "PATIMAT",
   "HAMZAD"
  ],
  "ordered_events": [
   {
    "position": 1,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Sets his rifle on the embankment without rising",
    "quote": "sets his rifle on the embankment without rising"
   },
   {
    "position": 2,
    "who": "BATA",
    "event": "physical_action",
    "detail": "Wipes mud from his lock, eyes the slope above",
    "quote": "wipes mud from his lock and eyes the slope"
   },
   {
    "position": 3,
    "who": "BATA",
    "event": "speech",
    "detail": "Warns the ditch is shallow and exposed",
    "quote": "bad ditch. Shallow. The wolf does not sleep"
   },
   {
    "position": 4,
    "who": "BATA",
    "event": "physical_action",
    "detail": "Spits toward the open ground",
    "quote": "spits toward the open ground"
   },
   {
    "position": 5,
    "who": "GAMZALO",
    "event": "physical_action",
    "detail": "Returns from the edge and lays rifle across earthwork",
    "quote": "lays his rifle across the earthwork"
   },
   {
    "position": 6,
    "who": "GAMZALO",
    "event": "speech",
    "detail": "Reports Karganov's militia on both sides of the clump",
    "quote": "Karganov. Militia. Both sides of the clump."
   },
   {
    "position": 7,
    "who": "KHANEFI",
    "event": "object_transfer",
    "detail": "Slides a powder pouch to Hadji Murad's hand",
    "quote": "slides a powder pouch toward Hadji Murad's hand"
   },
   {
    "position": 8,
    "who": "KHANEFI",
    "event": "speech",
    "detail": "Reports powder dry, forty rounds, and the dagger ready",
    "quote": "Powder dry. Forty rounds, agha — and the dagger."
   },
   {
    "position": 9,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Cuts a branch with his dagger, lays it on the bank",
    "quote": "cuts a branch with his dagger, lays it on the bank"
   },
   {
    "position": 10,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Orders three men to dig the ditch deeper",
    "quote": "dig deeper. A handful of earth is worth a brother"
   },
   {
    "position": 11,
    "who": "HADJI AGA",
    "event": "arrival",
    "detail": "Reins in twenty paces off the ditch, stays mounted",
    "quote": "reins in twenty paces off"
   },
   {
    "position": 12,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Lowers his rifle a finger's width, looks across",
    "quote": "lowers his rifle a finger's width. Looks across"
   },
   {
    "position": 13,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Reminds Hadji Aga he once ate from his dish",
    "quote": "Once you ate from my dish. Today you bring two hundred guns"
   },
   {
    "position": 14,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Turns his head toward Karganov's line",
    "quote": "turns his head a fraction toward the open ground"
   },
   {
    "position": 15,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Challenges Karganov to come closer and count again",
    "quote": "Karganov. You are many. We are six. Come closer and count again."
   },
   {
    "position": 16,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Nods toward the clearing edge at the black mare",
    "quote": "nods once toward the clearing edge"
   },
   {
    "position": 17,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Orders Bata to send the black mare out first",
    "quote": "the black mare first. A horse without a rider tells the militia"
   },
   {
    "position": 18,
    "who": "BATA",
    "event": "physical_action",
    "detail": "Tightens his belt, does not look back",
    "quote": "tightens his belt. Does not look back"
   },
   {
    "position": 19,
    "who": "BATA",
    "event": "speech",
    "detail": "Says his horse will walk home alone and proud",
    "quote": "she walks home alone, she walks proud"
   },
   {
    "position": 20,
    "who": "BATA",
    "event": "physical_action",
    "detail": "Climbs to the bank",
    "quote": "He climbs to the bank"
   },
   {
    "position": 21,
    "who": "BATA",
    "event": "death",
    "detail": "Shot while climbing the bank, dies instantly",
    "quote": "A shot cracks. Bata pitches into the mud. Still."
   },
   {
    "position": 22,
    "who": "ELDAR",
    "event": "physical_action",
    "detail": "Half-rises from the ditch, dagger half-drawn",
    "quote": "half-rises from the ditch, dagger half-drawn"
   },
   {
    "position": 23,
    "who": "ELDAR",
    "event": "speech",
    "detail": "Warns it is Akhmet Khan on the ridge",
    "quote": "It is Akhmet Khan. He rode at your stirrup once."
   },
   {
    "position": 24,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Orders Khanefi to reload, tells Eldar to sit",
    "quote": "Eldar, sit. A dagger is for the last step, not the first."
   },
   {
    "position": 25,
    "who": "ELDAR",
    "event": "physical_action",
    "detail": "Settles, plants a knee against the earth wall",
    "quote": "settles. Plants a knee against the earth wall"
   },
   {
    "position": 26,
    "who": "KHAN MAHOMA",
    "event": "physical_action",
    "detail": "Fires, lowers the smoking rifle, spits",
    "quote": "fires, lowers the smoking rifle, spits"
   },
   {
    "position": 27,
    "who": "KHAN MAHOMA",
    "event": "speech",
    "detail": "Reports a boy crawling the bushes toward them",
    "quote": "The boy is here, agha. Crawling the bushes himself."
   },
   {
    "position": 28,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Marks one shrub with his eyes, then the next",
    "quote": "marks one shrub with his eyes, then the next"
   },
   {
    "position": 29,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Says he knew the boy's father, will meet the son soon",
    "quote": "The son I will meet soon enough."
   },
   {
    "position": 30,
    "who": "GAMZALO",
    "event": "physical_action",
    "detail": "Shifts nearer to Hadji Murad, thumbs a fresh cartridge",
    "quote": "shifts one pace nearer to Hadji Murad"
   },
   {
    "position": 31,
    "who": "GAMZALO",
    "event": "speech",
    "detail": "Says the shrubs do half the work, ready to act",
    "quote": "Let them come. The shrubs do half the work."
   },
   {
    "position": 32,
    "who": "GAMZALO",
    "event": "physical_action",
    "detail": "Glances once at the dying mare in the bushes",
    "quote": "Gamzalo glances at it once"
   },
   {
    "position": 33,
    "who": "GAMZALO",
    "event": "speech",
    "detail": "Notes his horse is down, one less rein to hold",
    "quote": "My horse is down. Good. One less rein to hold."
   },
   {
    "position": 34,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Glances at the dying mare, then the sun on a branch",
    "quote": "glances at the dying mare in the grass"
   },
   {
    "position": 35,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Says when sun clears the branch they go to the river",
    "quote": "When the sun clears that branch, we go to the river."
   },
   {
    "position": 36,
    "who": "KHANEFI",
    "event": "physical_action",
    "detail": "Loads powder, passes long gun up, touches Hadji Murad's sleeve",
    "quote": "slaps powder into the pan, passes the long gun up"
   },
   {
    "position": 37,
    "who": "KHANEFI",
    "event": "speech",
    "detail": "Says he came to repay Hadji Murad's mother's milk",
    "quote": "Your mother's milk. I came to give it back. It is done."
   },
   {
    "position": 38,
    "who": "HADJI MURAD",
    "event": "object_transfer",
    "detail": "Gives Yusuf's silver coin to Khanefi to deliver",
    "quote": "presses it once, drops it into Khanefi's palm"
   },
   {
    "position": 39,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Instructs the coin go to the boy, no words needed",
    "quote": "this, to the boy. No words. He will read it."
   },
   {
    "position": 40,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Draws both palms slowly down his beard",
    "quote": "He draws both palms slowly down his beard."
   },
   {
    "position": 41,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Says Allah knows, it is well",
    "quote": "Allah knows. It is well."
   },
   {
    "position": 42,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Rises, fires twice, wades out of the ditch into the open",
    "quote": "rises. He fires, fires again, wades up out of the ditch"
   },
   {
    "position": 43,
    "who": "ELDAR",
    "event": "wound",
    "detail": "Struck down in the militia volley at the earth wall",
    "quote": "Eldar goes down at the earth wall"
   },
   {
    "position": 44,
    "who": "KHANEFI",
    "event": "capture",
    "detail": "Dragged back, pistol struck from his hand",
    "quote": "Khanefi is dragged back, his pistol struck from his hand"
   },
   {
    "position": 45,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Reaches a single tree, sets his shoulder to the trunk",
    "quote": "reaches a single tree and sets his shoulder to the trunk"
   },
   {
    "position": 46,
    "who": "HADJI MURAD",
    "event": "wound",
    "detail": "Wounded at his side, shoulder, and face",
    "quote": "Blood at his side, his shoulder, his face"
   },
   {
    "position": 47,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Fires until the rifle is empty, draws the dagger",
    "quote": "He fires until the rifle is empty, draws the dagger."
   },
   {
    "position": 48,
    "who": "HADJI MURAD",
    "event": "wound",
    "detail": "Militia closes in, he collapses at the foot of the tree",
    "quote": "He goes down at the foot of the tree"
   },
   {
    "position": 49,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Calls out his son's name as he lies dying",
    "quote": "Yusuf..."
   },
   {
    "position": 50,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "His hand searches the bark of the tree",
    "quote": "His hand searches the bark of the tree."
   },
   {
    "position": 51,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Calls out to his mother, asks for the song",
    "quote": "Mother. The song."
   },
   {
    "position": 52,
    "who": "KHAN MAHOMA",
    "event": "capture",
    "detail": "Ordered bound alive along with Khanefi and Gamzalo",
    "quote": "Bind them — Khanefi, Khan Mahoma, Gamzalo."
   },
   {
    "position": 53,
    "who": "GAMZALO",
    "event": "capture",
    "detail": "Ordered bound alive along with Khanefi and Khan Mahoma",
    "quote": "Bind them — Khanefi, Khan Mahoma, Gamzalo."
   },
   {
    "position": 54,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Murmurs of a horse, a black one",
    "quote": "A horse. A black one."
   },
   {
    "position": 55,
    "who": "KHAN MAHOMA",
    "event": "speech",
    "detail": "Mocks the militia rolling the severed head like a melon",
    "quote": "they roll his head like a melon"
   },
   {
    "position": 56,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Body shudders, pushes once from the trunk",
    "quote": "Hadji Murad's body shudders. He pushes once from the trunk."
   },
   {
    "position": 57,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Declares Hadji Murad has stood",
    "quote": "Hadji Murad has stood."
   },
   {
    "position": 58,
    "who": "GAMZALO",
    "event": "physical_action",
    "detail": "Bound, leans toward the body, praying",
    "quote": "leans toward the body, jaw set, lips moving in prayer"
   },
   {
    "position": 59,
    "who": "GAMZALO",
    "event": "speech",
    "detail": "Vows he follows one step behind, as he swore",
    "quote": "Hadji Agha. I come. One step before. As I swore."
   },
   {
    "position": 60,
    "who": "KHANEFI",
    "event": "physical_action",
    "detail": "Bound beside Gamzalo, sets his back to Gamzalo's",
    "quote": "sets his back to Gamzalo's"
   },
   {
    "position": 61,
    "who": "KHANEFI",
    "event": "speech",
    "detail": "Sings of Hamzad's grave and the avenger who did not sleep",
    "quote": "The earth dried on Hamzad's grave — the avenger did not sleep."
   },
   {
    "position": 62,
    "who": "HADJI MURAD",
    "event": "physical_action",
    "detail": "Palms try to draw down the beard, then fall",
    "quote": "Hadji Murad's palms try to draw down the beard. They fall."
   },
   {
    "position": 63,
    "who": "HADJI MURAD",
    "event": "speech",
    "detail": "Final words, Allah knows",
    "quote": "Allah knows."
   },
   {
    "position": 64,
    "who": "HADJI MURAD",
    "event": "death",
    "detail": "Dies at the foot of the tree",
    "quote": "He is still."
   },
   {
    "position": 65,
    "who": "KHAN MAHOMA",
    "event": "physical_action",
    "detail": "Stiffens, looks away from the corpse",
    "quote": "stiffens, then looks away from the corpse"
   },
   {
    "position": 66,
    "who": "KHAN MAHOMA",
    "event": "speech",
    "detail": "Tells Khanefi to listen, says Allah is not impressed",
    "quote": "Quiet, Khanefi. Listen. The nightingales again. Allah is not impressed."
   },
   {
    "position": 67,
    "who": "KHAN MAHOMA",
    "event": "physical_action",
    "detail": "Lifts bound hands toward the Russian line",
    "quote": "lifts his bound hands toward the Russian line"
   },
   {
    "position": 68,
    "who": "KHAN MAHOMA",
    "event": "speech",
    "detail": "Insists he rode beside Hadji Murad, demands it be recorded",
    "quote": "I rode beside him, you understand? Beside. Write that down somewhere, Russian."
   },
   {
    "position": 69,
    "who": "KHANEFI",
    "event": "physical_action",
    "detail": "Drops the spent pistol, lifts both wrists to the militiaman",
    "quote": "Khanefi drops the spent pistol, lifts both wrists to the militiaman."
   },
   {
    "position": 70,
    "who": "KHANEFI",
    "event": "speech",
    "detail": "Tells the militiaman to bind him, his hands are nothing now",
    "quote": "Bind me, dog. My hands are nothing now."
   }
  ],
  "objects": [
   {
    "object": "powder pouch",
    "action": "transferred",
    "holder": "HADJI MURAD",
    "detail": "Khanefi slides it to Hadji Murad, powder confirmed dry"
   },
   {
    "object": "dagger",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "Cuts a branch with it, later drawn as the rifle empties"
   },
   {
    "object": "long gun",
    "action": "transferred",
    "holder": "HADJI MURAD",
    "detail": "Khanefi passes it up loaded during the firefight"
   },
   {
    "object": "powder flask",
    "action": "transferred",
    "holder": "HADJI MURAD",
    "detail": "Khanefi sets the last flask within Hadji Murad's reach"
   },
   {
    "object": "silver coin",
    "action": "transferred",
    "holder": "KHANEFI",
    "detail": "Hadji Murad gives Yusuf's coin to Khanefi for the boy"
   },
   {
    "object": "pistol",
    "action": "destroyed",
    "holder": "KHANEFI",
    "detail": "Struck from his hand when captured; later drops the spent pistol"
   },
   {
    "object": "rifle",
    "action": "used",
    "holder": "HADJI MURAD",
    "detail": "Fired repeatedly until empty during the final stand"
   },
   {
    "object": "severed head",
    "action": "used",
    "holder": "HADJI AGA",
    "detail": "Rolled aside with his foot after the beheading"
   }
  ],
  "counts": [
   {
    "what": "defenders in the ditch",
    "value": 6,
    "quote": "Six men crouch behind the earth wall"
   },
   {
    "what": "militia (Khan Mahoma's count)",
    "value": 200,
    "quote": "Hadji Aga brings two hundred guests"
   },
   {
    "what": "rounds of ammunition",
    "value": 40,
    "quote": "Forty rounds, agha"
   },
   {
    "what": "Hadji Murad's age",
    "value": 47,
    "quote": "HADJI MURAD, forty-seven, broad and still"
   }
  ],
  "time_markers": [
   "DAWN",
   "Mist sits in the hollows.",
   "The sun clears the branch.",
   "The mist lifts."
  ],
  "injuries": [
   {
    "character": "BATA",
    "injury": "Shot dead while climbing to the bank",
    "quote": "A shot cracks. Bata pitches into the mud. Still."
   },
   {
    "character": "ELDAR",
    "injury": "Struck down in the militia volley at the earth wall",
    "quote": "Eldar goes down at the earth wall"
   },
   {
    "character": "HADJI MURAD",
    "injury": "Wounded at his side, shoulder, and face before falling",
    "quote": "Blood at his side, his shoulder, his face"
   },
   {
    "character": "HADJI MURAD",
    "injury": "Dies at the foot of the tree",
    "quote": "He is still."
   },
   {
    "character": "HADJI MURAD",
    "injury": "Beheaded posthumously by Hadji Aga",
    "quote": "Move the foot. Not the shoe — the head. Clean. Clean."
   }
  ]
 }
]

CANDIDATES:
[
 {
  "candidate_id": "H1",
  "rule": "holistic_pass",
  "type": "character_status",
  "severity": "critical",
  "scenes": [
   "Character Descriptions",
   "43",
   "45",
   "KEY_SCENE"
  ],
  "description": "Eldar's death is described as happening first, by falling onto Hadji Murad's leg after being shot, in the character list and treatment scene 43, but in the fully dramatized Key Scene he survives through nearly the entire firefight and dies last, at the same moment Hadji Murad exits the ditch for his own death charge, with no leg-fall moment at all.",
  "evidence_quotes": [
   "who dies first in the ditch, falling onto his master's leg",
   "Eldar half-rises, dagger drawn, leans past the bank — a bullet takes him; he reels back onto Hadji Murad's leg; the two men hold each other's eyes once before Hadji Murad draws his leg slowly free.",
   "Hadji Murad rises. He fires, fires again, wades up out of the ditch into the open. The shrubs erupt. Muzzle-flash from every side. Eldar goes down at the earth wall."
  ]
 },
 {
  "candidate_id": "H2",
  "rule": "holistic_pass",
  "type": "timeline",
  "severity": "high",
  "scenes": [
   "7",
   "18"
  ],
  "description": "Michael Vorontsov is shown on-site at the frontier fort the night before Hadji Murad's surrender, already aware something is imminent, yet is later shown in Tiflis learning of the defection for the first time via a courier dispatch, presented as a surprise to a room of dinner guests.",
  "evidence_quotes": [
   "MICHAEL VORONTSOV (~70), silver-haired viceroy, is summoned out by a servant, returns composed, calls for champagne, and reveals nothing. As the guests put on their coats he draws Poltoratsky aside: his company is ordered to the forest tomorrow.",
   "Michael Vorontsov takes a sealed dispatch in the doorway of his dining room, thirty candlelit guests behind him, reads it standing, then raises his eyes to ELIZABETH (~55) and gives a small, deliberate nod. He tells the room the Caucasus has produced a surprise: Hadji Murad has crossed to their side."
  ]
 },
 {
  "candidate_id": "H3",
  "rule": "holistic_pass",
  "type": "identity",
  "severity": "high",
  "scenes": [
   "19",
   "45",
   "KEY_SCENE"
  ],
  "description": "In the Key Scene, Eldar identifies the rider on the ridge as 'Akhmet Khan' himself, but Akhmet Khan was already established as dead, and the treatment's own prose account of the same moment identifies the rider as Akhmet Khan's son, not Akhmet Khan.",
  "evidence_quotes": [
   "Hadji Murad answers that Akhmet Khan is dead and Shamil lives; he will not die before he settles it.",
   "It is Akhmet Khan. He rode at your stirrup once.",
   "A YOUNG RIDER at his shoulder — Akhmet Khan's son, the inherited feud made flesh, his father's debt riding on his face"
  ]
 },
 {
  "candidate_id": "H4",
  "rule": "holistic_pass",
  "type": "object",
  "severity": "medium",
  "scenes": [
   "15",
   "23",
   "26"
  ],
  "description": "The gold repeater watch is established as belonging to Simon Vorontsov, and Hadji Murad explicitly declines to accept it when offered as a gift, yet an earlier scene in the same dictation sequence shows Hadji Murad producing a gold repeater watch from his own breast pocket as though he already owns one.",
  "evidence_quotes": [
   "Hadji Murad turns it once to the light, holds it to his ear, and hands it back face-up",
   "Hadji Murad draws a gold repeater watch from his breast pocket and presses the spring: twelve delicate chimes from a different world.",
   "Vorontsov slides the case across the table; Hadji Murad does not take it"
  ]
 },
 {
  "candidate_id": "H5",
  "rule": "holistic_pass",
  "type": "object",
  "severity": "medium",
  "scenes": [
   "37",
   "KEY_SCENE"
  ],
  "description": "The silver coin Yusuf gave Hadji Murad is established as worn on a leather thong at his throat, but in the Key Scene he produces the same coin from his belt instead.",
  "evidence_quotes": [
   "his hand finds the small leather thong at his throat — the silver coin Yusuf gave him, the son's token",
   "He works the small silver coin Yusuf gave him from his belt, presses it once, drops it into Khanefi's palm."
  ]
 },
 {
  "candidate_id": "H6",
  "rule": "holistic_pass",
  "type": "object",
  "severity": "medium",
  "scenes": [
   "36",
   "37"
  ],
  "description": "Hadji Murad sweeps Kirillov's bribe gold into his sleeve in one motion, but the same gold is described in the next scene sitting untouched in a heap on the floor, with no scene showing it removed from his sleeve.",
  "evidence_quotes": [
   "Kirillov counts seven piles of ten gold coins onto the table; Hadji Murad sweeps them into his sleeve in one motion",
   "The gold he was paid sits untouched in a bright heap on the floor."
  ]
 },
 {
  "candidate_id": "H7",
  "rule": "holistic_pass",
  "type": "character_status",
  "severity": "medium",
  "scenes": [
   "37",
   "44",
   "Summary"
  ],
  "description": "A spy reports Yusuf has been relocated away from Vedeno to a newly dug pit 'beyond' it, but the summary places Yusuf's final pit scene as being 'beneath Vedeno,' and scene 44 lists 'the pit' as a location distinct from 'Vedeno' in its own heading — the two accounts of where Yusuf ends up are not reconciled.",
  "evidence_quotes": [
   "the old spy adds that Yusuf has been moved deeper — Vedeno, then beyond, the pit already dug.",
   "in the pit beneath Vedeno, Yusuf presses his ear to cold stone and listens upward into the dark"
  ]
 },
 {
  "candidate_id": "H8",
  "rule": "holistic_pass",
  "type": "count",
  "severity": "medium",
  "scenes": [
   "25",
   "40"
  ],
  "description": "Hadji Murad demands a guard of honor of twenty chosen Cossacks as his condition for cooperating, but only five Cossacks are shown accompanying him on the ride during which he makes his escape, with no explanation for the discrepancy.",
  "evidence_quotes": [
   "a guard of honor of twenty chosen Cossacks, himself at its head, riding the foothills near the line",
   "White Kabarda mare, five Cossack mounts flanking close."
  ]
 },
 {
  "candidate_id": "H9",
  "rule": "holistic_pass",
  "type": "character_status",
  "severity": "medium",
  "scenes": [
   "Summary",
   "32"
  ],
  "description": "The summary frames Shamil as proactively seizing Hadji Murad's already-present family after learning of the defection, while scene 32 states the family was intercepted while attempting to reach the Russian line themselves — two different, unreconciled accounts of how the family came to be captured.",
  "evidence_quotes": [
   "Shamil, learning of the defection, moves against the family. He takes Hadji Murad's wives, mother, and Yusuf prisoner, forces the boy to write a letter under duress",
   "reports that Hadji Murad's wife, mother, and son Yusuf were intercepted before they reached the Russian line"
  ]
 },
 {
  "candidate_id": "H10",
  "rule": "holistic_pass",
  "type": "count",
  "severity": "low",
  "scenes": [
   "39",
   "42"
  ],
  "description": "The breakout party is staged with 'five horses' at the ridge above Nukha, but the ditch stand explicitly establishes six men (Hadji Murad plus five murids) making up the full party, implying a mismatched horse count.",
  "evidence_quotes": [
   "Five horses in frost-burned scrub, breath steaming, girths tight.",
   "Six men cut branches with daggers, throw earth onto a low bank"
  ]
 },
 {
  "candidate_id": "H11",
  "rule": "holistic_pass",
  "type": "identity",
  "severity": "low",
  "scenes": [
   "Character Descriptions",
   "22"
  ],
  "description": "Hadji Murad's present age (47) minus his stated flashback age (twenty-five) implies the remembered event occurred about 22 years earlier, while Shamil's present age (mid-50s) minus his stated flashback age (~38) implies only about 17 years earlier for the same remembered event.",
  "evidence_quotes": [
   "HADJI MURAD (47)",
   "SHAMIL (mid 50s; ~38 in flashback)",
   "a lean, hard young man at a latticed window inside the Khunzakh palace — HADJI MURAD AT TWENTY-FIVE."
  ]
 }
]

FULL DOCUMENT:
──────────────────────────────────
# HADJI MURAD — Treatment (Pipeline Treatment Format)
*Fiction Project — Long Feature Film (approx. 141 min) · Based on the novella by Lev Tolstoy*

## Log-Line / Genre / Format

In the last winter of the Caucasian War, a legendary Avar warlord defects from the rebel imam who holds his family hostage and throws himself on the mercy of the Russian Empire — only to discover that both the holy warrior and the Tsar will use him, neither will save his wife and son, and a man who refuses to submit to either has nowhere left to stand but his own grave.

GENRE: Historical War Tragedy / Anti-Imperial Fable

FORMAT: Cinema-Feature (Long Feature Film, approx. 141 min)

## Character Descriptions

CHARACTER DESCRIPTIONS


MAIN CHARACTERS


HADJI MURAD (47) is the last great Avar naib — a warrior whose name alone turned Russian columns back to their forts. He wants one thing: to recover his wife, mother, and son from Shamil's captivity by handing the Russians something they cannot refuse, never naming that the exchange makes him a hostage in his turn. A commander now navigating by patience and flattery, he buys every gilded salon against the single fact of his son in a stone pit at Vedeno. He dies in a ditch not because he miscalculated but because he calculated correctly — and the calculation made him unbearable.

SHAMIL (mid 50s; ~38 in flashback) is the Imam of Dagestan and Chechnya, the mountains' sacred sovereign — and the film's most dangerous antagonist, because he is never wrong about the political logic of what he does. The defection of a naib is not a military loss but a theological crack, and he means to close it: Hadji Murad back in submission, or dead. He holds the family as leverage, forces Yusuf to write under duress, and calls the whole machine justice while turning a page of the Quran. In the flashback he already stands two paces behind the killing.

MICHAEL VORONTSOV (~70) is Viceroy of the Caucasus, English-educated, conqueror at Krasnoe, wielding imperial power with the ease of a man who has never doubted his place in history. He wants Hadji Murad delivered to Petersburg as a bloodless trophy confirming his mastery of an impossible frontier. He receives his guest with courtesy and calculation in the same gesture — his sympathy real, and insufficient to protect the man he has taken in.

SIMON VORONTSOV (28) commands the Kurin Regiment and receives Hadji Murad's defection as a personal coup, vindication of the Vorontsov name on the line. He hosts his guest at the fort and later across a plain table in Tiflis, pouring the wine himself, his warmth quickly becoming real. What he must learn is that his pledged word and the empire's are not the same — his decency genuine and useless at once — and he watches from inside the machinery as the man he respected is maneuvered beyond his reach.

LORIS-MELIKOV (32) is Vorontsov's assigned supervisor and interpreter for Hadji Murad in Tiflis — professionally Russian, personally Caucasian, quietly aware of both. Through the long dictation of Hadji Murad's life he turns from paid listener into moral witness, and the report he produces begins to indict the system that commissioned it. He carries the empire's evasions in his own mouth, saying patience once too often, and ends loyal in form, holding a record that will outlast the regime he serves.

MARYA DMITRIEVNA (30) is the frontier fort's de facto wife — practical, fair-haired, very freckled, the only person at the outpost without a rank to hide behind. She overrules the major to lodge Hadji Murad properly, takes the white burka he gives her, and tells him to bring himself home. When drunken officers parade his severed head, she steps clean out of her domestic role — a dead man's head belongs in the earth, she says — and walks into the dark, the film's last and plainest verdict.

YUSUF (18) is Hadji Murad's son, held in a stone pit at Vedeno awaiting Shamil's judgment. He wants to stand beside his father as a warrior; what he needs is to accept that surviving is not cowardice. Brought up reeking and black-eyed to write the letter that travels to the Russian fort like a blade, he snatches a dagger at his own throat and is wrenched back into the dark. He remains in the pit, ear pressed to cold stone — the pressure that destroys his father.


SUPPORTING CHARACTERS


BUTLER (24) is the young officer newly down from the Guards, full of the romance of the war, whom Hadji Murad chooses with two extended fingers and who survives to watch the empire kiss what it killed.

SADO (58) is the highland host who shelters Hadji Murad and defies Shamil's arrest order to honor the kunak bond, then buries his own son when the aoul is destroyed.

ELDAR (22) is Hadji Murad's closest murid — a wrestler's body and a shy child's face hiding the retinue's most violent capacity — who dies first in the ditch, falling onto his master's leg.

BATA (35) is the sun-blackened guide who sells Hadji Murad the road to the Russian lines for a pinch of millet and dies in the final ditch.

KHANEFI, KHAN MAHOMA and GAMZALO are the three murids who ride the whole defection — the grief-singer, the smiling one who keeps singing under fire, the one-eyed scarred fighter — and survive the stand only to stand bound, watching him die.

PANOV (38) is the veteran NCO of dry calm who leads the night ambush patrols and sits longest at Avdeev's deathbed, holding the candle upright in the dying hands.

AVDEEV (32) is the regiment's cheerful peasant soldier, shot in a skirmish, who dictates his last words home and is filed up the chain as a routine line.

HADJI AGA (~40s) was once Hadji Murad's kunak and now leads the militia at the marsh, calling the surrender and then taking the head with his own dagger, eyes turned from the face throughout.

PETROV (mid 40s) is the frontier major who holds his sector together through routine and ends drunk, pressing his mouth to the severed forehead.

MARYA VASILEVNA (30), Simon Vorontsov's wife, and ELIZABETH (~55), Michael Vorontsov's, are the salon hostesses who treat Hadji Murad's arrival as the season's coup.

NICHOLAS I (~50) rules from a distance so great it becomes the film's most violent force, while his Minister of War CHERNYSHOV (~60) renders Vorontsov's opportunity into the only grammar the Tsar reads — a name, a cost, a use.

PATIMAT (~70) is Hadji Murad's mother, grey-haired and fierce-eyed, who alone refuses to watch Shamil's entry into Vedeno; with SOFIAT (~35), his wife, glimpsed behind the lattice, she is the hostage the story turns on.

KIRILLOV (~45), JEMAL EDDIN (30), TARKHANOV (~45), KARGANOV (~40), NAZAROV (28) and KAMENEV (~40) are the functionaries of the closing machinery — the councillor whose bribe earns a slap, the secretary who reads the death-proclamation, the interpreter-prince, the commander who calls the parley, the Cossack at the last break, and the officer who hauls the head from a sack.

In the Khunzakh flashback, HAMZAD (~45), ABU NUTSAL KHAN (~25), and the KHANSHA (~28) enact the buried wound — the rival Imam who murders his guests under hospitality, the foster-brother who rides to his death against warning, and the scarred mother whose fear sets the blood-debt running.

## Summary

In the Caucasus of 1851, a lone thistle survives at the edge of a cart track — mauled, stem crushed, yet flowering. It is the film's first image and its last.

Hadji Murad, the legendary Avar war chief, has spent a lifetime fighting both the Russian Empire and the mountain theocracy of Shamil. When Shamil's men arrive in the night to arrest him, Hadji Murad makes a decision that will destroy him: he rides toward the Russian lines and surrenders. His calculation is cold and clear — by offering the Russians his knowledge and his name, he buys the leverage to ransom his family, wife, mother, and son Yusuf, still held in Shamil's stronghold at Vedeno.

The Russians receive him with the careful ceremonial warmth of men who want his intelligence more than his safety. In a series of drawing rooms moving from the frontier fort to Tiflis to the Viceroy's palace, Hadji Murad navigates an empire that treats him as a trophy and a tool simultaneously. Viceroy Vorontsov is gracious and calculating in equal measure; his wife's curiosity is genuine; the bureaucratic machinery behind them — Chernyshov, Meller-Zakomelsky, the distant Tsar Nicholas — processes Hadji Murad's fate with the unhurried indifference of men signing other men's death warrants between dinner courses.

Meanwhile Shamil, learning of the defection, moves against the family. He takes Hadji Murad's wives, mother, and Yusuf prisoner, forces the boy to write a letter under duress, and sentences Hadji Murad to death by any hand that can reach him. The family will not be freed. Petersburg grants Hadji Murad provisional cooperation but says nothing about a wife. Nothing about a son. The dispatch authorizing his use arrives and does not contain the one word — pardon — that would make any of it matter. Hadji Murad refuses to wait the paper out: he sets his own terms, demanding to ride the foothills near the line with a guard of honor so that his name does the work no dispatch will do.

Relocated to a house near a mosque in Nukha, Hadji Murad waits as weeks become months. The intelligence he traded has been absorbed; his value is declining; his family remains in the pit. In the small hours before morning prayers, he makes his second and final decision. He orders the horses saddled and rides out — not as a guest, not as a prisoner.

The breakout ends in flooded rice-fields at the base of the mountains, in a shallow ditch cut from mud and branches. Six men against two hundred. His retinue is broken — Eldar and Bata die in the ditch, the others taken bound and forced to watch. He himself is shot through, drags himself from the bank, walks forward on a broken leg with a dagger in his hand, and is brought down by a second volley against a young tree. He speaks his son's name once into the open air. Hadji Aga severs the head and rolls it away from the body.

In three rooms the same news arrives differently: Vorontsov dictates an honorable telegram because it costs the empire nothing to say so; Shamil turns a single page of the Quran without looking up; in the pit beneath Vedeno, Yusuf presses his ear to cold stone and listens upward into the dark.

The film's last image returns to the first: the thistle at the roadside, bent and bloodied at the base of the ditch, crown still upright. Match cut to midsummer — the same slope, the same thistle, flowering in full light, the Caucasus unchanged behind it.

## Treatment

ACT ONE

1. EXT. CAUCASIAN STEPPE — LATE SUMMER, AFTERNOON

A harvested field: stubble gray-gold, earth stripped bare. At the verge of a cart track stands a single thistle — stem crushed, leaves torn, one branch still upright and vivid with purple flower. A HORSEMAN emerges from the tree line, unhurried across the flat country in mountain dress, sheepskin papakha low over his face. He passes the thistle without pausing. The steppe absorbs him. The thistle trembles in the wind and does not fall.

2. EXT. MAHKET AOUL — DUSK

A lone rider holds his horse to a walk on the descent above the aoul. Below: mud-walled saklyas packed tight as honeycomb, kizyak smoke rising in thin blue columns against the darkening sky. HADJI MURAD (47), tall and broad-shouldered, keeps his eyes on the rooftops, one hand loose at his side. A murid follows three lengths behind. The muezzin's call dies on the wind. Hadji Murad does not slow.

3. EXT./INT. MAHKET — SADO'S SAKLYA — NIGHT

Two riders move through a narrow side street, hoods low. Hadji Murad stops at a saklya cut into the hillside and taps a sleeping shape on the roof with his whip handle. SADO (58), lashless eyes carrying thirty years of war, descends without hurry and works his feet into wooden-heeled slippers. ELDAR (22), enormous and alert, moves the old man aside by placement alone. Inside: whitewashed clay walls, two copper basins catching lamplight, weapons racked in order. An old servant lifts Hadji Murad's rifle and sword and hangs them beside the house weapons — slow, both hands, the gesture of a man handling something consecrated. Sado's wife sets cushions along the front wall without looking at the men. The two leaders lower themselves to the floor, exchange greetings, and pray in near-silence, drawing their hands down their beards in unison. Sado confirms what Hadji Murad already knows: Shamil's order arrived yesterday — the village cannot openly defy it. Hadji Murad names his requirement — a guide to the Russian lines. Sado calls his son; the boy returns with BATA (35), sun-blackened, compact, coat frayed at every seam. Bata takes in Hadji Murad without flinching and grins.

4. INT. SADO'S SAKLYA — NIGHT

A wooden bowl of millet sits between them, untouched. Sado withdraws to the door post and half-turns away — host, not party to the bargain. Hadji Murad keeps his eyes on the millet, not on Bata, and names the road he wants and the silence he is buying. Bata pinches a few grains of millet from the bowl, rolls them once between thumb and finger, and lets them fall back — the price set, the count understood, no number spoken aloud. Hadji Murad's hand stays on the worn bone hilt of his kindjal. The grin does not leave Bata's face. The deal closes without a handshake.

5. INT. SADO'S SAKLYA — NIGHT

Sado pours cold water from a metal ewer over Hadji Murad's hands. Hadji Murad turns his sleeves back with precise, unhurried movements and dries on a coarse towel. At the low table he draws a rolled note from beneath a cartridge-bullet and lays it on the boards between them. He eats sparingly — a sliver of bread, a scrape of cheese — then presses honey onto a crust with the flat of his small knife and eats that too, slowly, as a man eats who means the meal to be witnessed. He instructs that the note travel to his son; any reply returns through Sado. Sado lays his right palm flat over his own heart and holds it there — the kunak bond, sworn without a word, binding as blood. Eldar reaches for the bread, sees Hadji Murad's hand withdraw, and draws his own back. Sado's hand closes over the note and does not move from it.

6. EXT. FOREST AMBUSH POST — VOZVIZHENSK — NIGHT

Three Russian soldiers move single-file through dark forest and halt at a blackened plane tree. PANOV (38) squats against the trunk, coat pockets empty. AVDEEV (32), broad-cheeked, hollows a depression in the soil, seats a pipe stem into it, packs tobacco flush, gets the ember going, draws once, rolls aside to make room. Panov wipes the stem on his sleeve and lies prone. Smoke curls into bare branches; the stars do not move. Panov says Hadji Murad himself may have crossed near Mahket. No one answers. Then two silhouettes break from the treeline — BATA, both empty hands raised wide, a taller murid mirroring him. Bata steps into thin moonlight and announces himself before anyone demands it, extending a folded letter between two worlds. Panov takes the paper; AVDEEV and BONDARENKO (26) march the pair toward the fort's distant lights. Returning, Avdeev drops his rifle butt to the earth and crouches by the fire, shaking his head — those shaved-headed boys are fine fellows. One lit window burns gold behind the pines.

7. INT. FORT — VORONTSOV DRAWING ROOM — NIGHT

Four candles burn on a card table. Rich curtains, carpeted floors — a Petersburg salon transplanted whole into the Caucasian war. SIMON VORONTSOV (28) deals. PRINCESS MARYA VASILEVNA (30) leans toward POLTORATSKY (25) across the green baize, her crinoline pressing his leg; he plays an ace into a losing hand and does not care. MICHAEL VORONTSOV (~70), silver-haired viceroy, is summoned out by a servant, returns composed, calls for champagne, and reveals nothing. As the guests put on their coats he draws Poltoratsky aside: his company is ordered to the forest tomorrow. After the last candle is pinched out, Marya Vasilevna confronts Simon in the empty room, arms crossed. Simon corrects her with unmistakable pride: it was not Hadji Murad himself — his emissary. Hadji Murad will come tomorrow, in person. The candle dies.

8. INT. SADO'S SAKLYA — NIGHT

The embers are nearly cold; a wick gutters in its wall niche. Hadji Murad's hand finds his pistol before his eyes open — SADO is already crouching before him without a lamp. A woman on a roof saw him; the aoul knows; the elders have gone to the mosque and mean to hold him until morning. Outside, wooden shoes clatter on packed dirt, voices gathering. Eldar sleeps in the corner with pistol and dagger still in his belt, lips moving slightly. Sado rests a hand on his own chest and says his house is Hadji Murad's house, the horses saddled. Hadji Murad rises without a word.

9. EXT. SADO'S COURTYARD / VILLAGE LANE — NIGHT

Starlight only. Saklya roofs cut black silhouettes; the mosque stands at the top of the lane like a held breath. A boy holds two steaming horses. Hadji Murad swings into the saddle in one continuous motion, rifle across his thigh; Eldar settles behind him. Sado walks alongside in an oversized sheepskin, crossing from side to side of the lane as though to absorb any bullet aimed at the rider. At the lane's mouth shadows peel from a wall — five men, muskets rising, a voice barking the command to halt. Hadji Murad does not halt. He draws the pistol from his belt and spurs straight into them; the line breaks apart against the wall and the horses pass through. Sado's hand rises once at the lane's end, then drops.

10. EXT. RAVINE ABOVE THE STREAM — NIGHT

Hadji Murad reins the blowing horse in on a rise. Below, water runs over stone. Behind him in the aoul, cocks answer one another across the roofs — and beneath them, a tramp of hooves, the low voices of many men. Eldar halts at his shoulder, rifle half out of its cover. Hadji Murad does not look back. He nudges the horse forward at a walk, holding the pace until twenty mounted men close the gap and fan out behind him in the dark. Then he stops. He drops the bridle from his right hand. With his left he unbuttons the rifle-cover, draws the weapon halfway, and lets it ride loose across his thigh — facing forward, away from the riders, a man declining to run and declining to fight, daring the dark to decide first. The riders hold their distance. No shot comes. After a long beat he buttons the cover, takes up the bridle, and rides on at the same unbroken walk. The hooves behind him thin, fall back, and are gone.

11. EXT. FOREST GLADE — NIGHT TO PRE-DAWN

A bonfire smolders between dark pines. KHANEFI (30), GAMZALO (40), and two murids crouch around it; at Hadji Murad's arrival the coals are scattered with boot heels and stamped to ash. Gamzalo lifts a rifle and moves to the forest edge unbidden; Eldar ties the horses apart between two trees. In the cold hour before dawn Hadji Murad pours water over his hands from an ewer, removes his shoes, spreads his burka on the needle-covered earth, and prays — lips moving, the only sound. Jackals howl across the ravine, a cry between weeping and laughter. The eastern sky bleeds grey-rose behind the pines. KHAN MAHOMA (27) rides in at first light: the Russian prince received him and will see Hadji Murad tomorrow. Hadji Murad says only that it is well, and shakes earth from his burka.

12. EXT. FOREST ROAD — MORNING

Mist drifts through felled timber; axes thud at the tree line in a slow mechanical rhythm. Hadji Murad rides into the clearing at the head of a small mounted party, erect, weapons gleaming from the night's cleaning. The Russians stop eating; POLTORATSKY rises. Hadji Murad halts twenty paces out and waits — he does not dismount, does not speak. Khan Mahoma translates the silence: he said he would come; he came. The column forms and moves into the forest. Poltoratsky and his officers eat from paper wrappings on upturned drums, laughing about a general's famous saber charge — a story they all know was invented. A rifle shot cracks; a bullet splinters a birch twenty meters off. Nobody flinches. Poltoratsky grins, calls for his horse, and rides out into a thin, inconclusive exchange with Chechen horsemen across the ravine. The Chechens turn their horses and pull back into the trees. Panov, behind him, keeps his own counsel.

13. EXT. WIDE BIRCH GLADE — MORNING

Cold filtered light. SIMON VORONTSOV sits his English chestnut at the center, adjutant and Chechen interpreter flanking; sharpshooters have dissolved into the brush. Hooves silent on pine needles, Hadji Murad rides in on a white-maned horse, weapons gold-ornamented, turban white, four murids behind him in absolute formation. He reins in three paces from Vorontsov; neither man moves; the forest settles into silence. Hadji Murad draws his palms slowly down his beard and speaks through the interpreter: he has come, and it is well. Vorontsov dismounts first — the courtesy of a host, not a captor — and extends his hand. The gold on Hadji Murad's weapons catches once in slanting light as the two horses turn together toward the fort road.

---

ACT TWO

---

14. EXT. FORT VOZDVIZHENSKAYA GATE / VORONTSOV HOUSE — MORNING

The frozen road before the fort, rutted ice catching grey light. Hadji Murad dismounts first, places his right hand on his heart, and speaks through the interpreter: he surrenders himself to the will of the Russian Tsar; he wished to serve long ago, but Shamil would not let him. Simon Vorontsov listens without expression, white-gloved hand extended. Hadji Murad studies the gloved fingers a long beat before pressing them — not submission, a contract. Behind him his four murids sit their horses without moving: Eldar broad and watchful; GAMZALO one-eyed and scarred, his single red eye crossing the crowding soldiers without contempt or fear; Khanefi holding a high-headed black stud-horse on a taut lead, the animal stamping at the strangers; Khan Mahoma the only one who smiles. Vorontsov waves an officer silent rather than disperse the gawkers — he wants this seen. Inside the house — pale Petersburg plaster, a French clock on the mantel, chairs from another continent — Hadji Murad stands at the center, papakha still on, filling the room with a stillness the furniture does not understand. MARYA VASILEVNA extends her hand; he takes it briefly, formally, and a flush crosses his face before he masters it. A boy of six watches from beside her skirt. Through the interpreter Hadji Murad sets his terms: a kunak's house is sacred, his family is sacred. The boy drifts close and reaches for the kinzhal at his belt; Hadji Murad lets him touch the hilt. The clock chimes once; he does not look at it.

15. INT. VORONTSOV HOUSE — DINING ROOM / HADJI MURAD'S ROOM — AFTERNOON

White tablecloth, low afternoon light along the silver. Hadji Murad sits rigid and takes only from the dish Marya Vasilevna has already served herself; she murmurs to her husband that he does it every meal. Simon Vorontsov draws a gold repeater watch from his waistcoat, touches the spring — twelve thin chimes. Hadji Murad goes still, then reaches; Vorontsov sets the watch in his palm and, at his wife's quiet word, leaves it there. Hadji Murad turns it once to the light, holds it to his ear, and hands it back face-up — a man weighing another man's craft. Later, alone, he tests the door's weight with one hand and counts the windows. Eldar reports from the threshold: horses in the stable, the black stud among them, men in the barn, weapons not taken. They are not yet prisoners. Hadji Murad sits motionless on the divan, the kinzhal across his knees, eyes open in the dark.

16. INT. MELLER-ZAKOMELSKY'S HEADQUARTERS — ANTEROOM — DAY

A bare anteroom: cracked plaster, one oil lamp, a hard bench. Simon Vorontsov murmurs reassurance; Hadji Murad does not sit but reads the room the way a soldier reads ground. Through the wall comes the muffled quarrel — MELLER-ZAKOMELSKY (~55) planted between desk and door, refusing Vorontsov a chair, declaring he has not served twenty-seven years to let men who began yesterday on family connections act under his nose. Hadji Murad runs one finger along the grain of the bench and waits. Two men are fighting over the right to file him. Empire has registered its prize, assigned the paperwork, and already begun forgetting the man at its center.

17. INT. FIELD HOSPITAL — DAY TO NIGHT

Avdeev is carried in and lowered onto the last cot, a wax taper waiting unlit on the crate beside it. He groans once, clamps his jaw, presses both hands over his belly. The DOCTOR turns him to check the exit wound, sees old flogging scars crossing his back like surveyor's lines; Avdeev says they were for money he drank, long ago. The doctor plasters the wound and walks out composing the log entry. Panov and SEROGIN (28) come in caps in hand; Panov lays his palm against Avdeev's cold hand and asks whether there is word for home. Avdeev dictates slowly, choosing each word like a man who cannot revise it — the distance from the village, the brother, the wife. Outside the flap Poltoratsky watches the stretcher pass, an unlit cigar in his fingers, and tells an orderly only to carry on. By night the taper is pressed between Avdeev's fingers, but the hands will not grip; Panov closes both his own hands around them and holds the candle upright until the flame steadies, then leans to the still chest, straightens, and sets the candle on the empty cot ledge. Far off, in a snow-buried village, a sealed notice will arrive, and the woman who receives it will fold it with both hands, the way you fold laundry, and go back to work.

18. INT. VORONTSOV'S PALACE — TIFLIS — DINING ROOM — EVENING

A dust-caked courier crosses the lamplit foyer. Michael Vorontsov takes a sealed dispatch in the doorway of his dining room, thirty candlelit guests behind him, reads it standing, then raises his eyes to ELIZABETH (~55) and gives a small, deliberate nod. He tells the room the Caucasus has produced a surprise: Hadji Murad has crossed to their side. Elizabeth says at once that they must receive him properly; Vorontsov allows the thinnest smile — they already are. At the table the CARROTY GENERAL (~50) names the Dargo ambush, how Hadji Murad cut the column in two, and uses the word twice; Vorontsov's fingers still on the wine stem, his smile holding, his eyes not. MANANA ORBELYANI (~40) pivots smoothly to the General's Tiflis quarters; he blinks, derailed. The machinery of the command is already turning.

19. INT. VORONTSOV'S CABINET — TIFLIS — DAY

Sunlight through green blinds cuts the oak table in long bars. The antechamber empties of petitioners; Hadji Murad enters in his white Circassian coat, silver lace at the collar, crosses the floor with a lame gait that makes each step a ceremony, places both hands on his chest, eyes lowered, and through Prince TARKHANOV's (~45) translation makes his formal submission. Vorontsov answers in French — gracious, committing to nothing — then raises the word pardon; Hadji Murad's jaw tightens. He insists: he served faithfully in 1839; Akhmet Khan lied to the general; that drove him out. Vorontsov turns to how Hadji Murad means to settle his account with Shamil. Hadji Murad answers that Akhmet Khan is dead and Shamil lives; he will not die before he settles it. Vorontsov will write to Petersburg. Until then, Hadji Murad is his guest. On the way out Hadji Murad passes a chained wall-clock and does not slow.

20. INT. TIFLIS THEATER / VORONTSOV RESIDENCE — EVENING

The theater glitters — chandeliers, bare shoulders, champagne. Hadji Murad sits beside LORIS-MELIKOV (32), papakha on, watching the Italian opera the way a man waits out weather; at the interval he rises without explanation and walks into the corridor. The next evening at the salon, Elizabeth offers pleasantries; Loris-Melikov translates; Hadji Murad answers in Avar that the hall was bright, and Loris-Melikov tells her it was magnificent. Hadji Murad inclines his head and stays exactly where he stands — on display, unbroken, unreachable.

21. INT. HADJI MURAD'S QUARTERS — TIFLIS — DAY

A whitewashed room, a leather notebook open on Loris-Melikov's knee, pen above a blank page. He explains: the Prince has read what others wrote; he wants it from Hadji Murad; it goes to the Emperor. A long pause. Hadji Murad takes a small ivory-handled knife and begins to whittle a sliver of wood, shavings dropping to the stone floor as he speaks without looking up — of Tselmess, the small aoul near Khunzakh; of his mother, who nursed the Khan's sons; of the day his father sent her back to the Khansha. He stops the blade. He presses two fingers against his own ribs, finding on his body a scar that belongs to her. The shavings lie pale on the dark stone. Loris-Melikov's pen moves steadily.

22. INT. TIFLIS GUESTHOUSE / EXT. CAUCASUS MOUNTAINS — PAST (FLASHBACK)

The lamp burns amber. Hadji Murad lays his right hand flat on the table and presses down, as if testing the wood for something underneath. Then he speaks, and the room gives way.

A rooftop in Khunzakh, the night sky raked with stars: a woman lies under a fur coat, a small boy against her side. KHANSHA (~28) lifts the edge of her blouse and sets the boy's hand on the puckered ridge of a saber scar across her sternum. His fingers trace it in the dark while she sings — a low mountain lament, barely above breath. The song ends; the boy's hand stays where she placed it.

A cut across years: a lean, hard young man at a latticed window inside the Khunzakh palace — HADJI MURAD AT TWENTY-FIVE. The Khansha sits rigid behind him, amber beads clicking twice, then stopping. Her son ABU NUTSAL KHAN (~25) paces in ceremonial cherkesska, fastening a silver belt with shaking fingers; two brothers already hostage in Hamzad's camp. The Khansha says the one thing left to her — that she sees he is afraid. He calls for his horse. Hadji Murad rides at his stirrup, into the mountains.

Hamzad's camp on the high ridge: banners snapping, a ring of murids in deep-indigo cherkesskas firing celebratory volleys. HAMZAD (~45) comes forward on foot and lays his hand on Abu Nutsal's stirrup, a courtesy kept for kings. SHAMIL (~38) stands two paces behind, beard still, eyes moving once to Hadji Murad and away. Hamzad gestures the Khan toward a great tent of bleached cream wool; Hadji Murad moves to follow. Shamil steps into his path — no word, only a stillness that shuts a door. The flap falls. A single muffled gunshot, like a hand pressed over a mouth. Silence. Wind through empty grass. The bridles go slack in Hadji Murad's fist. He runs — down scree and scrub-oak, boots slipping on frost-slick stone, not looking back at the tent where the Khansha's sons lie still.

23. INT. TIFLIS GUESTHOUSE — NIGHT (RETURN FROM FLASHBACK)

Back in the room. Hadji Murad's face has gone dark red; he says he was seized with fear and ran. The lamp turns his hands to old bronze. Loris-Melikov has not written a word. After a silence the length of a prayer, Hadji Murad draws a gold repeater watch from his breast pocket and presses the spring: twelve delicate chimes from a different world. Never after that, he says — since then he has always remembered the shame, and when he remembers it he fears nothing. He gives the cliff in a flat clerk's voice on his way to the burka — the rope path above Mansokha, the bound arms, the soldier he dragged into the air with him; both bodies fell, the mist took them, and he, as Loris can observe, remained alive. He lifts the hem of his right trouser leg and presses the shortened, twisted limb flat to the floorboards as if testing whether it still holds him, then drops the cloth: it is time to pray. Through the doorway the four murids keep their separate orbits around a dying fire — Eldar upright, rifle across his knees; Gamzalo plaiting a bridle with fast tight fingers; Khan Mahoma whittling; Khanefi with a sack of rice. Loris-Melikov watches men bound by an oath older than his army, his empire, his language, and understands for the first time that Hadji Murad is not here because Russia won.

24. INT. WAR MINISTRY — ST. PETERSBURG — DAY

Winter light through frosted glass. CHERNYSHOV (~60) breaks Vorontsov's wax seal without haste and reads; nothing shifts in his face. He folds the dispatch with the same crease as the twenty identical packets stacked by his lamp, crosses to the cabinet for a fresh sheet, dips his pen, writes a line, strikes it out, writes again. What Vorontsov frames as opportunity, Chernyshov renders into the only grammar NICHOLAS I (~50) will read: a name, a probable cost, a use. Above him, in apartments he enters only when summoned, the Tsar has not yet been given the name Hadji Murad.

25. INT. LORIS-MELIKOV'S OFFICE — TIFLIS — AFTERNOON (THE ULTIMATUM)

Maps pinned to plaster, Hadji Murad's papakha balanced on his knee because no one has offered a hook. Loris-Melikov reads the latest dispatch flat: Shamil will not release the family; a pardon and rank may come, but the family stays hostage until Petersburg decides. Hadji Murad sets the papakha on the table and stands. He crosses to the map and lays one finger on Vedeno, then drags it down to the Russian line and stops — the whole distance measured on the wall in front of the interpreter. He will not sit in salons while the paper travels north and south and changes nothing. He gives Loris-Melikov terms to carry up, not a plea: a guard of honor of twenty chosen Cossacks, himself at its head, riding the foothills near the line — close enough that the mountains can see him moving and his name does the work no dispatch will do. His hand goes to the hilt of his dagger and rests there — not drawn. He does not go back into Shamil's hand. Allah holds the day. He waits, standing, until Loris-Melikov writes the condition into the report exactly as given.

26. INT. VORONTSOV RESIDENCE — TIFLIS — EVENING TO MORNING

Simon Vorontsov sits across the dinner table from Hadji Murad in a plain house coat, no servant, and pours two glasses himself. Hadji Murad turns the glass once and drinks. Loris-Melikov translates, but the silences run longer than the words: Vorontsov asks the name of the aoul where Hadji Murad was born; Hadji Murad names it and goes quiet; Vorontsov says he has ridden that valley. Hadji Murad looks at him — not trust, but the recognition that a man who has ridden that valley is not only an enemy. Marya Vasilevna pauses in the doorway to refill the lamp; Hadji Murad rises unasked, a mountain courtesy that startles the room more than any speech. In grey morning light he finds Vorontsov at his writing table, the gold repeater open beside the inkwell — the same chime from the dining room weeks ago. He lifts it, holds it to his ear at the quarter-hour, sets it back face-up, and gives one nod: a craftsman to another's work. Vorontsov slides the case across the table; Hadji Murad does not take it; Vorontsov draws it back without embarrassment. No transaction, but something offered and weighed.

27. INT. WINTER PALACE — ST. PETERSBURG — DAY / LORIS-MELIKOV'S ANTEROOM — TIFLIS — EVENING

Petitions in neat stacks on Nicholas's green baize. The Caucasus dispatch has come north by post-horse and stamped leather pouch; Chernyshov opens the folder. Nicholas drags two fingers across a Caucasus map as if scraping the mountains bare, stamps a verdict without looking up, then turns to a student-case folder and sentences a Polish Catholic to pass twelve times through a thousand men while reaching for the next seal. He signs.

The answer travels south. In Tiflis, Loris-Melikov brings it to Hadji Murad in a single folded sheet. Hadji Murad holds the paper at arm's length, tilted, weight forward, the way he holds a weapon, and reads it once. It authorizes cooperation, grants provisional trust, lets him ride with Russian columns. It does not name his wife. It does not name his son Yusuf. It does not name his mother. He folds it along its crease and hands it back without a word. The lamp throws two shadows on the wall that do not touch.

28. EXT. TIFLIS PARADE GROUND — LATE AFTERNOON

Vorontsov and Hadji Murad ride the outer edge, away from the drilling companies, dust hanging gold behind the hooves. Vorontsov points to the distant ridge and names the peaks in Russian; Hadji Murad gives the Avar names back, one by one, correcting without weight. At the far gate Vorontsov tries a short phrase in broken Avar; Hadji Murad answers slowly, as a man teaches a child. The paper said nothing about a son, and Vorontsov does not ask what it said. They ride back without speaking.

29. EXT. RUINED AOUL — SADO'S SAKLYA — DAY

Smoke drifts from collapsed beams; the fountain runs grey through ash. Under a burka in the courtyard lies the small shape of Sado's son. The mother crouches over him, smock torn, fingernails dragging blood from her own face, her wail stripped of words. The grandfather sits against a scorched wall whittling a stick, eyes on nothing. Hadji Murad enters on foot, stops at the broken gate, looks at the boy's shape, then at SADO working a spade into hard earth. He sets his hand on the shaft; Sado lets it go. They dig in silence. My house was your house, Sado says at last, eyes down — what is left, Allah saw. Hadji Murad has no answer, and gives none.

30. INT./EXT. MAJOR PETROV'S FORT — STREET / PARLOR — DAY

BUTLER (24), newly down from the Guards, strolls the fort street when hoofbeats part the dust: Hadji Murad on a chestnut, moving in tight controlled steps, everything around him slack by comparison. His gaze passes over Butler; two fingers extend, whip hanging from them; Butler grips them. Hadji Murad names himself, asks who Butler is, and moves on. MARYA DMITRIEVNA (30) watches from a shaded doorway with the stillness of someone who has learned that the most dangerous men announce nothing. Inside, MAJOR PETROV (mid 40s) enters still chewing bread, reads the orders without sitting, eyes moving between paper and guest as if pricing livestock. Hadji Murad stands motionless, hand on dagger hilt, a contemptuous smile on the middle distance. The major offers the storeroom; Marya Dmitrievna overrides him from the kitchen doorway — guest chamber, at least then we know where he is. Petrov protests that women have no business here; a ladle rings on iron in answer. Hadji Murad states his terms quietly: lodging is beneath discussion; he needs men to carry word to the mountains. He extends his hand to Butler alone. Butler shakes it and understands, all at once, that he has just been chosen.

31. INT. SHAMIL'S COMPOUND — VEDENO — DAY

SHAMIL (mid 50s) rides into Vedeno on a white Arab, plain brown cloak, white turban, face unmoving at the center of a storm of caracoling murids firing into the winter sky. He dismounts without returning the salute; a murid presents a sealed prisoner list and Shamil takes it without a glance. Inside the saklya HADJI MURAD'S WIVES press against the lattice; PATIMAT (~70), his mother, sits with her arms locked around her knees, staring into dying embers, and does not turn. Below, in a stone pit, YUSUF (18) sets his face to a slit of winter light and hears the chanting arrive muffled and final.

32. INT. SHAMIL'S COUNCIL CHAMBER — VEDENO — DAY (THE VERDICT)

JEMAL EDDIN (30) reports that Hadji Murad's wife, mother, and son Yusuf were intercepted before they reached the Russian line — all three now held under guard in Vedeno. Shamil listens without moving his hands and says it is written: a man is known by what he reaches for when he thinks no one watches, and Hadji Murad reached for the infidel. To the council Jemal Eddin reads the proclamation — better to die in enmity with the Russians than to live with the Unbelievers. Shamil nods once; the scribe presses the seal. A councilor names Hadji Murad; Shamil's hand stills on his beard. Hadji Murad loves his son, he says — and the room understands. Yusuf is brought up from the pit, thin, reeking, black eyes burning, and set at a writing-board, a reed pen shaking over paper; the letter will travel to the Russian fort like a blade. Outside the chamber Yusuf snatches a dagger and drives it at his own throat; murids wrench his arm and force him back into the dark. Shamil stands alone in his white fur cloak, the fountain ticking under wind. He has not raised his voice.

33. INT. MAJOR PETROV'S HOUSE — FRONTIER FORT — EVENING (TRUST AT ITS PEAK)

Khanefi stands in the kitchen doorway with a copper bowl; Marya Dmitrievna points him to the water without a glance. Eldar carries Hadji Murad's tray through, smiling shyly, and the fort's rhythms fold around the Avars as if they had always been there. That evening Khanefi sings — a high grief-scored tenor about a brother who will never take revenge — and Hadji Murad stands eyes shut, arms folded, already elsewhere; Butler leans forward between his knees, listening to the only honest voice in the room. When the last note dies, Hadji Murad says it is a good song and a wise song — four words from a man who has recognized his own obituary.

34. INT./EXT. MAJOR PETROV'S HOUSE — FRONTIER FORT — MORNING (THE BOND BREAKS)

On the morning of departure the white burka comes across Eldar's arm, startling against the dark tunics. Hadji Murad limps to Marya Dmitrievna and holds it out with both hands; she has understood before the interpreter speaks; her freckled cheeks flush and she wipes her palms on her apron before taking it. The Gurda sword goes to Petrov, who fumbles, ashamed of his empty hands; Hadji Murad waves the debt off with a flat gesture touching mountains and heart. Butler asks when they shall meet again; Hadji Murad answers in a mix of Avar and Russian — strong kunak — and Butler holds the two extended fingers a beat longer than the first time. On the porch Marya Dmitrievna watches him mount and calls after him to bring them home. He turns in the saddle: good-bye, my lass — I thank you — and she hears that he expects no rescue, only a clean road out. The riders dwindle; Butler's raised hand falls. Inside, an officer mutters the man will be up to tricks, a terrible rogue. Marya Dmitrievna sets the burka on the table and says quietly that it is a pity there are not more Russian rogues of such a kind — courteous, wise, just — and the silence after is the only verdict the room deserves.

35. INT. OFFICERS' MESS / GOVERNMENT HOUSE — TIFLIS — DAY

Hadji Murad's family is not freed. The news arrives as its own absence — no courier, no dispatch, only Loris-Melikov's careful silence and the word patience used once more. They stand on pale stone steps under a blinding Tiflis sky, Loris-Melikov beside him with the practiced warmth of a man whose job is to make waiting feel like something else. Argutinski arrives next week, Loris-Melikov says — then the Prince can speak with more authority. Hadji Murad says he said next week before. There is the other matter: the Prince grants leave to go to Nukha, a town to the east, a mosque, a quieter place to wait. Hadji Murad asks about his family. Loris-Melikov looks at the mountains barely visible in the haze and does not answer quickly enough.

---

ACT THREE

---

36. INT. HADJI MURAD'S HOUSE — NUKHA — DAY

A bare whitewashed reception room near the mosque: the place where a man is kept when the empire wishes to be courteous about keeping him. Bright haze stops at the small high window, too high to see the road; the room holds shade, a single low table, a folded prayer rug, and a sentry's shadow that crosses the doorway and comes back. Hadji Murad enters in riding dress, dust on his boots, and does not sit. He sets a folded spy's report on the table between himself and COUNCILLOR KIRILLOV (~45), who has arrived with a leather satchel, a sealed dispatch, and nothing useful to offer. Kirillov rises and extends the dispatch; Hadji Murad does not take it. He raises both hands, then four fingers, holds them suspended until Kirillov looks away — a count, a measure, an accusation pressed into a gesture. Kirillov counts seven piles of ten gold coins onto the table; Hadji Murad sweeps them into his sleeve in one motion, then slaps Kirillov's bald pate with the flat of his hand — a dry crack in the quiet room — and walks out while Kirillov's hand drifts toward his sword hilt and stops, understanding nothing can be done.

37. INT. HADJI MURAD'S QUARTERS — NUKHA — DUSK TO NIGHT

Grey-blue dusk. Two SPIES enter hooded. The Tavlinian brings word that Shamil has sworn the knife to any man who moves for Hadji Murad's house; the old spy adds that Yusuf has been moved deeper — Vedeno, then beyond, the pit already dug. Two road-dusted messengers add that Shamil's watchers are on every road; even his cousins keep their doors shut; his friends will not move. Hadji Murad's hands rest motionless on his knees. He slides a gold coin across the carpet to each man and draws his palms slowly down his beard. They wait for an answer to carry back; he has none to give. The gold he was paid sits untouched in a bright heap on the floor. Hours later, only the wick changed, his hand finds the small leather thong at his throat — the silver coin Yusuf gave him, the son's token — and closes around it. He rises, lifts down a saddle blanket, folds it once, sets it beside his sword. Eldar stands without being told. Hadji Murad reads the darkness — the hour when a man on a fast horse can reach the first ravine before anyone counts the empty rooms — and tells Eldar to saddle the bay and the second horse.

38. INT. HENCHMEN'S ROOM — NUKHA — BEFORE FIRST LIGHT

Khanefi sings low against the wall — winged ones flying home — the words barely above breath. Bata murmurs the response. Gamzalo, cross-legged in the dark, listens without expression. Not prayer. Preparation.

39. EXT. RIDGE ABOVE NUKHA — FIRST GREY LIGHT

Five horses in frost-burned scrub, breath steaming, girths tight. Hadji Murad rests a hand on Eldar's shoulder, draws his palms down his beard, looks east. Hoofbeats on the ridge — Cossacks, coming fast. He swings into the saddle, dagger already drawn. Tell them Hadji Murad rode out at dawn.

40. EXT. FORT GATE / MOUNTAIN ROAD — MORNING

White Kabarda mare, five Cossack mounts flanking close. NAZAROV (28) rides at his stirrup. A mile out, Hadji Murad veers toward the ridge. Nazarov calls. A pistol clears the burka — three heartbeats, four Cossacks down in the dust, the fifth bent low over his horse's neck, riding hard for the watchtower. Powder smoke. Gamzalo: four down, one away.

41. EXT. FORKED TRACK / FLOODED RICE-FIELDS — DAY TO DEEP NIGHT

Right to the mountains, left to flooded rice-fields and the Alazan. Every instinct bends right. Hadji Murad turns left, saying they will look for him where his heart goes. The horses wade into the mirror of water and shatter the ridgeline's reflection; far behind, the watchtower trails its first thread of smoke. Deep night now — burkas spread like dark altars on the only dry ground, the horses grazing, the men eating in silence. A faint silver wash, nightingale song over slow water. Hadji Murad spreads his burka and kneels — the nightingales sing again, he says; last night he heard the song of Hamzad; bring water, he will pray. Eldar's voice, low: horses, many of them. Hadji Murad does not rise. He hears them; finish the prayer first. He bows his forehead to the ground while the hoofbeats grow.

42. EXT. SHALLOW DITCH ABOVE THE BOG — PRE-DAWN

Pre-dawn cold. Six men cut branches with daggers, throw earth onto a low bank; hooves splash on both flanks. Hadji Murad works beside them, hands in the mud, settling into the manner of his end. KARGANOV's (~40) surrender call drifts across the shrubs. Hadji Murad presses Eldar's shoulder down without a glance and counts the advance, shrub to shrub.

43. EXT. DITCH — CONTINUOUS (THE STAND)

Spring greens, black blood on grass, a dying mare thrashing at the rim. HADJI AGA (~40s) reins in twenty paces off, two hundred riders behind him, and calls across the open ground. Hadji Murad lowers his rifle: once Hadji Aga ate from his dish; today he brings two hundred guns to his ditch. The appeal — the road back open for one hour — cracks against the silence. A volley tears the shrubs. Hadji Murad lies wedged behind the bank, beshmet torn, blackened cotton wool in the wound; he takes the rifle Khanefi passes and sights without hurry. Eldar half-rises, dagger drawn, leans past the bank — a bullet takes him; he reels back onto Hadji Murad's leg; the two men hold each other's eyes once before Hadji Murad draws his leg slowly free. Bata sits hard in the dirt, throat ragged, spits red, goes still. Khan Mahoma's singing does not stop. Khanefi sets the last powder flask within reach and kneels to the wall, and the ditch goes on working — loading, firing, naming nothing aloud.

44. INT./EXT. THREE ROOMS — TIFLIS / VEDENO / THE PIT — CONTINUOUS

Tiflis: Vorontsov sets a teacup down without sound, reads a folded telegram, tests a pen nib against his thumb, dictates that the dispatch shall say Hadji Murad fell bravely, surrounded, refusing surrender — that much is true, and it costs the Empire nothing to say. Vedeno: Shamil on a low cushion, Quran across his knees; a courier kneels with a cloth bundle on the carpet; Shamil does not look up, strokes his beard once, turns a page. The pit: Yusuf presses his ear to cold stone and listens upward into the dark beside an untouched bowl, then turns his face to the wall.

45. EXT. DITCH / OPEN GROUND — DAY (THE DEATH)

Hadji Murad drags himself from behind the bank, fires his pistol once, and walks forward on the broken leg — dagger in hand, straight at the guns. Several rifles crack; he goes down, finds the trunk of a young tree, pushes up against the bark, blood at his side and shoulder and face, and speaks his son's name once into the open air before the second volley takes him. A nightingale starts in the smoke-thinned silence. Hadji Aga is first to the body. He stands over it a beat too long, dagger still sheathed, his own breath loud — the militiamen behind him waiting for the man who promised them this head to take it. A YOUNG RIDER at his shoulder — Akhmet Khan's son, the inherited feud made flesh, his father's debt riding on his face — leans in to watch the throat, and that is what moves Hadji Aga's hand: not hatred, the witness. He kneels, plants his boot on the dead man's back, and reaches down — but his face stays turned from the slack one beneath him, fixed on the trampled reeds, on the grazing horses, on anything that is not the man he once ate beside. Two clean strokes, eyes on the middle distance, and the head comes free. He rolls it away with the side of his foot, careful of his shoes, then wipes the blade twice on his own sleeve when once would do, and a third time, and stops himself. KHANEFI, KHAN MAHOMA and GAMZALO stand bound, watching, naming nothing.

46. EXT. MOONLIT YARD / INT. MAJOR'S QUARTERS — FORT — NIGHT (THE SEVERED HEAD)

KAMENEV (~40) dismounts in the moonlit yard and lifts a heavy linen sack from the saddle-bag; Butler and Marya Dmitrievna stand on the steps. He hauls out the head by the shaven skull — black beard, one eye half-open, a strange childlike calm on the ruined face. Butler's jaw locks. Marya turns her back. Butler tells him to cover it — the moonlight is indecent on a face like that. At the same dim hour, at the clerk's table inside, a corporal seals a thin packet for the post: the notice of Private Avdeev, killed in the Kurin engagement, addressed to a snow-covered village his major could not name; the corporal licks the flap, sets it on the outgoing pile, and turns up the lamp for the celebration. Inside the parlor, lamplight on a stained tablecloth, the drunk officers lurch forward as the head comes out again. Petrov sways toward it, eyes wet, presses his mouth to the dead forehead; the officers grin. A COSSACK, expressionless, slides the head back into the canvas and lays it down with strange care, as if not to bruise it. Butler stands rigid, color draining, watching empire kiss what it killed while one sealed packet waits in the dark for a horse to the north.

47. EXT. PORCH OF MAJOR'S HOUSE — FORT — NIGHT

Marya Dmitrievna sits on the cold step, shawl pulled tight over the white burka she has carried out and laid across her knees, while laughter and the recitation of Kamenev's speech leak through the door. Butler steps out and reaches for a word; she turns her face away. They are all cut-throats, she says, flat and final — a dead man's head belongs in the earth, not bumping fort to fort in a sack for officers to kiss between toasts. He looked at her like she was a person; the major in there has not done that since Easter. She smooths the burka once with the flat of her hand, the way you settle a thing that will not be settled again, then stands, descends the last step, and walks toward the dark without looking back — leaving Butler on the porch with the noise behind him and nothing ahead.

48. EXT. DITCH / ROADSIDE SLOPE — DAY (EPILOGUE)

At the edge of the ditch, bent and bloodied but not broken, a thistle holds its crown above the flattened earth. Match cut — the same roadside slope in midsummer light, the thistle upright and flowering, a cart track beyond it, mountains rising blue at the horizon, the Caucasus unmoved.

## Key Scene — Fully Realized Dialogue

*We have chosen Hadji Murad's final stand for full dialogue treatment: dawn in a reed-choked ravine, six men behind an earth wall against two hundred militia (treatment scenes 43–45), the film's climax and the warlord's death. Here the picture's central lines converge — kunak loyalty against betrayal, the hostage family as unspoken stake, the recurring thistle that survives every boot. The subtext runs densest in this scene, and rendering it as spoken dialogue demonstrates the craft the image-based treatment, written in reported speech, deliberately withholds.*

```
EXT. SHRUB-CHOKED RAVINE - DAWN

A clump of low brush on a marshy slope. A shallow ditch cut into the embankment. Mist sits in the hollows. Hobbled horses stamp among the branches. Six men crouch behind the earth wall, rifles laid across it.

HADJI MURAD, forty-seven, broad and still, a graying beard, sets his rifle on the embankment without rising.

BATA wipes mud from his lock and eyes the slope above.

BATA
Brother — bad ditch. Shallow. The wolf does not sleep where the hunter sees his ear.

He spits toward the open ground.

GAMZALO returns from the edge, one eye narrowed, and lays his rifle across the earthwork.

GAMZALO
Karganov. Militia. Both sides of the clump.

KHANEFI slides a powder pouch toward Hadji Murad's hand.

KHANEFI
Bismillah. Powder dry. Forty rounds, agha — and the dagger.

Hadji Murad cuts a branch with his dagger, lays it on the bank. He does not look up.

HADJI MURAD
Khanefi, Gamzalo, Khan Mahoma — dig deeper. A handful of earth is worth a brother today.

Out on the slope, hooves. HADJI AGA reins in twenty paces off, a tribal commander in a black cherkeska, dagger at his belt. He does not dismount. He keeps his face from the ditch.

HADJI AGA
Hadji Murad.
(the name catches; he steadies it)
The Russians offer the road back. Take it. I would rather not earn what they pay me today.

Hadji Murad lowers his rifle a finger's width. Looks across.

HADJI MURAD
Hadji Aga. Once you ate from my dish. Today you bring two hundred guns to my ditch.

HADJI AGA
(spitting into the wet grass)
We are many. You are six. By Allah, count your cartridges before you count your honor.

KHAN MAHOMA snaps his breech shut and grins sideways at Khanefi.

KHAN MAHOMA
Eh — Hadji Aga brings two hundred guests. Khanefi, load faster, brother — the wedding starts.

Hadji Murad turns his head a fraction toward the open ground, toward Karganov's line.

HADJI MURAD
Karganov. You are many. We are six. Come closer and count again.

He nods once toward the clearing edge, where a black mare strains at her hobble.

HADJI MURAD (CONT'D)
Bata — the black mare first. A horse without a rider tells the militia what waits in the ditch.

Bata tightens his belt. Does not look back.

BATA
I go first to the bank. Tell my horse — she walks home alone, she walks proud.

He climbs to the bank. A shot cracks. Bata pitches into the mud. Still.

ELDAR, young, jaw tight, half-rises from the ditch, dagger half-drawn.

ELDAR
Agha — the ridge.
(his voice drops)
It is Akhmet Khan. He rode at your stirrup once.

Hadji Murad does not turn his head. His voice is no louder than the reloading.

HADJI MURAD
Khanefi — the long gun. Load the short one after. Eldar, sit. A dagger is for the last step, not the first.

Eldar settles. Plants a knee against the earth wall.

Khan Mahoma fires, lowers the smoking rifle, spits. Then goes still, peering through the leaves. His voice flattens.

KHAN MAHOMA
The boy is here, agha. Crawling the bushes himself. He does not trust the Russians to bring you down.

Hadji Murad marks one shrub with his eyes, then the next.

HADJI MURAD
I knew the father. Good man, hard hand.
(quiet)
The son I will meet soon enough.

Out on the slope Hadji Aga half-turns to a young rider at his shoulder, still not facing the ditch. He touches the dagger hilt. Does not draw.

HADJI AGA
Swords. Through the shrubs — do not stop at the first shot.
(to the boy at his shoulder, lower)
Akhmet, the right. We close the ring, and may God forget my name in it.

Gamzalo shifts one pace nearer to Hadji Murad. Thumbs a fresh cartridge.

GAMZALO
Let them come. The shrubs do half the work.
(meeting Hadji Murad's eyes)
It is enough. Say the word.

In the bushes, a horse thrashes and bleeds. Gamzalo glances at it once.

GAMZALO (CONT'D)
My horse is down. Good. One less rein to hold.

Hadji Murad glances at the dying mare in the grass, then up at the sun edging a high branch.

HADJI MURAD
Gamzalo. The black mare bleeds in the grass. When the sun clears that branch, we go to the river.

Khanefi slaps powder into the pan, passes the long gun up. He sets the last flask in Hadji Murad's reach. Touches his sleeve, once.

KHANEFI
Your mother's milk. I came to give it back. It is done.

A volley. Smoke rolls across the ditch. Men shout in the shrubs, closer now.

Hadji Murad pauses. He works the small silver coin Yusuf gave him from his belt, presses it once, drops it into Khanefi's palm.

HADJI MURAD
If your road runs through Vedeno — this, to the boy. No words. He will read it.

He draws both palms slowly down his beard.

HADJI MURAD (CONT'D)
Allah knows. It is well.

The sun clears the branch.

Hadji Murad rises. He fires, fires again, wades up out of the ditch into the open. The shrubs erupt. Muzzle-flash from every side. Eldar goes down at the earth wall. Khanefi is dragged back, his pistol struck from his hand.

Hadji Murad reaches a single tree and sets his shoulder to the trunk. Blood at his side, his shoulder, his face. He fires until the rifle is empty, draws the dagger.

A wall of militia closes. He goes down at the foot of the tree.

Hooves. Hadji Aga dismounts, steps through the smoke. He stands over the fallen man and will not look at the face. He touches the dagger hilt.

HADJI AGA
Hadji Murad. On your face. By Allah, the thistle falls the same as the rose.

Hadji Murad's bleeding head lifts. His eyes find no horizon.

HADJI MURAD
Yusuf...

His hand searches the bark of the tree.

HADJI MURAD (CONT'D)
Mother. The song.

Hadji Aga steps over the body, eyes on his militiamen, not on the ground.

HADJI AGA
Take the others alive. Bind them — Khanefi, Khan Mahoma, Gamzalo.
(quieter, almost to himself)
The Russians pay for heads that talk. Not for honest dead.

Hadji Murad's lips move against the dirt.

HADJI MURAD
A horse. A black one.

Hadji Aga plants his boot on the corpse's back, lifts the dagger.

HADJI AGA
Move the foot. Not the shoe — the head. Clean. Clean.

Khan Mahoma jerks his chin toward the boot on the body.

KHAN MAHOMA
Look — they roll his head like a melon. Careful, dog, do not scuff your boots.

Hadji Murad's body shudders. He pushes once from the trunk.

HADJI MURAD
Hadji Murad has stood.

GAMZALO, bound, leans toward the body, jaw set, lips moving in prayer.

GAMZALO
Hadji Agha. I come. One step before. As I swore.

Hadji Aga rolls the severed head away with the side of his foot.

HADJI AGA
He ran to them first. Remember that.

Khanefi, bound beside Gamzalo, watches the tree. He sets his back to Gamzalo's.

KHANEFI
(singing, low)
The earth dried on Hamzad's grave — the avenger did not sleep.

Hadji Murad's palms try to draw down the beard. They fall.

HADJI MURAD
Allah knows.

He is still.

Somewhere above the powder-smoke, nightingales start again. Khan Mahoma stiffens, then looks away from the corpse, mouth twisting.

KHAN MAHOMA
Quiet, Khanefi. Listen. The nightingales again. Allah is not impressed.

He lifts his bound hands toward the Russian line, voice cracking once.

KHAN MAHOMA (CONT'D)
I rode beside him, you understand? Beside. Write that down somewhere, Russian.

Khanefi drops the spent pistol, lifts both wrists to the militiaman.

KHANEFI
Bind me, dog. My hands are nothing now.

The mist lifts. The nightingales sing on.

FADE OUT.
```

──────────────────────────────────

OUTPUT as valid JSON only — no markdown fences, no commentary:
{"findings": [
    {"finding_id": "F1", "type": "character_status|object|count|timeline|injury|identity",
      "severity": "critical|high|medium|low", "scenes": ["<scene numbers or KEY_SCENE>"],
      "description": "<one sentence>",
      "evidence_quotes": ["<exact quote>", "<exact quote>"],
      "origin": "candidate|judge_scan"}
  ],
  "rejected": [{"candidate_id": "<id>", "why": "<short reason>"}]}