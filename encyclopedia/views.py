from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
import markdown2
import random
from django import forms
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/entry_not_found.html", {
            "title": title,
        })
    else:
        converted_content = markdown2.markdown(content)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": converted_content
        })


def search(request):
    query = request.GET.get('q', '')
    matching_entries = []

    if query:
        entries = util.list_entries()
        matching_entries = [entry for entry in entries if query.lower() in entry.lower()]

        exact_match = next((entry for entry in entries if entry.lower() == query.lower()), None)
        if exact_match:
            return redirect('entry', title=exact_match)

    return render(request, 'encyclopedia/search_results.html', {
        'query': query,
        'results': matching_entries
    })



class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 50}))

def new_entry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            
            if util.get_entry(title):
                return render(request, "encyclopedia/error.html", {
                    "error_message": "It appears that the title you have submitted is already in existence within our entries."
                })
            
            util.save_entry(title, content)
            return redirect('entry', title=title)
    else:
        form = NewEntryForm()
    
    return render(request, "encyclopedia/new_entry.html", {
        "form": form
    })



class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

def edit(request, title):
    content = util.get_entry(title)
    if content is None:
        raise Http404("Entry not found")

    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            new_content = form.cleaned_data["content"]
            util.save_entry(title, new_content)
            return redirect('entry', title=title)
    else:
        form = EditForm(initial={"content": content})

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": form
    })



def random_page(request):
    entries = util.list_entries()
    if entries:
        random_entry = random.choice(entries)
        return HttpResponseRedirect(reverse('entry', args=[random_entry]))
    else:
        return render(request, "encyclopedia/error.html", {
            "error_message": "No entries available to display a random page."
        })
