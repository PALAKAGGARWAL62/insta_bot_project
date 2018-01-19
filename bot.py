# to perform internet operations
import requests

# to download media from internet
import urllib

# to implement nlp
from textblob import TextBlob

# to implement text analysis, either positive, negative or neutral
from textblob.sentiments import NaiveBayesAnalyzer

# to implement database
import models

# to plot bar graph
import matplotlib.pyplot as plt

from wordcloud import WordCloud

''' 
#fetch access token   ...json format url
 response = requests.get ('https://jsonbin.io/b/59d0f30408be13271f7df29c').json ()
 access_token = response['access_token']
'''

'''
Note: To make instabot work over your own account make a developer client account of instagram.
      Generate your own access token and paste it below. 
'''
access_token = '6861336753.6e6b53e.c8f3bd13244f450eaafe46c0aab33695'
base_url = 'https://api.instagram.com/v1/'

'''
Note: To use any username based operation of instabot the user must be added in your sandbox.
'''


# Function to get your own instagram account information
def self_info():
    try:
        request_url = (base_url + 'users/self/?access_token=%s') % access_token
        print 'Request url for self information : %s' % request_url
        user_info = requests.get (request_url).json ()
        if user_info['meta']['code'] == 200:
            # Request successful
            print 'Request successful\n\n'
            print 'USER INFORMATION\n'
            print 'ID: ' + user_info['data']['id']
            print 'USER NAME: ' + user_info['data']['username']
            print 'PROFILE PICTURE LINK: ' + user_info['data']['profile_picture']
            print 'FULL NAME: ' + user_info['data']['full_name']
            print 'BIO: ' + user_info['data']['bio']
            print 'WEBSITE: ' + user_info['data']['website']
            print 'IS IT A BUSINESS APP: ' + str (user_info['data']['is_business'])
            print 'MEDIA: ' + str (user_info['data']['counts']['media'])
            print 'FOLLOWS %s' % (user_info['data']['counts']['follows'])
            print 'FOLLOWED BY %s' % (user_info['data']['counts']['followed_by'])
            print 'CODE %s' % (user_info['meta']['code'])
            query = models.user.select ().where (models.user.user_id == user_info['data']['id'])
            if len (query) > 0:
                query[0].user_name = user_info['data']['username']
                query[0].fullanme = user_info['data']['full_name']
                query[0].followed_by_count = user_info['data']['counts']['followed_by']
                query[0].follows_count = user_info['data']['counts']['follows']
                query[0].save ()
            else:
                self_pro = models.user (user_id=user_info['data']['id'], user_name=user_info['data']['username'],
                                        fullname=user_info['data']['full_name'],
                                        followed_by_count=user_info['data']['counts']['followed_by'],
                                        followers_count=user_info['data']['counts']['follows'])
                self_pro.save ()
            return user_info['data']['id']
        else:
            print 'Status code other than 200 received!'
    except Exception as e:
        print e
        print 'There is an exception in self information'


# Function to get our media id
def self_media_id():
    try:
        request_url = (base_url + 'users/self/media/recent/?access_token=%s') % access_token
        own_info = requests.get (request_url).json ()
        if own_info['meta']['code'] == 200:
            if len (own_info['data']) > 0:
                print 'Total posts are: ' + str (len (own_info['data']))
                x = input ('Which post you want to fetch id: ')
                x -= 1
                media_id = own_info['data'][x]['id']
                print media_id
                return media_id
            else:
                print 'no posts'
        else:
            print 'code not 200'
    except Exception as e:
        print e
        print 'Exception in self media id'


# Function to get self comments
def own_comments():
    try:
        my_media_id = self_media_id ()
        request_url = (base_url + 'media/%s/comments?access_token=%s') % (my_media_id, access_token)
        print request_url
        response = requests.get (request_url).json ()
        if response['meta']['code'] == 200:
            # Check if we have comments on the post
            if len (response['data']) > 0:
                # And then read them one by one
                for comment in response['data']:
                    comment_id = comment['id']
                    comment_text = comment['text']
                    blob = TextBlob (comment_text, analyzer=NaiveBayesAnalyzer ())
                    print blob.sentiment
                    print blob.sentiment.classification
                    comment = models.self_comment (media_id=my_media_id, comment_id=comment_id,
                                                   comment_text=comment_text,
                                                   classification=blob.sentiment.classification,
                                                   positive_sentiments=blob.sentiment.p_pos,
                                                   negative_sentiments=blob.sentiment.p_neg)
                    comment.save ()
                    return comment_id
            else:
                print 'No comments'
        else:
            print 'code other than 200'
    except Exception as e:
        print e
        print 'Exception in own comments'


# Function to delete self negative comments
def self_comment_delete():
    try:
        media_id = self_media_id ()
        my_media_id = self_media_id ()
        request_url = (base_url + 'media/%s/comments?access_token=%s') % (my_media_id, access_token)
        print request_url
        response = requests.get (request_url).json ()
        if response['meta']['code'] == 200:
            # Check if we have comments on the post
            if len (response['data']) > 0:
                # And then read them one by one
                for comment in response['data']:
                    comment_id = comment['id']
                    comment_text = comment['text']
                    blob = TextBlob (comment_text, analyzer=NaiveBayesAnalyzer ())
                    print blob.sentiment
                    print blob.sentiment.classification

                    comment = models.self_comment (media_id=my_media_id, comment_id=comment_id,
                                                   comment_text=comment_text,
                                                   classification=blob.sentiment.classification,
                                                   positive_sentiments=blob.sentiment.p_pos,
                                                   negative_sentiments=blob.sentiment.p_neg)
                    comment.save ()

                    if blob.sentiment.p_neg > blob.sentiment.p_pos:
                        delete_url = (base_url + 'media/%s/comments/%s/?access_token=%s') % (
                            media_id, comment_id, access_token)
                        print 'DELETE request url : %s' % delete_url

                        delete_info = requests.delete (delete_url).json ()

                        if delete_info['meta']['code'] == 200:
                            print 'Comment successfully deleted!'
                        else:
                            print 'Could not delete the comment'
    except Exception as e:
        print e
        print 'Exception in self comment deletion'


# Function to get your own posts
def get_own_post():
    try:
        request_url = (base_url + 'users/self/media/recent/?access_token=%s') % access_token
        print 'Get request url for own posts : %s' % request_url
        own_info = requests.get (request_url).json ()
        if own_info['meta']['code'] == 200:
            if len (own_info['data']) > 0:
                print 'Total posts are: ' + str (len (own_info['data']))
                x = input ('Which post you want to see: ')
                x -= 1
                if own_info['data'][x]['type'] == 'image':
                    # download own posts
                    print own_info['data'][x]['id']
                    media_name = str (x) + str (own_info['data'][x]['id']) + '.jpg'
                    media_url = own_info['data'][x]['images']['standard_resolution']['url']
                    urllib.urlretrieve (media_url, media_name)

                elif own_info['data'][x]['type'] == 'video':
                    media_name = str (x) + str (own_info['data'][x]['id']) + '.mp4'
                    media_url = own_info['data'][x]['videos']['standard_resolution']['url']
                    urllib.urlretrieve (media_url, media_name)

                elif own_info['data'][x]['type'] == 'carousel':
                    x = 0
                    for data in own_info['data'][x]['carousel_media']:
                        media_name = str (x) + str (own_info['data'][data]['id']) + '.jpg'
                        m_type = data['type']
                        media_url = data[m_type + 's']['standard_resolution']['url']
                        urllib.urlretrieve (media_url, media_name)
                        x += 1

                print 'media id: ' + str (own_info['data'][x]['id'])
                print 'Liked by ' + str (own_info['data'][x]['likes']['count']) + ' people.'
                print 'Total comments: ' + str (own_info['data'][x]['comments']['count'])
                return own_info['data'][x]['id']
            else:
                print 'No post by the user'
        else:
            print'Status code other than 200 received!'
    except Exception as e:
        print e
        print 'There is some error.'


# Function to get recently liked self media and sve post to database
def recent_liked_posts():
    try:
        media_link = ''
        request_url = base_url + 'users/self/media/liked?access_token=%s' % access_token
        response = requests.get(request_url).json()
        if response['meta']['code'] == 200:
            if len(response['data']) > 0:
                for index in range(len(response['data'])):
                    media_id = response['data'][index]['id']
                    m_type = response['data'][index]['type']
                    likes = response['data'][index]['likes']['count']
                    comment_count = response['data'][index]['comments']['count']
                    if m_type == 'image' or 'video':
                        media_link = response['data'][index][m_type+'s']['standard_resolution']['url']
                    elif response['type'] == 'carousel':
                        media_link = response['data'][index]['images']['standard_resolution']['url']
                    print str(index+1) + ' Media id: ' + str(media_id)
                    print str(index+1) + ' Likes: ' + str(likes)
                    print str (index + 1) + ' Comments: ' + str(comment_count)
                    print str(index+1) + ' Media caption: ' + response['data'][index]['caption']['text']
                    query = models.recent_liked_posts.select().where(models.recent_liked_posts.media_id == media_id)
                    if len(query) > 0:
                        query[0].likes = likes
                        query[0].comment_count = comment_count
                        query[0].save()
                    else:
                        post = models.recent_liked_posts(media_id=media_id, media_type=m_type, media_link=media_link,
                                                         likes=likes, comment_count=comment_count)
                        post.save()
            else:
                print'no posts'
        else:
            print 'code not 200'
    except Exception as e:
        print e
        print 'Exception in recent liked posts'


# Function to get user id by username
def get_user_id(insta_username):
    try:
        request_url = base_url + 'users/search?q=' + insta_username + '&access_token=' + access_token
        response = requests.get (request_url).json ()
        if response['meta']['code'] == 200:
            if len (response['data']) > 0:
                return response['data'][0]['id']
            else:
                print 'no user exist with ' + insta_username + ' such name'
                return None
        else:
            print 'Status code other than 200 received!'
    except Exception as e:
        print e
        print 'Exception in getting user id.'


# Function to get information of any instagram user by username
def get_user_info(insta_user):
    try:
        user_id = get_user_id (insta_user)
        if user_id is None:
            print 'User does not exist!'
            exit ()
        request_url = base_url + 'users/%s/?access_token=%s' % (user_id, access_token)
        response = requests.get (request_url).json ()
        # print 'Request url for user info: ' + request_url
        if response['meta']['code'] == 200:
            print 'Information fetched successfully'
            if len (response['data']):
                fullname = response['data']['full_name']
                follows_count = response['data']['counts']['follows']
                followed_by = response['data']['counts']['followed_by']
                print 'Username: %s' % insta_user
                print 'Fullname: %s' % fullname
                print 'No. of followers: %s' % follows_count
                print 'No. of people %s following: %s' % (insta_user, followed_by)
                print 'No. of posts: %s' % (response['data']['counts']['media'])

                query = models.user.select ().where (models.user.user_id == user_id)
                if len (query) > 0:
                    print 'update'
                    query[0].username = insta_user
                    query[0].full_name = fullname
                    query[0].follows_count = follows_count
                    query[0].followed_by_count = followed_by
                    query[0].save ()
                else:
                    new_user = models.user (user_id=user_id, user_name=insta_user, follows_count=follows_count,
                                            fullname=fullname, followed_by_count=followed_by)
                    new_user.save ()
                return response['data']['counts']['media']

            else:
                print 'There is no data for this user!'
        else:
            print 'Status code other than 200 received!'
    except Exception as e:
        print e
        print 'Exception in getting user information.'


# Function to get instagram user posts
def get_user_post(insta_username):
    try:
        user_id = get_user_id (insta_username)
        if user_id is None:
            print 'User does not exist!'
            exit ()
        media_cnt = get_user_info (insta_username)
        request_url = base_url + 'users/' + str (user_id) + '/media/recent/?access_token=' + access_token
        user_post = requests.get (request_url).json ()
        print 'request url for media: ' + request_url
        if user_post['meta']['code'] == 200:
            if len (user_post['data']) > 0:
                print 'Data  fetched'
                print 'Total posts of user are ' + str (media_cnt)
                x = input ('Which post you want to fetch? \n')
                x -= 1
                if user_post['data'][x]['type'] == 'image':
                    # download own posts
                    print user_post['data'][x]['id']
                    media_name = str (x) + str (user_post['data'][x]['id']) + '.jpg'
                    media_url = user_post['data'][x]['images']['standard_resolution']['url']
                    urllib.urlretrieve (media_url, media_name)

                elif user_post['data'][x]['type'] == 'video':
                    media_name = str (x) + str (user_post['data'][x]['id']) + '.mp4'
                    media_url = user_post['data'][x]['videos']['standard_resolution']['url']
                    urllib.urlretrieve (media_url, media_name)

                elif user_post['data'][x]['id'] == 'carousel':
                    x = 0
                    for data in user_post['data'][x]['carousel_media']:
                        media_name = str (x) + str (user_post['data'][data]['id']) + '.jpg'
                        m_type = data['type']
                        media_url = data[m_type + 's']['standard_resolution']['url']
                        urllib.urlretrieve (media_url, media_name)
                        x += 1

                print 'media id: ' + str (user_post['data'][x]['id'])
                print 'Liked by ' + str (user_post['data'][x]['likes']['count']) + ' people.'
                print 'Total comments: ' + str (user_post['data'][x]['comments']['count'])
                print 'media downloaded'
                media_type = user_post['data'][x]['type']

                query = models.media.select ().where (models.media.media_id == user_post['data'][x]['id'])
                if len (query) > 0:
                    print'update'
                    query[0].media_link = user_post['data'][x][media_type + 's']['standard_resolution']['url']
                    query[0].likes = user_post['data'][x]['likes']['count']
                    query[0].comment_count = user_post['data'][x]['comments']['count']
                    query[0].save ()
                else:
                    new_media = models.media (user_id=user_id, media_id=user_post['data'][x]['id'],
                                              media_type=media_type,
                                              media_link=user_post['data'][x][media_type + 's']['standard_resolution'][
                                                  'url'],
                                              likes=user_post['data'][x]['likes']['count'],
                                              comment_count=user_post['data'][x]['comments']['count'])
                    new_media.save ()

                return user_post['data'][x]['id']

            else:
                print 'no posts'
        else:
            print 'Status code other than 200 received!'
            print user_post['meta']['code']
    except Exception as e:
        print e
        print 'Exception in get user posts'


# Function to fetch list og post likers
def post_liker_list():
    try:
        media_id = 0
        user_id = 0
        c = input ('\n1. To get self post liker'
                   '\n2. To get user post liker'
                   '\n Enter your choice: ')
        if c == 1:
            media_id = self_media_id ()
            user_id = self_info ()
        elif c == 2:
            name = raw_input ('Enter username')
            media_id = get_user_post (name)
            user_id = get_user_info (name)
        request_url = base_url + 'media/%s/likes?access_token=%s' % (media_id, access_token)
        print request_url
        response = requests.get (request_url).json ()
        if response['meta']['code'] == 200:
            if len (response['data']) > 0:
                x = 1
                for likers in response['data']:
                    print str (x) + ' ' + likers['username']
                    x += 1
                    like = models.likers_list (user_id=user_id, media_id=media_id, liker_username=likers['username'])
                    like.save ()
            else:
                print 'no likes'
        else:
            print 'code not 200'
    except Exception as e:
        print e
        print 'Exception in post liker list'


# Function to get media id for liking or commenting any instagram user post
def get_media_id(insta_user):
    try:
        user_id = get_user_id (insta_user)
        request_url = base_url + 'users/' + str (user_id) + '/media/recent/?access_token=' + access_token
        response = requests.get (request_url).json ()
        print request_url
        if response['meta']['code'] == 200:
            for index in range (len (response['data'])):
                for data_item in response['data']:
                    media_id = data_item['id']
                    media_type = data_item['type']
                    media_link = data_item[media_type + 's']['standard_resolution']['url']
                    likes = data_item['likes']['count']
                    comment_count = data_item['comments']['count']
                    query = models.media.select ().where (models.media.media_id == media_id)
                    if len (query) > 0:
                        print'update'
                        query[0].media_link = media_link
                        query[0].likes = likes
                        query[0].comment_count = comment_count
                        query[0].save ()
                    else:
                        new_media = models.media (user_id=user_id, media_id=media_id,
                                                  media_type=media_type, media_link=media_link, likes=likes,
                                                  comment_count=comment_count)
                        new_media.save ()
                return response['data'][0]['id']
        else:
            print 'Status code other than 200 received!'
    except Exception as e:
        print e
        print 'Exception in get media id'


# Function to like a post
def like_a_post(insta_username):
    try:
        media_id = get_user_post (insta_username)
        request_url = (base_url + 'media/%s/likes') % media_id
        payload = {"access_token": access_token}
        print 'POST request url : %s' % request_url
        post_a_like = requests.post (request_url, payload).json ()
        if post_a_like['meta']['code'] == 200:
            print 'Like was successful!'
            query = models.media.select ().where (models.media.media_id == media_id)
            if len (query) > 0:
                query[0].likes += 1
                query[0].save ()
        else:
            print 'Status code other than 200 received!'
    except Exception as e:
        print e
        print 'Exception in like a post'


# Function to comment on a user post
def comment_a_post(insta_username):
    try:
        media_id = get_user_post (insta_username)
        request_url = (base_url + 'media/%s/comments') % media_id
        comment_text = raw_input ('Enter comment text: ')
        payload = {"access_token": access_token, "text": comment_text}
        print 'POST request url : %s' % request_url
        post_a_like = requests.post (request_url, payload).json ()
        if post_a_like['meta']['code'] == 200:
            print 'Comment was successful!'
            query1 = models.media.select ().where (models.media.media_id == media_id)
            query1[0].comment_count += 1
            query1[0].save ()
        else:
            print 'Status code other than 200 received!'
    except Exception as e:
        print e
        print 'Exception in comment a post'


# Function for deletion of negative comments
def delete_negative_comment(insta_username):
    try:
        user_id = get_user_id (insta_username)
        media_id = get_user_post (insta_username)
        request_url = (base_url + 'media/%s/comments/?access_token=%s') % (media_id, access_token)
        print 'GET request url : %s' % request_url
        comment_info = requests.get (request_url).json ()
        if comment_info['meta']['code'] == 200:
            # Check if we have comments on the post
            if len (comment_info['data']) > 0:
                # And then read them one by one
                for comment in comment_info['data']:
                    comment_id = comment['id']
                    comment_text = comment['text']
                    blob = TextBlob (comment_text, analyzer=NaiveBayesAnalyzer ())
                    print blob.sentiment
                    print blob.sentiment.classification
                    comment = models.comments (user_id=user_id, media_id=media_id, comment_id=comment_id,
                                               comment_text=comment_text)
                    comment.save ()
                    if blob.sentiment.p_neg > blob.sentiment.p_pos:
                        comment_id = comment['id']
                        delete_url = (base_url + 'media/%s/comments/%s/?access_token=%s') % (
                            media_id, comment_id, access_token)
                        print 'DELETE request url : %s' % delete_url

                        delete_info = requests.delete (delete_url).json ()

                        if delete_info['meta']['code'] == 200:
                            print 'Comment successfully deleted!'
                        else:
                            print 'Could not delete the comment'

            else:
                print 'No comments found'
        else:
            print 'Status code other than 200 received!'
    except Exception as e:
        print e
        print 'Exception in comment deletion'


# to check tags on a media using media id  and add tag to dictionary as a key
# if tag already exists its value is incremented by one
def calculate_frequency(trends, m_id):
    try:
        request_url = base_url + 'media/%s?access_token=%s' % (m_id, access_token)
        response = requests.get(request_url).json()
        if response['meta']['code'] == 200:
            # check tags on a post
            for tag_name in response['data']['tags']:
                if tag_name in trends:
                    # incrementing value of tag name key in trends
                    trends[tag_name] += 1
                else:
                    # adding tag name as a key to trends dictionary
                    trends[tag_name] = 1
        else:
            print 'code other than 200'
    except Exception as e:
        print e
        print 'Exception in calculate frequency'


# Function to get posts of a user with tags to analyse trendy posts
def trendy_posts():
    try:
        tag_name = raw_input('Enter main tag name: ')
        request_url = base_url + 'tags/%s/media/recent?access_token=%s' % (tag_name, access_token)
        print request_url
        response = requests.get(request_url).json()
        if response['meta']['code'] == 200:
            if len(response['data']) > 0:
                trends = {}
                for tag in response['data']:
                    post_id = tag['id']
                    calculate_frequency(trends, post_id)
                if tag_name in trends:
                    # pop main tag from dictionary trends
                    trends.pop(tag_name, None)
                if len(trends) > 0:
                    # displaying bar graph for sub_tags to check trends
                    plt.bar(range(len(trends)), trends.values())
                    plt.xticks(range(len(trends)), trends.keys())
                    plt.show()
                else:
                    print 'nothing to plot'
            else:
                print'no posts'
        else:
            print'code not 200'
    except Exception as e:
        print e
        print ' Exception in visualization of user tags'


# Function to analyse user posts to check their interest
def analyse_user_interest(insta_user):
    try:
        user_id = get_user_id(insta_user)
        request_url = base_url + 'users/%s/media/recent/?access_token=%s' % (user_id, access_token)
        print request_url
        response = requests.get(request_url).json()
        if response['meta']['code'] == 200:
            interests = {}
            for media_post in response['data']:
                for tag_name in media_post['tags']:
                    # incrementing value of tag name key in interests
                    if tag_name in interests:
                        interests[tag_name] += 1
                    else:
                        # adding tag name as a key to interests dictionary
                        interests[tag_name] = 1
            if len(interests) > 0:
                wordcloud = WordCloud().generate_from_frequencies(interests)
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.show()
        else:
            print 'code not 200'
    except Exception as e:
        print e
        print 'Exception in analyse user interest'


# Function to start the bot for the selection of different functionality available
def start_bot():
    flag = True
    try:
        while flag:
            choice = input ('What do you want to do?'
                            '\n1. Get self information'
                            '\n2. Get your own recent posts'
                            '\n3. Get media details for all posts of a user and store in database'
                            '\n4. Get user recent post'
                            '\n5. Like a post'
                            '\n6. Negative comment deletion'
                            '\n7. Get user details'
                            '\n8. Comment on post'
                            '\n9. Get own comments'
                            '\n10. Self media id'
                            '\n11. Self recently liked posts'
                            '\n12. Self negative comment deletion'
                            '\n13. List of people liked self post'
                            '\n14. Get posts by tags and visualize likings'
                            '\n15. Determine user interest'
                            '\n16. Exit'
                            '\n Your choice please: ')
            if choice == 1:
                # Display self information
                self_info ()
            elif choice == 2:
                # help in own post selection
                get_own_post ()
            elif choice == 3:
                # get media details for all posts by a user and store data in database
                name = raw_input ('Enter user name: ')
                get_media_id (name)
            elif choice == 4:
                # get selected user post
                name = raw_input ('Enter user name: ')
                get_user_post (name)
            elif choice == 5:
                # liking a post
                name = raw_input ('Enter user name: ')
                like_a_post (name)
            elif choice == 6:
                # deletion of negative comments of a user
                name = raw_input ('Enter user name: ')
                delete_negative_comment (name)
            elif choice == 7:
                # getting user information
                name = raw_input ('Enter user name: ')
                get_user_info (name)
            elif choice == 8:
                # commenting a user post
                name = raw_input ('Enter user name: ')
                comment_a_post (name)
            elif choice == 9:
                # getting comments of your own posts
                own_comments ()
            elif choice == 10:
                # getting media id of your own posts
                self_media_id ()
            elif choice == 11:
                # getting own recently liked posts
                recent_liked_posts()
            elif choice == 12:
                # deletion of negative comments over self posts
                self_comment_delete ()
            elif choice == 13:
                # fetching list of people like post
                post_liker_list ()
            elif choice == 14:
                # posts by tags
                trendy_posts()
            elif choice == 15:
                # analyse user interest
                name = raw_input ('Enter user name: ')
                analyse_user_interest(name)
            elif choice == 16:
                # Exit
                flag = False
            else:
                print 'Invalid choice'
    except Exception as e:
        print e
        print 'Exception in start bot'


start_bot ()
