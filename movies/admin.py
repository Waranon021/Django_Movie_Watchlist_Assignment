from django.contrib import admin

from .models import Movie


# Register Movie model กับ Django Admin
# ทำให้สามารถเพิ่ม ดู แก้ไข และลบ Movie
# ผ่านหน้า /admin/ ได้โดยไม่ต้องสร้างหน้า CRUD เองในขั้นนี้
admin.site.register(Movie)