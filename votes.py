#! /usr/bin/python3

import re, os, sys, json, bs4, urllib.request, shelve

def get_dossiertitel( nummer ):
  pattern = re.compile( '/dossier/{0}/(kst-{0}-[^?]*)'.format(nummer) )
  print( 'downloading dossier', nummer )
  for page in range(1,99):
    with urllib.request.urlopen( 'https://zoek.officielebekendmakingen.nl/dossier/{}?_page={}'.format(nummer,page) ) as response:
      soup = bs4.BeautifulSoup( response )
    for li in soup.find( 'div', class_='lijst' ).ul.find_all( 'li' ):
      match = pattern.match( li.a['href'] )
      if match:
        kst = match.group(1)
        print( 'downloading {}.xml'.format(kst) )
        with urllib.request.urlopen( 'https://zoek.officielebekendmakingen.nl/{}.xml'.format(kst) ) as response:
          soup = bs4.BeautifulSoup( response )
          return soup.dossier.titel.text
  raise Exception
 
def main( van, tot, titel ):
  pattern = re.compile( '^detail[?]id=....P.....$' )
  dossiers = {}
  for jaar in range( int(van.split('-')[0]), int(tot.split('-')[0])+('-' in tot) ):
    print( 'scanning', jaar )
    for item in os.listdir( os.path.join('json',str(jaar)) ):
      if pattern.match(item):
        with open( os.path.join('json',str(jaar),item), 'r' ) as fid:
          for data in json.load( fid ):
            if 'stemmingresultaat' in data and van <= data['publicatiedatum'] <= tot:
              dossiers.setdefault( data['nummer'].split('-')[0], [] ).append( data )
  print( 'opening votes.html' )
  dossiertitels = shelve.open( 'dossiers.db' )
  url_kamerstukken = 'https://www.tweedekamer.nl/kamerstukken/'
  description = 'Stemmingen in de Tweede Kamer van {} tot {}'.format( van, tot )
  with open( 'votes.html', 'w' ) as html:
    print( '<html>', file=html )
    print( '<head>', file=html )
    print( '<title>{}</title>'.format(titel), file=html )
    print( '<meta name="description" content="{}" />'.format(description), file=html )
    print( '<base href="{}">'.format(url_kamerstukken), file=html )
    print( '<style>a { text-decoration: none; } pre { white-space: pre-wrap; }</style>', file=html )
    print( '</head>', file=html )
    print( '<body>', file=html )
    print( '<pre>\n<b>{}</b>\n</pre><pre>\n{}'.format(titel,description), file=html )
    for nummer in sorted(dossiers):
      if not nummer:
        continue
      print( 'writing dossier', nummer )
      if not nummer:
        dossiertitel = 'Onbekend'
      elif nummer in dossiertitels:
        dossiertitel = dossiertitels[nummer]
      else:
        dossiertitels[nummer] = dossiertitel = get_dossiertitel( nummer )
      print( '</pre><hr><pre id="{0}">\nDossier {0}: <a href="https://zoek.officielebekendmakingen.nl/dossier/{0}">{1}</a>'.format( nummer, dossiertitel ), file=html )
      for data in sorted( dossiers[nummer], key=lambda data: [data['publicatiedatum']]+[item.rjust(5) for item in data['nummer'].split('-')] ):
        item, naam = re.match( '^(.*?motie |.*?amendement |)(.*)$', data['titel'], flags=re.IGNORECASE ).groups()
        suffix = data['nummer'][len(nummer)+1:]
        if suffix:
          item += suffix + ' '
        print( '</pre><pre id="{}">'.format( data['nummer'] ), file=html )
        assert data['link'].startswith( url_kamerstukken )
        url = data['link'][len(url_kamerstukken):]
        print( '{}<a href="{}">{}</a>{}'.format( item, url, naam, ' ({})'.format(data['fractie']) if 'fractie' in data else '' ), file=html )
        votes = data['stemmingresultaat']
        nvotes = sum( vote['voor'] + vote['tegen'] for vote in data['stemmingresultaat'] )
        for side in 'voor', 'tegen':
          total = sum( vote[side] for vote in votes )
          print( '[+]' if side == 'voor' else '[-]',
            '{} ({}{})'.format( ', '.join( vote['fractie'] for vote in votes if vote[side] ), total, '*' if total >= nvotes/2 else '' ) if total else '(0)', file=html )
    print( '</pre>', file=html )
    print( '</body>', file=html )
    print( '</html>', file=html )

if __name__ == '__main__':
  if len(sys.argv) != 4:
    sys.exit( 'usage: {} van tot itel'.format(sys.argv[0]) )
  main( *sys.argv[1:] )
