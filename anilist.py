import requests
import json

def test_anilist(url):

    anime_id, anime_name = url.replace('https://anilist.co/anime/','').split('/',1)
    print(anime_id, anime_name.strip('/'))

    query = '''
    query ($id: Int) { # Define which variables will be used in the query (id)
      Media (id: $id, type: ANIME) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
        id
        description
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

def test_mutation(anime, token):
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
        "mediaId" => 1,
        "status" => "CURRENT"
    }

    data = (requests.post('https://graphql.anilist.co', json={'query': mutation, headers=headers}))

    print(data)
       