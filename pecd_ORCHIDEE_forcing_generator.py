from cdo import Cdo
import xarray as xr
import numpy as np

cdo = Cdo()

def mergeAll(year) :

    ssrd_file = ""
    ssrd_file_out = ""
    strd_file = ""
    strd_file_out = ""
    tp_file = ""
    rain_file_out = ""
    sf_file = ""
    sf_file_out = ""
    sp_file = ""
    d2m_file = ""
    q_file_out = ""
    ws10_file = ""
    t2m_file = ""
    altitude_file = ""
    forcing_tmp = ""
    forcing_orchidee = ""

    ## genere un mergefile pour toutes les variables en forcast
    cdo.expr(
        'SWdown=ssrd/3600.',
        input = '-mergetime ' + ssrd_file,
        output = ssrd_file_out
    ) ## attention les unités sont pas les bonnes (J/m2 au lieu de W/m2)
    cdo.expr(
        'LWdown=strd/3600.',
        input = '-mergetime ' + strd_file,
        output = strd_file_out
    ) ## attention les unités sont pas les bonnes (J/m2 au lieu de W/m2)
    cdo.expr(
        'Snowf=sf',
        input = '-mergetime ' + sf_file,
        output = sf_file_out
    )
    cdo.expr(
        'Rainf=(tp-sf)*(tp-sf > 0)',
        input = (
            '-merge '
            '-mergetime ' + tp_file
            '-mergetime ' + sf_file
        ),
        out = rain_file_out
    )

    ## calcul de l'humidité spécifique de l'air
    

    cdo.expr(
        "T = d2m - 273.16;"
        "e = 611.21*exp(17.502*T/(T + 240.97));"
        "Qair = 0.62198*e/(sp - (1 - 0.62198)*e)",
        input = "-merge " + sp_file + " " + d2m_file,
        output = q_file_out
    )

    ## création du fichier de forçage orchidee
    

    cdo.remapnn(
        ws10_file,
        input = "-chname,t2m,Tair,sp,PSurf -setlon180 -merge " +
        sp_file + " " + 
        strd_file_out + " " + 
        t2m_file + " " + 
        q_file_out + " " + 
        ssrd_file_out + " " +
        rain_file_out + " " +
        sf_file_out + " " +
        altitude_file,
        output = forcing_tmp

    )

    cdo.setattribute(
        'PSurf@cell_methods="time: instantaneous",' +
        'LWdown@cell_methods="time: mean(end)",' +
        'LWdown@cell_methods="units: (W m-2)",' +
        'SWdown@cell_methods="time: mean(end)",' +
        'SWdown@cell_methods="units: (W m-2)",' +
        'Tair@cell_methods="time: instantaneaous",' +
        'Qair@cell_methods="time: instantaneous",' +
        'Wind@cell_methods="time: instantaneous",' +
        'Rainf@cell_methods="time: mean(end)",' +
        'Snowf@cell_methods="time: mean(end)",',
        input = forcing_tmp,
        output = forcing_orchidee
    )