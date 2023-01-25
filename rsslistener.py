# encoding: utf-8

import feedparser

def test_title(title):

    print(title)
    title = title.replace('[SubsPlease] ','')
    print(title)
    title, episode = title.split(' - ')
    episode, trash = episode.split(' ', 1)
    if episode[0] == '0':
        episode = episode[1]
    print('Ja esta disponivel o episodio '+ episode + ' de ' + title)

def ler_rss(feed, old_feed):
    textos = []
    feed = feedparser.parse(feed)
    entries = feed.entries
    for entry in entries:
        if old_feed == []:
           old_feed = entries
        if entry not in old_feed:
            print(entry)
            texto = ''

            partes = entry.title.split(' ')

            title = entry.title

            title = title.replace('[SubsPlease] ','')
            title, episode = title.rsplit(' - ', 1)
            episode, trash = episode.split(' ', 1)
            if episode[0] == '0':
                episode = episode[1]

            
            texto += 'Ja esta disponivel para download o episodio '+ episode + ' de ' + title + '\n\n'
            texto += 'Link do nyaa: <' + entry.id + '> \n\n'
            texto += 'Ou se preferir, o hash: ' + entry.nyaa_infohash + '\n\n'

            print('novo:',entry.title)

            textos.append(texto)

        else:
            pass

    old_feed = entries

    return textos, old_feed



#def ler_rss(feed, list):
#    texto = ''
#    Feed = feedparser.parse(feed)
#    pointer = Feed.entries[0]

#    if pointer.title not in list:
    
#        texto += 'summary = ' + pointer.summary
#        #texto += '\n\n' + 'link = ' + pointer.link
#        #texto += '\n\n' + 'published = ' + pointer.published
#        texto += '\n\n' + 'title = ' + pointer.title
#        texto += '\n\n' + 'hash = ' + pointer.nyaa_infohash
#        texto += '\n\n' + 'id = <' + pointer.id + '>'
#        #for item in pointer:
#        #    texto += '\n\n pointer item: ' + item

#        print('novo:',pointer.title)

#        return texto, pointer.title
    
#    else:
#        texto = ''
#        return texto, pointer.title