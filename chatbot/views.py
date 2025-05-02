from django.shortcuts import render
import requests
import json
from .utils import format_bot_response
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST


api_url = "https://api.mistral.ai/v1/chat/completions"
model = 'mistral-large-latest'

def chatbot(request):
    bot_response = None
    user_input = None

    # Clé API Mistral
    api_key ='T7ZAHydnKw3DeLEupGG1l8zKaVjjg19p'

    # Récupérer l'historique de la session ou initialiser une liste vide
    conversation_history = request.session.get('conversation_history', [])
    show_history = request.session.get('show_history', True)

    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        if user_input:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }

                # Ajouter le message de l'utilisateur à l'historique avant d'envoyer la requête
                conversation_history.append({"role": "user", "content": user_input})

                # Construire le payload avec le rôle "system" uniquement au début
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Réponds toujours en français et fournis moi les références de tes informations comme des liens vers des sites internet."}
                    ] + conversation_history
                }

                response = requests.post(
                    api_url,
                    headers=headers,
                    data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
                )

                if response.status_code == 200:
                    result = response.json()
                    bot_response = result["choices"][0]["message"]["content"]
                    # Ajouter la réponse du bot à l'historique
                    conversation_history.append({"role": "assistant", "content": bot_response})

                else:
                    bot_response = f"Erreur API: {response.status_code} - {response.text}"

            except Exception as e:
                bot_response = f"Erreur d'exécution : {str(e)}"

        if bot_response and isinstance(bot_response, str):
            bot_response = format_bot_response(bot_response)

        # Sauvegarder l'historique mis à jour dans la session
        request.session['conversation_history'] = conversation_history

    return render(request, 'chatbot/chatbot.html', {
        "user_input": user_input,
        "bot_response": bot_response,
        "conversation_history": conversation_history,
        "show_history": show_history
    })

@require_POST
def clear_history(request):
    if 'conversation_history' in request.session:
        del request.session['conversation_history']
    return HttpResponseRedirect(reverse('chatbot:chatbot'))

@require_POST
def toggle_history(request):
    show_history = request.session.get('show_history', True)
    request.session['show_history'] = not show_history
    return HttpResponseRedirect(reverse('chatbot:chatbot'))
