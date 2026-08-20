from django import forms

from .models import Movie


class MovieForm(forms.ModelForm):
    """
    Form สำหรับเพิ่มและแก้ไขข้อมูล Movie

    Form นี้ใช้ร่วมกันโดย:
        - movie_add()
        - movie_edit()

    Personal Rating ไม่อยู่ใน Form นี้แล้ว
    เพราะ Checkpoint 10 ย้ายการให้คะแนน
    ไปเป็น Inline Rating บน WATCHED Movie Card

    การแยก Rating ออกจาก Form ช่วยให้ UI สื่อกฎได้ชัดเจนว่า:
        - Movie ที่ยังไม่ได้ดู ไม่ควรให้คะแนน
        - Movie ที่ดูแล้วสามารถให้คะแนน 1–5 ได้จากหน้า Home

    Movie model ยังมี personal_rating field เหมือนเดิม
    และข้อมูลยังถูกเก็บใน PostgreSQL ตามปกติ
    """

    class Meta:
        model = Movie

        # title, genre และ release_year เป็นข้อมูลหลักของ Movie
        # watched ยังคงอยู่ใน Form
        # เพื่อให้ Manual Add/Edit สามารถระบุได้ว่า
        # Movie นี้เคยดูแล้วหรือยัง
        # personal_rating ถูกย้ายไปจัดการด้วย movie_rate()
        fields = [
            "title",
            "genre",
            "release_year",
            "watched",
        ]

        # เปลี่ยนข้อความของ watched checkbox
        # ให้ผู้ใช้เข้าใจง่ายกว่าการเห็นชื่อ Boolean field ตรง ๆ
        labels = {
            "watched": "Already watched",
        }

        help_texts = {
            "watched": (
                "Check this if you have already watched the movie. "
                "You can rate watched movies from the watchlist."
            ),
        }