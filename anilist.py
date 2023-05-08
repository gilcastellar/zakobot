import requests
import json
import random

def query_anilist(anime_id):

    #anime_id, anime_name = url.replace('https://anilist.co/anime/','').split('/',1)
    #print(anime_id, anime_name.strip('/'))

    query = '''
    query ($id: Int) { # Define which variables will be used in the query (id)
      Media (id: $id, type: ANIME) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
        id
        format
        duration
        episodes
        averageScore
        title {
            romaji
            english
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

def get_last_page():
    query = '''
    {
        Page(page: 351, perPage: 50) {
            pageInfo {
              lastPage
            }
            media(type: ANIME, status_not_in: [NOT_YET_RELEASED, RELEASING, CANCELLED]) {
              id
            }
        }
    }
    '''

    # Define our query variables and values that will be used in the query request

    url = 'https://graphql.anilist.co'

    return requests.post(url, json={'query': query})

def query_random_anime():

    query = '''
    query ($page: Int, $perPage: Int) {
        Page(page: $page, perPage: $perPage) {
            pageInfo {
              total
              currentPage
              lastPage
              hasNextPage
              perPage
            }
            media(type: ANIME, status_not_in: [NOT_YET_RELEASED, RELEASING, CANCELLED], countryOfOrigin: JP) {
              id
              format
              popularity
              episodes
              duration
              title {
                romaji
              }
            }
          }
        }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        'page': random.randrange(1,350),
        'perPage': 50
    }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    return requests.post(url, json={'query': query, 'variables': variables})

def query_list(prequery, page, user_name, status=None):
    query = prequery


    if status != None:
        variables = {
            "status": status,
            "userName": user_name,
            "page": page
            }
    else:
        variables = {
            "userName": user_name,
            "page": page
            }


    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    return requests.post(url, json={'query': query, 'variables': variables})

def query_anime_id(id):

    #anime_id, anime_name = url.replace('https://anilist.co/anime/','').split('/',1)
    #print(anime_id, anime_name.strip('/'))

    query = '''
    query ($id: Int) {
      Media (id: $id, type: ANIME) {
        id
        format
        episodes
        duration
        popularity
        status
        averageScore
        title {
            romaji
            english
        }
        startDate {
            day
            month
            year
        }
        relations {
            edges {
                relationType
                node {
                    id
                    title {
                        romaji
                        english
                    }
                    format
                    duration
                    startDate {
                        day
                        month
                        year
                    }
                }
            }
        }
      }
    }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        'id': id
    }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    return requests.post(url, json={'query': query, 'variables': variables})

def query_manga_id(id):

    #anime_id, anime_name = url.replace('https://anilist.co/anime/','').split('/',1)
    #print(anime_id, anime_name.strip('/'))

    query = '''
    query ($id: Int) {
      Media (id: $id, type: MANGA) {
        id
        format
        title {
            romaji
        }
      }
    }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        'id': id
    }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    return requests.post(url, json={'query': query, 'variables': variables})

def query_list_by_status(status, user_name, page=1):

    query = '''
    query ($page: Int, $status: MediaListStatus, $userName: String) {
        Page (page: $page, perPage: 50) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            mediaList(status: $status, userName: $userName, type: ANIME) {
                mediaId
                id
                userId
                progress
                status
            }
        }
    }
    '''

    variables = {
        "status": status,
        "userName": user_name,
        "page": page
        }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    return requests.post(url, json={'query': query, 'variables': variables})

def query_user_list(anime_id,user_name):

    #anime_id, anime_name = url.replace('https://anilist.co/anime/','').split('/',1)
    #print(anime_id, anime_name.strip('/'))

    query = '''
    query ($mediaId: Int, $userName: String) {
      MediaList (mediaId: $mediaId, userName: $userName type: ANIME) {
        userId
        mediaId
        progress
        status
        score (format: POINT_10_DECIMAL)
      }
    }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        'mediaId': anime_id,
        'userName': user_name
    }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    return requests.post(url, json={'query': query, 'variables': variables})

def check_max_episodes(anime_id):
    response = query_anime_id(anime_id)
    print(json.dumps(response.json(), indent=2))
    o = response.json()


    return o['data']['Media']['episodes']

def check_episode(anime_id, user_name):
    
    response = query_user_list(anime_id, user_name)
    print(json.dumps(response.json(), indent=2))
    o = response.json()

    print(o)
    print(o['data']['MediaList']['progress'])

    return o['data']['MediaList']['progress']

def put_in_status(anime, status, token):
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
        "status": status
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

def give_score(anime, score, user, token):
    headers = {
        'Authorization': token
        }

    mutation = '''
    mutation ($mediaId: Int, $score: Float) {
        SaveMediaListEntry (mediaId: $mediaId, score: $score) {
            id
            score
        }
    }
    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        "mediaId": anime,
        "score": score
    }

    data = (requests.post('https://graphql.anilist.co', json={'query': mutation, 'variables':variables}, headers=headers).json())
    
    print(data)
    
