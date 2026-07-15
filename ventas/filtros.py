"""
=========================================================
FILTROS DEL DASHBOARD
=========================================================
"""

import pandas as pd


MESES = {

    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"

}


def obtener_filtros(df):

    fecha = "Asiento contable/Fecha de factura"

    fechas = pd.to_datetime(

        df[fecha],

        errors="coerce"

    )

    meses = sorted(

        fechas.dt.month.dropna().unique()

    )

    años = sorted(

        fechas.dt.year.dropna().unique()

    )

    semanas = sorted(

        fechas.dt.isocalendar().week.unique()

    )

    opciones_meses = [

        {

            "label": MESES[m],

            "value": int(m)

        }

        for m in meses

    ]

    opciones_años = [

        {

            "label": str(a),

            "value": int(a)

        }

        for a in años

    ]

    opciones_semanas = [

        int(s)

        for s in semanas

    ]

    return {

        "meses": opciones_meses,

        "años": opciones_años,

        "semanas": opciones_semanas

    }