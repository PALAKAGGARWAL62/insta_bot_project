import requests

response = requests.get('https://jsonbin.io/b/59d0f30408be13271f7df29c').json()
access_token= response['access_token']
base_url='https://api.instagram.com/v1/'

def self_info():
    request_url = (base_url + 'users/self/?access_token=%s') % (access_token)
    print 'GET request url : %s' % (request_url)
    user_info = requests.get (request_url).json ()
    if user_info['meta']['code'] == 200:
        # Request successful
        print 'Request successfull'
        print 'USER INFORMATION'
        print 'ID: '+user_info['data']['id']
        print 'USER NAME: ' + user_info['data']['username']
        print 'PROFILE PICTURE LINK: ' + user_info['data']['profile_picture']
        print 'FULL NAME: ' + user_info['data']['full_name']
        print 'BIO: '+user_info['data']['bio']
        print 'WEBSITE: '+user_info['data']['website']
        print 'IS IT A BUSSINESS APP: '+str(user_info['data']['is_business'])
        print 'MEDIA: '+str(user_info['data']['counts']['media'])
        print 'FOLLOWS %s' %(user_info['data']['counts']['follows'])
        print 'FOLLOWED BY %s' % (user_info['data']['counts']['followed_by'])
        print 'CODE %s'%(user_info['meta']['code'])
    else:
        print 'Status code other than 200 received!'

self_info()