def checkName(filename):
    filepath = ""
    if "systemOne" in filename:
        filepath = "path to Sys1Crit.csv"
    if "systemTwo" in filename:
        filepath = "path to Sys2Crit.csv"
    return filepath