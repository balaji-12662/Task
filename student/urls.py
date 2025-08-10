from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("students/", views.list_students, name="get_method"),
    path("students/add/", views.add_student, name="post_method"),
    path("students/update-marks/", views.update_marks, name="update_marks"),
    path("students/delete/", views.delete_student, name="delete_student"),
]
