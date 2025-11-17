from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        consumo_medio = []

        for impianto in self._impianti:
            consumi_impianti = impianto.get_consumi()
            somma_kwh = 0
            somma_giorni = 0

            if consumi_impianti:
                for consumo in consumi_impianti:
                    if consumo.data.month == mese:
                        somma_kwh += consumo.kwh
                        somma_giorni += 1

            if somma_giorni > 0:
                media = somma_kwh / somma_giorni
                consumo_medio.append((impianto.nome, media))
            else:
                consumo_medio.append((impianto.nome, 0))

        return consumo_medio

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO
        if giorno > 7:
            # Se la sequenza è completa, verifico se il costo corrente è il migliore finora
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale[:]
            return

        # Interrompo se il costo attuale supera già l'ottimo trovato
        if self.__costo_ottimo != -1 and costo_corrente >= self.__costo_ottimo:
            return

        # --- Calcolo del costo ---
        for id_impianto in consumi_settimana.keys():
            indice_giorno = giorno - 1
            costo_variabile_kwh = consumi_settimana[id_impianto][indice_giorno]
            costo_spostamento = 0

            # Calcolo il Costo Fisso (5€) solo se si cambia impianto (si sposta)
            if ultimo_impianto is not None and id_impianto != ultimo_impianto:
                costo_spostamento = 5

            # Calcolo del nuovo costo totale (somma di Costo Variabile + Costo Fisso Spostamento)
            costo_intervento = costo_variabile_kwh + costo_spostamento
            nuovo_costo_totale = costo_corrente + costo_intervento

            # --- Chiamata Ricorsiva ---
            nuova_sequenza = sequenza_parziale + [id_impianto]

            # Passa al giorno successivo
            self.__ricorsione(
                nuova_sequenza,
                giorno + 1,
                id_impianto,  # L'impianto attuale diventa l'ultimo per il giorno successivo
                nuovo_costo_totale,
                consumi_settimana
            )

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO
        consumi_prima_settimana = {}

        for impianto in self._impianti:
            id_impianto = impianto.id
            consumi_impianti = impianto.get_consumi()
            consumi_giornalieri = [0] * 7

            for consumo in consumi_impianti:
                giorno_consumo = consumo.data.day
                mese_consumo = consumo.data.month

                if mese_consumo == mese and 1 <= giorno_consumo <= 7:
                    indice = giorno_consumo - 1
                    consumi_giornalieri[indice] += consumo.kwh

            consumi_prima_settimana[id_impianto] = consumi_giornalieri

        return consumi_prima_settimana