from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Client, Project
from .serializers import ClientSerializer, ClientDetailSerializer, ProjectSerializer
from django.contrib.auth.models import User

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClientDetailSerializer
        return ClientSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def projects(self, request, pk=None):
        client = get_object_or_404(Client, pk=pk)
        project_name = request.data.get('project_name')
        user_ids = [u['id'] for u in request.data.get('users', [])]
        users = User.objects.filter(id__in=user_ids)
        project = Project.objects.create(
            project_name=project_name,
            client=client,
            created_by=request.user
        )
        project.users.set(users)
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(users=self.request.user)

