from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MovieForm
from .models import Movie


def movie_list(request):
    """
    แสดง Movie ในหน้า Home โดยรองรับการค้นหาจากชื่อหนัง

    ถ้ามี query จากช่อง Search:
        filter Movie ตาม title ก่อน

    จากนั้นแยกผลลัพธ์เป็น:
        - Plan to Watch
        - Watched

    แต่ละกลุ่มยังเรียง newest first ตาม date_added
    """

    # รับคำค้นจาก URL query parameter ชื่อ q
    # ตัวอย่าง URL: /?q=batman
    # ถ้าไม่มี q จะใช้ string ว่างแทน
    query = request.GET.get("q", "").strip()

    # เริ่มจาก QuerySet ของ Movie ทั้งหมด
    # จากนั้นค่อยเพิ่ม filter ตามสิ่งที่ผู้ใช้ค้นหา
    movies = Movie.objects.all()

    # ถ้ามีคำค้นจริง จึง filter ตาม title
    # __icontains หมายถึงค้นหาข้อความที่มีคำนี้อยู่
    # โดยไม่สนตัวพิมพ์เล็กหรือใหญ่
    if query:
        movies = movies.filter(title__icontains=query)

    # แยก Movie ที่ยังไม่ได้ดูออกเป็น PLAN TO WATCH
    # และยังคงเรียงจากรายการที่เพิ่มล่าสุดก่อน
    plan_to_watch_movies = movies.filter(
        watched=False
    ).order_by("-date_added")

    # แยก Movie ที่ดูแล้วออกเป็น WATCHED
    # และยังคงเรียง newest first เช่นเดียวกัน
    watched_movies = movies.filter(
        watched=True
    ).order_by("-date_added")

    # ส่งทั้ง QuerySet และคำค้นปัจจุบันไปยัง template
    # query ใช้แสดงค่าที่ผู้ใช้ค้นหาไว้ในช่อง Search
    context = {
        "plan_to_watch_movies": plan_to_watch_movies,
        "watched_movies": watched_movies,
        "query": query,
    }

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


# Django มี decorator นี้โดยตรงสำหรับ view ที่ควรรับเฉพาะ POST.
# นี่เหมาะกับการเปลี่ยนสถานะ เพราะ GET ควรใช้สำหรับอ่าน/เปิดหน้า ไม่ใช่ trigger การเปลี่ยนข้อมูล ส่วน POST เป็น unsafe method ที่สามารถป้องกันด้วย CSRF ได้
@require_POST
def movie_toggle_watched(request, movie_id):
    """
    สลับสถานะ watched ของ Movie

    False → True  : Plan to Watch → Watched
    True  → False : Watched → Plan to Watch

    View นี้รับเฉพาะ POST request เพราะมีการเปลี่ยนข้อมูลใน database
    """

    # ค้นหา Movie จาก primary key
    # ถ้าไม่มี Movie id นี้ Django จะตอบกลับด้วย HTTP 404
    movie = get_object_or_404(Movie, pk=movie_id)

    # Boolean สามารถสลับค่าได้ด้วย not
    # False จะกลายเป็น True และ True จะกลายเป็น False
    movie.watched = not movie.watched

    # บันทึกเฉพาะ field watched ที่มีการเปลี่ยนแปลง
    # ไม่จำเป็นต้อง update field อื่นของ Movie
    movie.save(update_fields=["watched"])

    # เมื่อเปลี่ยนสถานะสำเร็จ กลับไปหน้า Movie Watchlist
    return redirect("movie_list")