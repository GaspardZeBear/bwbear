# bwbear
Pandas experiments


Usage


(venv) ubu@ubu:~/bwbear$ python PP.py ppcompare --help
Usage: PP.py ppcompare [OPTIONS]

Options:
  --file1 TEXT                file1
  --file2 TEXT                file2
  --output TEXT
  --highresponsetime INTEGER
  --autofocusmean INTEGER
  --autofocuscount INTEGER
  --ymax INTEGER
  --ppregex TEXT
  --ppregexclude TEXT
  --verbose
  --help                      Show this message and exit.

NB : ne sait travailler qu'avec des .pan généré par le PP.py ppanalyze !
python PP.py ppcompare --file2 Blazemeter-RCET-PP-20190109-15h04-15h24.csv.pan --file1 Blazemeter-RCET-PP-20183110-14h21.csv.pan  --ymax 1000 --ppregexclude transaction/list > z.htm
python PP.py ppcompare --file2 Blazemeter-RCET-PP-20190109-15h04-15h24.csv.pan --file1 Blazemeter-RCET-PP-20183110-14h21.csv.pan  --ymax 1000 --ppregexclude "transaction" > z.htm
python PP.py ppcompare --file2 Blazemeter-RCET-PP-20190109-15h04-15h24.csv.pan --file1 Blazemeter-RCET-PP-20183110-14h21.csv.pan  --ppregex remittance --ymax 12000 > z.htm
python PP.py ppcompare --file2 Blazemeter-RCET-PP-20190109-15h04-15h24.csv.pan --file1 Blazemeter-RCET-PP-20183110-14h21.csv.pan   --ymax 12000 > z.htm


(venv) ubu@ubu:~/bwbear$ python PP.py ppanalyze --help
Usage: PP.py ppanalyze [OPTIONS]

Options:
  --datafile TEXT             datafile
  --formatfile TEXT           formatfile
  --output TEXT
  --timegroupby TEXT
  --timeformat TEXT
  --decimal TEXT
  --highresponsetime INTEGER
  --buckets TEXT
  --autofocusmean INTEGER
  --autofocuscount INTEGER
  --ymax INTEGER
  --ppregex TEXT
  --timeregex TEXT
  --steps TEXT
  --ppregexclude TEXT
  --workdir TEXT
  --type TEXT
  --verbose
  --quick
  --nobuckets
  --nodescribe
  --nographs
  --help                      Show this
python ../PP.py ppanalyze --datafile ../DYN-PP-PROD-Blazemeter-20181121-15h-17h.csv --formatfile ../CentralReport.json  --buckets 0,100,200,300,400,500,1000,3000,10000,20000,100000 --decimal '.'> index.htm
python ../PP.py ppanalyze --datafile ../DYN-PP-PROD-Blazemeter-20181121-15h-17h.csv.pan --formatfile ../CentralReport.json --buckets 0,100,200,300,400,500,1000,3000,10000,20000,100000 --decimal '.'> index.htm


(venv) ubu@ubu:~/bwbear$ python PP.py sqlcompare --help
Usage: PP.py sqlcompare [OPTIONS]

Options:
  --file1 TEXT                file1
  --file2 TEXT                file2
  --output TEXT
  --highresponsetime INTEGER
  --autofocusmean INTEGER
  --autofocuscount INTEGER
  --sqlregex TEXT
  --sqlregexclude TEXT
  --verbose
  --help                      Show this message and exit.
python PP.py sqlcompare --file1 DB.csv --file2 DB1.csv --output html > c.htm
python PP.py sqlcompare --file1 DB.csv --file2 DB1.csv --output html --sqlregex insert> c.htm
python PP.py sqlcompare --file1 DB.csv --file2 DB1.csv --output html --sqlregex "tab_0\." > c.htm



