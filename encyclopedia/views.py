import re
import secrets
from django import forms
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from markdown2 import Markdown

from . import util

markdowner = Markdown()
list_entries = util.list_entries()
lower_list = [entry.lower() for entry in list_entries]



class CreateEntryForm(forms.Form):
    title = forms.CharField(label="" , widget=forms.TextInput(attrs={"placeholder": "Title", "class":"form-control", }))
    content = forms.CharField(label="", widget=forms.Textarea(attrs={"placeholder": "Content", "class":"form-control"}))
class EditEntryForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={"placeholder": "Content"}))

def index(request):
    description = []
    for entry in list_entries:
        description.append(markdowner.convert(util.get_entry(entry)))
        zipped_content = zip(list_entries, description)
    return render(request, "encyclopedia/index.html", {
        "context": zipped_content,
        "page_name": "Home"
    })

def entry(request, title):
    # If the entry does exist, display the content of the entry
    if title.lower() in lower_list:
        position = lower_list.index(title.lower())
        html_content = markdowner.convert(util.get_entry(list_entries[position]))
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": html_content
        })
    # If an entry does not exist, display error page requested page was not found
    else:
        description = []
        messages.error(request, f'No results found for "{title}"')
        for entry in list_entries:
            description.append(markdowner.convert(util.get_entry(entry)))
            zipped_content = zip(list_entries, description)
        return render(request, "encyclopedia/index.html", {
            "context": zipped_content,
            "page_name": "Others articles that may be of interest"
        })

def search(request):
    query = request.GET.get("q", "")
    filtered_list = []
    # If the query is in the list of entries, display the entry
    if query.lower() in lower_list:
        position = lower_list.index(query.lower())
        return HttpResponseRedirect(reverse("entry", args=[list_entries[position]]))
    # Else, displays a list of all encyclopedia entries that have the query as a substring
    else:
        r = re.compile(f".*{query}", re.IGNORECASE)
        filtered_list = list(filter(r.match, list_entries))
        if len(filtered_list) > 0:
            description = []
            for entry in filtered_list:
                description.append(markdowner.convert(util.get_entry(entry)))
                zipped_content = zip(filtered_list, description)
            return render(request, "encyclopedia/index.html", {
                "context": zipped_content,
                "page_name": f'Results found for "{query}"'
            })
        # If no entries are found, display error page
        else:
            description = []
            for entry in list_entries:
                description.append(markdowner.convert(util.get_entry(entry)))
                zipped_content = zip(list_entries, description)
            messages.error(request, f'No results found for "{query}"')
            return render(request, "encyclopedia/index.html", {
                "context": zipped_content,
                "page_name": "Others articles that may be of interest"
            })

def create(request):
    if request.method == "GET":
        return render(request, "encyclopedia/createPage.html", {
            "createPageForm": CreateEntryForm()
        })
    elif request.method == "POST":
        form = CreateEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title.lower() in lower_list:
                messages.error(request, f"{title} already exists")
                return render(request, "encyclopedia/createPage.html", {
                     "createPageForm": CreateEntryForm(),
                })
            else:
                util.save_entry(title, content)
                list_entries.append(title)
                lower_list.append(title.lower())
                html_content = markdowner.convert(content)
                messages.success(request, "New post has been created.")
                return render(request, "encyclopedia/entry.html", {
                "title": title,
                "content": html_content
                })
        else:
            return render(request, "encyclopedia/createPage.html", {
                "createPageForm": form
            })

def edit(request, title):
    if request.method == "GET":
        return render(request, "encyclopedia/editPage.html", {
            "editPageForm": EditEntryForm(initial={ "content": util.get_entry(title)}),
            "title": title
        })
    elif request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            messages.success(request, f"{title} has been successfully edited." )
            return HttpResponseRedirect(reverse("entry", args=[title]))
        else:
            return render(request, "encyclopedia/editPage.html", {
                "editPageForm": form,
                "title": title
            })


def random(request):
    random_entry = secrets.choice(list_entries)
    return HttpResponseRedirect(reverse("entry", args=[random_entry]))