import math
import json
from pyproj import Transformer, transformer

def geojson(adresy_vzdalenosti, kontejnery_vzdalenosti, adresy_geojson):
    #data ={}
    #adresni_mista = {}
    #souradnice = {}
    #data["adresni mista"] = adresni_mista,souradnice
    #adresni_mista["features"] =[]
    #souradnice["geometry"] =[]
    for item,item2 in zip(adresy_vzdalenosti.items(),kontejnery_vzdalenosti.items()):
        adresy_geojson["features"]["properties"]["id"] = item2[0]
        #adresni_mista["features"].append({"adresa": item[0],"vzdalenost":item[1],"id":item2[0]})
        #souradnice["geometry"].append({"x":souradnice_adr[item[0]][0],"y":souradnice_adr[item[0]][1]})
    with open('adresy_kontejnery.geojson', 'w', encoding="UTF-8") as outfile:
        json.dump(adresy_geojson, outfile)

#vypocet vzdalenosti
def Vzdalenost (souradnice_adr, souradnice_kon, typ_kontejneru):
    min_vzdalenosti_adr ={}
    min_vzdalenosti_kon = {}
    vzdalenosti = {}
    vzdalenosti_kon ={}
    for items in souradnice_adr.items():
        vzdalenost_default = 10000
        #vypocet vzdalenosti mezi adresnim mistem a vsemi kontejnery
        adresa = items[0]
        souradnice1 = items[1]
        for items2,items3 in zip(souradnice_kon.items(),typ_kontejneru.items()):
            adr_kon = items2[0].split(" ")
            kon_ulice = adr_kon[0]
            kon_cp = adr_kon[1].split("/")
            try:
                adr_kon_uprava = kon_ulice,kon_cp[1]
            except IndexError:
                adr_kon_uprava = kon_ulice
            kon_adresa = " ".join(adr_kon_uprava)
            souradnice2 = items2[1]
            id_kon = items3[0]
            typ_kon = items3[1]
            if typ_kon == "obyvatelům domu":
                if kon_adresa == adresa:
                    #adresa:vzdalenost = 0
                    vzdalenosti[adresa] = 0
                    #id:vzdalenost = 0
                    vzdalenosti_kon[id_kon] = 0
                else:
                    continue
            else:
                x = abs(souradnice1[0]-souradnice2[0])
                y = abs(souradnice1[1]-souradnice2[1])
                vzdalenost = math.sqrt((x**2)+(y**2))
                if vzdalenost <= vzdalenost_default:
                    vzdalenost_default = vzdalenost
                    #adresa:vzdalenost
                    min_vzdalenosti_adr[adresa] = vzdalenost
                    #id:vzdalenost
                    min_vzdalenosti_kon[id_kon] = min_vzdalenosti_adr[adresa]

        #vzdalenosti k jednotlivym kontejnerum z adresy setridene podle velikosti
        #vzdalenosti_adr_sort = dict(sorted(vzdalenosti.items(),key=lambda x: x[1]))
        #vzdalenosti od jednotlivych kontejneru(id) k adresam setridene podle velikosti
        #vzdalenosti_kon_sort = dict(sorted(vzdalenosti_kon.items(),key=lambda x: x[1]))
        #adresa:nejkratsi vzdalenost
        #min_vzdalenosti_adr[adresa] = list(vzdalenosti_adr_sort.values())[0]
        #id:nejkratsi vzdalenost
        #min_vzdalenosti_kon[adresa] = list(vzdalenosti_kon_sort.values())[0]

    #nejkratsi vzdalenosti serazene podle velikosti, adresy
    min_vzdalenosti_sort = dict(sorted(min_vzdalenosti_adr.items(),key=lambda x: x[1]))

    geojson(min_vzdalenosti_adr,min_vzdalenosti_kon, souradnice_adr)

    return min_vzdalenosti_sort
        

souradnice_kon = {}
typ_kontejneru = {}
souradnice_adr = {}

#prevodnik
wgs2jtsk = Transformer.from_crs(4326, 5514, always_xy=True)

#nacteni dat adresnich mist
with open("adresy.geojson", encoding="UTF-8") as file:
    data_adresy = json.load(file)

#nacteni dat o kontejnerech
with open("kontejnery.geojson", encoding="UTF-8") as file2:
    data_kontejnery = json.load(file2)

#ziskani souradnic a typu pristupu kontejneru slovniku 
for feature in data_kontejnery["features"]:
    souradnice_kon[feature["properties"]["STATIONNAME"]] = feature["geometry"]["coordinates"]
    typ_kontejneru[feature["properties"]["ID"]] = feature["properties"]["PRISTUP"]

#ziskani souradnic, jmen ulic a popisných cisel do slovniku
for feature in data_adresy["features"]:
    souradnice_wgs = feature["geometry"]["coordinates"]
    #prevod souradnic
    souradnice_jtsk = wgs2jtsk.transform(*souradnice_wgs)
    try:
        ulice = feature["properties"]["addr:street"]
        ulicni_cislo = feature["properties"]["addr:streetnumber"]
        adr = ulice + " " + ulicni_cislo
        souradnice_adr[adr] = souradnice_jtsk
    except KeyError:
        souradnice_adr[adr] = souradnice_jtsk

#vypocet min vzdalenosti od kontejneru pro kazde adresni misto
min_vzdalenosti = Vzdalenost(souradnice_adr, souradnice_kon, typ_kontejneru)
prumer = sum(min_vzdalenosti.values())/len(min_vzdalenosti)
max_vzdalenost = list(min_vzdalenosti.items())[-1]
#median
pocet_prvku = len(min_vzdalenosti)
if pocet_prvku%2 == 0:
    index = int(pocet_prvku/2)
    median =  (list(min_vzdalenosti.values())[index] + list(min_vzdalenosti.values())[index+1])/2
else:
    median = list(min_vzdalenosti.values())[(pocet_prvku//2)+1]

#VYSTUP
#pocet adresnich mist a kontejneru
print(f"Bylo načteno {len(souradnice_adr)} adresních míst.")
print(f"Bylo načteno {len(souradnice_kon)} kontejnerů.")
print(f"Průměrná vzdálenost ke kontejneru je {prumer} metrů.")
print(f"Medián vzdálenosti je {median} metrů.")
print(f"Nejdále mají ke kontejneru na adrese {max_vzdalenost[0]} a to {round(max_vzdalenost[1],0)} metrů.")