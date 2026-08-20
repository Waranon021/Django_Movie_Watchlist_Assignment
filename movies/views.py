from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MovieForm
from .models import Movie
from .services.tmdb import (
    TMDBServiceError,
    get_movie_details,
    search_movies,
)


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


def tmdb_search(request):
    """
    ค้น Movie จาก TMDB API

    Search นี้แยกจาก Local Watchlist Search:
    - Local Search ค้น Movie ที่อยู่ใน PostgreSQL ของเรา
    - TMDB Search ค้น Movie จาก external TMDB catalog
    """

    # รับคำค้นจาก query parameter ชื่อ q
    # ตัวอย่าง URL:
    # /movies/tmdb/search/?q=dune
    query = request.GET.get("q", "").strip()

    # ค่าเริ่มต้นเป็น list ว่าง
    # ถ้ายังไม่ได้ Search หน้า template จะยังไม่มี results
    results = []

    # เก็บข้อความ error แบบทั่วไป
    # ไม่ส่งรายละเอียด request หรือ API token ไปยัง browser
    error_message = ""

    # เรียก TMDB เฉพาะเมื่อผู้ใช้กรอกคำค้นจริง
    if query:
        try:
            # ใช้ service layer ที่สร้างไว้ใน 9.6
            #
            # จำกัด 10 รายการแรกเพื่อให้หน้า Search
            # ไม่ยาวเกินไปสำหรับ Assignment
            results = search_movies(query)[:10]

        except TMDBServiceError as exc:
            # Service เปลี่ยน external API errors
            # เป็นข้อความที่ปลอดภัยสำหรับ application แล้ว
            error_message = str(exc)

    # ดึงเฉพาะ TMDB IDs ของ Movie
    # ที่ถูก import เข้า Local Watchlist แล้ว
    existing_tmdb_ids = set(
        Movie.objects.exclude(
            tmdb_id__isnull=True
        ).values_list(
            "tmdb_id",
            flat=True,
        )
    )

    # เตรียมข้อมูลเพิ่มเติมสำหรับ template
    for result in results:
        # TMDB ส่ง release_date ในรูปแบบ YYYY-MM-DD
        # แต่หน้า Search ของเราต้องการแสดงเพียงปี
        release_date = result.get("release_date") or ""

        if len(release_date) >= 4:
            result["release_year"] = release_date[:4]
        else:
            result["release_year"] = ""

        # เช็กว่า TMDB Movie เรื่องนี้มีอยู่ใน Watchlist แล้วหรือยัง
        # ถ้ามีแล้ว Template จะแสดง Already in Watchlist
        result["already_added"] = (
            result.get("id") in existing_tmdb_ids
        )

    context = {
        "query": query,
        "results": results,
        "error_message": error_message,
    }

    return render(
        request,
        "movies/tmdb_search.html",
        context,
    )


@require_POST
def tmdb_add_movie(request, tmdb_id):
    """
    เพิ่ม Movie จาก TMDB ลง Local Watchlist

    Browser ส่งมาเฉพาะ TMDB ID
    จากนั้น Django backend จะดึงรายละเอียดจาก TMDB อีกครั้ง
    ก่อนบันทึกข้อมูลลง PostgreSQL
    """

    try:
        # ไม่เชื่อ title / year / genre ที่ browser ส่งกลับมา
        # Django ใช้ TMDB ID ไปขอข้อมูลจริงจาก TMDB server-side อีกครั้ง
        details = get_movie_details(tmdb_id)

    except TMDBServiceError as exc:
        # ถ้า TMDB API มีปัญหา ให้แสดง error แบบทั่วไป
        # โดยไม่เปิดเผย API token หรือ request internals
        context = {
            "query": "",
            "results": [],
            "error_message": str(exc),
        }

        return render(
            request,
            "movies/tmdb_search.html",
            context,
            status=502,
        )

    # TMDB บางรายการอาจไม่มี release_date
    release_date = details.get("release_date") or ""

    # แปลงเฉพาะ YYYY ให้เป็น integer
    # ถ้าไม่มีปีหรือข้อมูลผิดรูปแบบให้เก็บเป็น None
    if (
        len(release_date) >= 4
        and release_date[:4].isdigit()
    ):
        release_year = int(release_date[:4])
    else:
        release_year = None

    # TMDB Movie Details ส่ง genres เป็น list ของ dictionaries
    # เช่น:
    # [{"id": 18, "name": "Drama"}, ...]
    genre_names = [
        genre["name"]
        for genre in details.get("genres", [])
        if genre.get("name")
    ]

    # Movie.genre ของเรา max_length=100
    # จึงรวมชื่อ Genre แล้วจำกัดความยาวก่อนบันทึก
    genre_text = ", ".join(genre_names)[:100]

    # ค้น Movie ด้วย TMDB ID ก่อน
    # ถ้ายังไม่มีจึงสร้างใหม่
    #
    # tmdb_id มี unique=True ใน Model
    # ช่วยป้องกัน TMDB Movie เดียวกันถูกเพิ่มซ้ำ
    movie, created = Movie.objects.get_or_create(
        tmdb_id=tmdb_id,
        defaults={
            # ใช้ title จาก TMDB
            # และป้องกันข้อความยาวเกิน max_length=255
            "title": (
                details.get("title")
                or details.get("original_title")
                or "Untitled"
            )[:255],

            "genre": genre_text,
            "release_year": release_year,

            # ไม่ใช้คะแนน TMDB เป็น Personal Rating
            # เพราะ Personal Rating เป็นคะแนนของผู้ใช้เอง
            "personal_rating": None,

            # Movie ที่ import ใหม่เริ่มต้นใน PLAN TO WATCH
            "watched": False,

            # เก็บ poster path ไว้ใช้ใน Checkpoint 10
            "poster_path": details.get("poster_path") or "",
        },
    )

    # created จะเป็น:
    # True  = เพิ่งสร้าง Movie ใหม่
    # False = Movie นี้มีอยู่แล้ว
    #
    # ตอนนี้ยังไม่ต้องใช้ตัวแปรนี้แสดง notification
    # แต่เก็บไว้เพื่อให้เห็น behavior ของ get_or_create()

    return redirect("movie_list")