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
    # field นี้จะใช้เรียงหนังแบบ newest first ใน Checkpoint 3
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        กำหนดข้อความที่ใช้แทน Movie object
        เช่นใน Django Admin หรือ Django shell
        """
        return self.title