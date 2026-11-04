import os
import shutil

import chainlit as cl
from config import Config
from database import Database
from document_processor import DocumentProcessor
from utils import LLMHelper

db = Database()

dp = DocumentProcessor()
added, updated, removed = dp.process_documents(db)
print(f"Document sync complete: {added} added, {updated} updated, {removed} removed")


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Ricerca candidato",
            message="Cercami un candidato che abbia le competenze di un saldatore",
        ),
    ]


@cl.action_callback("db_stats")
async def on_db_stats(action: cl.Action):
    actions = [
        cl.Action(
            name="db_stats",
            icon="mouse-pointer-click",
            payload={"value": "db_stats"},
            label="Ricalcola Statistiche Database",
        ),
    ]
    db_info = db.get_stats()
    response = await LLMHelper.get_db_stats(db_info)
    await cl.Message(author="system_assistant", content=response, actions=actions).send()


@cl.action_callback("db_reindex")
async def on_db_reindex(action: cl.Action):
    await cl.Message(author="system_assistant", content="reindicizzazione in corso ...").send()
    added, updated, removed = dp.process_documents(db)
    message = f"DB reindicizzato con successo. Document sync complete: {added} added, {updated} updated, {removed} removed"
    await cl.Message(author="system_assistant", content=message).send()


@cl.action_callback("db_remove")
async def on_db_remove(action: cl.Action):
    db.delete_collection()
    message = "Il database e' stato completamente rimosso. E' necessario lanciare il reindex."
    await cl.Message(author="system_assistant", content=message).send()


@cl.on_chat_start
async def start():
    actions = [
        cl.Action(
            name="db_stats",
            icon="mouse-pointer-click",
            payload={"value": "db_stats"},
            label="Statistiche Database",
        ),
        cl.Action(
            name="db_reindex",
            icon="mouse-pointer-click",
            payload={"value": "db_reindex"},
            label="Reindex Database",
        ),
        cl.Action(
            name="db_remove",
            icon="mouse-pointer-click",
            payload={"value": "db_remove"},
            label="Svuota completamente il Database",
        ),
    ]

    await cl.Message(author="system_assistant", content="Informazioni del sistema:", actions=actions).send()

    cl.user_session.set(
        "messages",
        [
            {
                "role": "system",
                "content": """
                    Sei un assistente specializzato nel mondo HR, rispondi in modo professionale, sintetico e pragmatico.
                    Il tuo ruolo è individuare il candidato ideale rispetto alle richieste dell'utente.
                """,
            }
        ],
    )


async def _process_and_index_file(file_path, file_name):
    documents, metadatas, ids = dp.process_single_document(file_path)
    if documents:
        db.remove_document_by_source(file_name)
        db.add_documents(documents, metadatas, ids)
        return f"File '{file_name}' caricato e indicizzato con successo."
    return f"Errore nel processare il file '{file_name}'."


async def _file_upload(file):
    file_name = os.path.basename(file.name)
    dst_file_path = os.path.join(Config.DOCUMENTS_DIR, file_name)
    os.makedirs(Config.DOCUMENTS_DIR, exist_ok=True)
    shutil.move(file.path, dst_file_path)

    return await _process_and_index_file(dst_file_path, file_name)


async def rispondi(messages, prompt):
    messages.append({"role": "user", "content": prompt})

    response_message = cl.Message(author="hr_assistant", content="")
    await response_message.send()

    try:
        stream = LLMHelper.chat(messages)

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                await response_message.stream_token(chunk.choices[0].delta.content)

        messages.append({"role": "assistant", "content": response_message.content})
        await response_message.update()

    except Exception as e:
        error_message = f"Si è verificato un errore: {str(e)}"
        await cl.Message(author="hr_assistant", content=error_message).send()
        print(error_message)


@cl.on_message
async def handle_message(message: cl.Message):
    if message.elements:
        await cl.Message(author="system_assistant", content="Caricamento e indicizzazione documenti").send()

        files = [
            file
            for file in message.elements
            if file.name.lower().endswith(tuple(DocumentProcessor.SUPPORTED_EXTENSIONS))
        ]

        if files:
            results = [await _file_upload(file) for file in files]
        else:
            results = ["Nessun file caricato"]

        await cl.Message(author="system_assistant", content="\n".join(results)).send()
        await cl.Message(author="system_assistant", content=f"Caricati {len(files)} file").send()

        if not message.content.strip():
            return

    user_question = message.content
    intent = LLMHelper.classify_intent(user_question)
    messages = cl.user_session.get("messages", [])

    if intent == "search_cv":
        results = db.query(user_question)

        if not results["documents"][0]:
            error_message = (
                "Nessun curriculum trovato per la tua richiesta.\n"
                "- Prova con parole chiave più specifiche (es. 'developer Python senior')\n"
                "- Invia una nuova richiesta con dettagli aggiuntivi\n"
            )
            await cl.Message(author="hr_assistant", content=error_message).send()
            return

        filename = results["metadatas"][0][0]["source"]
        context_lines = dp.read_first_lines(
            os.path.join(Config.DOCUMENTS_DIR, filename), 20
        )

        context = (
            f"Nome file: {filename}\n"
            f"Estratto dal CV:\n"
            f"```{results['documents'][0][0]}```"
        )

        prompt = LLMHelper.create_prompt(context, user_question, context_lines)
        await rispondi(messages, prompt)

        cl.user_session.set("last_cv_context", context)
        cl.user_session.set("last_cv_header", context_lines)

    elif intent == "info_cv":
        context = cl.user_session.get("last_cv_context", "")
        header = cl.user_session.get("last_cv_header", "")

        if not context:
            error_message = (
                "Non ci sono CV recenti a cui fare riferimento.\n"
                "Prova a cercare prima un candidato con una domanda come:\n"
                "- 'Mostrami i candidati per sviluppatore Python'\n"
                "- 'Chi ha esperienza con Kubernetes?'"
            )
            await cl.Message(author="hr_assistant", content=error_message).send()
            return

        prompt = LLMHelper.create_prompt(context, user_question, header)
        await rispondi(messages, prompt)

    else:
        await cl.Message(author="hr_assistant", content="Non ho capito la tua richiesta. Puoi riformularla?").send()

    cl.user_session.set("messages", messages)
