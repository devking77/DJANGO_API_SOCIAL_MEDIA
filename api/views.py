from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import datetime

from .models import Post, Comment, Like


class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return JsonResponse({
            'token': response.data['access']
        })


@csrf_exempt
@api_view(['POST'])
def authenticate_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)

    if user is not None:
        login(request, user)
        return Response({
            'token': str(user.auth_token),
        })
    else:
        return Response({
            'error': 'Invalid credentials',
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, id):
    user_to_follow = User.objects.get(id=id)
    request.user.profile.following.add(user_to_follow)
    return Response({
        'message': 'You are now following {}!'.format(user_to_follow.username),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, id):
    user_to_unfollow = User.objects.get(id=id)
    request.user.profile.following.remove(user_to_unfollow)
    return Response({
        'message': 'You have unfollowed {}.'.format(user_to_unfollow.username),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    followers_count = user.profile.followers.count()
    following_count = user.profile.following.count()
    return Response({
        'username': user.username,
        'followers': followers_count,
        'following': following_count,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_post(request):
    title = request.data.get('title')
    description = request.data.get('description')
    post = Post.objects.create(
        title=title,
        description=description,
        created_by=request.user,
        created_at=datetime.utcnow(),
    )
    return Response({
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'created_at': post.created_at,
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, id):
    try:
        post = Post.objects.get(id=id, created_by=request.user)
        post.delete()
        return Response({
            'message': 'Post has been deleted successfully.',
        })
    except Post.DoesNotExist:
        return Response({
            'error': 'Post not found or you are not the owner of this post.',
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, id):
    try:
        post = Post.objects.get(id=id)
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if created:
            return Response({
                'message': 'You have liked this post.',
            })
        else:
            return Response({
                'message': 'You have already liked this post.',
            })
    except Post.DoesNotExist:
        return Response({
            'error': 'Post not found.',
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlike_post(request, id):
    try:
        post = Post.objects.get(id=id)
        like = Like.objects.get(post=post, user=request.user)
        like.delete()
        return Response({
        'message': 'You have unliked this post.',
        })
    except (Post.DoesNotExist, Like.DoesNotExist):
        return Response({
        'error': 'Post not found or you have not liked this post yet.',
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, id):
    comment_text = request.data.get('comment')
    try:
        post = Post.objects.get(id=id)
        comment = Comment.objects.create(
        post=post,
        user=request.user,
        comment=comment_text,
        created_at=datetime.utcnow(),
        )
        return Response({
        'id': comment.id,
        })
    except Post.DoesNotExist:
        return Response({
        'error': 'Post not found.',
         })
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_posts(request):
    posts = Post.objects.filter(created_by=request.user).order_by('-created_at')
    result = []
    for post in posts:
        likes_count = post.likes.count()
        comments = Comment.objects.filter(post=post).values('id', 'comment', 'user__username')
        result.append({
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'created_at': post.created_at,
        'likes': likes_count,
        'comments': comments,
        })
    return Response(result)        