from django.shortcuts import render
from .models import local, Ocorrencia
from .forms import LocalForm, OcorrenciaForm
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Count
from datetime import datetime

# Create your views here.

def index(request):
    """ Página principal do local"""
    return render(request, 'local/index.html')

@login_required
def vloc(request):
    """Mostra uma lista com todos os locais cadastrados, com opção de pesquisa."""
    query = request.GET.get('q', '')  # Captura o termo de busca
    if query:
        loc = local.objects.filter(
            insc__icontains=query
        ).order_by('date_added')  # Filtra os locais pelo campo "insc"
    else:
        loc = local.objects.order_by('date_added')  # Lista todos os locais

    context = {'loc': loc, 'query': query}
    return render(request, 'local/locais.html', context)

@login_required
def vlocs(request, insc_id):
    """Mostra um único local com todas as suas ocorrências"""
    loc=local.objects.get(id = insc_id)
    ocorr= loc.ocorrencia_set.order_by('-date_added')
    context={'loc': loc, 'ocorr':ocorr}
    return render(request, 'local/ocloc.html', context) #ocloc é ocorrencia por local

@login_required
def new_local(request):
    """ Adiciona um novo local"""
    if request.method != 'POST':
        #nenhum dadoo submetido, cria um formulário em branco
        form = LocalForm()
    else:
        #Dados de POST submetidos processa os dados
        form = LocalForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('vloc'))
    context = {'form': form}
    return render(request, 'local/new_local.html', context)

@login_required
def new_ocorrencia(request, insc_id):
    """ Acrescenta uma nova ocorrencia para cada local"""
    loc= local.objects.get(id= insc_id)
    if request.method != 'POST':
        #nenhum dado submetido, cria um formulário em branco
        form = OcorrenciaForm()
    else:
        #Dados de POST submetidos processa os dados
        form = OcorrenciaForm(data= request.POST)
        if form.is_valid():
            new_ocor= form.save(commit=False)
            new_ocor.nsc = loc
            new_ocor.owner = request.user 
            #new_ocor.loc = loc
            new_ocor.save()

            return HttpResponseRedirect(reverse('vlocs', args=[insc_id]))
    context = {'loc': loc,'form': form}
    return render(request, 'local/new_ocorrencia.html', context)

@login_required
def edit_ocorrencia(request, ocorr_id):
    """Edita uma ocorrencia existente"""
    ocorr = Ocorrencia.objects.get(id = ocorr_id)
    loc = ocorr.nsc

        # Garante que o assunto pertence ao usuário atual:

    if ocorr.owner != request.user:
        raise Http404

    if request.method != "POST":
        # Requisição inicial: preenche previamente o formulário com a ocorrencia atual
        form = OcorrenciaForm(instance=ocorr)
    
    else:
        #Dados do POST submetidos; processa os dados
        form = OcorrenciaForm(instance=ocorr, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('vlocs', args=[loc.id]))
        
    context= {'ocorr': ocorr, 'loc': loc, 'form': form}
    return render(request, 'local/edit_ocorrencia.html', context)

#---------------------------------------------------------------------------------------------

@login_required
def gerar_relatorio_pdf(request):
    """Gera um relatório em PDF com as informações do sistema"""
    
    # Dados para o relatório
    total_locais = local.objects.count()
    total_ocorrencias = Ocorrencia.objects.count()

    local_com_mais_ocorrencias = (
        local.objects.annotate(num_ocorrencias=Count('ocorrencia')).order_by('-num_ocorrencias').first()
    )
    local_mais_ocorrencias = local_com_mais_ocorrencias.insc if local_com_mais_ocorrencias else "N/A"

    fogo_ocorrencias = Ocorrencia.objects.filter(status="fogo").values_list("date_added", flat=True)
    meses_fogo = [data.month for data in fogo_ocorrencias]
    mes_mais_fogo = max(set(meses_fogo), key=meses_fogo.count) if meses_fogo else "N/A"

    motivo_principal = (
        Ocorrencia.objects.values("status").annotate(total=Count("status")).order_by("-total").first()
    )
    motivo_principal = motivo_principal["status"] if motivo_principal else "N/A"

    
    
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    # Contexto do relatório
    context = {
        "total_locais": total_locais,
        "total_ocorrencias": total_ocorrencias,
        "local_mais_ocorrencias": local_mais_ocorrencias,
        "mes_mais_fogo": mes_mais_fogo,
        "motivo_principal": motivo_principal,
        "nome_usuario": request.user.get_full_name() or request.user.username,
        "data_relatorio": data_hoje,
        
    }

    # Gera o PDF
    html_string = render_to_string("local/relatorio.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=relatorio.pdf"
    HTML(string=html_string).write_pdf(response)

    return response


# -------------------------gera relatório por local ---------------------------------------------------------------------

@login_required
def gerar_relatorio_local_pdf(request, insc_id):
    """Gera um relatório em PDF para um local específico."""
    loc = local.objects.get(id=insc_id)
    ocorrencias = loc.ocorrencia_set.all()
    
    total_ocorrencias = ocorrencias.count()

    # Principal motivo de ocorrências
    motivo_principal = (
        ocorrencias.values("status")
        .annotate(total=Count("status"))
        .order_by("-total")
        .first()
    )
    motivo_principal = motivo_principal["status"] if motivo_principal else "N/A"

    # Mês com mais ocorrências
    meses_ocorrencias = [ocorr.date_added.month for ocorr in ocorrencias]
    mes_mais_ocorrencias = (
        max(set(meses_ocorrencias), key=meses_ocorrencias.count) if meses_ocorrencias else "N/A"
    )

    # Total de vezes que foi notificado
    total_notificacoes = ocorrencias.filter(noti=True).count()

    # Data atual para o relatório
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    # Contexto para o template
    context = {
        "loc": loc,
        "total_ocorrencias": total_ocorrencias,
        "motivo_principal": motivo_principal,
        "mes_mais_ocorrencias": mes_mais_ocorrencias,
        "total_notificacoes": total_notificacoes,
        "nome_usuario": request.user.get_full_name() or request.user.username,
        "data_relatorio": data_hoje,
    }

    # Renderizando o template para PDF
    html_string = render_to_string("local/relatorio_local.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=relatorio_local_{loc.insc}.pdf"
    HTML(string=html_string).write_pdf(response)

    return response


