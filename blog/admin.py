from blog.models import Post,Category
from django.contrib import admin
class PostAdmin(admin.ModelAdmin):
	class Media:
		js = ('/js/tinymce/tinymce.js', '/js/textareas.js')
 
admin.site.register(Post, PostAdmin)

admin.site.register(Category)
