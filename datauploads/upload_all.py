import bulk_upload
import regional_produce_data_upload
import user_rating_data_upload
import time
import os
import elasticsearch

if __name__ == "__main__":
    time.sleep(int(os.environ['ES_WAIT_TIME']))
    try:
        bulk_upload.main()
    except elasticsearch.exceptions.RequestError:
        print("Index Already Exists")

    try:
        regional_produce_data_upload.main()
    except elasticsearch.exceptions.RequestError:
        print("Index Already Exists")

    try:
        user_rating_data_upload.main()
    except elasticsearch.exceptions.RequestError:
        print("Index Already Exists")
    print("====================================")
    print("READY FOR ANALYSIS!")
    print("====================================")
