#!/usr/bin/env python3
"""verify.py -- CI gate. Ujrafuttatja a rust referenciat a kanonikus korpuszon, es exit 0 IFF minden
eset egyezik ES a korpusz nem degeneralt. A kimenet a publish-kapu (compute-oracle) szerzodese: utolso
sor "ZOLD". Nincs recall/FP: konformancia-korpuszon az hamis metrika volna.
FUGGOSEG: rust futtato a PATH-on (a bundle kodja nem python). Ha nincs, a gate NEM-MERT-tel bukik --
az nem "eltores", hanem "nem tudtam megnezni", es a kimenet kimondja."""
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
BASE = os.path.dirname(os.path.abspath(__file__))
RUNNER = ['rustc']


def main():
    if not shutil.which(RUNNER[0]):
        print("NEM-MERT: nincs %s futtato a PATH-on -- ez nem eltores, hanem nem tudtam megnezni" % RUNNER[0])
        return 2
    probes = [json.loads(l) for l in open(os.path.join(BASE, "probes", "probes.jsonl"), encoding="utf-8")
              if l.strip()]
    if len({json.dumps(p["expect"], sort_keys=True) for p in probes}) < 2:
        print("DEGENERALT korpusz -- PIROS")
        return 1
    src = open(os.path.join(BASE, "oracle", "probe.rs"), encoding="utf-8").read()
    inputs = [p["input"] for p in probes]
    cwd = os.path.join(BASE, "oracle")
    if RUNNER[0] == "rustc":
        # RUST: fordit ES futtat. A `rustc probe.rs` CSAK forditana -> a verify IndexError-rel bukott
        # (nem volt kimeneti sor). Ket lepes, es a fordito hibaja is nevesitve jelenik meg.
        c = subprocess.run(["rustc", "-O", "-o", "probe_bin", "probe.rs"], capture_output=True,
                           text=True, timeout=180, cwd=cwd)
        if c.returncode != 0:
            print("forditas-hiba: %s" % (c.stderr or "")[-160:])
            return 1
        r = subprocess.run([os.path.join(cwd, "probe_bin")], capture_output=True, text=True,
                           timeout=60, cwd=cwd)
    else:
        r = subprocess.run(RUNNER + ["probe.rs"], input=None, capture_output=True, text=True,
                           timeout=60, cwd=cwd)
    if r.returncode != 0:
        print("futas-hiba: %s" % (r.stderr or "")[-120:])
        return 1
    lines = [l for l in r.stdout.strip().splitlines() if l.strip().startswith("{")]
    if not lines:
        print("nincs JSON-sor a kimenetben (rc=%s): %s" % (r.returncode, (r.stdout or "")[:120]))
        return 1
    out = json.loads(lines[-1])["out"]
    agree = disagree = 0
    for p, o in zip(probes, out):
        # KET ALAK: a js/php/ruby probe {"ok":..,"v":..}-t ad, a rust NYERS erteket (a std-ben nincs
        # JSON -> kezi szerializalas, es a wrapper-mezok escape-elese tul torekeny volt). Mindketto jo.
        _v = o.get("v") if isinstance(o, dict) else o
        _ok = o.get("ok", True) if isinstance(o, dict) else True
        if _ok and _v == p["expect"]:
            agree += 1
        else:
            disagree += 1
            print("  ELTERES input=%r" % (p["input"],))
    print("matching-brackets conformance oracle (rust): probes=%d | agree=%d | disagree=%d"
          % (len(probes), agree, disagree))
    if disagree:
        return 1
    print("ZOLD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
