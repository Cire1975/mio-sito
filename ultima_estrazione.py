import requests
from bs4 import BeautifulSoup
import os

def estrai_e_salva_ultima_estrazione_aggiornata():
    """
    Scarica l'ultima estrazione del Lotto dal nuovo sito, estrae i dati rilevanti
    utilizzando i nuovi selettori e li salva in un file HTML formattato.
    """
    # 1. Definizioni AGGIORNATE
    URL = "https://www.estrazionedellotto.it/" # Nuovo URL fornito
    FOLDER_PATH = r"C:\Flutter\sito_estrazioni\sito\templates" # Percorso della cartella
    
    try:
        # 2. Richiesta HTTP
        print(f"Sto scaricando la pagina da: {URL}...")
        response = requests.get(URL)
        response.raise_for_status()

        # 3. Parsing dell'HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 4. Estrazione dell'elemento contenitore principale
        # Troviamo il div contenitore con la classe "tabellaLotto"
        tabella_lotto_container = soup.find('div', class_='tabellaLotto')

        if not tabella_lotto_container:
            print("Errore: Impossibile trovare il contenitore principale ('tabellaLotto').")
            return
            
        # 5. Estrazione Data e Numero Estrazione (NUOVI SELETTORI)
        
        # Il numero di estrazione è in <span class="estr-n">
        num_estrazione_tag = tabella_lotto_container.find('span', class_='estr-n')
        num_estrazione = num_estrazione_tag.text.strip() if num_estrazione_tag else "N. ESTRAZIONE SCONOSCIUTO"

        # La data è in <span class="datetime">
        data_estrazione_tag = tabella_lotto_container.find('span', class_='datetime')
        data_estrazione = data_estrazione_tag.text.strip() if data_estrazione_tag else "DATA SCONOSCIUTA"

        print(f"Estrazione trovata: {num_estrazione} del {data_estrazione}")
        
        # 6. Estrazione dei Dati delle Ruote e Numeri
        
        # Troviamo la tabella con la classe "tabellaEstrazioni" all'interno del container
        tabella_estrazioni = tabella_lotto_container.find('table', class_='tabellaEstrazioni')
        tbody = tabella_estrazioni.find('tbody') if tabella_estrazioni else None
        righe_dati = ""

        if tbody:
            # Iteriamo su tutte le righe <tr> all'interno del <tbody>
            for i, riga in enumerate(tbody.find_all('tr')):
                colonne = riga.find_all('td')
                if len(colonne) >= 6: # Ci aspettiamo almeno 6 colonne (Ruota + 5 numeri)
                    
                    # Il nome della Ruota
                    ruota = colonne[0].text.strip()
                    
                    # I 5 numeri estratti. NOTA: qui i numeri sono diretti nel <td>, non in uno <span>
                    numeri = [td.text.strip() for td in colonne[1:6]]
                    
                    # Formattiamo la riga per il file HTML di output
                    # Alterniamo la classe per le righe (come nell'esempio: trNumero-arch)
                    tr_class = 'trNumero-arch' if (i + 1) % 2 == 0 else ''
                    
                    # Controlliamo l'ultima estrazione (il 5° numero) per applicare la classe "oro"
                    quinto_numero = numeri[4] if len(numeri) == 5 else ''
                    
                    righe_dati += f"""
<tr>
<td class="nomeRuota-arch estratto-arch">{ruota}</td>
<td><span>{numeri[0]}</span></td>
<td><span>{numeri[1]}</span></td>
<td><span>{numeri[2]}</span></td>
<td><span>{numeri[3]}</span></td>
<td><span class="oro">{quinto_numero}</span></td>
</tr>"""



        # 7. Costruzione del Contenuto HTML di Output
        
        # Puliamo la data per il nome del file (es: "Martedì 14 ottobre 2025" -> "14102025.html")
        # Tentiamo una pulizia più robusta:
        try:
            from datetime import datetime
            # Ipotizziamo che BeautifulSoup abbia estratto "Martedì 14 ottobre 2025"
            # Cerchiamo solo la parte della data numerica se possibile.
            # Se l'estrazione è "Martedì 14 ottobre 2025", non è facile convertirla direttamente. 
            # Per semplicità, estraiamo solo i caratteri alfanumerici.
            
            # Una soluzione più robusta sarebbe mappare i mesi italiani
            data_pulita_parts = data_estrazione.split()
            # Tentativo di isolare la parte numerica (es. 14, 10, 2025)
            # In assenza di una formattazione chiara, usiamo una stringa semplice.
            import re
            match = re.search(r'(\d+)\s+([\w\s]+)\s+(\d{4})', data_estrazione)
            if match:
                day, month_name, year = match.groups()
                # Una mappatura dei mesi non è ideale senza importare altre librerie (locale), 
                # ma per un output rapido, useremo una semplice stringa.
                nome_file = "ultima_estrazione.html"
            else:
                 # Fallback: solo caratteri alfanumerici
                nome_file = "".join(c for c in data_estrazione if c.isalnum()) + ".html"

        except Exception:
            nome_file = "".join(c for c in data_estrazione if c.isalnum()) + ".html"
            
        full_path = os.path.join(FOLDER_PATH, nome_file)

        # Usiamo l'esempio di HTML fornito per la struttura di output
        contenuto_html = f"""<html>
<head>
<title>Estrazioni Lotto Anno Corrente</title>
</head>
<body>
<table class="tabellaEstrazioni-arch">
<thead>
<tr class="rif-estr-arch">
<td class="estr-n-arch" colspan="3">{num_estrazione}</td>
<td class="datetime-arch" colspan="3">del {data_estrazione}</td>
</tr>
<tr>
<th class="nomeRuota-arch thRuota-arch">RUOTA</th>
<th class="thEstratto-arch">1<sup>o</sup> estr.</th>
<th class="thEstratto-arch">2<sup>o</sup> estr.</th>
<th class="thEstratto-arch">3<sup>o</sup> estr.</th>
<th class="thEstratto-arch">4<sup>o</sup> estr.</th>
<th class="thEstratto-arch">5<sup>o</sup> estr.</th>
</tr>
</thead>
<tbody>
{righe_dati.strip()}
</tbody>
</table>
</body>
</html>"""

        # 8. Salvataggio del File

        # Creiamo la cartella se non esiste
        os.makedirs(FOLDER_PATH, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(contenuto_html)
        
        print(f"\n✅ Estrazione salvata con successo in: {full_path}")

    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta web: {e}")
    except Exception as e:
        print(f"Si è verificato un errore inaspettato: {e}")

# Chiamata alla funzione aggiornata
estrai_e_salva_ultima_estrazione_aggiornata()