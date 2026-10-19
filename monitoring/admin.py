from django.contrib import admin
from .models import LLMRequest, Evaluation, TraceEvent

admin.site.register(LLMRequest)
admin.site.register(Evaluation)
admin.site.register(TraceEvent)
