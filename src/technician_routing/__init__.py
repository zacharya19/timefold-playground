import uvicorn

from .rest_api import app


def main():
    config = uvicorn.Config("technician_routing:app",
                            port=8080,
                            log_config="logging.conf",
                            use_colors=True,
                            reload=True)
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    main()
