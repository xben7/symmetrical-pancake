#!/usr/bin/env python

#########################################################
### Script name:
### Author: Jesús Pérez
### Department: WAF SOC
### Version:
########################################################

import requests
import argparse
import getpass
import sys
import warnings
import datetime
import time
import json

#Credentials

#-------------------IMPERVA API--------------------------

print ("Enter API ID and Key: ")
if sys.stdin.isatty():
   IMPERVA_API_ID = input("Username: ")
   IMPERVA_API_KEY = getpass.getpass("Password: ")
else:
   IMPERVA_API_ID = sys.stdin.readline().rstrip()
   IMPERVA_API_KEY = sys.stdin.readline().rstrip()

IMPERVA_headers = {
    "x-API-key": IMPERVA_API_KEY,
    "x-API-id": IMPERVA_API_ID,
    "Content-Type" : "application/json"
}
IMPERVA_URL_PREFIX = "https://my.imperva.com/api/prov/v1"
#--------------------------------------------------------

parser=argparse.ArgumentParser()
parser.add_argument("--accountid", type=str, help="ID of the account in Imperva")
##  REST OF ARGUMENTS

args = parser.parse_args()

def getAccountName(accountid):

    response=""
    payload=""
    feature = "/account"
    url = IMPERVA_URL_PREFIX + feature + "?account_id=" + str(accountid)
    try:
        response = requests.post(url, headers=IMPERVA_headers, data=payload, verify=False)
        jsonresp = json.dumps(response.json())
        response_dict = json.loads(jsonresp)
        return response_dict["account"]["account_name"]

    except:
        print("API interaction error: GetAccountName" + str(response))

def listSitesforAccount (account_id):
    feature="/sites/list"
    payload=""
    page_id=0
    count_item_per_page = 20
    finished_pagination = False


    while not finished_pagination:
        url = IMPERVA_URL_PREFIX + feature + "?page_size=" + str(count_item_per_page) + "&page_num=" + str(
            page_id) + "&account_id=" + str(account_id)
        response = requests.post(url, headers=IMPERVA_headers, data=payload, verify=False)
        jsonresp = json.dumps(response.json())
        response_dict = json.loads(jsonresp)

        if response_dict["sites"] == []: # Condition to exit loop: Paginated all elements
            finished_pagination = True
            break


        #print("i: " + str(page_id) + "\n" + str(response_dict) + "\n") DEBUG
#def getcerttypes(custom, generated, none):
#    if (custom == False):


        for i in range(len(response_dict["sites"])):
            try:
                certexpdate = response_dict["sites"][i]['ssl']['custom_certificate']['expirationDate']
                accountname=getAccountName(response_dict["sites"][i]["account_id"])
                cert = response_dict["sites"][i]['ssl']['custom_certificate']['active']
                #print(str(cert))

                #print(response_dict["sites"][i]['ssl']['generated_certificate'])
                if response_dict["sites"][i]['ssl']['generated_certificate']['ca'] == 'GS':
                    certgenerated = 'Autogenerado'
                    print(response_dict["sites"][i]["domain"] + "," + str(accountname) + "," + datetime.datetime.fromtimestamp(int(certexpdate / 1000)).strftime('%d/%m/%Y %H:%M:%S') + "," + (certgenerated))

                else:
                    if (str(cert) == 'True'):
                        certgenerated = 'Custom'
                        print(response_dict["sites"][i]["domain"] + "," + str(accountname) + "," + datetime.datetime.fromtimestamp(int(certexpdate / 1000)).strftime('%d/%m/%Y %H:%M:%S'))
                        print(', Tiene Custom Cert')

                    else:
                        print(response_dict["sites"][i]["domain"] + "," + str(accountname) + "," + datetime.datetime.fromtimestamp(int(certexpdate / 1000)).strftime('%d/%m/%Y %H:%M:%S') + "," + "No tiene certificado")
            except:
                print(response_dict["sites"][i]["domain"] + "," + str(accountname) + "," + datetime.datetime.fromtimestamp(int(certexpdate / 1000)).strftime('%d/%m/%Y %H:%M:%S'))

        page_id += 1




def main():
    warnings.filterwarnings("ignore")
    listSitesforAccount(args.accountid)

if __name__ == '__main__':
    main()