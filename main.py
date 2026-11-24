from http.server import ThreadingHTTPServer

import config.setting as settings
from config.connection import Database
from handlers.user_handler import create_handler
from repositories.user_repository import UserRepository
from services.user_service import UserService


def main():
    database = Database()
    user_repository = UserRepository(database)
    user_service = UserService(user_repository)
    handler = create_handler(user_service)

    server = ThreadingHTTPServer(
        (settings.SERVER_HOST, settings.SERVER_PORT),
        handler,
    )
    print(
        f"Server running at "
        f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()