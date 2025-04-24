def montar_conversa(system_prompt, user_input):
    return [
        system_prompt,
        {"role": "user", "content": user_input}
    ]
