#! /usr/bin/python3

import sys, os, re, bs4, json

def text( obj, lstrip=None ):
  text = ' '.join( line.strip() for line in obj.text.splitlines() )
  if lstrip and text.startswith( lstrip ):
    text = text[len(lstrip):]
  return text.strip()

def main( year ):
  srcdir = os.path.join( 'html', year )
  dstdir = os.path.join( 'json', year )
  assert os.path.isdir( srcdir )
  if not os.path.isdir( dstdir ):
    os.mkdir( dstdir )
  jsonset = set( os.listdir(dstdir) )
  pattern = re.compile( '^detail[?]id=....P.....$' )
  for detail in sorted( item for item in os.listdir(srcdir) if pattern.match(item) and item not in jsonset ):
    print( detail, '...' )
    with open( os.path.join( srcdir, detail ), 'r' ) as fid:
      soup = bs4.BeautifulSoup( fid )
    datas = []
    for ul in soup.find_all( 'ul', class_='search-result-list' ):
      for li in ul.find_all( 'li' ):
        data = {}
        for child in li.children :
          if isinstance( child, str ) or 'class' not in child.attrs:
            pass
          elif 'search-result-content' in child['class']:
            data['titel'] = text( child.h3 )
            data['link'] = 'https://www.tweedekamer.nl' + child.h3.a['href']
            submitter = child.find( class_='submitter' )
            data['indiener'] = text( submitter, lstrip='Indiener:' )
            for a in submitter.find_all( 'a' ):
              if a['href'].startswith( '/kamerleden/fracties/' ):
                data['fractie'] = text( a )
                break
            data['besluit'] = text( child.find( class_='result' ), lstrip='Besluit:' )
          elif 'search-result-category' in child['class']:
            data['categorie'] = text( child )
          elif 'search-result-properties' in child['class']:
            data['nummer'] = text( child.p )
            day, month, year = text( child.find( class_='date' ) ).split()
            data['publicatiedatum'] = '{0:}-{1:02d}-{2:02d}'.format( year, ['jan','feb','maa','apr','mei','jun','jul','aug','sep','okt','nov','dec'].index(month[:3])+1, int(day) )
          elif 'links' in child['class']:
            pass
          elif 'trigger' in child['class'] and 'plus' in child['class']:
            pass
          elif 'vote-result' in child['class']:
            data['stemmingsoort'] = text( child.p, lstrip='Stemmingsoort:' )
            headers = [ col.text.lower().strip() for col in child.table.thead.tr.find_all('th') ]
            assert headers[:4] == [ 'fractie', 'zetels', 'voor', 'tegen' ]
            votes = []
            for tbody in child.table.find_all( 'tbody' ):
              for tr in tbody.find_all( 'tr' ):
                if 'class' in tr.attrs and 'individual-vote' in tr['class']:
                  continue
                cols = tr.find_all( 'td' )
                vote = {}
                vote['fractie'] = text( cols[0] )
                vote['zetels'] = int( cols[1].text )
                for side, col in ('voor',cols[2]), ('tegen',cols[3]):
                  if col.img:
                    alt = col.img['alt']
                    assert alt.endswith( ' stemmen' )
                    n = int( alt[:-7] )
                  else:
                    n = 0
                  vote[side] = n
                if len(headers) >= 5 and headers[4] == 'details' and cols[4].text.strip():
                  vote['details'] = text( cols[4] )
                votes.append( vote )
            data['stemmingresultaat'] = votes
          else:
            raise Exception( child )
        if data:
          datas.append( data )
    with open( os.path.join( dstdir, detail ), 'w' ) as fid:
      json.dump( datas, fid )

if __name__ == '__main__':
  for year in sys.argv[1:]:
    main( year )
