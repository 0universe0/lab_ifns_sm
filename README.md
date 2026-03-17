# lab_ifns_sm
lab reports repo

## TODO

### general

- add logic to put saved canvases into specific subdirectory [?]
- move functions Zscore MeanError to utils.py

### campo magnetico al variare della corrente

- aggiungere errori di default (fissali tipo a 0.1, poi li metteremo giusti con le specifiche degli strumenti) agli array di corrente e campo magnetico
- aggiungere ai test Z con le funzioni di simo gli array con gli errori 

### tensione di hall al variare di i

- dare una sistemata al codice (del tipo: aggiungere qualche commento su quello che stiamo facendo/che array si riferisce a che serie di dati)
- da tutti i parametri (forse solo i coefficienti angolari? bisogna pensarci) dei fit con B != 0, sottrarre i parametri del fit con B=0 (con propagazione errori)
- verificare che tutte le quote siano compatibili con 0
- fare un fit lineare delle quote contro B in modo da stimare R_H

### tensione di hall al variare di B

- pulire/commentare il codice (tutti gli array scritti da luca non sono dei campi magnetici ma delle correnti)
- usare le rette dei cicli di isteresi per creare gli array dei campi magnetici a partire da quelli di corrente (forse c’è un modo migliore?) propagando gli errori
- sottrarre (o sommare, dipende dai punti di vista) anche il contributo ohmico a tutte le rette (cioè la tensione di Hall misurata allo specifico valore di corrente quando B=0: achtung in realtà bisogna interpolare usando la retta del fit V_H(i) a B=0 se vogliamo essere precissisimi)
- verificato che le quote di tutti i fit siano compatibili con 0, fare un fit lineare con tutti i coefficienti angolari per stimare R_H

### mobilità dei portatori

- fare fit lineare della caratteristica I(V) della sonda
- sostituire dati giusti (con propagazione errore) nel calcolo di mu
