"""Checks of the azimuth argument of model.bilayer_t (T4).

1. azimuth 0 reproduces the pre-T4 model (old file passed with --old).
2. azimuth 90 = azimuth 0 for TE and TM (C4 lattice and C4v holes, shift 0).
3. azimuth 45 (lattice diagonal, a mirror line): TE and TM decouple, |t_TE_TM|, |t_TM_TE| ~ 0.
Usage: python check_azimuth.py [--old /path/to/old_model.py] [--params '{"a":..}'] [--n_terms 60 --ngrid 64]
"""
import argparse, json, importlib.util
import numpy as np
from model import bilayer_t

ap = argparse.ArgumentParser()
ap.add_argument("--old"); ap.add_argument("--params", default='{"a":0.62,"t":0.22,"r":0.12}')
ap.add_argument("--gap", type=float, default=0.2)
ap.add_argument("--n_terms", type=int, default=60); ap.add_argument("--ngrid", type=int, default=64)
args = ap.parse_args()
p = json.loads(args.params); kw = dict(n_terms=args.n_terms, ngrid=args.ngrid)
lam = np.array([1.48, 1.50, 1.52, 1.55, 1.48, 1.50, 1.52, 1.55])
th = np.array([0.5, 0.5, 0.5, 0.5, 6.0, 6.0, 6.0, 6.0])
call = lambda f, az: f(lam, th, p["a"], p["t"], p["r"], args.gap, c4=p.get("c4", 0.0), c8=p.get("c8", 0.0),
                       r2=p.get("r2"), t2=p.get("t2"), **kw, **({} if az is None else {"azimuth_deg": az}))
o0, o90, o45 = call(bilayer_t, 0.0), call(bilayer_t, 90.0), call(bilayer_t, 45.0)
res = {}
if args.old:
    sp = importlib.util.spec_from_file_location("model_old", args.old); m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m); oo = call(m.bilayer_t, None)
    res["az0_vs_old_max_abs_dt"] = float(max(np.max(np.abs(np.asarray(o0[k]) - np.asarray(oo[k]))) for k in ("t_TE", "t_TM")))
res["az90_vs_az0_max_abs_dT"] = float(max(np.max(np.abs(np.asarray(o90[k]) - np.asarray(o0[k]))) for k in ("T_TE", "T_TM")))
res["az0_max_cross"] = float(max(np.max(np.abs(np.asarray(o0[k]))) for k in ("t_TE_TM", "t_TM_TE")))
res["az45_max_cross"] = float(max(np.max(np.abs(np.asarray(o45[k]))) for k in ("t_TE_TM", "t_TM_TE")))
res["T_TE az0/45"] = [[round(float(a), 4), round(float(b), 4)] for a, b in zip(o0["T_TE"], o45["T_TE"])]
res["T_TM az0/45"] = [[round(float(a), 4), round(float(b), 4)] for a, b in zip(o0["T_TM"], o45["T_TM"])]
print(json.dumps(dict(settings=dict(p, gap=args.gap, **kw), lam=lam.tolist(), theta=th.tolist(), **res), indent=1))
