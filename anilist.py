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

def query_user_list(anime_id, user_name):

    #anime_id, anime_name = url.replace('https://anilist.co/anime/','').split('/',1)
    #print(anime_id, anime_name.strip('/'))

    query = '''
    query ($id: Int, $mediaId: Int, $userName: String) { # Define which variables will be used in the query (id)
      MediaList (mediaId: $mediaId, userName: $userName type: ANIME) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
        id
        userId
        progress
      }
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
        'id': anime_id,
        'mediaId': anime_id,
        'userName': user_name
    }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    return requests.post(url, json={'query': query, 'variables': variables})

def check_max_episodes(anime_id):
    response = query_anilist(anime_id)

    o = response.json()

    return o['data']['Media']['episodes']

def check_episode(anime_id, user_name):
    
    response = query_user_list('1453', user_name)

    o = response.json()

    print(o)
    print(o['data']['MediaList']['progress'])
    
    print('max =', o['data']['MediaList']['episodes'])

    return o['data']['MediaList']['progress']


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