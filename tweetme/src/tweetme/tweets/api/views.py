from django.contrib.auth.models import User
from .serializers import TweetModelSerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from tweets.models import Tweet
from django.db.models import Q
from rest_framework import permissions
from .pagination import StandardResultPagination
from rest_framework.views import APIView
from rest_framework.response import Response


class RetweetApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        tweet_qs = Tweet.objects.filter(pk=pk)
        message = "Not allowed"
        if tweet_qs.exists() and tweet_qs.count() == 1:
            # if request.user.is_authenticated:
            new_tweet = Tweet.objects.retweet(
                request.user, tweet_qs.first())
            if new_tweet is not None:
                data = TweetModelSerializer(new_tweet).data
                return Response(data)
            message = "Cannot retweet the same tweet is one day"
        return Response({'message': message}, status=400)


class LikeToggleApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        tweet_qs = Tweet.objects.filter(pk=pk)
        message = "Not allowed"
        if request.user.is_authenticated:
            is_liked = Tweet.objects.like_toggle(
                request.user, tweet_qs.first())
            return Response({'liked': is_liked})
        return Response({'message': message}, status=400)


class TweetCreateApiView(generics.CreateAPIView):
    serializer_class = TweetModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TweetListApiView(generics.ListAPIView):
    serializer_class = TweetModelSerializer
    pagination_class = StandardResultPagination

    def get_serializer_context(self, *args, **kwargs):
        context = super(TweetListApiView, self).get_serializer_context(
            *args, **kwargs)
        context['request'] = self.request
        return context

    def get_queryset(self):
        requested_user = self.kwargs.get('username')
        if requested_user:
            queryset = Tweet.objects.filter(
                user__username=requested_user).order_by("-timestamp")
        else:
            im_following = self.request.user.profile.get_following()
            qs1 = Tweet.objects.filter(
                user__in=im_following)
            qs2 = Tweet.objects.filter(
                user=self.request.user)
            queryset = (qs1 | qs2).distinct().order_by("-timestamp")

        query = self.request.GET.get("q", None)
        if query is not None:
            queryset = queryset.filter(
                Q(content__icontains=query) | Q(
                    user__username__icontains=query)
            )
        return queryset
