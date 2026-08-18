from django.urls import path

from . import views


# URL patterns ของ movies app
# แต่ละ path จะเชื่อม URL ที่ผู้ใช้เปิดกับ view function ที่ต้องทำงาน
urlpatterns = [
    # หน้าแรกของเว็บไซต์ใช้ movie_list view
    # name="movie_list" ใช้อ้างถึง URL นี้จาก template หรือ Django code ภายหลัง
    path("", views.movie_list, name="movie_list"),

    # หน้าเพิ่ม Movie ใหม่
    path("movies/add/", views.movie_add, name="movie_add"),
]