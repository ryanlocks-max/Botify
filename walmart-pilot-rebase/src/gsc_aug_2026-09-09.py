import json, pandas as pd, numpy as np
# GSC US/WEB by bucket, pulled 9 Sep 2026 via Botify MCP (walmart0/walmart-sw-demo, search_console_by_property_flat)
# date: [anon clicks, anon impr, brand clicks, brand impr, nonbrand clicks, nonbrand impr]
R = {
"2026-08-09":[1087678,82273443,506201,3930744,106355,7156263],
"2026-08-10":[1079103,81418061,528606,3600325,97431,6674036],
"2026-08-11":[1058556,80228202,512976,3477231,98038,6749449],
"2026-08-12":[1005310,80191899,490434,3622669,93909,7901965],
"2026-08-13":[1020026,80802420,513934,3707009,91988,8157382],
"2026-08-14":[972322,79656064,513955,3675894,90353,7303038],
"2026-08-15":[1005485,81702902,508800,3684634,97823,7845392],
"2026-08-16":[1041164,83595920,503254,3672731,100583,7977817],
"2026-08-17":[1037884,81012853,520512,3609056,90525,7785502],
"2026-08-18":[1036031,81815019,506616,3558138,87630,7277780],
"2026-08-19":[1050184,83378218,509541,3543523,87643,7289600],
"2026-08-20":[1043605,81781115,514565,3610525,85730,7307686],
"2026-08-21":[1042095,79345216,524210,3719948,86517,6668877],
"2026-08-22":[1098753,76093824,517050,3684826,98136,7439251],
"2026-08-23":[1132075,77372755,508876,3553208,103645,7541998],
"2026-08-24":[1088233,81172168,518637,3452589,94686,6968560],
"2026-08-25":[1044650,85118718,491297,3307237,95174,6624199],
"2026-08-26":[1085122,84360384,489577,3349807,98081,6861509],
"2026-08-27":[1062305,85342153,497822,3530128,94436,7166345],
"2026-08-28":[1057542,85154838,513509,3620662,96492,8048894],
"2026-08-29":[1111131,87974523,501469,3623488,106789,7838682],
"2026-08-30":[1156517,90975319,506568,3671781,112482,8446011],
"2026-08-31":[1171964,89829177,602467,3676657,99776,8005778],
"2026-09-01":[1029743,85374871,552000,3659324,91510,7921470],
"2026-09-02":[1021326,83308751,554777,3578604,87675,7018062],
"2026-09-03":[996533,86592167,490112,3276579,86061,7161399],
"2026-09-04":[1053402,88075308,551552,3848474,88867,8509211],
"2026-09-05":[1090146,91304208,500052,3785798,96542,8974316],
"2026-09-06":[1083581,93380035,495151,3736198,97973,8712849],
}
P=json.load(open("src/payload.json")); g=P["gsc"]
start=pd.Timestamp(g["start"]); n=len(g["anon"]); last=start+pd.Timedelta(days=n-1)
assert str(last.date())=="2026-08-09", last
a=R["2026-08-09"]; assert (g["anon"][-1],g["brand"][-1],g["nonbrand"][-1])==(a[0],a[2],a[4]), "archive parity on 9 Aug failed"
d=last
while True:
    d=d+pd.Timedelta(days=1); k=str(d.date())
    if k not in R: break
    r=R[k]; g["anon"].append(r[0]); g["imprAnon"].append(r[1]); g["brand"].append(r[2]); g["imprBrand"].append(r[3]); g["nonbrand"].append(r[4]); g["imprNonbrand"].append(r[5])
P["meta"]["gscRange"][1]=str((d-pd.Timedelta(days=1)).date()); P["meta"]["gscPulled"]="2026-09-09 via Botify MCP (walmart0 / walmart-sw-demo)"
P["walmartBaseline"]={"2026-09":148100000,"2026-10":161200000,"2026-11":175100000,"2026-12":208800000,"source":"Walmart draft baseline clause, received 9 Sep 2026","method":"year-over-year run-rate methodology applied to Walmart's current performance"}
json.dump(P,open("src/payload.json","w"),separators=(',',':'))
print("gsc now ends", P["meta"]["gscRange"][1], "len", len(g["anon"]))
# analysis: GSC Aug 2026 YoY and Sep 1-6 YoY (364-aligned), Walmart same
idx=pd.date_range(start, periods=len(g["anon"]))
gs=pd.Series(np.array(g["anon"])+np.array(g["brand"])+np.array(g["nonbrand"]), index=idx)
nb=pd.Series(g["nonbrand"], index=idx)
def yoy(s,a,b):
    a=pd.Timestamp(a); b=pd.Timestamp(b); r=s[a:b].sum(); p=s[a-pd.Timedelta(days=364):b-pd.Timedelta(days=364)].sum(); return r,p,r/p-1
for lbl,(a,b) in {"Aug 2026":("2026-08-01","2026-08-31"),"Sep 1-6 2026":("2026-09-01","2026-09-06"),"Jul 2026":("2026-07-01","2026-07-31"),"trailing 91d to Aug 31":("2026-06-02","2026-08-31")}.items():
    r,p,c=yoy(gs,a,b); r2,p2,c2=yoy(nb,a,b); print(f"GSC {lbl}: all {r/1e6:.1f}M vs {p/1e6:.1f}M -> {c:+.1%} | nonbrand {r2/1e6:.2f}M vs {p2/1e6:.2f}M -> {c2:+.1%}")
U="/root/.claude/uploads/0bd646d7-f5d6-502b-bb57-38109b20ed9a/"
seo=pd.read_excel(U+"a463391e-DMP_SEO_9thJul24.xlsx", sheet_name="SEO_Daily", header=1); seo.columns=['date','gmv','orders','visits']; seo['date']=pd.to_datetime(seo['date']); v=seo.dropna(subset=['date']).set_index('date').visits.astype(float); v[v==0]=np.nan; v=v.interpolate()
for lbl,(a,b) in {"Aug 2026":("2026-08-01","2026-08-31"),"Sep 1-6 2026":("2026-09-01","2026-09-06")}.items():
    r,p,c=yoy(v,a,b); print(f"Walmart {lbl}: {r/1e6:.1f}M vs {p/1e6:.1f}M -> {c:+.1%}")
# ratio Aug 2026
print("Aug 2026 visits per GSC click:", round(v['2026-08-01':'2026-08-31'].sum()/gs['2026-08-01':'2026-08-31'].sum(),2), " Sep 1-6:", round(v['2026-09-01':'2026-09-06'].sum()/gs['2026-09-01':'2026-09-06'].sum(),2))
