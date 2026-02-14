from django.contrib import admin
from .models import IonizableLipid, HeadGroup, Linker, Tail, HelperLipid, Cholesterol, PEGLipid

@admin.register(IonizableLipid)
class IonizableLipidAdmin(admin.ModelAdmin):
    list_display = ["name", "molecular_weight", "logp", "has_ester", "has_carbonate", "source"]
    list_filter = ["source", "has_ester", "has_carbonate", "has_disulfide"]
    search_fields = ["name", "smiles"]
    readonly_fields = ["created_at"]

@admin.register(HeadGroup)
class HeadGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "smiles"]
    search_fields = ["name"]

admin.site.register(Linker)
admin.site.register(Tail)
admin.site.register(HelperLipid)
admin.site.register(Cholesterol)
admin.site.register(PEGLipid)
