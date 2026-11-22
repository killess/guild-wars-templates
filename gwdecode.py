import re, sys, os, json

B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
PROF = ["None","Warrior","Ranger","Monk","Necromancer","Mesmer","Elementalist",
        "Assassin","Ritualist","Paragon","Dervish"]
PABBR = ["X","W","R","Mo","N","Me","E","A","Rt","P","D"]
ATTR = {0:"Fast Casting",1:"Illusion Magic",2:"Domination Magic",3:"Inspiration Magic",
 4:"Blood Magic",5:"Death Magic",6:"Soul Reaping",7:"Curses",8:"Air Magic",9:"Earth Magic",
 10:"Fire Magic",11:"Water Magic",12:"Energy Storage",13:"Healing Prayers",14:"Smiting Prayers",
 15:"Protection Prayers",16:"Divine Favor",17:"Strength",18:"Axe Mastery",19:"Hammer Mastery",
 20:"Swordsmanship",21:"Tactics",22:"Beast Mastery",23:"Expertise",24:"Wilderness Survival",
 25:"Marksmanship",29:"Dagger Mastery",30:"Deadly Arts",31:"Shadow Arts",32:"Communing",
 33:"Restoration Magic",34:"Channeling Magic",35:"Critical Strikes",36:"Spawning Power",
 37:"Spear Mastery",38:"Command",39:"Motivation",40:"Leadership",41:"Scythe Mastery",
 42:"Wind Prayers",43:"Earth Prayers",44:"Mysticism"}

def load_skills(path):
    names, cur = {}, -1
    body = open(path, encoding="utf-8").read()
    body = body[body.index("enum class SkillID"):]
    body = body[body.index("{")+1: body.index("};")]
    body = re.sub(r"//.*", "", body)
    for tok in body.split(","):
        tok = tok.strip()
        if not tok: continue
        m = re.match(r"(\w+)\s*(?:=\s*(\w+))?", tok)
        if not m: continue
        cur = int(m.group(2), 0) if m.group(2) else cur + 1
        names.setdefault(cur, m.group(1).replace("_", " "))
    return names

class Bits:
    def __init__(self, s):
        self.b = []
        for c in s:
            v = B64.index(c)
            self.b += [(v >> i) & 1 for i in range(6)]
        self.p = 0
    def read(self, n):
        if self.p + n > len(self.b): raise ValueError("truncated")
        v = sum(self.b[self.p+i] << i for i in range(n)); self.p += n; return v

def decode(code):
    code = code.strip().rstrip("=")
    bs = Bits(code)
    t = bs.read(4)
    if t == 14: bs.read(4)           # version
    elif t == 15: return {"type":"equipment"}
    elif t != 0: raise ValueError("unknown header %d" % t)
    pl = bs.read(2)*2 + 4
    p1, p2 = bs.read(pl), bs.read(pl)
    na, al = bs.read(4), bs.read(4) + 4
    attrs = [(bs.read(al), bs.read(4)) for _ in range(na)]
    sl = bs.read(4) + 8
    skills = [bs.read(sl) for _ in range(8)]
    return {"type":"skills","p1":p1,"p2":p2,"attrs":attrs,"skills":skills}

def main(root, skillfile, out):
    names = load_skills(skillfile)
    rows, bad = [], []
    for dp, _, fs in os.walk(root):
        for f in sorted(fs):
            if not f.lower().endswith(".txt"): continue
            full = os.path.join(dp, f); rel = os.path.relpath(full, root)
            raw = open(full, encoding="utf-8", errors="replace").read().strip()
            code = raw.split()[0] if raw else ""
            try:
                d = decode(code)
            except Exception as e:
                bad.append((rel, code, str(e))); continue
            if d["type"] != "skills":
                rows.append({"file":rel,"code":code,"type":d["type"]}); continue
            rows.append({"file":rel,"code":code,"type":"skills",
                "primary":PROF[d["p1"]] if d["p1"]<len(PROF) else d["p1"],
                "secondary":PROF[d["p2"]] if d["p2"]<len(PROF) else d["p2"],
                "prof":f'{PABBR[d["p1"]]}/{PABBR[d["p2"]]}' if max(d["p1"],d["p2"])<len(PABBR) else "?",
                "attributes":[[ATTR.get(a, f"Attr{a}"), v] for a, v in d["attrs"]],
                "skills":[names.get(s, f"#{s}") if s else "(empty)" for s in d["skills"]],
                "skill_ids":d["skills"]})
    json.dump({"rows":rows,"bad":bad}, open(out,"w",encoding="utf-8"), indent=1)
    print(len(rows), "decoded,", len(bad), "failed")
    for b in bad[:20]: print("FAIL", b)

if __name__ == "__main__":
    # Usage: python gwdecode.py [templates_dir] [Skills.h] [output.json]
    # Defaults: Templates, Skills.h and decoded.json next to this script.
    here = os.path.dirname(os.path.abspath(__file__))
    defaults = [os.path.join(here, "Templates"),
                os.path.join(here, "Skills.h"),
                os.path.join(here, "decoded.json")]
    args = sys.argv[1:4] + defaults[len(sys.argv[1:4]):]
    main(*args)
