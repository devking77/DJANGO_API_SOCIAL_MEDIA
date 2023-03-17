from django.urls import path
from api.views import *

urlpatterns = [
    path('api/authenticate/', authenticate_user),
    path('api/follow/<int:user_id>/', follow_user),
    path('api/unfollow/<int:user_id>/', unfollow_user),
    path('api/user/', get_user_profile),
    path('api/posts/', add_post),
    path('api/posts/<int:post_id>/', delete_post),
    path('api/like/<int:post_id>/', like_post),
    path('api/unlike/<int:post_id>/', unlike_post),
    path('api/comment/<int:post_id>/', add_comment),
    # path('api/posts/<int:post_id>/', get_post),
    path('api/all_posts/', get_all_posts),
]
