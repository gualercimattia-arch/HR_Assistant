from config import Config
from openai import OpenAI

client = OpenAI(base_url=Config.AI_API_URL, api_key=Config.AI_API_KEY)


class LLMHelper:
    @staticmethod
    def chat(messages):
        return client.chat.completions.create(
            model=Config.LLM_MODEL, messages=messages, stream=True
        )

    @staticmethod
    async def get_candidate_name(context):
        response = client.chat.completions.create(
            model=Config.LLM_MODEL_LOW,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                      Dato il seguente contesto individua il nome e cognome del candidato e ritorna solo il nome e cognome del candidato. Quello che sto per fornirti e' l'inizio del curriculum vitae del candidato: {context}
                      """,
                }
            ],
        )
        return response.choices[0].message.content

    @staticmethod
    async def get_db_stats(context):
        response = client.chat.completions.create(
            model=Config.LLM_MODEL_LOW,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                      Il tuo compito è quello di descrivere in modo testuale, ma sintetico, le statistiche legate al database dei frammenti indicizzati da questo sistema. Ecco le informazioni necessarie per le statistiche da fornire: {context}
                      """,
                }
            ],
        )
        return response.choices[0].message.content

    @staticmethod
    def classify_intent(user_question):
        system_prompt = """
        Sei un assistente AI che aiuta a elaborare domande sugli annunci di lavoro.
        Classifica la richiesta dell'utente in una delle due categorie:
        - search_cv: l'utente sta cercando un candidato con determinate competenze.
        - info_cv: l'utente sta chiedendo informazioni su un candidato già trovato.
        Rispondi solo con search_cv o info_cv, senza aggiungere altro testo.
        """
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "mi serve un idraulico"},
                {"role": "assistant", "content": "search_cv"},
                {"role": "user", "content": "cerco un esperto di marketing"},
                {"role": "assistant", "content": "search_cv"},
                {"role": "user", "content": "chi conosce Python?"},
                {"role": "assistant", "content": "search_cv"},
                {"role": "user", "content": "qual è la sua email?"},
                {"role": "assistant", "content": "info_cv"},
                {"role": "user", "content": "dove abita?"},
                {"role": "assistant", "content": "info_cv"},
                {"role": "user", "content": "quanti anni di esperienza ha?"},
                {"role": "assistant", "content": "info_cv"},
                {"role": "user", "content": user_question},
            ],
        )
        risposta = response.choices[0].message.content.strip().lower()

        if "info_cv" in risposta:
            return "info_cv"
        if "search_cv" in risposta:
            return "search_cv"
        return risposta

    @staticmethod
    def create_prompt(context, question, context_lines):
        return f"""
        Sei un assistente esperto nella selezione del personale. Devi analizzare il seguente contesto e rispondere alla domanda dell'utente nel modo più chiaro ed efficace possibile.

        **CONTENUTO DEL DOCUMENTO ANALIZZATO:**
        [[[
        {context}
        ]]]

        **DOMANDA DELL'UTENTE:**
        [[[ {question} ]]]

        **Se l'utente sta cercando un CV:**
        - Conferma che nel file individuato è presente un candidato adatto.
        - Spiega perché è adatto, citando le competenze e le esperienze rilevanti.
        - Assicurati di indicare **il nome del file** in cui si trova il profilo.

        **Se l'utente sta chiedendo informazioni su un CV già individuato:**
        - Rispondi in modo conciso e diretto, fornendo **solo l'informazione richiesta**.
        - Evita dettagli superflui o ripetizioni.

        **In entrambi i casi:**
        - Usa il seguente contesto aggiuntivo per individuare il **nome del candidato** o altre informazioni utili:
        [[[ {context_lines} ]]]
        - Assicurati che il testo sia scritto in **italiano corretto** e senza errori.
        """
