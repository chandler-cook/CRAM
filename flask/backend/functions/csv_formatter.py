import os
import pandas as pd
import shutil

def csv(filename, output):
    df = pd.read_csv(filename)
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
    df.to_csv(output, index=False)

def checkName(path, filename):
    filepath = ""
    if "systemOne" in filename:
        filepath = os.path.join(path, 'System1Crit.csv')
    if "systemTwo" in filename:
        filepath = os.path.join(path, 'System2Crit.csv')
    return filepath

def changeCrit(sys1CritPath, sysCopyPath):
    shutil.copy(sys1CritPath, sysCopyPath)
    df = pd.read_csv(sysCopyPath)
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
    for i, value in enumerate(names):
        if names[i] == "Virtualization Manager Server":
            F5s[i] = 'X'
            F6s[i] = 'X'
        else:
            F5s[i] = ''
            F6s[i] = ''
    data_dict = {
        "Endpoint": names,
        "F1": F1s,
        "F2": F2s,
        "F3": F3s,
        "F4": F4s,
        "F5": F5s,
        "F6": F6s,
        "F7": F7s,
        "F8": F8s,
        "F9": F9s,
        "F10": F10s,
        "F11": F11s,
        "F12": F12s,
        "F13": F13s,
        "F14": F14s,
        "F15": F15s,
        "CVEs": CVEs
    }
    df = pd.DataFrame(data_dict)
    df.to_csv(sysCopyPath, index=False)