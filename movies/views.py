from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MovieForm
from .models import Movie
from .services.tmdb import (
    TMDBServiceError,
    get_movie_details,
    get_movie_genres,
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

    Local Search:
        ค้น Movie ที่อยู่ใน PostgreSQL ของ application แล้ว

    TMDB Search:
        ค้น Movie จาก external TMDB catalog
        ผ่าน Django backend และ TMDB service layer

    หน้า Search จะแสดง:
        - Poster
        - Title
        - Release Year
        - TMDB Rating
        - Genre
        - Overview
        - Add to Plan to Watch
        - Add to Watched
    """

    # รับคำค้นจาก query parameter ชื่อ q
    # ตัวอย่าง:
    # /movies/tmdb/search/?q=dune
    query = request.GET.get("q", "").strip()

    # ถ้ายังไม่ได้ค้น
    # Template จะได้รับ list ว่าง
    results = []

    # Genre map ใช้แปลง TMDB genre_ids
    # เป็นชื่อ Genre ที่อ่านได้
    genre_map = {}

    # เก็บข้อความ error แบบทั่วไป
    # โดยไม่เปิดเผย Token หรือ HTTP request internals
    error_message = ""


    # เรียก TMDB เฉพาะเมื่อมีคำค้นจริง
    if query:
        try:
            # Search Movie จาก TMDB
            # จำกัด 10 รายการแรกเพื่อให้หน้า Search
            # กระชับและเหมาะกับ Assignment
            results = search_movies(query)[:10]

        except TMDBServiceError as exc:
            # ถ้า Search API ใช้งานไม่ได้
            # จึงไม่สามารถสร้าง Search Results ได้
            error_message = str(exc)


        # Genre เป็นข้อมูลเสริม
        # ถ้า Movie Search สำเร็จแต่ Genre endpoint
        # มีปัญหาชั่วคราว เราไม่ควรทำให้ Search ทั้งหน้าล้ม
        # Search Results จึงยังแสดงได้
        # เพียงแต่ไม่มี Genre
        if results:
            try:
                genre_map = get_movie_genres()

            except TMDBServiceError:
                genre_map = {}


    # ดึง TMDB IDs ของ Movie
    # ที่ถูก import เข้า PostgreSQL แล้ว
    # set เหมาะกับการเช็ก membership ด้วย "in"
    existing_tmdb_ids = set(
        Movie.objects.exclude(
            tmdb_id__isnull=True
        ).values_list(
            "tmdb_id",
            flat=True,
        )
    )


    # เตรียมข้อมูลเพิ่มเติมก่อนส่งไปยัง Template
    for result in results:

        # TMDB ส่ง release_date เช่น:
        # 2021-09-15
        # UI ต้องการแสดงเพียง:
        # 2021
        release_date = result.get("release_date") or ""

        if len(release_date) >= 4:
            result["release_year"] = release_date[:4]
        else:
            result["release_year"] = ""


        # ตรวจว่า Movie เรื่องนี้
        # อยู่ใน Local Watchlist แล้วหรือยัง
        result["already_added"] = (
            result.get("id") in existing_tmdb_ids
        )


        # TMDB Search ส่ง poster_path เช่น:
        # /abc123.jpg
        # browser ต้องการ URL เต็มจึงจะแสดงภาพได้
        poster_path = result.get("poster_path") or ""

        if poster_path:
            result["poster_url"] = (
                "https://image.tmdb.org/t/p/w500"
                f"{poster_path}"
            )
        else:
            # ถ้า TMDB ไม่มี poster
            # Template จะแสดง No Poster placeholder
            result["poster_url"] = ""


        # Search Movie ส่ง Genre เป็น ID
        # ตัวอย่าง:
        # genre_ids = [28, 878]
        # ใช้ genre_map ที่ได้จาก /genre/movie/list
        # เพื่อแปลงเป็น:
        # ["Action", "Science Fiction"]
        genre_names = [
            genre_map[genre_id]
            for genre_id in result.get("genre_ids", [])
            if genre_id in genre_map
        ]

        # รวม Genre สำหรับแสดงบน Card
        # result["genre_text"] เป็นข้อมูล presentation
        # ไม่ได้แก้ข้อมูลต้นฉบับของ TMDB
        result["genre_text"] = ", ".join(genre_names)


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

    Browser ส่งข้อมูลหลักกลับมาเพียง:
        - TMDB ID
        - watch_status

    watch_status มีสองค่าที่ application ยอมรับ:
        plan
        watched

    Title, Genre, Release Year และ Poster
    จะไม่ถูกเชื่อจาก browser

    Django backend จะดึง Movie Details
    จาก TMDB อีกครั้งก่อนบันทึกลง PostgreSQL
    """

    # รับสถานะที่ผู้ใช้เลือกจาก TMDB Search Card
    #
    # ค่า valid มีเพียง:
    # plan     → watched=False
    # watched  → watched=True
    watch_status = request.POST.get(
        "watch_status",
        "",
    ).strip()


    # Browser เป็น user-controlled environment
    #
    # ถึง Template ของเราจะส่งเฉพาะค่าที่ถูกต้อง
    # ผู้ใช้สามารถแก้ request ด้วย DevTools ได้
    #
    # Server จึงต้อง whitelist ค่าที่ยอมรับอีกครั้ง
    if watch_status not in {"plan", "watched"}:
        return redirect("tmdb_search")


    try:
        # ไม่เชื่อข้อมูล Movie ที่ browser ส่งมา
        #
        # Django ใช้ TMDB ID
        # ไปดึงรายละเอียดจริงจาก TMDB server-side
        details = get_movie_details(tmdb_id)

    except TMDBServiceError as exc:
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


    # TMDB บาง Movie ไม่มี release_date
    release_date = details.get("release_date") or ""

    if (
        len(release_date) >= 4
        and release_date[:4].isdigit()
    ):
        release_year = int(release_date[:4])
    else:
        release_year = None


    # Movie Details ส่ง genres เป็น list เช่น:
    #
    # [
    #     {"id": 28, "name": "Action"},
    #     {"id": 878, "name": "Science Fiction"}
    # ]
    genre_names = [
        genre["name"]
        for genre in details.get("genres", [])
        if genre.get("name")
    ]


    # Movie.genre มี max_length=100
    # จึงจำกัดความยาวก่อนบันทึก
    genre_text = ", ".join(genre_names)[:100]


    # แปลง status ที่ผ่าน validation แล้ว
    # เป็น Boolean สำหรับ Movie.watched
    watched = watch_status == "watched"


    # get_or_create ป้องกันการสร้าง
    # TMDB Movie เรื่องเดียวกันซ้ำ
    #
    # Movie.tmdb_id ยังมี unique=True
    # เป็น database constraint อีกชั้นหนึ่ง
    movie, created = Movie.objects.get_or_create(
        tmdb_id=tmdb_id,
        defaults={
            "title": (
                details.get("title")
                or details.get("original_title")
                or "Untitled"
            )[:255],

            "genre": genre_text,
            "release_year": release_year,

            # Movie ใหม่ยังไม่มี Personal Rating
            #
            # ถึงผู้ใช้เลือก Add to Watched
            # ก็ยังไม่บังคับให้ Rating ทันที
            #
            # สามารถให้คะแนนจาก WATCHED Card
            # หลัง redirect กลับหน้า Home
            "personal_rating": None,

            # สถานะขึ้นอยู่กับ button
            # ที่ผู้ใช้เลือกบน TMDB Search page
            "watched": watched,

            "poster_path": (
                details.get("poster_path") or ""
            ),
        },
    )


    # created:
    # True  → สร้าง Movie ใหม่
    # False → มี TMDB ID นี้อยู่แล้ว
    #
    # Search UI ป้องกัน duplicate อยู่แล้ว
    # และ database unique constraint ป้องกันอีกชั้นหนึ่ง
    #
    # จึงยังไม่จำเป็นต้องมี notification system
    # สำหรับ Assignment นี้
    return redirect("movie_list")


@require_POST
def movie_rate(request, movie_id):
    """
    ให้หรือแก้ Personal Rating ของ Movie

    Rating ทำได้เฉพาะ Movie ที่ watched=True

    หน้า Home ส่ง POST โดยตรงจาก WATCHED Movie Card
    จึงไม่จำเป็นต้องสร้าง Rating page แยก

    คะแนนที่ยอมรับ:
        1
        2
        3
        4
        5

    นอกจากนี้รองรับค่า:
        clear

    เพื่อให้ผู้ใช้สามารถลบ Personal Rating เดิมได้
    """

    # ค้น Movie จาก primary key
    # ถ้าไม่มี ID นี้ Django จะตอบ HTTP 404
    movie = get_object_or_404(
        Movie,
        pk=movie_id,
    )


    # Movie ที่ยังไม่ได้ดู
    # ไม่สามารถรับ Rating ใหม่ผ่าน endpoint นี้ได้
    #
    # ถึงมีคนแก้ HTML หรือสร้าง POST request เอง
    # backend ก็ยังตรวจ watched อีกครั้ง
    if not movie.watched:
        return redirect("movie_list")


    rating = request.POST.get(
        "rating",
        "",
    ).strip()


    # รองรับการลบ Rating เดิม
    if rating == "clear":
        movie.personal_rating = None

        movie.save(
            update_fields=["personal_rating"]
        )

        return redirect("movie_list")


    # Validation ฝั่ง server
    #
    # ไม่เชื่อ value จาก HTML button เพียงอย่างเดียว
    valid_ratings = {
        "1",
        "2",
        "3",
        "4",
        "5",
    }

    if rating not in valid_ratings:
        return redirect("movie_list")


    # Model ใช้ PositiveSmallIntegerField
    # จึงแปลง string จาก POST เป็น int
    movie.personal_rating = int(rating)

    movie.save(
        update_fields=["personal_rating"]
    )

    return redirect("movie_list")


def about(request):
    """
    แสดงข้อมูลเกี่ยวกับ Movie Watchlist project

    หน้า About เป็น static informational page
    จึงไม่มี database modification

    หน้านี้จะรวม:
        - Project overview
        - Features
        - Technology stack
        - TMDB attribution
        - AI Disclosure
    """

    return render(
        request,
        "movies/about.html",
    )


def contact(request):
    """
    แสดงช่องทางการติดต่อและ GitHub repository

    หน้า Contact ไม่มี Form
    และไม่มีการเขียนข้อมูลลง PostgreSQL
    """

    return render(
        request,
        "movies/contact.html",
    )