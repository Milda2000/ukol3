import math
import json
from pyproj import Transformer, transformer
#vyresit mnozstvi kontejneru



#vypocet vzdalenosti
def Vzdalenost (souradnice1, souradnice2):
    x = abs(souradnice1[0]-souradnice2[0])
    y = abs(souradnice1[1]-souradnice2[1])
    vzdalenost = math.sqrt((x**2)+(y**2))
    return vzdalenost
    

souradnice_adr = []
ulice = []
souradnice_kon = []
typ = []
sum_vzdalenost = 0
min_vzdalenosti = []
max_vzdalenosti = []
vzdalenosti = []

#prevodnik
wgs2jtsk = Transformer.from_crs(4326, 5514, always_xy=True)

#nacteni dat adresnich mist
with open("adresy.geojson", encoding="UTF-8") as file:
    data_adresy = json.load(file)

#nacteni dat o kontejnerech
with open("kontejnery.geojson", encoding="UTF-8") as file2:
    data_kontejnery = json.load(file2)

#ziskani souradnic a typu pristupu kontejneru do listu 
for feature in data_kontejnery["features"]:
    souradnice_kon.append(feature["geometry"]["coordinates"])
    typ.append(feature["properties"]["PRISTUP"])

#ziskani souradnic, jmen ulic a popisných cisel do listu
for feature in data_adresy["features"]:
    souradnice_wgs = feature["geometry"]["coordinates"]
    #prevod souradnic
    souradnice_jtsk = wgs2jtsk.transform(*souradnice_wgs)
    souradnice_adr.append(souradnice_jtsk)
    
    ulice.append(feature["properties"]["addr:street"])
    #nektrefe adresy nemaji cislo popisne
    #cislo_popisne = feature["properties"]["addr:streetnumber"]

#vypocet vzdalenosti pro kazde adresni misto
for item in souradnice_adr:
    #vypocet vzdalenosti mezi adresnim mistem a vsemi kontejnery
    for item2 in souradnice_kon:
        vzdalenost = Vzdalenost(item,item2)
        if vzdalenost <= 10000:
            vzdalenosti.append(vzdalenost)
    #ziskani nejkratsi vzdalenosti
    vzdalenosti.sort()
    min_vzdalenost = vzdalenosti[0]
    if min_vzdalenost > 10000:
        quit()
    min_vzdalenosti.append(min_vzdalenost)
    vzdalenosti.clear()

    sum_vzdalenost += min_vzdalenost

#vypocet prumerne vzdalenosti
prumer = sum_vzdalenost/len(souradnice_adr)
#ziskani maximalni vzdalenosti z listu minimalnich vzdalenosti
min_vzdalenosti.sort()
max_vzdalenost = min_vzdalenosti[-1]
#median
pocet_prvku = len(min_vzdalenosti)
if pocet_prvku%2 == 0:
    median =  (min_vzdalenosti[pocet_prvku/2] + min_vzdalenosti[(pocet_prvku/2)+1])/2
else:
    median = min_vzdalenosti[(pocet_prvku//2)+1]

print(max_vzdalenost)
print(median)
#print(souradnice_wgs)
#print(souradnice_adr)
#print(vzdalenosti)
