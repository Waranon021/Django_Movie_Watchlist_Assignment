from django.shortcuts import render

from .models import Movie


def movie_list(request):
    """
    แสดง Movie ทั้งหมดในหน้า Home
    โดยเรียงจากรายการที่ถูกเพิ่มล่าสุดไปหารายการเก่าที่สุด
    """

    # Django ORM อ่านข้อมูลจากตาราง movies_movie ใน PostgreSQL
    # เครื่องหมาย "-" หน้า date_added หมายถึงเรียงแบบ descending
    # จึงได้ Movie ที่เพิ่มล่าสุดอยู่ก่อน
    movies = Movie.objects.order_by("-date_added")

    # ส่งข้อมูล Movie ไปยัง template ผ่าน context dictionary
    # key "movies" จะกลายเป็นตัวแปรชื่อ movies ที่ใช้ใน HTML template
    context = {
        "movies": movies,
    }

    # render() รวม template + context แล้วคืน HTTP response ให้ browser
    return render(request, "movies/movie_list.html", context)