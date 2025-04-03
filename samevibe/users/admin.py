from django.contrib import admin
from interests.models import *
from chat.models import *
from users.models import *
from friends.models import *

selected_models = [Interest, Hobby, MusicGenre, Profile, Friendship]
admin.site.register(selected_models)
