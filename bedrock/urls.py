from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard_ca'),
    path('members/', views.members, name='members'),
    path('members/delete/<int:mem_id>', views.member_delete,
         name='member_delete'),
    path('members/verify/<int:mem_id>', views.member_verify,
         name='member_verify'),
    path('tasks/', views.tasks_create, name='tasks_create'),
    path('tasks/delete/<int:task_id>', views.task_del, name='task_del'),
    path('tasks/active/<int:task_id>', views.task_active, name='tog_active'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('score/<int:mem_id>', views.score_update, name='score_update'),
    path('submit_task/<int:task_id>', views.submit_task, name='submit_task'),
    path('submissions/', views.submissions, name='submissions'),
    path('submissions/<int:submission_id>', views.verify_submission,
         name='verify_submission'),
    path('instructions', views.instructions, name='instructions'),
    path('capoints', views.capoints, name='capoints'),
]
