from django import forms
from .models import Ocorrencia, local

class LocalForm(forms.ModelForm):
    class Meta:
        model = local
        fields = ['insc', 'endereco']
        labels= {'insc': 'Inscrição Imobiliaria', 'endereco':'Endereço'}



class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ['status', 'desc', 'noti', 'prazo', 'andamento']
        labels = {
            'status': 'Status da Ocorrência:',
            'desc': 'Descrição da Ocorrência:',
            'noti': 'Notificado?',
            'prazo': 'Prazo para regularização:',
            'andamento': 'Andamento:',
        }
        widgets = {
            'desc': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Descreva a ocorrência aqui...',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'noti': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'prazo': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'andamento': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Torna o campo 'andamento' somente leitura (disabled)
        #if 'andamento' in self.fields:
         #   self.fields['andamento'].disabled = True