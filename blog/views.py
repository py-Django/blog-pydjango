from django.http import HttpResponse
from blog.models import Post
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.views.generic import ListView,DetailView
from django.shortcuts import render_to_response







def main(request):
    """Main listing."""
    posts = Post.objects.all().order_by("-created")
    paginator = Paginator(posts, 4)

    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1

    try:
        posts = paginator.page(page)
    except (InvalidPage, EmptyPage):
        posts = paginator.page(paginator.num_pages)

    return render_to_response("postlist.html", dict(posts=posts, user=request.user))





class IndexView(ListView):
	queryset = Post.objects.filter(published=True).order_by('-created')

class CategoryView(ListView):
	def get_queryset(self):
		return Post.objects.filter(category__slug=self.kwargs['slug'],published=True).order_by('-created')

class TagsView(ListView):
        context_object_name="posts"
        template_name="postlist.html"
	def get_queryset(self):
		return Post.objects.filter(tags__name__in=[self.kwargs['tagslug']]).order_by('-created')

class ShowPost(DetailView):
	template_name="post.html"
	context_object_name='post'

	def get_object(self):
		return get_object_or_404(Post.objects.filter(category__slug=self.kwargs['catslug'],slug=self.kwargs['postslug'],published=True))











