from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os,time,boto3


def is_file_downloaded(filename, timeout=60):
    end_time = time.time() + timeout
    while not os.path.exists(filename):
        time.sleep(1)
        if time.time() > end_time:
            print("File not found within time")
            return False

    if os.path.exists(filename):
        print("File found")
        return True
        
def enable_download(driver):
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': "/tmp"}}
    driver.execute("send_command", params)


def lambda_handler(event, context):
    prefs = {
        "download.default_directory": "/tmp",
        }
    options = Options()
    options.binary_location = '/opt/headless-chromium'
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome('/opt/chromedriver',chrome_options=options)
    
    enable_download(driver)
    
    driver.get('http://xcal1.vodafone.co.uk/')

    ### simulating the downloading proccess
    download_btn = driver.find_element_by_xpath("/html/body/table[@class='dltable']/tbody/tr[17]/td/a[1]")
    download_btn.click()

    file_path = '/tmp/5MB.zip'

    if is_file_downloaded(file_path, 120):
        print("yes")
    else:
        print("No")


    print("----TMP")
    os.system("ls /tmp")

    s3 = boto3.client("s3")

    print("UPLOADING FILE....")
    s3.upload_file(
        Filename="/tmp/5MB.zip",
        Bucket="testdtlambdaslayers",
        Key="5MB.zip",
    )

    print("----FINISH---")

    title = driver.title

    driver.close();
    driver.quit();

    response = {
        "statusCode": 200,
        "body": title
    }

    return response
