from django.shortcuts import render
import os
import json
import requests
from mistralai import Mistral, ToolMessage  # si vous en avez besoin
from dotenv import load_dotenv

load_dotenv()

# Récupération de l'API key et initialisation du client Mistral
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

# Spécifiez le modèle à utiliser
model = 'mistral-large-latest'

# URL de l'API Mistral
api_url = "https://api.mistral.ai/v1/chat/completions"

# Définition d’un outil pour récupérer les références (exemple)
get_information_tool = {
    "type": "function",
    "function": {
        "name": "get_information",
        "description": "Obtenir des informations depuis une source externe avec les références.",
        "parameters": {}
    }
}

def get_information():
    """
    Fonction simulant le retour d’informations référencées.
    Vous pouvez ici adapter la logique pour récupérer vos véritables références.
    """
    references = {
        "0": {"title": "Source Exemple", "url": "https://exemple.com"}
    }
    return json.dumps(references)

def chatbot(request):
    bot_response = None
    references_info = None

    # Récupération (ou initialisation) de l’historique depuis la session
    chat_history = request.session.get('chat_history', [])
    if not chat_history:
        # Le message système est défini une fois
        chat_history.append({
            "role": "system",
            "content": "Réponds toujours en français en fournissant des références."
        })

    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        if user_input:
            # Ajout du message de l’utilisateur à l’historique
            chat_history.append({"role": "user", "content": user_input})

            try:
                # Construction de la charge utile à envoyer à l'API
                payload = {
                    "model": model,
                    "messages": chat_history
                }
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                # Premier appel à l’API
                response = requests.post(
                    api_url,
                    headers=headers,
                    data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
                )
                
                if response.status_code == 200:
                    result = response.json()
                    message = result["choices"][0]["message"]
                    
                    # Vérifier si la réponse contient un appel d’outil pour des références
                    if "tool_calls" in message:
                        # Récupère le premier appel d’outil
                        tool_call = message["tool_calls"][0]
                        # Ajoute le message initial (contenant l'appel) à l’historique
                        chat_history.append(message)
                        
                        # Appeler la fonction get_information pour simuler la récupération de références
                        tool_result = get_information()
                        
                        # Créer un message de réponse « tool message »
                        tool_message = {
                            "role": "tool",
                            "name": tool_call["function"]["name"],
                            "content": tool_result,
                            "tool_call_id": tool_call.get("id", None)
                        }
                        # Ajout de la réponse de l’appel d’outil à l’historique
                        chat_history.append(tool_message)
                        
                        # Réaliser un nouvel appel à l’API avec l’historique mis à jour
                        payload = {
                            "model": model,
                            "messages": chat_history
                        }
                        response = requests.post(
                            api_url,
                            headers=headers,
                            data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
                        )
                        if response.status_code == 200:
                            result = response.json()
                            message = result["choices"][0]["message"]

                    # Traitement de la réponse finale
                    # Certains modèles renvoient une chaîne de caractères simple, d'autres renvoient une liste de "chunks"
                    if isinstance(message["content"], list):
                        final_text = ""
                        refs_used = []
                        for chunk in message["content"]:
                            if chunk.get("type") == "text":
                                final_text += chunk.get("text", "")
                            elif chunk.get("type") == "reference":
                                refs_used.update(chunk.get("reference_ids", []))
                        
                        bot_response = final_text
                        
                        if refs_used:
                            references_info = []
                            # Ici nous récupérons les références retournées par get_information (simulé)
                            refs_data = json.loads(get_information())
                            for i, ref_id in enumerate(set(refs_used), 1):
                                if str(ref_id) in refs_data:
                                    ref = refs_data[str(ref_id)]
                                    references_info.append(f"{i}. {ref['title']}: {ref['url']}")
                    else:
                        # Si la réponse est une simple chaîne
                        bot_response = message["content"]

                    # Ajout de la réponse finale de l’assistant dans l’historique
                    chat_history.append({"role": "assistant", "content": bot_response})
                else:
                    bot_response = f"Erreur API: {response.status_code} - {response.text}"
            except Exception as e:
                bot_response = f"Erreur : {str(e)}"

            # Sauvegarde de l’historique dans la session
            request.session['chat_history'] = chat_history

    return render(request, 'chatbot/chatbot.html', {
        "chat_history": chat_history,
        "bot_response": bot_response,
        "references": references_info
    })
