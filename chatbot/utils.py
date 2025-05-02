import re
import html

def format_bot_response(text: str) -> str:
    """
    Formate une réponse de chatbot en HTML stylisé avec Tailwind.
    Détecte et transforme les URLs en liens cliquables.
    """
    if not text:
        return "<p class='text-red-500'>Erreur : Réponse vide</p>"

    # Échapper les caractères HTML
    escaped_text = html.escape(text)

    # Transformer les URLs en liens HTML
    url_pattern = re.compile(r'https?://[^\s\)]+')
    escaped_text = url_pattern.sub(
        r"<a href='\g<0>' class='text-lime-600 underline hover:text-lime-800' target='_blank'>\g<0></a>",
        escaped_text
        )

    # Diviser en paragraphes
    paragraphs = escaped_text.strip().split('\n')
    html_paragraphs = [f"<p class='mb-2 text-gray-800'>{p}</p>" for p in paragraphs if p.strip()]

    return f"""
    <div class='bg-gray-100 p-4 rounded-lg shadow-md'>
        {''.join(html_paragraphs)}
    </div>
    """
