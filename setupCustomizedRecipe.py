import os
import time

print("Installing sklearn--------------")
os.system("pip3 install sklearn")
print("--------------------------------")
print("Installing numpy --------------")
os.system("pip3 install numpy")
print("--------------------------------")
print("Installing streamlit -----------")
os.system("pip3 install streamlit")
print("--------------------------------")

print("Installing elasticsearch -----------")
os.system("pip3 install elasticsearch")
print("--------------------------------")

print("Installing plotnine -----------")
os.system("pip3 install plotnine")
print("--------------------------------")
print("Installing tqdm -----------")
os.system("pip3 install tqdm")
print("--------------------------------")


print("Uploading data and creating indices --------------")

print("Starting Kibana and Elastic Search ---------------")
os.system("docker-compose up >kibanaES.txt &")
time.sleep(20)

os.system("python3 datauploads/bulk_upload.py")

os.system("python3 datauploads/regional_produce_data_upload.py")
os.system("python3 datauploads/user_rating_data_upload.py")
print("Starting the web app -----------------------------")
os.system("streamlit run src/ui2.py")

