"""T18b: number tables from wedge_average.json (written by wedge_postprocess.py). Usage: python wedge_tables.py runs/<..>_T18b_wedge_average"""
import json, csv, sys, numpy as np
run = sys.argv[1]; d = json.load(open(f"{run}/wedge_average.json"))
f_ = lambda x: "" if x is None else f"{x:.1f}"
with open(f"{run}/table_a.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["structure", "g0_nm", "pol", "lam0_nm", "Q0", "Gamma0_nm", "dlam_dg_nm_per_nm", "D_um",
                                   "alpha_10pct_numeric_urad", "alpha_10pct_analytic_urad", "alpha_2x_numeric_urad", "alpha_2x_analytic_urad",
                                   "fwhm_ratio_at_200urad", "peak_ratio_at_200urad"])
    for k, v in d["a"].items():
        s, g0, pol = k.split("|")
        for D in ("50", "100", "200"):
            th = v["thresholds"][D]; r200 = [r for r in v["rows"] if r["D_um"] == int(D) and r["alpha_urad"] == 200][0]
            w.writerow([s, g0, pol, f"{v['lam0_nm']:.3f}", f"{v['Q0']:.0f}", f"{v['Gamma0_nm']:.4f}", f"{v['dlam_dg']:.4f}", D,
                        f_(th["10pct_numeric_urad"]), f_(th["10pct_analytic_urad"]), f_(th["100pct_numeric_urad"]), f_(th["100pct_analytic_urad"]),
                        f"{r200['fwhm_nm'] / v['Gamma0_nm']:.3f}", f"{r200['peak']:.3f}"])
with open(f"{run}/table_bc.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["part", "D_um", "alpha_or_dither_urad", "centre_urad", "expected_urad", "S_zero_deg", "S_slope_per_deg",
                                   "S_slope_first_order_per_deg", "S_max_abs", "theta_at_S_max_deg", "S_sign_change_deg", "max_dev_from_first_order"])
    for k, v in d["b"]["curves"].items():
        D, al = k[1:].split("_a"); w.writerow(["b", D, al, f"{v['centre_urad']:.3f}", f"{v['expected_urad']:.1f}"] + [""] * 7)
    for k, v in d["c"].items():
        D, ad = k[1:].split("_ad"); t = np.array(v["theta_deg"]); S = np.array(v["S"])
        kk = np.where((np.sign(S[:-1]) != np.sign(S[1:])) & (t[:-1] > 1))[0]
        ring = float(np.interp(0, [S[kk[0] + 1], S[kk[0]]], [t[kk[0] + 1], t[kk[0]]])) if len(kk) else float("nan")
        w.writerow(["c", D, ad, "", "", f"{v['zero_deg']:.1e}", f"{v['slope_per_deg']:.4e}", f"{v['slope_first_order_per_deg']:.4e}",
                    f"{v['S_max']:.4e}", f"{v['theta_at_S_max']:.2f}", f"{ring:.3f}", f"{v['max_dev_from_first_order']:.2e}"])
print("tables written")
