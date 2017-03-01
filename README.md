# tweedekamer

Some simple scripts to create an overview of the voting history in the Dutch
Second Chamber of Parliament by scraping the https://www.tweedekamer.nl
website.

NOTE. Since starting this project I discovered the excellent website
https://watstemthetparlement.nl, which is a much more professional take on this
idea and provides a searchable interface to all the same data and more.
Visitors that are looking to analyze the voting history of Dutch Members of
Parliament are advised to visit this site instead, however I will leave the
scripts up as a reference for those that like to crunch their own numbers.

## how to create a simple one-page overview of votes

Requirements: wget, python3, beautifulsoup4.

Step 1. Download webpages in html/yyyy

    $ ./fetch.sh 2012 2013 2014 2015 2016 2017

Step 2. Parse webpages and convert to json in in json/yyyy

    $ ./parse.py 2012 2013 2014 2015 2016 2017

Step 3. Aggregate json data into a single webpage "votes.html"

    $ ./votes.py 2012-11-05 2017-02-23 "Kabinet-Rutte II"

The resulting 4.3M static webpage can be found here:

https://gertjanvanzwieten.github.io/tweedekamer/votes.html
