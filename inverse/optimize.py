"""Response-based inverse design of a tunable, polarization-independent flat band (aligned Si bilayer).

Why response-based: following Steven Johnson's advice (see docs/HANDOFF.md), we do not track eigenvalues.
A band is flat at wavelength lam_k if the transmission dip sits at lam_k for every angle and both polarizations.
So for each mechanical state k (gap g_k, shift s_k) we ask
    T(lam_k, theta, pol) -> 0          for theta in thetas, pol in {TE, TM}   (flat, both polarizations)
    T(lam_k +- dl, theta, pol) -> high                                         (narrow: linewidth < 2 dl)
and the tuning constraint  (max lam_k - min lam_k) / mean lam_k >= tune_min.
lam_k are optimization variables. The optimizer is L-BFGS-B (deterministic problem: not Adam).

Usage:  python optimize.py --config configs/stage1.json --out ../runs/<name>
"""
import argparse, json, os, time, csv
import numpy as np, jax, jax.numpy as jnp
from scipy.optimize import minimize
from model import bilayer_t

ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--maxiter", type=int, default=None)
args = ap.parse_args()
cfg = json.load(open(args.config))
os.makedirs(args.out, exist_ok=True)
json.dump(cfg, open(os.path.join(args.out, "config.json"), "w"), indent=1)

names = cfg["design_vars"]            # e.g. ["a","t","r","c4","c8"]
fixed = cfg.get("fixed", {})
states = cfg["states"]                # list of {"gap":..,"shift":..}
K = len(states)
th = jnp.asarray(cfg["thetas_deg"])
dl_frac = cfg.get("half_window_frac", 0.002)     # dl = lam * dl_frac (narrowness probe)
w_side = cfg.get("w_side", 1.0)
tune_min = cfg.get("tune_min", 0.02)
kw = dict(n_terms=cfg.get("n_terms", 120), ngrid=cfg.get("ngrid", 128), n_slab=cfg.get("n_slab", 3.48))

init = dict(cfg["init"]); init_lams = list(cfg["init_lams"])
if cfg.get("init_from"):  # continue from an earlier run's best.json (path relative to this file's folder)
    prev = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), cfg["init_from"])))
    init.update({n: prev[n] for n in names if n in prev})
    init_lams = [prev.get(f"lam{k}", init_lams[k]) for k in range(len(init_lams))]
x0 = np.array([init[n] for n in names] + init_lams)
lb = np.array([cfg["bounds"][n][0] for n in names] + [cfg["lam_bounds"][0]] * K)
ub = np.array([cfg["bounds"][n][1] for n in names] + [cfg["lam_bounds"][1]] * K)
# Trust region around the start (keeps L-BFGS-B from jumping to box corners on its first step):
#   bound_window_frac: each design variable within +- frac * |init| (absolute floor bound_window_abs, um)
#   lam_window_frac:   each lam_k within +- frac * init lam_k
#   trust_center "init": centre the windows on cfg["init"]/cfg["init_lams"] instead of the start point
#   (used when resuming a stopped run with init_from, so the trust region stays the same as the original run)
xc = np.array([cfg["init"][n] for n in names] + list(cfg["init_lams"])) if cfg.get("trust_center") == "init" else x0
if cfg.get("bound_window_frac"):
    f = cfg["bound_window_frac"]; fa = cfg.get("bound_window_abs", 0.01)
    for i in range(len(names)):
        w = max(f * abs(xc[i]), fa)
        lb[i] = max(lb[i], xc[i] - w); ub[i] = min(ub[i], xc[i] + w)
if cfg.get("lam_window_frac"):
    f = cfg["lam_window_frac"]
    for k in range(K):
        j = len(names) + k
        lb[j] = max(lb[j], xc[j] * (1 - f)); ub[j] = min(ub[j], xc[j] * (1 + f))
x0 = np.clip(x0, lb, ub)
scale = ub - lb

def unpack(z):
    p = dict(fixed)
    for i, n in enumerate(names):
        p[n] = z[i]
    return p, z[len(names):]

def loss_contrast(z):
    """objective = "contrast" (controller, 2026-11-20): require a NARROW dip at lam_k for every angle and both
    polarizations.  contrast = min(T(lam(1-d)), T(lam(1+d))) - T(lam);  penalty relu(c0 - contrast).
    A broad stop band (T low on both sides) and a one-sided Fano peak both score badly; a narrow resonance that
    stays at lam_k up to the largest angle scores well. With d = 0.2 % and thetas up to 10 deg this asks for |M| >~ 10."""
    p, lams = unpack(z)
    d = cfg["half_window_frac"]; c0 = cfg.get("contrast_target", 0.5)
    L_dip, L_con = 0.0, 0.0
    for k, st in enumerate(states):
        lam = lams[k]
        lam_pts = jnp.concatenate([jnp.full(th.shape, lam), jnp.full(th.shape, lam * (1 - d)),
                                   jnp.full(th.shape, lam * (1 + d))])
        th_pts = jnp.concatenate([th, th, th])
        o = bilayer_t(lam_pts, th_pts, p["a"], p["t"], p["r"], st["gap"], shift=st.get("shift", 0.0),
                      c4=p.get("c4", 0.0), c8=p.get("c8", 0.0), r2=p.get("r2"), **kw)
        n = th.shape[0]
        for pol in ("T_TE", "T_TM"):
            T = o[pol]
            dip = T[:n]; side = jnp.minimum(T[n:2 * n], T[2 * n:])
            L_dip = L_dip + jnp.mean(dip)
            L_con = L_con + jnp.mean(jax.nn.relu(c0 - (side - dip)))
    tune = (jnp.max(lams) - jnp.min(lams)) / jnp.mean(lams)
    L_tune = jax.nn.relu(tune_min - tune) / tune_min
    L = cfg.get("w_dip", 1.0) * L_dip / (2 * K) + cfg.get("w_contrast", 1.0) * L_con / (2 * K) \
        + cfg.get("w_tune", 1.0) * L_tune
    return L, (L_dip / (2 * K), L_con / (2 * K), tune)

def loss_sharp(z):
    """objective = "sharp" (controller = PI chat, 2026-11-20 21:00). Ask for a narrow resonance AT lam_k, for every
    angle and both polarizations, through the spectral sharpness of the complex transmission:
        S = lam * |dt/dlam|  (central difference, step fd_frac * lam, well below the target linewidth)
    For a pole t ~ A*g/(lam - lam0 + i g) next to lam_k, S peaks at lam_k = lam0 with S ~ 2 A Q and falls as a
    Lorentzian tail away from it, so log S keeps a gradient towards the nearest resonance even on a featureless
    background (the plateau that stopped T6a/T6b). Penalty relu(log S_t - log S) per angle and polarization: it is
    zero only when a resonance with S >= S_t sits at lam_k at every angle (flat) for TE and TM (degenerate).
    Broad stop bands (small S), resonances that move with angle (S high at one angle only) and featureless spectra
    all score badly."""
    p, lams = unpack(z)
    e = cfg.get("fd_frac", 3e-5); logSt = jnp.log(cfg.get("sharp_target", 1000.0))
    L_sh, L_dip = 0.0, 0.0
    for k, st in enumerate(states):
        lam = lams[k]
        lam_pts = jnp.concatenate([jnp.full(th.shape, lam * (1 - e)), jnp.full(th.shape, lam * (1 + e)),
                                   jnp.full(th.shape, lam)])
        th_pts = jnp.concatenate([th, th, th])
        o = bilayer_t(lam_pts, th_pts, p["a"], p["t"], p["r"], st["gap"], shift=st.get("shift", 0.0),
                      c4=p.get("c4", 0.0), c8=p.get("c8", 0.0), r2=p.get("r2"), **kw)
        n = th.shape[0]
        for pol in ("TE", "TM"):
            t = o["t_" + pol]
            S = jnp.abs(t[n:2 * n] - t[:n]) / (2 * e)
            L_sh = L_sh + jnp.mean(jax.nn.relu(logSt - jnp.log(S + 1e-6)))
            L_dip = L_dip + jnp.mean(o["T_" + pol][2 * n:])
    tune = (jnp.max(lams) - jnp.min(lams)) / jnp.mean(lams)
    L_tune = jax.nn.relu(tune_min - tune) / tune_min
    L = cfg.get("w_sharp", 1.0) * L_sh / (2 * K) + cfg.get("w_dip", 0.0) * L_dip / (2 * K) \
        + cfg.get("w_tune", 1.0) * L_tune
    return L, (L_dip / (2 * K), L_sh / (2 * K), tune)

def loss_fn(z):
    if cfg.get("objective") == "sharp":
        return loss_sharp(z)
    if cfg.get("objective") == "contrast":
        return loss_contrast(z)
    p, lams = unpack(z)
    L_dip, L_side = 0.0, 0.0
    for k, st in enumerate(states):
        lam = lams[k]
        lam_pts = jnp.concatenate([jnp.full(th.shape, lam), jnp.full(th.shape, lam * (1 - dl_frac)),
                                   jnp.full(th.shape, lam * (1 + dl_frac))])
        th_pts = jnp.concatenate([th, th, th])
        o = bilayer_t(lam_pts, th_pts, p["a"], p["t"], p["r"], st["gap"], shift=st.get("shift", 0.0),
                      c4=p.get("c4", 0.0), c8=p.get("c8", 0.0), r2=p.get("r2"), **kw)
        n = th.shape[0]
        for pol in ("T_TE", "T_TM"):
            T = o[pol]
            L_dip = L_dip + jnp.mean(T[:n])
            L_side = L_side + jnp.mean(1.0 - T[n:])
    tune = (jnp.max(lams) - jnp.min(lams)) / jnp.mean(lams)
    L_tune = jax.nn.relu(tune_min - tune) / tune_min
    L = L_dip / (2 * K) + w_side * L_side / (2 * K) + cfg.get("w_tune", 1.0) * L_tune
    return L, (L_dip / (2 * K), L_side / (2 * K), tune)

vg = jax.value_and_grad(loss_fn, has_aux=True)
hist = []
t0 = time.time()
def f(u):
    z = jnp.asarray(lb + u * scale)
    (L, aux), g = vg(z)
    g = np.asarray(g) * scale
    rec = dict(it=len(hist), loss=float(L), dip=float(aux[0]), side=float(aux[1]),  # contrast deficit ("contrast") or log-sharpness deficit ("sharp")
                tune=float(aux[2]),
               wall_s=round(time.time() - t0, 1), **{n: float(z[i]) for i, n in enumerate(names)},
               **{f"lam{k}": float(z[len(names) + k]) for k in range(K)})
    hist.append(rec); print(json.dumps(rec), flush=True)
    with open(os.path.join(args.out, "history.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rec)); w.writeheader(); w.writerows(hist)
    best = min(hist, key=lambda r: r["loss"])
    json.dump(best, open(os.path.join(args.out, "best.json"), "w"), indent=1)
    return float(L), g

u0 = (x0 - lb) / scale
res = minimize(f, u0, jac=True, method="L-BFGS-B", bounds=[(0, 1)] * len(u0),
               options=dict(maxiter=args.maxiter or cfg.get("maxiter", 60)))
json.dump(dict(message=str(res.message), nit=int(res.nit), wall_s=round(time.time() - t0, 1)),
          open(os.path.join(args.out, "done.json"), "w"), indent=1)
print("done", res.message)
