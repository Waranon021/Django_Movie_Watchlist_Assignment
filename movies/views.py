from django.shortcuts import get_object_or_404, redirect, render

from .forms import MovieForm
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


def movie_add(request):
    """
    เพิ่ม Movie ใหม่ลงใน Watchlist

    GET:
        แสดง form เปล่าให้ผู้ใช้กรอก

    POST:
        รับข้อมูลจาก form ตรวจ validation
        แล้วบันทึก Movie ลง PostgreSQL
    """

    # ตรวจ HTTP method ที่ browser ส่งเข้ามา
    if request.method == "POST":
        # request.POST คือข้อมูลที่ผู้ใช้ submit มาจาก HTML form
        form = MovieForm(request.POST)

        # ตรวจ validation ตาม Movie model และ MovieForm
        # เช่น title ต้องมีค่า และ personal_rating ต้องอยู่ระหว่าง 1–5
        if form.is_valid():
            # ModelForm.save() สร้าง Movie object
            # และบันทึกลง PostgreSQL ผ่าน Django ORM
            form.save()

            # หลังบันทึกสำเร็จ กลับไปหน้า Home
            # ใช้ชื่อ URL แทนการ hard-code "/"
            return redirect("movie_list")

    else:
        # GET request ยังไม่มีข้อมูลจากผู้ใช้
        # จึงสร้าง form เปล่าสำหรับแสดงในหน้า Add Movie
        form = MovieForm()

    # ถ้าเป็น GET หรือ POST ที่ validation ไม่ผ่าน
    # ให้ render form อีกครั้ง
    context = {
        "form": form,
    }

    return render(request, "movies/movie_form.html", context)


def movie_edit(request, movie_id):
    """
    แก้ไข Movie ที่มีอยู่แล้วใน Watchlist

    GET:
        โหลดข้อมูล Movie เดิมมาแสดงใน form

    POST:
        รับข้อมูลที่แก้ไข ตรวจ validation
        แล้ว update Movie object เดิมใน PostgreSQL
    """

    # ค้นหา Movie จาก primary key (id)
    # ถ้าไม่พบ Django จะตอบกลับด้วย HTTP 404 แทนการเกิด server error
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.method == "POST":
        # ผูกข้อมูลจาก POST เข้ากับ Movie object เดิม
        # instance=movie คือจุดที่ทำให้ form.save()
        # แก้ไข row เดิมแทนการสร้าง Movie ใหม่
        form = MovieForm(request.POST, instance=movie)

        if form.is_valid():
            form.save()

            # เมื่อแก้ไขสำเร็จ กลับไปหน้า Movie Watchlist
            return redirect("movie_list")

    else:
        # GET request ใช้ Movie object เดิมเป็น instance
        # Django จึงเติมข้อมูลปัจจุบันลงใน form ให้อัตโนมัติ
        form = MovieForm(instance=movie)

    context = {
        "form": form,
        "movie": movie,
    }

    return render(request, "movies/movie_form.html", context)


def movie_delete(request, movie_id):
    """
    ลบ Movie ออกจาก Watchlist

    GET:
        แสดงหน้า confirmation ก่อนลบ

    POST:
        ลบ Movie object ออกจาก PostgreSQL
        แล้วกลับไปหน้า Movie Watchlist
    """

    # ค้นหา Movie จาก primary key
    # ถ้าไม่มี Movie id นี้ Django จะตอบกลับด้วย HTTP 404
    movie = get_object_or_404(Movie, pk=movie_id)

    # การลบข้อมูลจริงจะเกิดเฉพาะ POST request
    # เพื่อไม่ให้การเปิด URL ธรรมดาทำให้ข้อมูลถูกลบทันที
    if request.method == "POST":
        # delete() ลบ Movie object นี้ออกจาก database ผ่าน Django ORM
        movie.delete()

        # หลังลบสำเร็จ กลับไปหน้า Home
        return redirect("movie_list")

    # GET request จะแสดงหน้า confirmation ก่อน
    context = {
        "movie": movie,
    }

    return render(request, "movies/movie_confirm_delete.html", context)