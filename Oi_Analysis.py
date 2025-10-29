from nsepython import nse_optionchain_scrapper
import pandas as pd

SPOT_PRICE = 22500  
MIN_STRIKE = SPOT_PRICE - 500
MAX_STRIKE = SPOT_PRICE + 500

try:
    print("NIFTY Option Chain data from NSE:")
    data = nse_optionchain_scrapper("NIFTY")
except Exception as e:
    print("Error in fetching option chain data.", e)
    exit(1)

records = data["records"]["data"]

rows = []
for rec in records:
    strike = rec.get("strikePrice")
    if strike and MIN_STRIKE <= strike <= MAX_STRIKE:
        call_oi = rec.get("CE", {}).get("openInterest", 0)
        put_oi = rec.get("PE", {}).get("openInterest", 0)
        rows.append([strike, call_oi, put_oi])

df = pd.DataFrame(rows, columns=["Strike Price", "Call OI", "Put OI"])
df.sort_values("Strike Price", inplace=True)
df["Total OI"] = df["Call OI"] + df["Put OI"]

max_pain = df.loc[df["Total OI"].idxmax()]
print("\nNIFTY Option Chain OI (±500 pts)")
print(df.to_string(index=False))

print("\n MAX PAIN RESULT")
print(f"Strike Price  : {int(max_pain['Strike Price'])}")
print(f"Total OI     : {int(max_pain['Total OI'])}")
print("Analysis complete.")
