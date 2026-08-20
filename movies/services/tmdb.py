import requests
from django.conf import settings


class TMDBServiceError(Exception):
    """
    Exception ของ application สำหรับกรณีที่การเรียก TMDB API ไม่สำเร็จ

    View สามารถจัดการ TMDBServiceError ได้โดยไม่ต้องรู้รายละเอียด
    ของ requests library หรือ external API error ภายใน
    """

    pass


def _tmdb_get(path, params=None):
    """
    Helper function สำหรับส่ง GET request ไปยัง TMDB API

    รวม authentication, timeout และ error handling ไว้ที่เดียว
    เพื่อไม่ให้ View แต่ละตัวต้องเขียน logic เหล่านี้ซ้ำ
    """

    # ตรวจว่ามี API Read Access Token ก่อนเรียก TMDB
    # ไม่แสดงค่าของ token ใน error message เพื่อป้องกัน secret รั่ว
    if not settings.TMDB_API_TOKEN:
        raise TMDBServiceError(
            "TMDB API token is not configured."
        )

    # API Read Access Token ถูกส่งจาก Django backend
    # ไปยัง TMDB ผ่าน Authorization header
    # Token นี้จะไม่ถูกส่งไปยัง HTML template หรือ browser
    headers = {
        "Authorization": f"Bearer {settings.TMDB_API_TOKEN}",
        "accept": "application/json",
    }

    try:
        # requests ใช้ params สำหรับสร้าง query string
        # แทนการนำ user input มาต่อเข้ากับ URL โดยตรง
        response = requests.get(
            f"{settings.TMDB_API_BASE_URL}{path}",
            headers=headers,
            params=params,
            timeout=10,
        )

        # ถ้า TMDB ตอบกลับด้วย HTTP error เช่น
        # 401, 404, 429 หรือ 5xx จะ raise exception
        response.raise_for_status()

        # แปลง JSON response เป็น Python dictionary
        return response.json()

    except (requests.RequestException, ValueError) as exc:
        # ไม่ส่งรายละเอียดของ request, header หรือ token กลับไปยัง browser โดยตรง
        # from exc เก็บ original exception ไว้สำหรับ debugging
        # แต่ข้อความที่ application ใช้จะเป็นข้อความทั่วไป
        raise TMDBServiceError(
            "Unable to retrieve data from TMDB right now."
        ) from exc


def search_movies(query):
    """
    ค้น Movie จาก TMDB ด้วยชื่อที่ผู้ใช้กรอก
    """

    data = _tmdb_get(
        "/search/movie",
        params={
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": 1,
        },
    )

    # TMDB ส่งรายการ Movie กลับมาใน key ชื่อ results
    # ถ้าไม่มี key นี้ ให้คืน list ว่างแทน
    return data.get("results", [])


def get_movie_details(tmdb_id):
    """
    ดึงรายละเอียด Movie หนึ่งเรื่องจาก TMDB ด้วย TMDB ID

    function นี้จะถูกใช้ตอน Add to Watchlist
    เพื่อให้ Django ดึงข้อมูลจริงจาก TMDB server-side อีกครั้ง
    แทนการเชื่อข้อมูล Movie ที่ส่งมาจาก browser
    """

    return _tmdb_get(
        f"/movie/{tmdb_id}",
        params={
            "language": "en-US",
        },
    )


def get_movie_genres():
    """
    ดึงรายการ Genre สำหรับ Movie จาก TMDB

    TMDB Search Movie ส่ง Genre กลับมาเป็น genre_ids
    เช่น:
        [28, 878]

    แต่หน้า Search ของเราต้องการแสดงชื่อ Genre เช่น:
        Action, Science Fiction

    function นี้จึงเรียก TMDB Genre endpoint
    แล้วสร้าง dictionary สำหรับ map Genre ID → Genre Name

    ตัวอย่างผลลัพธ์:
        {
            28: "Action",
            878: "Science Fiction",
        }

    การใช้ Genre endpoint แยกดีกว่าการเรียก Movie Details
    เพิ่มอีกหนึ่งครั้งสำหรับ Movie ทุกเรื่องใน Search Results
    """

    data = _tmdb_get(
        "/genre/movie/list",
        params={
            "language": "en-US",
        },
    )

    # TMDB ส่ง genres มาเป็น list ของ dictionaries
    # ตัวอย่าง: [{"id": 28, "name": "Action"}, ...]
    # เราเปลี่ยนเป็น dictionary ที่ค้นหาด้วย ID ได้ง่ายกว่า
    return {
        genre["id"]: genre["name"]
        for genre in data.get("genres", [])
        if genre.get("id") and genre.get("name")
    }