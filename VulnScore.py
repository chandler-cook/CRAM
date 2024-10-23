import json
def newSoftScore(jsonFile, cveID, scoreS):
    with open(jsonFile, 'r') as file:
        data = json.load(file)
    for item in data:
        if 'cve_id' in item and item['cve_id'] == 'CVE':
            scoreS = scoreS + (int(item['cvss_base_score'])/3)
    return scoreS