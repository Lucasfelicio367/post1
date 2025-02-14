from django import forms
from .models import local, Ocorrencia

class LocalForm(forms.ModelForm):
    class Meta:
        model = local
        fields = ['insc', 'endereco']
        labels= {'insc': 'Inscrição Imobiliaria', 'endereco':'Endereço'}


class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ['status', 'desc', 'noti']
        labels = {
            'status': 'Status da Ocorrência:',
            'desc': 'Descrição da Ocorrência:',
            'noti': 'Notificado?',
        }
        widgets = {
            'desc': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,  # Define o número de linhas no campo de texto
                'placeholder': 'Descreva a ocorrência aqui...',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'noti': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

        

