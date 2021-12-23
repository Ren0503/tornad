from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Write, Vote
from .serializers import WriteSerializer

# Create your views here.


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def writes(request):
    query = request.query_params.get('q')
    if query == None:
        query = ''

    user = request.user
    following = user.following.select_related('user')

    following = user.following.all()

    ids = []
    ids = [i.user.id for i in following]
    ids.append(user.id)
    print('IDS:', ids)

    # Make sure parent==None is always on
    # Query 5 writes form users you follow | TOP PRIORITY

    writes = list(Write.objects.filter(
        parent=None, user__id__in=ids).order_by("-created"))[0:5]
    #writes = list(writes.filter(Q(user__userprofile__name__icontains=query) | Q(content__icontains=query)))

    recentWrites = Write.objects.filter(Q(parent=None) & Q(
        vote_rank__gte=0) & Q(rewrite=None)).order_by("-created")[0:5]

    # Query top ranked writes and attach to end of original queryset
    topWrites = Write.objects.filter(
        Q(parent=None)).order_by("-vote_rank", "-created")

    # Add top ranked writes to feed after prioritizing follow list
    index = 0
    for write in recentWrites:
        if write not in writes:
            writes.insert(index, write)
            index += 1

    # Add top ranked writes to feed after prioritizing follow list
    for write in topWrites:
        if write not in writes:
            writes.append(write)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(writes, request)
    serializer = WriteSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def write_details(request, pk):
    try:
        write = Write.objects.get(id=pk)
        serializer = WriteSerializer(write, many=False)
        return Response(serializer.data)
    except:
        message = {
            'detail': 'Write doesn\'t exist'
        }
        return Response(message, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def create_write(request):
    user = request.user
    data = request.data

    is_comment = data.get('isComment')
    if is_comment:
        parent = Write.objects.get(id=data['postId'])
        write = Write.objects.create(
            parent=parent,
            user=user,
            content=data['content'],
        )
    else:
        write = Write.objects.create(
            user=user,
            content=data['content']
        )

    serializer = WriteSerializer(write, many=False)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes((IsAuthenticated,))
def edit_write(request, pk):
    user = request.user
    data = request.data

    try:
        write = Write.objects.get(id=pk)
        if user != write.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = WriteSerializer(write, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    except Exception as e:
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def delete_write(request, pk):
    user = request.user
    try:
        write = Write.objects.get(id=pk)
        if user != write.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            write.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'details': f"{e}"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def write_comments(request, pk):
    write = Write.objects.get(id=pk)
    comments = write.write_set.all()
    serializer = WriteSerializer(comments, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def rewrite(request):
    user = request.user
    data = request.data
    original_write = Write.objects.get(id=data['id'])
    if original_write.user == user:
        return Response({'detail': 'You can not rewrite your own write.'}, status=status.HTTP_403_FORBIDDEN)
    try:
        write = Write.objects.filter(
            rewrite=original_write,
            user=user,
        )
        if write.exists():
            return Response({'detail': 'Already Wrote'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            write = Write.objects.create(
                rewrite=original_write,
                user=user,
            )
        serializer = WriteSerializer(write, many=False)
        return Response(serializer.data)
    except Exception as e:
        return Response({'detail': f'{e}'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def update_vote(request):
    user = request.user
    data = request.data

    write = Write.objects.get(id=data['post_id'])
    # What if user is trying to remove their vote?
    vote, created = Vote.objects.get_or_create(write=write, user=user)

    if vote.value == data.get('value'):
        # If same value is sent, user is clicking on vote to remove it
        vote.delete()
    else:

        vote.value = data['value']
        vote.save()

    # We re-query the vote to get the latest vote rank value
    write = Write.objects.get(id=data['post_id'])
    serializer = WriteSerializer(write, many=False)

    return Response(serializer.data)
