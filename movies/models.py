from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Movie(models.Model):
    """
    เก็บข้อมูลภาพยนตร์ที่ผู้ใช้เพิ่มเข้ามาใน Movie Watchlist

    แต่ละ object ของ Movie จะสัมพันธ์กับหนึ่ง row
    ในตาราง movies_movie ของ PostgreSQL
    """

    # ชื่อหนังเป็นข้อมูลบังคับตาม Assignment
    # CharField ต้องกำหนด max_length เพื่อระบุขนาดสูงสุดของข้อความ
    title = models.CharField(max_length=255)

    # Genre ไม่ได้ถูกระบุว่าเป็น required ใน Assignment
    # blank=True ทำให้ Django Form/Admin อนุญาตให้เว้นว่างได้
    genre = models.CharField(max_length=100, blank=True)

    # ปีที่ออกฉายเป็นเลขจำนวนเต็มบวก
    # null=True ใช้ NULL ใน database เมื่อไม่มีค่า
    # blank=True อนุญาตให้ช่องใน Form/Admin ว่างได้
    release_year = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    # Personal Rating ต้องอยู่ระหว่าง 1–5 ตาม Assignment
    # Validators ช่วยตรวจไม่ให้ข้อมูลนอกช่วงผ่าน Django validation
    # null=True และ blank=True ทำให้ผู้ใช้ยังไม่ต้องให้ rating ทันทีได้
    personal_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    # False หมายถึงยังไม่ได้ดู → แสดงใน PLAN TO WATCH
    # True หมายถึงดูแล้ว → แสดงใน WATCHED
    watched = models.BooleanField(default=False)

    # Django กำหนดวันและเวลาครั้งแรกที่สร้าง Movie object ให้อัตโนมัติ
    # field นี้จะใช้เรียงหนังแบบ newest first ในหน้า Movie Watchlist
    date_added = models.DateTimeField(auto_now_add=True)

    # TMDB ID ใช้เชื่อม Movie ใน Local Watchlist
    # กับ Movie record ของ TMDB
    #
    # null=True และ blank=True เพราะหนังที่เพิ่มด้วย Manual Add
    # ไม่จำเป็นต้องมาจาก TMDB
    #
    # unique=True ช่วยป้องกัน TMDB Movie เดียวกัน
    # ถูก import เข้ามาซ้ำด้วย TMDB ID เดิม
    tmdb_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
    )

    # เก็บเฉพาะ poster path ที่ TMDB ส่งกลับมา
    # ตัวอย่างแนวรูปแบบ: /abc123.jpg
    #
    # ไม่เก็บ URL เต็มใน PostgreSQL
    # เพราะ Checkpoint 10 จะสร้าง URL สำหรับแสดง Poster จาก path นี้
    poster_path = models.CharField(
        max_length=255,
        blank=True,
    )

    @property
    def poster_url(self):
        """
        สร้าง URL เต็มสำหรับ poster จาก TMDB

        ใน PostgreSQL เก็บเฉพาะ poster_path เช่น /abc123.jpg
        แทนการเก็บ URL เต็ม เพื่อไม่ผูกข้อมูลใน database
        กับ image size หรือ URL format แบบใดแบบหนึ่ง

        Movie ที่เพิ่มด้วย Manual Add หรือ Movie ที่ TMDB ไม่มี poster
        จะคืนค่า None เพื่อให้ Template แสดง placeholder แทน
        """

        # ถ้าไม่มี poster_path ไม่ควรสร้าง URL ที่ใช้ไม่ได้
        if not self.poster_path:
            return None

        # ใช้ TMDB image base URL ขนาด w500
        # แล้วต่อกับ poster_path ที่เก็บไว้ใน Movie object
        return (
            "https://image.tmdb.org/t/p/w500"
            f"{self.poster_path}"
        )

    def __str__(self):
        """
        กำหนดข้อความที่ใช้แทน Movie object
        เช่นใน Django Admin หรือ Django shell
        """
        return self.title