from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Dissertation, CommitteeMember


def index(request):
    return render(request, "index.html")


class DissListView(generic.ListView):
    model = Dissertation
    paginate_by = 10


class DissDetailView(generic.DetailView):
    model = Dissertation

    # use context data since more pertains to dissertation?
    # maybe under "dynamic filtering" in the docs
    """def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        self.scholar = get_object_or_404(CommitteeMember, scholar=self.kwargs["pk"])
        context["committeemember_name"] = self.scholar
        return context"""
