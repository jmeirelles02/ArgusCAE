from plyer import notification

def enviar_alerta(titulo: str, mensagem: str):
    """
    Envia uma notificação visual para o sistema operacional.
    """
    try:
        notification.notify(
            title=f"ARGUS: {titulo}",
            message=mensagem,
            app_name="Argus AI",
            timeout=10  # A notificação fica 10 segundos na tela
        )
        print(f"🔔 [NOTIFICAÇÃO ENVIADA] {titulo}")
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")