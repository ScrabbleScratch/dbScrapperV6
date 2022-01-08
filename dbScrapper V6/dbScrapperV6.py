#!/usr/bin/env python3
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import requests, json, argparse, time

# define console parameters to be parsed
parser = argparse.ArgumentParser(description="Scrap API data and save it into a MongoDB collection")
parser.add_argument("url", help="Api url to make requests", type=str)
parser.add_argument("host", help="MongoDB host connection string", type=str)
parser.add_argument("database", help="Name of the database to be used", type=str)
parser.add_argument("collection", help="Name of the table or collection to be used", type=str)
parser.add_argument("-s", "--start", default=0, help="Id to start from", type=int)
parser.add_argument("-f", "--finish", default=0, help="Id to finish at", type=int)
parser.add_argument("-d", "--delay", default=2.5, help="Specify a cycle delay", type=float)
parser.add_argument("-r", "--retry", default=3, help="Max number of retries allowed", type=int)
parser.add_argument("--status", default="status.json", help="Specify a path to save status file", type=str)
parser.add_argument("--override", default=False, help="Override status file data", type=bool)
args = parser.parse_args()

# define variables to store parsed arguments
parsedUrl = args.url
parsedHost = args.host
parsedDb = args.database
parsedColl = args.collection
parsedStart = args.start
parsedFinish = args.finish
parsedDelay = args.delay
parsedRetry = args.retry
parsedStatus = args.status
parsedOverride = args.override

print(f"""
Args parsed:
\tURL: {parsedUrl}

\tHOST: {parsedHost}
\tDATABASE: {parsedDb}
\tCOLLECTION: {parsedColl}

\tSTARTS: {parsedStart}
\tFINISH: {parsedFinish}
\tDELAY: {parsedDelay}

\tRETRIES: {parsedRetry}

\tSTATUS FILE: {parsedStatus}

\tOVERRIDE: {parsedOverride}
""")

# if parameters parsed then define variables, if not read status file
if parsedOverride:
    finished = False
    lastId = parsedStart
    maxId = parsedFinish
    print(f"-> Got lastId = {lastId} from parsed argument!\n")
else:
    # load status file to check for previus program status
    while True:
        try:
            with open(parsedStatus, "r") as file:
                print("Status file opened!")
                status = file.read()
                # if file content is not spaces and its length is grater than 0 then read content
                if not status.isspace() and len(status) > 0:
                    status = json.loads(status)
                    statusKeys = status.keys()
                    # if the needed keys are within the content then continue
                    if "finished" in statusKeys and "lastId" in statusKeys:
                        finished = status["finished"]
                        lastId = status["lastId"]
                        maxId = status["maxId"]
                        print(f"Finished: {finished}, LastId: {lastId}, Max Id: {maxId}")
                        break
                # if something fails raise an error
                raise FileNotFoundError
        # if the FileNotFound is raised then create a fresh status file with default parameters
        except FileNotFoundError:
            print("Status file not found or unusable!")
            with open(parsedStatus, "w") as file:
                print("Creating status file...")
                file.write(json.dumps({"finished":False, "lastId":parsedStart, "maxId":parsedFinish}, indent=4))

# initialize MongoDB client
try:
    mongo = MongoClient(parsedHost)
except Exception as e:
    print("Error while connecting to database:", e)
    print("Terminating program...")
    exit()

# if finished is false then continue
if not finished:
    print(f"Scrapping anime data from Id: {lastId} to Id: {maxId}")
    try:
        # scrap data from lastId to maxId
        for x in range(lastId, maxId + 1):
            # bucle until data gets valid data to evaluate
            i = 0
            while i < parsedRetry:
                # make a pause between iterations
                time.sleep(parsedDelay)

                # request data per id
                print("Requesting id", x, end=": ")
                rq = requests.get(parsedUrl + str(x))

                # check request status code
                match rq.status_code:
                    case 200:
                        jobject = dict(rq.json())

                        # remove unwanted fields within data
                        for k in {"request_hash", "request_cached", "request_cache_expiry"}:
                            try:
                                jobject.pop(k)
                            except KeyError:
                                pass
                        
                        # assign mal_id as _id in database
                        jobject["_id"] = jobject["mal_id"]

                        try:
                            # insert data into database
                            mongo[parsedDb][parsedColl].insert_one(jobject)
                            print("Entry inserted ( id", jobject["_id"], ")")
                        except DuplicateKeyError:
                            # update data if exists
                            mongo[parsedDb][parsedColl].replace_one({"_id":jobject["_id"]}, jobject)
                            print("Entry updated ( id", jobject["_id"], ")")
                    case 400:
                        print("Bad request")
                    case 404:
                        print("Not found")
                    case 429:
                        print("Too many requests")
                    case 500:
                        print("Jikan error")
                        with open("jikan_errors.txt", "at") as f:
                            f.write("\nId " + str(x) + ": " + rq.text)
                        continue
                    case 503:
                        # if the service is unavailable make the while iterate again
                        print("Service unavailable")
                        continue
                    case _:
                        # if status is unknown print the request response and exit
                        print("Unknown status:", rq.text)
                        exit()
                # break the while loop
                break
            else:
                print("Max number of retries reached. Terminating...")
                exit()
            # update status
            lastId = x
            with open(parsedStatus, "w") as status:
                print("\tUpdating status\n")
                status.write(json.dumps({"finished":False, "lastId":lastId, "maxId":maxId}, indent=4))
    #try: pass
    except Exception as e:
        error = "An error occurred while running the program!\nError: "+str(e)+"\nTerminating program..."
        print(error)
        exit()
    # when the maxId has been reached, update the finished parameter to True within the status file
    with open(parsedStatus, "w") as status:
        print("Update status file to finished")
        status.write(json.dumps({"finished":True, "lastId":lastId, "maxId":maxId}, indent=4))

# close the database connection when everything has finished
print("Closing database connection")

# print finished message
print("Scrapping is finished!")