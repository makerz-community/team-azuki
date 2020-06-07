from allauth.socialaccount.providers.oauth.views import OAuthLoginView
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter


class TwitterOAuthAdapterWithApplication(TwitterOAuthAdapter):
    print("new adapter is called")
    """
    ここに参加処理を実装する
    """
    pass

# class TwitterOAuthAdapter(OAuthAdapter):
#     provider_id = TwitterProvider.id
#     request_token_url = 'https://api.twitter.com/oauth/request_token'
#     access_token_url = 'https://api.twitter.com/oauth/access_token'
#     # Issue #42 -- this one authenticates over and over again...
#     # authorize_url = 'https://api.twitter.com/oauth/authorize'
#     authorize_url = 'https://api.twitter.com/oauth/authenticate'
#
#     def complete_login(self, request, app, token, response):
#         client = TwitterAPI(request, app.client_id, app.secret,
#                             self.request_token_url)
#         extra_data = client.get_user_info()
#         return self.get_provider().sociallogin_from_response(request,
#                                                              extra_data)


oauth_login = OAuthLoginView.adapter_view(TwitterOAuthAdapterWithApplication)
# oauth_callback = OAuthCallbackView.adapter_view(TwitterOAuthAdapter)
