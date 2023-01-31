import json,csv,sys
import pandas as pd
from json2table import convert
import numpy as np

# Opening JSON file
f = open('aufgabendaten_clean.json')
data = json.load(f)


t = open('aufgabendaten_clean_aufgabenanzahl.json')
data_erweitert = json.load(t)

fachbereiche=["bcp","erzpsy","vetmed","wiwiss","physik","jfk","geowiss","polsoz","philgeist","sz","rewiss","geschkult","matheinf"]
#Wie viele Lizenzen pro FB
def lizenzanalyse():
    fachbereiche_dict={}
    for eintrag in fachbereiche:
        fachbereiche_dict[eintrag]=0
    
    #{"bcp":0,"erzpsy":0,"vetmed":0,"wiwiss":0,"physik":0,"jfk":0,"geowiss":0,"polsoz":0,"philgeist":0,"sz":0,"rewiss":0,"geschkult":0,"matheinf":0}

    for eintrag in data:
        for key,items in fachbereiche_dict.items():
            if key==eintrag[1]["Fachbereich"]:
                #print(eintrag[1]["Fachbereich"],key)
                anzahl=items
                anzahl+=1
                neuer_eintrag={key:anzahl}
                print(eintrag[0],neuer_eintrag)
                fachbereiche_dict.update(neuer_eintrag)
                break
                #time.sleep(1)

    print(fachbereiche_dict)

#Wie viele Aufgaben durchschnittlich pro Prüfung
def aufgaben_pro_prüfung_generieren():
    for count,i in enumerate(data):
        #print(i[4]["Faecher"],"\n")
        fächer=i[4]["Faecher"]
        

        for count,eintrag in enumerate(fächer):
            zähler=0
            aufgabensammlung=eintrag["Aufgaben"]
            for z in aufgabensammlung:
               # print(z)
                zähler+=1
            k={'Aufgabenanzahl':zähler}
            i[4]["Faecher"][count].update(k)
            #print(i[4]["Faecher"][count])
    print(data)
    
    with open("aufgabendaten_clean_aufgabenanzahl.json","w") as f:
        json.dump(data, f)
    
def aufgaben_pro_fb():
    fachbereiche_dict={}
    for eintrag in fachbereiche:
        fachbereiche_dict[eintrag]=[0,0,0]

    for eintrag in data_erweitert:
        fächer=eintrag[4]["Faecher"]
        fb=eintrag[1]["Fachbereich"]


        anzahl_aufgaben_pro_lizenz=0
        fächer_pro_lizenz=len(fächer)

        anzahl_aufgaben_pro_fach_misc=0
        anzahl_fächer_misc=0

        for items in fächer:
            anzahl_aufgaben_pro_lizenz=anzahl_aufgaben_pro_lizenz+items["Aufgabenanzahl"]
        
        print(fachbereiche_dict.get(fb, False)[0])
 
        fachbereiche_dict.get(fb)[0]=fachbereiche_dict.get(fb)[0]+anzahl_aufgaben_pro_lizenz
        fachbereiche_dict.get(fb)[1]=fachbereiche_dict.get(fb)[1]+fächer_pro_lizenz
        
    for key,fachbereich in fachbereiche_dict.items():
        fachbereich[2]=round((fachbereich[0]/fachbereich[1]), 2)

    df_aufgaben_pro_fb = pd.DataFrame(columns=['Fachbereich', 'Aufgaben', 'Fächer', 'Ratio'])

    for key,item in fachbereiche_dict.items():
        data={"Fachbereich": key, "Aufgaben": str(item[0]), "Fächer": str(item[1]), "Ratio": str(item[2])}
        data = pd.DataFrame([data])
        df_aufgaben_pro_fb = pd.concat([df_aufgaben_pro_fb,data], ignore_index=True)

    
    df_aufgaben_pro_fb.to_excel("aufgaben_pro_fb.xlsx",  encoding="utf-8-sig", index=False)

def aufgabentypen_pro_prüfung():
    aufgabentypen={"MultipleChoice":0,"SpecialAnswer":0,"Cloze":0,"TextOnly":0,"RadioButton":0,"DragDropPicture":0,"DragDropText":0,"MultipleChoiceResponsiveLayout":0,"HotSpotSingle":0,"HotSpotGroup":0,"RadioButtonResponsiveLayout":0}

    zähler_aufgaben=0
    zähler_fächer=0

    for count,i in enumerate(data_erweitert):
        fächer=i[4]["Faecher"]
        
        for count,eintrag in enumerate(fächer):
            zähler_fächer+=1
            aufgabensammlung=eintrag["Aufgaben"]
            
            try:
                for t in aufgabensammlung:
                    for z in t:
                        for key,item in z.items():
                            for key2,item2 in aufgabentypen.items():
                                if item==key2:
                                    zähler_aufgaben+=1
                                    aufgabentypen[key2]+=1

            
            except:
                pass

    #Generieren der CSV
    #Zusammenfassen gleicher Aufgabentypen mit anderem Layout
    mc_aufgaben=0
    radiobutton=0
    hotspot=0
    for key,item in aufgabentypen.items():
        if "MultipleChoice" in key:
            mc_aufgaben=mc_aufgaben+item
        elif "RadioButton" in key:
            radiobutton=radiobutton+item
        elif "HotSpot" in key:
            hotspot=hotspot+item

    aufgabentypen_zusammengefasst={"MultipleChoice_zusammengefasst":mc_aufgaben,"Radiobutton_zusammengefasst":radiobutton,"HotSpot_zusammengefasst":hotspot}
    
    dropliste=["MultipleChoice","MultipleChoiceResponsiveLayout","RadioButton","RadioButtonResponsiveLayout","HotSpotSingle","HotSpotGroup"]
    for key,item in aufgabentypen.items():
        if key not in dropliste:
            aufgabentypen_zusammengefasst[key]=(item)
    aufgabentypen_zusammengefasst = sorted(aufgabentypen_zusammengefasst.items(), key=lambda x: x[1],reverse=True)   

    df_aufgabentyp_pro_prüfung = pd.DataFrame(columns=['Aufgabentyp', 'Häufigkeit', 'Gesamtzahl Aufgaben', 'Ratio'])

    for eintrag in aufgabentypen_zusammengefasst:
        data={"Aufgabentyp":eintrag[0],"Häufigkeit":str(eintrag[1]),"Gesamtzahl Aufgaben":zähler_aufgaben,"Ratio":str(round(eintrag[1]/zähler_aufgaben,3))}
        data = pd.DataFrame([data])
        df_aufgabentyp_pro_prüfung = pd.concat([df_aufgabentyp_pro_prüfung,data], ignore_index=True)
    
    df_aufgabentyp_pro_prüfung['Häufigkeit'] = df_aufgabentyp_pro_prüfung['Häufigkeit'].astype(int)
    df_aufgabentyp_pro_prüfung.loc["Total"] = df_aufgabentyp_pro_prüfung.sum()
    df_aufgabentyp_pro_prüfung.at["Total","Gesamtzahl Aufgaben"] = ""
    df_aufgabentyp_pro_prüfung.at["Total","Ratio"] = ""
    print(df_aufgabentyp_pro_prüfung)

    df_aufgabentyp_pro_prüfung.to_excel("aufgabentypen_pro_pruefung.xlsx", encoding="utf-8-sig", index=False)

def aufgabentypen_pro_prüfung_pro_semester():
    
    semester_sammlung=["Wintersemester 19/20","Sommersemester 2020","Wintersemester 2020/2021","Sommersemester 2021","Wintersemester 2021/2022","Sommersemester 2022","Wintersemester 2022/2023",None]
    
    zähler_aufgaben=0
    zähler_fächer=0
    zähler_fächer_semester=0
    aufgaben_gesamt=[]
    for semester in semester_sammlung:
        zähler_fächer_semester=0
        aufgabentypen={"MultipleChoice":0,"SpecialAnswer":0,"Cloze":0,"TextOnly":0,"RadioButton":0,"DragDropPicture":0,"DragDropText":0,"MultipleChoiceResponsiveLayout":0,"HotSpotSingle":0,"HotSpotGroup":0,"RadioButtonResponsiveLayout":0}
        for count,i in enumerate(data_erweitert):
            if i[2]["Semester"]==semester:
                fächer=i[4]["Faecher"]
                
                for count,eintrag in enumerate(fächer):
                    zähler_fächer+=1
                    zähler_fächer_semester+=1
                    aufgabensammlung=eintrag["Aufgaben"]
                    
                    try:
                        for t in aufgabensammlung:
                            for z in t:

                                for key,item in z.items():
                                    for key2,item2 in aufgabentypen.items():
                                        if item==key2:
                                            zähler_aufgaben+=1
                                            aufgabentypen[key2]+=1

                    except:
                        pass
                        #time.sleep(1)
        
        #Zusammenfassen gleicher Aufgabentypen mit anderem Layout
    
        mc_aufgaben=0
        radiobutton=0
        hotspot=0
        for key,item in aufgabentypen.items():
            if "MultipleChoice" in key:
                mc_aufgaben=mc_aufgaben+item
            elif "RadioButton" in key:
                radiobutton=radiobutton+item
            elif "HotSpot" in key:
                hotspot=hotspot+item

        aufgabentypen_zusammengefasst={"MultipleChoice_zusammengefasst":mc_aufgaben,"Radiobutton_zusammengefasst":radiobutton,"HotSpot_zusammengefasst":hotspot}
        
        dropliste=["MultipleChoice","MultipleChoiceResponsiveLayout","RadioButton","RadioButtonResponsiveLayout","HotSpotSingle","HotSpotGroup"]
        for key,item in aufgabentypen.items():
            if key not in dropliste:
                update_item={key,item}
                aufgabentypen_zusammengefasst[key]=(item)
        aufgabentypen_zusammengefasst = sorted(aufgabentypen_zusammengefasst.items(), key=lambda x: x[1],reverse=True)   

        semester_json=[{semester:aufgabentypen_zusammengefasst}]
        aufgaben_gesamt.append(semester_json)


    columns=["Aufgabentypen"]
    for i in aufgaben_gesamt:
        for e in i:
            for key,items in e.items():
                if key==None:
                    key="Nicht zuordenbar"
                columns.append(key)


    df_aufgabentypen_pro_prüfung_pro_semester = pd.DataFrame(columns=columns)

    aufgabentypen_csv={}
    for eintrag in aufgabentypen_zusammengefasst:
        aufgabentypen_csv[eintrag[0]]=[]

    for i in aufgaben_gesamt:
        for e in i:
            for key,items in e.items():
               # print(items)
                for eintrag in items:
                    for key3,eintrag2 in aufgabentypen_csv.items():
                        print(eintrag2)
                        if eintrag[0]==key3:
                            eintrag2.append(eintrag[1])
    
    for aufgabentyp, anzahl in aufgabentypen_csv.items():
        data={"Aufgabentypen":aufgabentyp}
        zahlen_zip=dict(zip(columns[1:-1], anzahl))
        
        data=data | zahlen_zip
        data = pd.DataFrame([data])
        df_aufgabentypen_pro_prüfung_pro_semester = pd.concat([df_aufgabentypen_pro_prüfung_pro_semester,data], ignore_index=True)


    for eintrag in columns[1:-1]:
        liste_für_ratio = df_aufgabentypen_pro_prüfung_pro_semester[eintrag].tolist()
        liste_mit_ratio=[]

        for zahl in liste_für_ratio:
            liste_mit_ratio.append(round(zahl/sum(liste_für_ratio),2))

        index=df_aufgabentypen_pro_prüfung_pro_semester.columns.get_loc(eintrag)
        df_aufgabentypen_pro_prüfung_pro_semester.insert(index+1, f"Ratio {index+1}", liste_mit_ratio)
    
    df_aufgabentypen_pro_prüfung_pro_semester.loc["Total"] = df_aufgabentypen_pro_prüfung_pro_semester.sum()
    df_aufgabentypen_pro_prüfung_pro_semester.at["Total","Aufgabentypen"] = ""
    print(df_aufgabentypen_pro_prüfung_pro_semester)
    
    df_aufgabentypen_pro_prüfung_pro_semester.to_excel("aufgabentypen_pro_prüfung_pro_semester.xlsx", encoding="utf-8-sig", index=False)

def aufgabenanzahl_pro_fb_semester():
    
    semester_sammlung=["Wintersemester 19/20","Sommersemester 2020","Wintersemester 2020/2021","Sommersemester 2021","Wintersemester 2021/2022","Sommersemester 2022","Wintersemester 2022/2023",None]

    ansammlung_gesamt=[]
    for semester in semester_sammlung:
        fachbereiche={"bcp":[0,0,0],"erzpsy":[0,0,0],"vetmed":[0,0,0],"wiwiss":[0,0,0],"physik":[0,0,0],"jfk":[0,0,0],"geowiss":[0,0,0],"polsoz":[0,0,0],"philgeist":[0,0,0],"sz":[0,0,0],"rewiss":[0,0,0],"geschkult":[0,0,0],"matheinf":[0,0,0]}

        for eintrag in data_erweitert:
            if eintrag[2]["Semester"] not in semester_sammlung:
                
                pass
                
            if eintrag[2]["Semester"]==semester:
                #print(eintrag)
                schalter_c=True
                fächer=eintrag[4]["Faecher"]

                fb=eintrag[1]["Fachbereich"]
                #print(fächer,fb)

                anzahl_aufgaben_pro_fach=0
                fächer_pro_lizenz=len(fächer)

                anzahl_aufgaben_pro_fach_misc=0
                anzahl_fächer_misc=0

                for items in fächer:
                    anzahl_aufgaben_pro_fach=anzahl_aufgaben_pro_fach+items["Aufgabenanzahl"]
                
                schalter=False
                for key,fachbereich in fachbereiche.items():
                    if fb==key:
                        fachbereich[0]=fachbereich[0]+anzahl_aufgaben_pro_fach
                        fachbereich[1]=fachbereich[1]+fächer_pro_lizenz
                        #print(key,fachbereich)
                        schalter=True

                if schalter==False:
                    anzahl_aufgaben_pro_fach_misc=anzahl_aufgaben_pro_fach_misc+anzahl_aufgaben_pro_fach
                    anzahl_fächer_misc=anzahl_fächer_misc+fächer_pro_lizenz
                    #print(eintrag)



            for key,fachbereich in fachbereiche.items():
                if fachbereich[0]!=0:
                    fachbereich[2]=round((fachbereich[0]/fachbereich[1]),2)


        ansammlung_gesamt.append({semester:fachbereiche})
    

    #Aufbau des pd Dataframes
    df = pd.DataFrame()
    fachbereiche_dataframe=[]
    for key,eintrag in fachbereiche.items():
        fachbereiche_dataframe.append(key)
    #print(fachbereiche_dataframe)
    df.insert(0, f'FB', fachbereiche_dataframe)

    df = pd.DataFrame()

    for sem in semester_sammlung:  		
        sem_head=sem
        if sem_head == None:
            sem_head = "Nicht zuordenbar"
        header = pd.MultiIndex.from_product([[sem_head],
                                            ['Anzahl Aufgaben','Anzahl Fächer','Ratio']],
                                            )
        
        data=[]
        for eintrag in ansammlung_gesamt:
            for key, value in eintrag.items():
                if key == sem:
                    for key2, value2 in value.items():
                        data.append(value2)
            
        #print(data)
        df123 = pd.DataFrame(
                        columns=header, 
                        index=fachbereiche.keys(),
                        data=data)

        df=pd.concat([df,df123],axis=1)

        print(df123)

    print(df)
    df.loc["Total"] = df.sum()
    df.to_excel("aufgabenanzahl_pro_fb_semester.xlsx", encoding="utf-8-sig", index=True)
    """
    header = pd.MultiIndex.from_product([["Wintersemester 21/22"],
                                        ['Anzahl Aufgaben','Anzahl Fächer','Ratio']],
                                        )
    df1234 = pd.DataFrame(
                    columns=header, 
                    index=['one'],
                    data=[[10,10,10]])

    df322=pd.concat([df123,df1234],axis=1)
    print(df322)
    #print(f"Nicht zuordnenbar: Fächer: {anzahl_fächer_misc}, Aufgaben: {anzahl_aufgaben_pro_fach_misc} \n\n")
    """

def freitext_antworten_bepunktet():
    aufgabentypen={"TextOnly":0}
    zähler_fächer=0
    zähler_lizenzen=0
    zähler_freitext_gesamt=0
    zähler_freitext_bepunktet=0
    zähler_freitext_unbepunktet=0

    for count,i in enumerate(data_erweitert):
        schalter_2=False
        fächer=i[4]["Faecher"]
        

        for count,eintrag in enumerate(fächer):
            schalter=False
            for t in eintrag["Aufgaben"]:
                
                for key,items in t[0].items():
                        
                    	if items=="TextOnly":
                            zähler_freitext_gesamt+=1

                            if float(t[1]["Average"])>0:
                                schalter=True
                                schalter_2=True
                                zähler_freitext_bepunktet+=1
                            else:
                                print(i[0],eintrag["Fach-ID"])
                                zähler_freitext_unbepunktet+=1

            if schalter:
                zähler_fächer+=1
        if schalter_2:
            zähler_lizenzen+=1

    

    print(f"Freitextaufgaben gesamt: {zähler_freitext_gesamt}, Freitextaufgaben bepunktet: {zähler_freitext_bepunktet}, Freitextaufgaben unbepunktet: {zähler_freitext_unbepunktet}, Fächer mit mindestens einer bepunkteten Freitextaufgabe: {zähler_fächer}, Lizenzen mit mindestens einer bepunkteten Freitextaufgabe: {zähler_lizenzen}")
    print(f"Essay tasks total: {zähler_freitext_gesamt}, essay tasks graded: {zähler_freitext_bepunktet}, essay tasks not graded: {zähler_freitext_unbepunktet}, subjects with at least one graded essay task: {zähler_fächer}, licenses with at least one graded essay task: {zähler_lizenzen}")

aufgabenanzahl_pro_fb_semester()