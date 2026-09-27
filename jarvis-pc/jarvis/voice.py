"""Voz: aperte-para-falar (v1). STT usa o endpoint gratuito e não-oficial do Google embutido
na biblioteca SpeechRecognition; TTS usa pyttsx3 (offline). Digitar continua sempre disponível
como alternativa — ver README.md para os detalhes por sistema operacional."""
import re

_tts = None


def _motor_tts():
    global _tts
    if _tts is None:
        import pyttsx3
        _tts = pyttsx3.init()
        _tts.setProperty("rate", 175)
    return _tts


def ouvir() -> str:
    """Grava um trecho do microfone e devolve o texto reconhecido em PT-BR (ou '' se falhar)."""
    try:
        import speech_recognition as sr
    except ImportError:
        print("[erro] biblioteca de voz não instalada. Rode 'pip install -r requirements.txt', ou digite sua mensagem.")
        return ""

    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            print("Ouvindo… (fale agora)")
            audio = r.listen(source, timeout=8, phrase_time_limit=20)
    except OSError as e:
        print(f"[erro] microfone indisponível: {e}")
        return ""
    except sr.WaitTimeoutError:
        print("[aviso] nada foi ouvido a tempo.")
        return ""

    try:
        return r.recognize_google(audio, language="pt-BR")
    except sr.UnknownValueError:
        print("[aviso] não entendi o que foi dito.")
        return ""
    except sr.RequestError as e:
        print(f"[erro] serviço de reconhecimento de voz falhou: {e}")
        return ""


def _para_fala(texto: str) -> str:
    texto = re.sub(r"https?://\S+", "link", texto)
    texto = re.sub(r"[*#_`>~|]", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


def falar(texto: str, cfg: dict):
    if not cfg.get("voz", True):
        return
    limpo = _para_fala(texto)
    if not limpo:
        return
    try:
        motor = _motor_tts()
        motor.say(limpo)
        motor.runAndWait()
    except ImportError:
        print("[aviso] biblioteca de voz (pyttsx3) não instalada — respondendo só em texto.")
    except Exception as e:
        print(f"[aviso] não consegui falar a resposta: {e}")
