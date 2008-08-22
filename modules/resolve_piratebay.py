import urllib2
import logging
from module_resolver import ResolverException
from manager import ModuleWarning

__pychecker__ = 'unusednames=parser,feed'

log = logging.getLogger('piratebay')

# this way we don't force users to install bs incase they do not want to use module
soup_present = True
try:
    from BeautifulSoup import BeautifulSoup
except:
    soup_present = False

class ResolvePirateBay:
    """PirateBay resolver."""

    def register(self, manager, parser):
        manager.register('resolve_piratebay', group='resolver')

    # resolver API
    def resolvable(self, feed, entry):
        url = entry['url']
        if url.endswith('.torrent'): return False
        if url.startswith('http://thepiratebay.org/'): return True
        if url.startswith('http://torrents.thepiratebay.org/'): return True
        return False
        
    # resolver API
    def resolve(self, feed, entry):
        if not soup_present:
            raise ResolverException('BeautifulSoup not present')
        if entry['url'].startswith('http://thepiratebay.org/search/'):
            # use search
            try:
                entry['url'] = self.search_title(entry['title'])
                log.debug('search returned %s' % entry['url'])
            except ModuleWarning, e:
                raise ResolverException(e)
        else:
            # parse download page
            entry['url'] = self.parse_download_page(entry['url'])
            
    def parse_download_page(self, url):
        try:
            page = urllib2.urlopen(url)
            soup = BeautifulSoup(page)
            tag_div = soup.find('div', attrs={'class':'download'})
            if not tag_div:
                raise ResolverException('Unable to locate download link from url %s' % url)
            tag_a = tag_div.find('a')
            torrent_url = tag_a.get('href')
            return torrent_url
        except Exception, e:
            raise ResolverException(e)    
            
    # search API
    def search(self, feed, entry):
        entry['url'] = self.search_title(entry['title'])
            
    def search_title(self, name, url=None):
        import urllib
        name = name.replace('.',' ').lower()
        if not url:
            url = 'http://thepiratebay.org/search/'+urllib.quote(name)
        try:
            page = urllib2.urlopen(url)
        except urllib2.URLError:
            raise ResolverException('Timed out when opening search page')
        
        soup = BeautifulSoup(page)
        torrents = []
        for link in soup.findAll('a', attrs={'class': 'detLink'}):
            if not link.string.replace('.', ' ').lower() == name:
                continue
            torrent = {}
            torrent['name'] = link.string
            torrent['link'] = 'http://thepiratebay.org'+link.get('href')
            tds = link.parent.parent.findAll('td')
            torrent['seed'] = tds[-2]
            torrent['leech'] = tds[-1]
            torrents.append(torrent)
            
        if not torrents:
            raise ModuleWarning('No matches for %s' % name)
            
        # TODO: choose best torrent based on leech / seed
        return torrents[0]['link']