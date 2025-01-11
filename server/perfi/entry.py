from config import Settings, get_settings
import uvicorn
import os


def get_host_and_port(settings: Settings):
    if os.getenv("CONTAINERIZED", "false").lower() == "true":
        # in container, bind to 0.0.0.0
        return "0.0.0.0", int(settings.APP_PORT)
    else:
        # default to 127.0.0.1 for local
        return "127.0.0.1", int(settings.APP_PORT)


def run():
    """
    Entry point for starting the FastAPI server.
    Optionally starts debugpy for VSCode debugging.
    """
    api_settings = get_settings()

    DEBUG_PORT = os.getenv("DEBUG_PORT", 5678)

    if os.getenv("DEBUG_MODE") == "1":
        try:
            import debugpy

            debug_port = int(DEBUG_PORT)
            print(f"Starting debugger on port {debug_port}...")
            debugpy.listen(("0.0.0.0", debug_port))
            print("Debugger is listening. Waiting for VSCode to attach...")
            debugpy.wait_for_client()
        except ImportError as e:
            print(
                "debugpy is not installed. Please install it with `poetry add debugpy --group dev`."
            )
            raise e

    host, port = get_host_and_port(api_settings)

    uvicorn.run(
        "perfi:app",
        host=host,
        port=port,
        reload=True,  # TODO: should only reload in dev
    )


if __name__ == "__main__":
    run()
