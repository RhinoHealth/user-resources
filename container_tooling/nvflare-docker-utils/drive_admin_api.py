import argparse
import contextlib
import io
import sys
import time

from nvflare.fuel.hci.client.api_status import APIStatus
from nvflare.fuel.hci.client.fl_admin_api import FLAdminAPI
from nvflare.fuel.hci.client.fl_admin_api_constants import FLDetailKey
from nvflare.fuel.hci.client.fl_admin_api_spec import FLAdminAPIResponse, TargetType


def login_to_admin(admin_api):
    print("Logging in to NVFlare admin API...")
    response = None
    start_time = time.monotonic()
    while time.monotonic() - start_time <= 100:
        response: FLAdminAPIResponse = admin_api.login_with_password(username="admin", password="admin")
        if response["status"] == APIStatus.SUCCESS:
            return
        time.sleep(1.0)
    details = response.get("details") if response else "(No details)"
    raise RuntimeError(f"Login to admin api failed: {details}")


def wait_for_clients_to_connect(admin_api, num_clients):
    print("Waiting for clients to connect to the server...")
    timeout_seconds = 1000.0
    start_time = time.monotonic()
    while time.monotonic() - start_time <= timeout_seconds:
        response = admin_api.check_status(target_type=TargetType.CLIENT)
        if response["status"] == APIStatus.SUCCESS and "details" in response:
            n_clients_up = len([
                row for row in response["details"]["client_statuses"][1:]
                if row[3] == "not started"
            ])
            if n_clients_up >= num_clients:
                return
        time.sleep(1.0)
    raise RuntimeError(f"Clients could not be started in {timeout_seconds:.0f} seconds.")


def run_app(admin_api, app_name, timeout_seconds):
    print(f"Running NVFlare app named {app_name}...")
    run_number = 1
    response = admin_api.set_run_number(run_number)
    if response["status"] != APIStatus.SUCCESS:
        raise RuntimeError(f"set_run_number failed: {response}")
    response = admin_api.upload_app(app=app_name)
    if response["status"] != APIStatus.SUCCESS:
        raise RuntimeError(f"upload_app failed: {response}")
    response = admin_api.deploy_app(app=app_name, target_type=TargetType.ALL)
    if response["status"] != APIStatus.SUCCESS:
        raise RuntimeError(f"deploy_app failed: {response}")
    response = admin_api.start_app(target_type=TargetType.ALL)
    if response["status"] != APIStatus.SUCCESS:
        raise RuntimeError(f"start_app failed: {response}")

    print("App running. Waiting for server and clients to stop...")
    start_time = time.monotonic()
    while time.monotonic() - start_time <= timeout_seconds:
        print(".", end="", flush=True)
        admin_status_response = admin_api.check_status(target_type=TargetType.SERVER)
        if admin_status_response["status"] != APIStatus.SUCCESS:
            raise RuntimeError(f"check_status server failed: {admin_status_response}")
        if admin_status_response.get("details", {}).get(FLDetailKey.SERVER_ENGINE_STATUS) == "stopped":
            client_status_response = admin_api.check_status(target_type=TargetType.CLIENT)
            if client_status_response["status"] != APIStatus.SUCCESS:
                raise RuntimeError(f"check_status client failed: {client_status_response}")
            if all(
                row[3] == "stopped"
                for row in client_status_response["details"]["client_statuses"][1:]
            ):
                print()
                return
        time.sleep(1)
    print()
    raise RuntimeError(f"App run timed out after {timeout_seconds:.0f} seconds.")


def shutdown(admin_api):
    response = admin_api.shutdown(target_type=TargetType.ALL)
    if response["status"] != APIStatus.SUCCESS:
        raise RuntimeError(f"shutdown all failed: {response}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost", help="host name of the FL server")
    parser.add_argument("--port", type=int, default=8003, help="admin API port of the FL server")
    parser.add_argument("--n-clients", type=int, default=2, help="number of clients in the FL network")
    parser.add_argument("--timeout", type=int, default=600, help="timeout for app run, in seconds")
    parser.add_argument("app_name", type=str, help="nvflare app name")

    args = parser.parse_args()

    # FLAdminAPI.__init__ prints an unneeded message to stdout when run with poc=True.
    with contextlib.redirect_stdout(io.StringIO()):
        admin_api = FLAdminAPI(
            host=args.host,
            port=args.port,
            upload_dir="transfer",
            download_dir="transfer",
            poc=True,
            debug=False,
        )

    login_to_admin(admin_api)
    wait_for_clients_to_connect(admin_api, args.n_clients)
    run_app(admin_api, args.app_name, args.timeout)
    shutdown(admin_api)
    return 0


if __name__ == "__main__":
    sys.exit(main())
