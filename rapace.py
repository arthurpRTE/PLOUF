from pymathisrte.client import MathisClient
import pandas as pd
import numpy as np
import datetime
import tqdm
import getpass
import pyfiglet



f = pyfiglet.figlet_format("RAPACE", font="slant")
print("")
print(f)
print("Recuperation Automatisée de la Production non Agrégée des Centrales Electriques")
print("")

user = input("utilisateur : ")
mdp = getpass.getpass("mot de passe : ")
client = MathisClient(username=user, password=mdp, cert_path="C:/Users/paoliniart/mathis.pem")
client.endpoint = "grpc://mathis.rte-france.com:32010"
client.connect()

print("-"*20)
date_start = input("date de debut pour l'extraction (format AAAA-MM-JJ) : ")
date_end = input("date de fin pour l'extraction (format AAAA-MM-JJ) : ")


dict_filiere = {"hydro" : 'HYDLQ', 
          "thermique" : 'THERM', 
          "nucleaire" : 'NUCLE', 
          "photovoltaique" : 'SOLAI',
          "eolien" : 'EOLIE'}

print("")
techno = input("technologie à recuperer (options : hydro, thermique, nucleaire, photovoltaique, eolien). Si rien n'est rentré, toutes les centrales seront recupérées : ")

if techno == "":
    df_install = client.execute_query("SELECT * FROM PRIV_SDC.INPUT.PROD_SDC.S001_SDC.SDC_DWH.RPT_REF_INSTALL")

else :
    df_install = client.execute_query("SELECT * FROM PRIV_SDC.INPUT.PROD_SDC.S001_SDC.SDC_DWH.RPT_REF_INSTALL WHERE " 
                        + "('" + dict_filiere[techno] + "' = CODE_FILIERE_PRINCIPAL)")

print("")
centrales = input("code des centrales à récuperer (format CENTRALE1,CENTRALE2...). Si rien n'est rentré, toutes les centrales seront recupérées : ")
if centrales == "" :
    ouvrages = tuple(df_install['CODE_INSTALLATION'].drop_duplicates())

else : 
    centrales = centrales.split(",")
    ouvrages = tuple(i for i in centrales if i in df_install['CODE_INSTALLATION'].drop_duplicates().values)
    print("les centrales suivantes n'ont pas été trouvées dans la liste demandée : " + str(tuple(i for i in centrales if i not in df_install['CODE_INSTALLATION'].drop_duplicates().values)))

racace_mode = input("c'est le monde a l'envers : voulez-vous recuperer les tirages des centrales et non les injections ?(y/n) : ")

if racace_mode == "y" :
    print("")
    print("'Once you start down the dark path, forever will it dominate your destiny. Consume you, it will.' — Yoda")
    print("")
    f = pyfiglet.figlet_format("RACACE", font="epic")
    print("")
    print(f)
    print("Recuperation Automatisée de la Consommation non Agrégée des Centrales Electriques")
    print("")
    print("extraction en cours ...")
    if len(ouvrages) == 1 :
        df_cdc = client.execute_query("SELECT * FROM PRIV_SDC.INPUT.PROD_SDC.S001_SDC.SDC_DWH.RPT_CDC_INSTALL WHERE (CODE_TYPE = 'AA') AND " 
                            + "('"+ date_start + "' <= DATE_CRB) AND "
                            + "('"+ date_end + "' >= DATE_CRB) AND "
                            + "(DATE_FIN_BI IS NULL) AND "
                            + "(CODE_INSTALLATION = '" + ouvrages[0] + "')")

    else :
        df_cdc = client.execute_query("SELECT * FROM PRIV_SDC.INPUT.PROD_SDC.S001_SDC.SDC_DWH.RPT_CDC_INSTALL WHERE (CODE_TYPE = 'AA') AND " 
                            + "('"+ date_start + "' <= DATE_CRB) AND "
                            + "('"+ date_end + "' >= DATE_CRB) AND "
                            + "(DATE_FIN_BI IS NULL) AND "
                            + "(CODE_INSTALLATION in " + str(ouvrages) + ")")

else :
    print("extraction en cours ...")
    if len(ouvrages) == 1 :
        df_cdc = client.execute_query("SELECT * FROM PRIV_SDC.INPUT.PROD_SDC.S001_SDC.SDC_DWH.RPT_CDC_INSTALL WHERE (CODE_TYPE = 'AR') AND " 
                            + "('"+ date_start + "' <= DATE_CRB) AND "
                            + "('"+ date_end + "' >= DATE_CRB) AND "
                            + "(DATE_FIN_BI IS NULL) AND "
                            + "(CODE_INSTALLATION = '" + ouvrages[0] + "')")

    else :
        df_cdc = client.execute_query("SELECT * FROM PRIV_SDC.INPUT.PROD_SDC.S001_SDC.SDC_DWH.RPT_CDC_INSTALL WHERE (CODE_TYPE = 'AR') AND " 
                            + "('"+ date_start + "' <= DATE_CRB) AND "
                            + "('"+ date_end + "' >= DATE_CRB) AND "
                            + "(DATE_FIN_BI IS NULL) AND "
                            + "(CODE_INSTALLATION in " + str(ouvrages) + ")")

print("")
print("extraction terminée, mise en forme des données ...")

date_range_output = pd.date_range(start=max(date_start, str(df_cdc["DATE_CRB"].min())), end=str(min(pd.to_datetime(date_end).date(), df_cdc["DATE_CRB"].max()) + datetime.timedelta(1)), freq="10min", tz="Europe/Paris")
date_range_output_daily = pd.date_range(start=max(date_start, str(df_cdc["DATE_CRB"].min())), end=min(date_end, str(df_cdc["DATE_CRB"].max())), freq="D", tz="Europe/Paris")

df_output = pd.DataFrame(np.empty((len(date_range_output), len(df_cdc["CODE_INSTALLATION"].drop_duplicates())))*(np.nan), index= date_range_output, columns = list(df_cdc["CODE_INSTALLATION"].drop_duplicates()))

puiss23 = ["PUISS" + str(i) for i in range(1, 139)]
puiss24 = ["PUISS" + str(i) for i in range(1, 145)]
puiss25 = ["PUISS" + str(i) for i in range(1, 151)]

for d in tqdm.tqdm(date_range_output_daily)  :
    tempDf = df_cdc[df_cdc["DATE_CRB"] == d.date()]
    if list(tempDf["NB_HEURES"])[0] == 24 :
        data_array = np.array(tempDf[puiss24], dtype= np.float64)
    elif list(tempDf["NB_HEURES"])[0] == 23 :
        data_array = np.array(tempDf[puiss23], dtype= np.float64)
    else :
        data_array = np.array(tempDf[puiss25], dtype= np.float64)
    df_output.loc[d + datetime.timedelta(minutes = 10) : d + datetime.timedelta(hours = int(list(tempDf["NB_HEURES"])[0])), list(tempDf["CODE_INSTALLATION"])] = data_array.T

print("mise en forme terminee")
print("")
hor = input("resampler au pas de temps horaire ?(y/n) : ")
hor_name = "10min"
if hor == "y" :
    df_output = df_output.resample('h').mean()
    hor_name = "H"

df_output.to_parquet(date_start + "_" + date_end + "_" + techno + "_" + hor_name + ("_soutirage" * (racace_mode == "y")) + ".parquet")
df_install = df_install[df_install['DATE_FIN_BI'].fillna(False) == False]
if len(ouvrages) == 1 :
    df_install = df_install[df_install['CODE_INSTALLATION'] == ouvrages[0]]
else :
    df_install = df_install[df_install['CODE_INSTALLATION'].isin(ouvrages)]
df_install = df_install[['CODE_INSTALLATION', 'DATE_DEBUT_VERSION', 'CODE_TECHNOLOGIE_PRINCIPAL', 'TYPE_INSTALLATION', 'LIBELLE_PROPRIETAIRE', 'PMAX_INST', 'CODE_TECHNOLOGIE_PRINCIPAL']].drop_duplicates(['CODE_INSTALLATION', 'CODE_TECHNOLOGIE_PRINCIPAL', 'TYPE_INSTALLATION', 'PMAX_INST', 'CODE_TECHNOLOGIE_PRINCIPAL']).copy()
df_install.to_csv(date_start + "_" + date_end + "_" + techno + "_" + hor_name + "_infos.csv")
print("enregistrement terminé")