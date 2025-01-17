# Should be called with PGPASSWORD=mysecretpassword

#!/bin/bash
dbMissing=true;
allDBs=(rucio)
while ${dbMissing};
do
    dbMissing=false;
    allExistingDBs=$(psql -U postgres -h rucio-db -p 5432 -c "\l");
    for db in "${allDBs[@]}";
    do
        if grep -q "${db}" <<< "${allExistingDBs}";
        then
            echo "${db} OK";
        else
            echo "${db} not created";
            dbMissing=true;
        fi;
    done;
    if ${dbMissing};
    then
        sleep 1;
    fi
done
