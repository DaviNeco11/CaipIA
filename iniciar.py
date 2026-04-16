import subprocess
import sys
import time


def main():
    processos = []

    try:
        api = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"])
        processos.append(api)

        time.sleep(2)

        bot = subprocess.Popen([sys.executable, "-m", "app.bot_telegram"])
        processos.append(bot)

        print("API e bot iniciados.")
        print("Pressione Ctrl + C para encerrar tudo.")

        for processo in processos:
            processo.wait()

    except KeyboardInterrupt:
        print("\nEncerrando processos...")

    finally:
        for processo in processos:
            if processo.poll() is None:
                processo.terminate()

        for processo in processos:
            if processo.poll() is None:
                processo.kill()

        print("Tudo encerrado.")


if __name__ == "__main__":
    main()