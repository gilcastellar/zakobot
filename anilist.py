import requests
import json

def test_anilist(url):

    anime_id, anime_name = url.replace('https://anilist.co/anime/','').split('/','')
    print(anime_id, anime_name.strip('/'))

    query = '''
    query ($id: Int) { # Define which variables will be used in the query (id)
      Media (id: $id, type: ANIME) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
        id
        title {
          romaji
          english
          native
        }
      }
    }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        'id': anime_id
    }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    return requests.post(url, json={'query': query, 'variables': variables})