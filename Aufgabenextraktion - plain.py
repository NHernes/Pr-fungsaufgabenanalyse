import requests,json, numpy as np
import time
from threading import Thread

def token():
    payload = {
        'grant_type': '',
        'client_id': "",
        'client_secret': "",

        'username': "",
        'password': ""
    }

    r = requests.post("https://fub.lplus-teststudio.de/token", 
        data=payload)
    token=json.loads(r.text)["access_token"]
    return token

access_token=token()

headers={
    "Authorization": f"Bearer {access_token}"
}


#Ziehe alle Lizenzen
r = requests.get("https://fub.lplus-teststudio.de/publicapi/v1/licences", 
    headers=headers)

alle_lizenzen=r.json()

Liste_Lizenzen=[]
lizenzen_skip=["demoprüfung", "doz", "probe", "cedis"]
anzahl_lizenzen=0
for count,eintrag in enumerate(alle_lizenzen):
    if any(lizenz_skip in eintrag["name"].lower() for lizenz_skip in lizenzen_skip):
        print(f"Diese Lizenz wurde ausgelassen: {eintrag['name']}")
        continue
    else:
        Übersicht_Fach=[{"Lizenzname":eintrag["name"]},{"Lizenz-ID":eintrag["id"]},{"Faecher":[]}]
        Liste_Lizenzen.append(Übersicht_Fach)
        anzahl_lizenzen+=1
    print(f"abgerufene Lizenzen: {anzahl_lizenzen}")



#Ziehe Alle zugehörigen Fächer

anzahl_fächer=0
for count,eintrag in enumerate(Liste_Lizenzen):
    lizenz_id=eintrag[1]["Lizenz-ID"]

    r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects", 
        headers=headers)
    #print(r.raise_for_status)
    einzellizenz=r.json()
    #print(einzellizenz)

    for zähler,fach in enumerate(einzellizenz):
        if any(lizenz_skip in fach["name"].lower() for lizenz_skip in lizenzen_skip):
            print(f"Dieses Fach wurde ausgelassen: {fach['name']}")
            continue
        else: 
            eintrag[2]["Faecher"]+=[{"Fach-ID":fach["id"]}]
            anzahl_fächer+=1
            print(f"Abgerufene Fächer: {anzahl_fächer}")


#Ziehe die Aufgaben-Ids für jedes Fach
Anzahl_Aufgaben=0
liste_aufgabennummern=[]
for count1,eintrag in enumerate(Liste_Lizenzen):
    for count2, inhalt in enumerate(eintrag[2]["Faecher"]):
        inhalt["Aufgaben"]=[]

        fach_id=inhalt["Fach-ID"]
        r = requests.get(f"https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz_id}/subjects/{fach_id}/questions", 
        headers=headers)
        
        try:
            fachaufgaben=r.json()
            for count,ergebnis in enumerate(fachaufgaben):
                if ergebnis["questionId"] not in liste_aufgabennummern:
                    liste_aufgabennummern.append(ergebnis["questionId"])
                    liste_aufgabennummern.sort()

                inhalt["Aufgaben"].append([{ergebnis["questionId"]:""},{"Average":""},{"Max":""}])
                Anzahl_Aufgaben+=1
                print(f"Abgerufene Aufgaben: {Anzahl_Aufgaben}")
        except:

            print(f"ACHTUNG - FEHLER beim Abruf des Aufgabensets \n Fach: {fach_id,r.raise_for_status} \n\n")

liste_aufgabennummern = [str(i) for i in liste_aufgabennummern]
with open("anzahl_unique_ids.txt","w") as f:
    f.write('\n'.join(liste_aufgabennummern))

#Ziehe die Aufgabentypen für jede Aufgabe
anzahl_gezogene_aufgaben=0
checker=0

#Effektiv: Ausschalten von Multithreading, um Produktivsystem nicht zu überlasten
if len(Liste_Lizenzen)<100000000000000:
    for count,eintrag in enumerate(Liste_Lizenzen):
        for count, inhalt in enumerate(eintrag[2]["Faecher"]):
            for z in inhalt["Aufgaben"]:
                for key,values in z[0].items():
                    aufgabe=key
                    lizenz=eintrag[1]["Lizenz-ID"]
                    fach=inhalt["Fach-ID"]
                    

                    if anzahl_gezogene_aufgaben>checker:
                        access_token=token()
                        headers={
                            "Authorization": f"Bearer {access_token}"
                        }
                        checker=checker+100
                        print(headers)
                        print("Token reset")


                    url=f"https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz}/subjects/{fach}/questions/{aufgabe}"
                    r = requests.get(url, headers=headers)
                    stop=r.status_code

                    try:
                        d=r.json()
                        anzahl_gezogene_aufgaben+=1

                        print(f"Detailinformationen abgerufen: {anzahl_gezogene_aufgaben} Aufgaben von insgesamt {Anzahl_Aufgaben}")
                        
                        time.sleep(0.05)

                        if stop == 500:
                            z[0][aufgabe]=None
                            z[1][aufgabe]=None
                            z[2][aufgabe]=None
                        else:
                            z[0][aufgabe]=d["questionKind"]
                            z[1]["Average"]=d["averagePointsForQuestion"]
                            z[2]["Max"]=d["maxPointsForQuestionItem"]
                    
                    except:
                        print(f"ACHTUNG - FEHLER beim Aufgabenabruf \n {r.text,r.raise_for_status} \n\n\n\n")

###Threading nicht weiter benutzen
else:
    pieces = 6
    new_arrays = np.array_split(Liste_Lizenzen, pieces)


    manipulierte_Masterliste=[]

    def threading_aufgabenanalyse(array):
        for count,eintrag in enumerate(array):
            for count, inhalt in enumerate(eintrag[2]["Faecher"]):
                for z in inhalt["Aufgaben"]:
                    for key,values in z[0].items():
                        if values=="TextOnly":
                            aufgabe=key
                            lizenz=eintrag[1]["Lizenz-ID"]
                            fach=inhalt["Fach-ID"]

                            url=f"https://fub.lplus-teststudio.de/publicapi/v1/licences/{lizenz}/subjects/{fach}/questions/{aufgabe}"
                            r = requests.get(url, headers=headers)
                            stop=r.status_code
                            d=r.json()

                            if stop==500:
                                z[0][aufgabe]=None
                            else:
                                z[1]["Average"]=d["averagePointsForQuestion"]
                        else:
                            z[1]["Average"]=None

        manipulierte_Masterliste.append(eintrag)


    threads = []
    for i in range(0,6):
        threads.append(Thread(target=threading_aufgabenanalyse, args=(new_arrays[i],)))
        threads[-1].start()
    for thread in threads:
        thread.join()

    finale_liste=[]
    for i in manipulierte_Masterliste:

        listeneintrag=i.tolist()
        finale_liste.append(listeneintrag)


with open('aufgabendaten.json', 'w') as f:
    json.dump(Liste_Lizenzen, f)

print("Extraktion abgeschlossen")