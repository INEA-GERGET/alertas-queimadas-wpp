from datetime import datetime, timedelta
import shapely.geometry
import pandas as pd
import geopandas as gpd
import time
from geopy.distance import geodesic
import random
from zap import *

setup_logging()

# Função para verificar se um foco está próximo de alguma indústria
def foco_em_industria(foco, industrias, raio_km=1.5):
    foco_coord = (foco['latitude'], foco['longitude'])
    for _, industria in industrias.iterrows():
        industria_coord = (industria['latitude'], industria['longitude'])
        if geodesic(foco_coord, industria_coord).km <= raio_km:
            return True
    return False

def viirs_utc_to_brasilia(acq_date, acq_time):
    # Garante que acq_time tenha 4 dígitos (ex: 332 → '0332')
    time_str = f"{int(acq_time):04d}"
    # Combina data e hora
    datetime_utc = datetime.strptime(f"{acq_date} {time_str}", "%Y-%m-%d %H%M")
    # Converte de UTC para BRT (UTC-3)
    datetime_brt = datetime_utc - timedelta(hours=3)
    datetime_brt = str(datetime_brt)[11:16]
    return datetime_brt

def formatar_mensagem(mensagem):
    try:
        pyautogui.hotkey('win', 'r')
        time.sleep(1)
        pyautogui.write('notepad')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)
        for letra in mensagem:
            pyautogui.write(letra)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        pyautogui.hotkey('alt', 'F4')
        pyautogui.hotkey('right')
        pyautogui.hotkey('enter')
        logging.info("Mensagem copiada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao formatar a mensagem: {e}")

def hora_envio():
    hora_atual = time.strftime("%H:%M")
    hora_envio = '7:'
    r1 = random.randint(0, 3)
    r2 = random.randint(0, 9)
    hora_envio = hora_envio + str(r1) + str(r2)
    logging.info(f"Hora atual: {hora_atual}")
    logging.info(f"Hora de envio: {hora_envio}")
    while True:
        if hora_atual == hora_envio:
            logging.info("Hora de enviar a mensagem!")
            break
        else:
            logging.info(f"Aguardando a hora de envio... Hora atual: {hora_atual}")
            time.sleep(60)
            hora_atual = time.strftime("%H:%M")

def main():
    # Obtendo o dia atual no formato YYYY-MM-DD
    hoje = time.strftime("%Y-%m-%d")
    logging.info(f"Hoje é: {hoje}")

    # Let's set your map key that was emailed to you. It should look something like 'abcdef1234567890abcdef1234567890'
    MAP_KEY = 'your_map_key_here'  # Substitua pelo seu MAP_KEY real

    # now let's check how many transactions we have
    url = 'https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY=' + MAP_KEY

    try:
        df = pd.read_json(url,  typ='series')
    except:
        logging.error("There is an issue with the query. \nTry in your browser: %s" % url)

    def get_transaction_count() :
        count = 0
        try:
            df = pd.read_json(url,  typ='series')
            count = df['current_transactions']
        except:
            logging.error ("Error in our call.")
        return count

    try:
        tcount = get_transaction_count()
        logging.info ('Our current transaction count is %i' % tcount)
        start_count = get_transaction_count()
        end_count = get_transaction_count()

        # URL para o Rio de Janeiro
        rio_bbox = "-45.4,-23.6,-40.9,-20.7"

        # --------------------------------------------- NOAA20 NRT ---------------------------------------------
        noa_url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_NOAA20_NRT/{rio_bbox}/1'
        rio_df_noa = pd.read_csv(noa_url)

        # --------------------------------------------- NOAA21 NRT ---------------------------------------------
        noaa_url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_NOAA21_NRT/{rio_bbox}/1'
        rio_df_noaa = pd.read_csv(noaa_url)

        # --------------------------------------------- MODIS NRT ---------------------------------------------
        modis_url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/MODIS_NRT/{rio_bbox}/1'
        rio_df_modis = pd.read_csv(modis_url)

        # --------------------------------------------- S-NPP NRT ---------------------------------------------
        snpp_url = f'https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/{rio_bbox}/1'
        rio_df_snpp = pd.read_csv(snpp_url)

        # Junta todos os DataFrames em um só
        rio_df = pd.concat([rio_df_noa, rio_df_noaa, rio_df_modis, rio_df_snpp], ignore_index=True)

        # Carregue os dados de focos de calor (df_area) e das plantas industriais (df_industrias)
        df_industrias = pd.read_excel('calor_fixo.xlsx')
        df_industrias = df_industrias.replace(',', '.')
    except Exception as e:
        logging.error(f"Erro ao carregar os dados: {e}")

    try:
        # Adiciona uma coluna indicando se o foco está em indústria
        rio_df['em_industria'] = rio_df.apply(lambda row: foco_em_industria(row, df_industrias), axis=1)
        # Filtra apenas os focos em indústrias
        focos_fixos = rio_df[rio_df['em_industria']]
        # Filtra apenas os focos do dia de hoje e que NÃO são fixos
        rio_df_hoje_sem_fixos = rio_df[(rio_df['acq_date'] == hoje) & (rio_df['em_industria'] != True)]
        rio_shape = gpd.read_file(r'RJ_setores_CD2022\RJ_setores_CD2022.shp')
        rio_shape = rio_shape.to_crs(epsg=4326)  # Converte para o sistema de coordenadas WGS84
        # Converte rio_df_hoje_sem_fixos em GeoDataFrame
        geometry = gpd.points_from_xy(rio_df_hoje_sem_fixos['longitude'], rio_df_hoje_sem_fixos['latitude'])
        gdf_pontos = gpd.GeoDataFrame(rio_df_hoje_sem_fixos, geometry=geometry, crs="EPSG:4326")
        # Faz o spatial join para adicionar o município correspondente
        gdf_pontos = gpd.sjoin(gdf_pontos, rio_shape[['geometry', 'NM_MUN', 'NM_BAIRRO', 'NM_DIST']], how='inner', predicate='within')
        # Renomeia a coluna NM_MUN para municipio
        gdf_pontos = gdf_pontos.rename(columns={'NM_MUN': 'municipio', 'NM_BAIRRO': 'Bairro', 'NM_DIST': 'Distrito'})
        # Remove colunas desnecessárias do join
        gdf_pontos = gdf_pontos.drop(columns=['geometry', 'index_right'])
        # Atualiza o DataFrame original
        rio_df_hoje_sem_fixos = gdf_pontos.reset_index(drop=True)
        rio_df_hoje_sem_fixos = rio_df_hoje_sem_fixos[['latitude', 'longitude', 'acq_date', 'acq_time', 'daynight', 'municipio' , 'Bairro', 'Distrito', 'satellite', 'instrument']]
        # Converter o DataFrame em uma lista de dicionários
        lista_dicts = rio_df_hoje_sem_fixos.to_dict(orient='records')
        logging.info(lista_dicts)

        mensagem = f"Focos de calor encontrados no Rio de Janeiro hoje ({hoje}):\n\n"
        qt = len(rio_df_hoje_sem_fixos)
        if qt == 0:
            mensagem = "Nenhum foco de calor encontrado hoje no Rio de Janeiro."
            logging.info(mensagem)
            return
        for i in range(qt):
            h = viirs_utc_to_brasilia(rio_df_hoje_sem_fixos.iloc[i]['acq_date'], rio_df_hoje_sem_fixos.iloc[i]['acq_time'])
            mensagem += f"Foco {i+1}:\n"
            mensagem += f"Latitude: {rio_df_hoje_sem_fixos.iloc[i]['latitude']}\n"
            mensagem += f"Longitude: {rio_df_hoje_sem_fixos.iloc[i]['longitude']}\n"
            mensagem += f"Data: {rio_df_hoje_sem_fixos.iloc[i]['acq_date']}\n"
            mensagem += f"Hora: {h}\n"
            if rio_df_hoje_sem_fixos.iloc[i]['daynight'] == 'D':
                mensagem += f"Dia ou noite: Dia\n"
            else:
                mensagem += f"Dia ou noite: Noite\n"
            mensagem += f"Municipio: {rio_df_hoje_sem_fixos.iloc[i]['municipio']}\n"
            mensagem += f"Bairro: {rio_df_hoje_sem_fixos.iloc[i]['Bairro']}\n"
            mensagem += f"Distrito: {rio_df_hoje_sem_fixos.iloc[i]['Distrito']}\n"
            mensagem += f"Fonte: {rio_df_hoje_sem_fixos.iloc[i]['satellite']}, {rio_df_hoje_sem_fixos.iloc[i]['instrument']}\n\n"
            print(mensagem)
    except Exception as e:
        logging.error(f"Erro durantes os filtros: {e}")

    try:
        hora_envio()
        formatar_mensagem(mensagem)
        enviar_mensagem("Alerta focos")
    except Exception as e:
        logging.error(f"Erro durante a execução: {e}")

try:
    main()
except Exception as e:
    logging.error(f"Erro durante a execução: {e}")
