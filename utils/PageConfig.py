from utils.Settings import *

class PageConfig:
    def __init__(self, title):
        self.page_config = {}

        self.page_config['page_logo'] = page_logo
        self.page_config['page_favicon'] = page_favicon

        self.page_config['page_footer'] = page_footer
        self.page_config['kakao_url'] = kakao_url
        self.page_config['facebook_url'] = facebook_url
        self.page_config['twitter_url'] = twitter_url
        self.page_config['insta_url'] = insta_url
        self.page_config['page_sns_kakao'] = page_sns_kakao
        self.page_config['page_sns_facebook'] = page_sns_facebook
        self.page_config['page_sns_twitter'] = page_sns_twitter
        self.page_config['page_sns_insta'] = page_sns_insta

        # common configurations
        self.page_config['comm_page_title'] = page_name + " - " + title
        self.page_config['comm_user_signin'] = False
        self.page_config['comm_root_signin'] = False
        self.page_config['comm_root_first'] = False
        
        # information configurations
        self.page_config['info_db_connection'] = False
        self.page_config['info_root_exist'] = False

        # data configuration
        self.page_config['data_images'] = []
        self.page_config['data_image'] = None
        self.page_config['data_page_length'] = 0
        self.page_config['data_page_last_query'] = 0


        self.page_config['message'] = ""

    def get(self, key):
        return self.page_config.get(key)
    
    def set(self, **kwargs):
        for key in kwargs:
            self.page_config[key] = kwargs[key]