import resiliency_score

CVE_FILE = 'testCVE'
JSON_FILE = 'all_cves.json'



def main():    
    resiliency_score.check_and_remove_previous_files('sw_cves.json', 'hw_cves.json')
    #resiliency_score.run_cve_scan(CVE_FILE, JSON_FILE)    
    resiliency_score.all_json_to_sw_hw_json(JSON_FILE)
    #if os.path.exists(json_file):
    #    os.remove(json_file)
if __name__ == '__main__':
    main()
    