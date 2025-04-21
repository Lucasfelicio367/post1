from django.shortcuts import render, get_object_or_404, redirect
from .models import local, Ocorrencia
from .forms import LocalForm, OcorrenciaForm
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Count, Q
from datetime import datetime
def index(request):
    return render(request, 'local/index.html')

@login_required
def vloc(request):
    query = request.GET.get('q', '')
    filtro_andamento = request.GET.get('andamento', '')

    loc = local.objects.all()

    if query:
        loc = loc.filter(insc__icontains=query)

    if filtro_andamento:
        loc = loc.filter(ocorrencia__andamento=filtro_andamento).distinct()

    context = {
        'loc': loc.order_by('date_added'),
        'query': query,
        'filtro_andamento': filtro_andamento,
    }

    return render(request, 'local/locais.html', context)


@login_required
def vlocs(request, insc_id):
    loc = get_object_or_404(local, id=insc_id)

    filtro_andamento = request.GET.get('andamento', '')
    ocorrencias = loc.ocorrencia_set.order_by('-date_added')

    if filtro_andamento:
        ocorrencias = ocorrencias.filter(andamento=filtro_andamento)

    context = {
        'loc': loc,
        'ocorr': ocorrencias,
        'filtro_andamento': filtro_andamento,
    }
    return render(request, 'local/ocloc.html', context)

@login_required
def new_local(request):
    if request.method != 'POST':
        form = LocalForm()
    else:
        form = LocalForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('local:vloc'))
    context = {'form': form}
    return render(request, 'local/new_local.html', context)

@login_required
def edit_local(request, local_id):
    loc = get_object_or_404(local, id=local_id)

    if request.method != "POST":
        form = LocalForm(instance=loc)
    else:
        form = LocalForm(instance=loc, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('local:vloc')  # Redireciona para a página de visualização dos locais

    context = {'form': form, 'loc': loc}
    return render(request, 'local/edit_local.html', context)


@login_required
def new_ocorrencia(request, insc_id):
    loc = get_object_or_404(local, id=insc_id)

    if request.method != 'POST':
        form = OcorrenciaForm()
    else:
        form = OcorrenciaForm(data=request.POST)
        if form.is_valid():
            new_ocor = form.save(commit=False)
            new_ocor.local = loc
            new_ocor.owner = request.user
            # Não sobrescreve o andamento manualmente aqui
            new_ocor.save()
            return HttpResponseRedirect(reverse('local:vlocs', args=[insc_id]))

    context = {'loc': loc, 'form': form}
    return render(request, 'local/new_ocorrencia.html', context)

@login_required
def edit_ocorrencia(request, ocorr_id):
    ocorr = Ocorrencia.objects.get(id=ocorr_id)
    loc = ocorr.local

    if ocorr.owner != request.user:
        raise Http404

    if request.method != "POST":
        form = OcorrenciaForm(instance=ocorr)
    else:
        form = OcorrenciaForm(instance=ocorr, data=request.POST)
        if form.is_valid():
            ocorrencia_editada = form.save(commit=False)

            # Atualiza andamento apenas se não estiver como 'resolvido'
            if ocorrencia_editada.andamento != 'resolvido':
                if ocorrencia_editada.prazo and ocorrencia_editada.prazo < datetime.now().date():
                    ocorrencia_editada.andamento = 'vencido'
                else:
                    ocorrencia_editada.andamento = 'em_andamento'

            ocorrencia_editada.save()
            return HttpResponseRedirect(reverse('local:vlocs', args=[loc.id]))

    context = {'ocorr': ocorr, 'loc': loc, 'form': form}
    return render(request, 'local/edit_ocorrencia.html', context)

@login_required
def gerar_relatorio_pdf(request):
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

    context = {
        "total_locais": total_locais,
        "total_ocorrencias": total_ocorrencias,
        "local_mais_ocorrencias": local_mais_ocorrencias,
        "mes_mais_fogo": mes_mais_fogo,
        "motivo_principal": motivo_principal,
        "nome_usuario": request.user.get_full_name() or request.user.username,
        "data_relatorio": data_hoje,
    }

    html_string = render_to_string("local/relatorio.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=relatorio.pdf"
    HTML(string=html_string).write_pdf(response)

    return response

@login_required
def gerar_relatorio_local_pdf(request, insc_id):
    loc = local.objects.get(id=insc_id)
    ocorrencias = loc.ocorrencia_set.all()

    total_ocorrencias = ocorrencias.count()

    motivo_principal = (
        ocorrencias.values("status")
        .annotate(total=Count("status"))
        .order_by("-total")
        .first()
    )
    motivo_principal = motivo_principal["status"] if motivo_principal else "N/A"

    meses_ocorrencias = [ocorr.date_added.month for ocorr in ocorrencias]
    mes_mais_ocorrencias = (
        max(set(meses_ocorrencias), key=meses_ocorrencias.count) if meses_ocorrencias else "N/A"
    )

    total_notificacoes = ocorrencias.filter(noti=True).count()

    data_hoje = datetime.now().strftime("%d/%m/%Y")

    context = {
        "loc": loc,
        "total_ocorrencias": total_ocorrencias,
        "motivo_principal": motivo_principal,
        "mes_mais_ocorrencias": mes_mais_ocorrencias,
        "total_notificacoes": total_notificacoes,
        "nome_usuario": request.user.get_full_name() or request.user.username,
        "data_relatorio": data_hoje,
    }

    html_string = render_to_string("local/relatorio_local.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=relatorio_local_{loc.insc}.pdf"
    HTML(string=html_string).write_pdf(response)

    return response
