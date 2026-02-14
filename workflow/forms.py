from django import forms
from ai_models.models import AIModel


_tw = "w-full bg-dark-700 border border-dark-400 text-dark-50 rounded-lg px-4 py-2.5 text-[13px] " \
      "focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none placeholder-dark-200"


class WorkflowCreateForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": _tw,
            "placeholder": "e.g. LNP Optimization Cycle #3",
        }),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": _tw,
            "rows": 3,
            "placeholder": "Describe the goals of this optimization run...",
        }),
    )
    ai_model = forms.ModelChoiceField(
        queryset=AIModel.objects.filter(is_active=True),
        required=False,
        empty_label="-- Select AI Model (optional) --",
        widget=forms.Select(attrs={"class": _tw}),
    )
