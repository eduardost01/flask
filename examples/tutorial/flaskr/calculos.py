
from flask import Blueprint, render_template, request, flash


bp = Blueprint(
    'calculos',
    __name__,
    url_prefix='/calculos'
)


def calcular_irpf(salario):

    # Desconto simplificado mensal de 2026
    base_calculo = max(0, salario - 607.20)

    if base_calculo <= 2428.80:
        imposto = 0

    elif base_calculo <= 2826.65:
        imposto = base_calculo * 0.075 - 182.16

    elif base_calculo <= 3751.05:
        imposto = base_calculo * 0.15 - 394.16

    elif base_calculo <= 4664.68:
        imposto = base_calculo * 0.225 - 675.49

    else:
        imposto = base_calculo * 0.275 - 908.73

    # Redução adicional do IRPF em 2026
    if salario <= 5000:
        reducao = imposto

    elif salario <= 7350:
        reducao = 978.62 - (0.133145 * salario)

    else:
        reducao = 0

    imposto = max(0, imposto - reducao)

    return round(imposto, 2)


def calcular_rescisao(salario, meses):

    decimo_terceiro = (salario / 12) * meses

    return round(decimo_terceiro, 2)


@bp.route('/painel', methods=('GET', 'POST'))
def painel():

    resultado_irpf = None
    resultado_rescisao = None

    if request.method == 'POST':

        tipo = request.form.get('tipo')

        try:

            if tipo == 'irpf':

                salario = float(
                    request.form['salario']
                )

                if salario <= 0:
                    raise ValueError

                resultado_irpf = calcular_irpf(salario)

            elif tipo == 'rescisao':

                salario = float(
                    request.form['salario_rescisao']
                )

                meses = int(
                    request.form['meses']
                )

                if salario <= 0 or meses < 1 or meses > 12:
                    raise ValueError

                resultado_rescisao = calcular_rescisao(
                    salario,
                    meses
                )

            else:
                flash('Tipo de cálculo inválido.')

        except (ValueError, TypeError):
            flash('Informe valores numéricos válidos.')

    return render_template(
        'calculos/index.html',
        resultado_irpf=resultado_irpf,
        resultado_rescisao=resultado_rescisao
    )
