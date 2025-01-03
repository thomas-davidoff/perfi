from perfi.core.dependencies.settings import get_settings
import uvicorn
import os


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

    uvicorn.run(
        "perfi:app",
        host=api_settings.APP_HOST,
        port=int(api_settings.APP_PORT),
        reload=True,
    )


if __name__ == "__main__":
    run()
