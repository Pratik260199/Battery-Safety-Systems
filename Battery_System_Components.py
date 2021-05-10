import pandas as pd

sheet_id = '1izazCry301klvetVCTs9cxpSZgSI671jXkG3dRcfnoI'

df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")
# df=pd.DataFrame(data)
print(df)
