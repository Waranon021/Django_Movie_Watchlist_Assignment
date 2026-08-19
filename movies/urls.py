from django.urls import path

from . import views


# URL patterns ของ movies app
# แต่ละ path จะเชื่อม URL ที่ผู้ใช้เปิดกับ view function ที่ต้องทำงาน

urlpatterns = [
    # หน้า Home แสดง Movie ทั้งหมด
    path("", views.movie_list, name="movie_list"),

    # หน้าเพิ่ม Movie ใหม่
    path("movies/add/", views.movie_add, name="movie_add"),

    # หน้าแก้ไข Movie
    # <int:movie_id> รับตัวเลขจาก URL แล้วส่งให้ movie_edit view
    path(
        "movies/<int:movie_id>/edit/",
        views.movie_edit,
        name="movie_edit",
    ),

    # หน้า confirmation สำหรับลบ Movie
    # movie_id ระบุ Movie object ที่ผู้ใช้ต้องการลบ
    path(
        "movies/<int:movie_id>/delete/",
        views.movie_delete,
        name="movie_delete",
    ),
]