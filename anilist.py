import requests
import json

def query_anilist(anime_id):

    #anime_id, anime_name = url.replace('https://anilist.co/anime/','').split('/',1)
    #print(anime_id, anime_name.strip('/'))

    query = '''
    query ($id: Int) { # Define which variables will be used in the query (id)
      Media (id: $id, type: ANIME) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
        id
        description
        episodes
        title {
            romaji
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

def check_max_episodes(anime_id):
    response = query_anilist(anime_id)

    o = response.json()

    return o['episodes']


def new_anime(anime, token):
    headers = {
        'Authorization': token
        }

    mutation = '''
    mutation ($mediaId: Int, $status: MediaListStatus) {
        SaveMediaListEntry (mediaId: $mediaId, status: $status) {
            id
            status
        }
    }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        "mediaId": anime,
        "status": "CURRENT"
    }

    data = (requests.post('https://graphql.anilist.co', json={'query': mutation, 'variables':variables}, headers=headers).json())
    
    print(data)
       
def update_episode(anime, episode, token):
    headers = {
        'Authorization': token
        }

    mutation = '''
    mutation ($mediaId: Int, $progress: Int) {
        SaveMediaListEntry (mediaId: $mediaId, progress: $progress) {
            id
            progress
        }
    }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        "mediaId": anime,
        "progress": episode
    }

    data = (requests.post('https://graphql.anilist.co', json={'query': mutation, 'variables':variables}, headers=headers).json())
    
    print(data)