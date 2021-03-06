from rest_framework import status, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.permissions import IsCharityOwner, IsBenefactor
from charities.models import Task
from charities.serializers import (
    TaskSerializer, CharitySerializer, BenefactorSerializer
)
from .models import Benefactor


class BenefactorRegistration(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        benfactor_serializer = BenefactorSerializer(data=request.data,user=request.user)
        if benfactor_serializer.is_valid():
            benfactor_serializer.create(request.data)
            
            return Response({'message': 'Benfactor registered successfully!'})

        return Response({'message': benfactor_serializer.errors})


class CharityRegistration(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        charity_serializer = CharitySerializer(data=request.data,user=request.user)
        if charity_serializer.is_valid():
            charity_serializer.create(request.data)
            
            return Response({'message': 'Charuty registered successfully!'})

        return Response({'message': charity_serializer.errors})


class Tasks(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all_related_tasks_to_user(self.request.user)

    def post(self, request, *args, **kwargs):
        data = {
            **request.data,
            "charity_id": request.user.charity.id
        }
        serializer = self.serializer_class(data = data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated, ]
        else:
            self.permission_classes = [IsCharityOwner, ]

        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset):
        filter_lookups = {}
        for name, value in Task.filtering_lookups:
            param = self.request.GET.get(value)
            if param:
                filter_lookups[name] = param
        exclude_lookups = {}
        for name, value in Task.excluding_lookups:
            param = self.request.GET.get(value)
            if param:
                exclude_lookups[name] = param

        return queryset.filter(**filter_lookups).exclude(**exclude_lookups)


class TaskRequest(APIView):
    permission_classes = [IsAuthenticated,IsBenefactor]
    def get(self, request,task_id):
        task = get_object_or_404(Task,pk=task_id)
        if task.state!="P":      
            return Response(data={'detail': 'This task is not pending.'},status=404)
        else:
            benefactor = Benefactor.objects.get(user=request.user)
            Task.objects.filter(pk=task_id).update(state="W",assigned_benefactor=benefactor)
            return Response(data={'detail': 'Request sent.'},status=200)


class TaskResponse(APIView):
    permission_classes = [IsAuthenticated,IsCharityOwner]
    def post(self, request,task_id):
        data = request.data
        task = get_object_or_404(Task, pk=task_id)
        if data['response'] != "A" and data['response'] != "R":
            return Response(data={'detail': 'Required field ("A" for accepted / "R" for rejected)'},status=400)
        else:
            if task.state!="W":      
                return Response(data={'detail': 'This task is not waiting.'}, status=404)
            else:
                if data['response'] == "A":
                    Task.objects.filter(pk=task_id).update(state="A")
                    return Response(data={'detail': 'Response sent.'},status=200)
                elif data['response'] == "R":
                    Task.objects.filter(pk=task_id).update(state="P", assigned_benefactor=None)
                    return Response(data={'detail': 'Response sent.'},status=200)
                   
           


class DoneTask(APIView):
    permission_classes = [IsAuthenticated,IsCharityOwner]
    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        if task.state!="A":      
                return Response(data={'detail': 'Task is not assigned yet.'}, status=404)
        else:
            Task.objects.filter(pk=task_id).update(state="D")
            return Response(data={'detail': 'Task has been done successfully.'},status=200)

        