import os
import pandas as pd

df = pd.read_csv("C:\\Users\\johno\\Desktop\\CRAM\\System2Crit.csv")
namesFinal = []
Criticality = []
CVEFinal = []
names = df["Endpoint"].tolist()
F1s = df["F1"].tolist()
F2s = df["F2"].tolist()
F3s = df["F3"].tolist()
F4s = df["F4"].tolist()
F5s = df["F5"].tolist()
F6s = df["F6"].tolist()
F7s = df["F7"].tolist()
F8s = df["F8"].tolist()
F9s = df["F9"].tolist()
F10s = df["F10"].tolist()
F11s = df["F11"].tolist()
F12s = df["F12"].tolist()
F13s = df["F13"].tolist()
F14s = df["F14"].tolist()
F15s = df["F15"].tolist()
CVEs = df["CVEs"].tolist()
namesFinal = names.copy()
CVEFinal = CVEs.copy()
for i, value in enumerate(names):
    if 'X' in str(F1s[i]) or 'X' in str(F2s[i]) or 'X' in str(F3s[i]) or 'X' in str(F4s[i]) or 'X' in str(F5s[i]) or 'X' in str(F6s[i]):
        Criticality.append('Critical')
    elif 'X' in str(F7s[i]) or 'X' in str(F8s[i]) or 'X' in str(F9s[i]) or 'X' in str(F10s[i]):
        Criticality.append('Medium')
    else:
        Criticality.append('Low')
dict = {"Endpoint": namesFinal, "Criticality": Criticality, "CVEs": CVEFinal}
df = pd.DataFrame(dict)
df.to_csv("C:\\Users\\johno\\Desktop\\CRAM\\Images\\System2CritFinal.csv", index=False)