from django import forms

from .models import Movie


class MovieForm(forms.ModelForm):
    """
    Form สำหรับเพิ่มและแก้ไขข้อมูล Movie

    ModelForm เชื่อมกับ Movie model โดยตรง
    ทำให้ Django สามารถสร้าง form fields และตรวจ validation
    จาก field definitions ใน models.py ได้
    """

    class Meta:
        # ระบุว่า form นี้ทำงานกับ Movie model
        model = Movie

        # ระบุ field ที่อนุญาตให้ผู้ใช้กรอกผ่าน form
        # date_added ไม่อยู่ในนี้ เพราะ Django สร้างให้อัตโนมัติ
        fields = [
            "title",
            "genre",
            "release_year",
            "personal_rating",
            "watched",
        ]