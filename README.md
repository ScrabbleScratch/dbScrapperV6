# dbScrapperV6
This script is used to scrap data from an _API_ and save it to a ***MongoDB*** database.

# Features
- The script gets the configuration parameters by parsing them through the console when the script is executed
- The script decides wether to insert or update the database depending on every entry

# How to run it
Open a command shell in the directory where the script is saved and run the following command:
```
dbScrapperV6.py url host database collection [-h] [-s START] [-f FINISH] [-d DELAY] [-r RETRY] [--status STATUS] [--override OVERRIDE]
```

**POSITIONAL ARGUMENTS:**
- **url**: Api url to make requests
- **host**: MongoDB host connection string
- **database**: Name of the database to be used
- **collection**: Name of the table or collection to be used

**OPTIONAL ARGUMENTS:**
- **-s**, **--start**: Id to start from _(default **0**)_
- **-f**, **--finish**: Id to finish at _(default **0**)_
- **-d**, **--delay**: Specify a cycle delay _(default **2.5**)_
- **-r**, **--retry**: Max number of retries allowed _(default **3**)_
- **--status**: Specify a path to save status file _(default **config/status.json**)_
- **--override**: Override status file data _(default **False**)_
