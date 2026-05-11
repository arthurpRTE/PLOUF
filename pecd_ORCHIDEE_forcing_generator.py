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
    ws10_file = "/homedata/apaolini/PECD4.2/HIST/CLIM/10WS/BIAS/H_ERA5_ECMW_T639_WS-_0010m_Pecd_025d_S195001010000_E195012312300_INS_MAP_01h_NA-_mbc_org_NA_NA---_NA---_NA---_PECD4.2_fv1.nc"
    t2m_file = ""
    altitude_file = "/homedata/apaolini/PECD4.2/MASKS/altitude.nc"
    forcing_tmp = ""
    forcing_orchidee = ""

    ## genere les paths pour aller chercher les fichiers et les noms des fichiers de sortie
    if (year < 2000) | (year > 2018) :
        for m in range(1, 13):
            t2m_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/AN_SF/{year}/t2m.{year}{m:02d}.as1e5.GLOBAL_025.nc "
            d2m_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/AN_SF/{year}/d2m.{year}{m:02d}.as1e5.GLOBAL_025.nc "
            sp_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/AN_SF/{year}/sp.{year}{m:02d}.as1e5.GLOBAL_025.nc "
            ssrd_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/FC_SF/{year}/{m:02d}/ssrd.{year}{m:02d}*.600.fs1e5.GLOBAL_025.nc "
            strd_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/FC_SF/{year}/{m:02d}/strd.{year}{m:02d}*.600.fs1e5.GLOBAL_025.nc "
            tp_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/FC_SF/{year}/{m:02d}/tp.{year}{m:02d}*.600.fs1e5.GLOBAL_025.nc "
            sf_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/FC_SF/{year}/{m:02d}/sf.{year}{m:02d}*.600.fs1e5.GLOBAL_025.nc "

    else :
        for m in range(1, 13):
            t2m_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/AN_SF_modif/{year}/t2m.{year}{m:02d}.as1e5.GLOBAL_025.nc "
            d2m_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/AN_SF_modif/{year}/d2m.{year}{m:02d}.as1e5.GLOBAL_025.nc "
            sp_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/AN_SF_modif/{year}/sp.{year}{m:02d}.as1e5.GLOBAL_025.nc "
            ssrd_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/FC_SF_modif/{year}/{m:02d}/ssrd.{year}{m:02d}*.600.fs1e5.GLOBAL_025.nc "
            strd_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/FC_SF_modif/{year}/{m:02d}/strd.{year}{m:02d}*.600.fs1e5.GLOBAL_025.nc "
            tp_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/FC_SF_modif/{year}/{m:02d}/tp.{year}{m:02d}*.600.fs1e5.GLOBAL_025.nc "
            sf_file += f"/bdd/ERA5/NETCDF/GLOBAL_025/hourly/FC_SF_modif/{year}/{m:02d}/sf.{year}{m:02d}*.600.fs1e5.GLOBAL_025.nc "
            
    ssrd_file_out = f"ssrd.{year}_temp.nc"
    strd_file_out = f"strd.{year}_temp.nc"
    tp_file_temp = f"tp.{year}_temp.nc"
    rain_file_out = f"rain.{year}_temp.nc"
    sf_file_out = f"sf.{year}_temp.nc"
    q_file_out = f"q.{year}_temp.nc"
    forcing_tmp = f"forcing.{year}_temp.nc"
    forcing_orchidee = f"forcing_orchidee.{year}.nc"

    print("-"*10)
    print(ssrd_file)
    print(ssrd_file_out)
    print(strd_file)
    print(strd_file_out)
    print(tp_file)
    print(rain_file_out)
    print(sf_file)
    print(sf_file_out)
    print(sp_file)
    print(d2m_file)
    print(q_file_out)
    print(ws10_file)
    print(t2m_file)
    print(altitude_file)
    print(forcing_tmp)
    print(forcing_orchidee)



    ## genere un mergefile pour toutes les variables en forcast
    print(f"grouping ssrd for year {year}...")
    cdo.expr(
        'SWdown=ssrd/3600.',
        input = '-mergetime ' + ssrd_file,
        output = ssrd_file_out
    ) ## attention les unités sont pas les bonnes (J/m2 au lieu de W/m2)
    print("ssrd - done")
    print(f"grouping strd for year {year}...")
    cdo.expr(
        'LWdown=strd/3600.',
        input = '-mergetime ' + strd_file,
        output = strd_file_out
    ) ## attention les unités sont pas les bonnes (J/m2 au lieu de W/m2)
    print("strd - done")
    print(f"grouping sf for year {year}...")
    cdo.expr(
        'Snowf=sf',
        input = '-mergetime ' + sf_file,
        output = sf_file_out
    )
    print("sf - done")
    print(f"grouping rain for year {year}...")
    cdo.mergetime(
        input = tp_file,
        output = tp_file_temp
    )
    cdo.expr(
        "'Rainf=(tp-Snowf)*(tp-Snowf > 0)'",
        input = "-merge " + tp_file_temp + " " + sf_file_out,
        output = rain_file_out
    )
    print("rain - done")
    
    ## calcul de l'humidité spécifique de l'air
    
    print(f"computing sh for year {year}...")
    cdo.expr(
        "'T = d2m - 273.16;'"
        "'e = 611.21*exp(17.502*T/(T + 240.97));'"
        "'Qair = 0.62198*e/(sp - (1 - 0.62198)*e)'",
        input = "-merge " + sp_file + " " + d2m_file,
        output = q_file_out
    )
    print("sh - done")
    ## création du fichier de forçage orchidee
    
    print("grouping...")
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

    print("setting attributes...")
    cdo.setattribute(
        'PSurf@cell_methods="time: instantaneous",' 
        'LWdown@cell_methods="time: mean(end)",' 
        'LWdown@units="W m-2",' 
        'SWdown@cell_methods="time: mean(end)",' 
        'SWdown@units="W m-2",' 
        'Tair@cell_methods="time: instantaneous",' 
        'Qair@cell_methods="time: instantaneous",' 
        'Wind@cell_methods="time: instantaneous",' 
        'Rainf@cell_methods="time: mean(end)",'
        'Snowf@cell_methods="time: mean(end)",',
        input = forcing_tmp,
        output = forcing_orchidee
    )
    print(f"forcing generated for year {year}")


mergeAll(1950)