# encoding: utf-8

import feedparser

def start_rss(feed):

    lista = []
    feed = feedparser.parse(feed)

    for entry in feed.entries:
        lista.append(entry.title)

    print(lista)
    
    return lista

def ler_rss(feed, lista):
    textos = []
    feed = feedparser.parse(feed)
    print(lista)

    #if feed != old_feed:
    for entry in feed.entries:
        if entry.title not in lista:
            
            #print(entry)
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

            lista.append(entry.title)

            textos.append(texto)

        else:
            print('Entry not inside old_feed')
            pass


    return textos, lista
