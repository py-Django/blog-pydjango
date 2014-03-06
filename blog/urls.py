from django.conf.urls import *
from blog.views import IndexView,CategoryView ,TagsView,ShowPost

urlpatterns = patterns('',
   

    url(r'^tag/(?P<tagslug>[-\w]+)/$',TagsView.as_view(),name='showtag'),
       
    url(r'^(?P<slug>[-\w]+)/$',CategoryView.as_view(),name='showcategory'),

 
)
