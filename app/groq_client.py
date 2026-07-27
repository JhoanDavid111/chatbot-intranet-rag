from groq import Groq

from app.config import settings


def call_groq(question: str, conversation_context: str = "") -> str:
    if not settings.USE_GROQ:
        return ""

    if not settings.GROQ_API_KEY:
        print("GROQ_API_KEY no está configurada.")
        return ""

    client = Groq(api_key=settings.GROQ_API_KEY)

    system_prompt = """
Eres Capi, el asistente virtual institucional de Canal Capital.

Tu objetivo es ayudar a los usuarios con información de la intranet, SICC, ERPC,
solicitud de salas, denuncias públicas, Recursos Humanos, soporte TIC y procesos internos.

Reglas:
- Responde siempre en español.
- Sé claro, amable, institucional y breve.
- No inventes enlaces, usuarios, contraseñas, procedimientos internos ni datos sensibles.
- Si no tienes información suficiente, dilo claramente.
- Si la consulta requiere soporte interno, orienta al usuario a Gestión TIC o al área correspondiente.
- No menciones Groq, modelos externos ni detalles técnicos internos.
"""

    user_prompt = f"""
Contexto reciente de la conversación:
{conversation_context or "Sin contexto previo relevante."}

Pregunta del usuario:
{question}

Responde de forma útil, clara y segura.
"""

    try:
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()}
            ],
            temperature=0.2,
            max_completion_tokens=350
        )

        return completion.choices[0].message.content.strip()

    except Exception as error:
        print(f"Error llamando GroqCloud: {error}")
        return ""