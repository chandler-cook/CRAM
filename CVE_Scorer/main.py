import resiliency_score
import os

CVE_FILE = 'testCVE'
JSON_FILE = 'all_cves.json'



def main():    
    resiliency_score.check_and_remove_previous_files('sw_cves.json', 'hw_cves.json')
    #resiliency_score.run_cve_scan(CVE_FILE, JSON_FILE)    
    resiliency_score.all_json_to_sw_hw_json(JSON_FILE, 'test.csv')
    #if os.path.exists(JSON_FILE):
     #   os.remove(JSON_FILE)
if __name__ == '__main__':
    main()
    