import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
import time
import traceback
from collections import namedtuple
from typing import List, Optional, Tuple, Union

import nvflare
from nvflare.fuel.hci.client.api_status import APIStatus
from nvflare.fuel.hci.client.fl_admin_api import FLAdminAPI
from nvflare.fuel.hci.client.fl_admin_api_constants import FLDetailKey
from nvflare.fuel.hci.client.fl_admin_api_spec import FLAdminAPIResponse, TargetType


def _get_nvflare_version_tuple() -> Union[Tuple[int, int, int], Tuple[int, int]]:
    try:
        version_str = nvflare.__version__
    except AttributeError:
        frozen_deps = subprocess.run(['pip', 'freeze'], capture_output=True, check=True).stdout.decode()
        nvflare_deps = [line for line in frozen_deps.splitlines() if line.lower().startswith('nvflare==')]
        if len(nvflare_deps) != 1:
            raise Exception("Couldn't find version of nvflare.")
        version_str = nvflare_deps[0].strip()[len('nvflare=='):]
    major, minor, patch, _remainder = re.match(r"(\d+)\.(\d+)(?:\.(\d+))?([^\d].*)?", version_str).groups()
    version_tuple = (int(major), int(minor))
    if patch:
        version_tuple += (int(patch),)
    return version_tuple


NVFLARE_VERSION_TUPLE = _get_nvflare_version_tuple()

if (2, 0) <= NVFLARE_VERSION_TUPLE < (2, 1):
    WAITING_CLIENT_STATUS = "not started"
elif (2, 2) <= NVFLARE_VERSION_TUPLE < (2, 5):
    WAITING_CLIENT_STATUS = "No Jobs"
else:
    raise Exception(f"Unsupported version of NVFLARE: {nvflare.__version__}")


def get_client_status_namedtuples(clients_status_response: FLAdminAPIResponse) -> List[namedtuple]:
    """Parse client statuses table as returned from the API."""
    # Examples with NVFLARE v2.2.3:
    #
    # [
    #   ['CLIENT', 'APP_NAME', 'JOB_ID', 'STATUS'],
    #   ['RhinoAgentQA1_1', 'nvflare-service-suhjjpyy', '80db3699-2958-4f8f-aebd-880a5ec45436', 'not started'],
    # ]
    #
    # [
    #   ['CLIENT', 'APP_NAME', 'JOB_ID', 'STATUS'],
    #   ['RhinoAgentQA1_1', 'nvflare-service-suhjjpyy', '80db3699-2958-4f8f-aebd-880a5ec45436', 'No Jobs'],
    # ]
    #
    # Example with NVFLARE v2.0.18:
    #
    # [
    #   ['CLIENT', 'APP_NAME', 'RUN_NUMBER', 'STATUS'],
    #   ['RhinoAgentQA1_1', 'nvflare-service-skfwqzch', '1', 'started'],
    # ]

    clients_statuses: list[list[str]] = clients_status_response["details"].get("client_statuses")
    if not clients_statuses:
        return []
    ClientStatus = namedtuple("ClientStatus", clients_statuses.pop(0))
    assert {"CLIENT", "STATUS"} <= set(ClientStatus._fields), repr(ClientStatus._fields)
    status_objects = [ClientStatus(*client_status_row) for client_status_row in clients_statuses]
    return status_objects


def raise_on_response_error(response: FLAdminAPIResponse, errmsg_prefix: Optional[str] = "NVFlare admin API error"):
    if response["status"] != APIStatus.SUCCESS:
        errmsg: str = response["details"].get("message") or str(response.get("details")) or response.get("raw") or ""
        raise Exception(f"{errmsg_prefix}: {errmsg}")


def _create_fl_admin_api(host: str, port: int) -> FLAdminAPI:
    if (2, 0) <= NVFLARE_VERSION_TUPLE < (2, 1):
        # FLAdminAPI.__init__ prints an unneeded message to stdout when run with poc=True.
        with contextlib.redirect_stdout(io.StringIO()):
            admin_api = FLAdminAPI(
                host=host,
                port=port,
                upload_dir="transfer",
                download_dir="transfer",
                poc=True,
                debug=False,
            )
    elif (2, 2) <= NVFLARE_VERSION_TUPLE < (2, 4):
        from nvflare.ha.dummy_overseer_agent import DummyOverseerAgent

        # FLAdminAPI.__init__ prints an unneeded message to stdout when run with poc=True.
        with contextlib.redirect_stdout(io.StringIO()):
            admin_api = FLAdminAPI(
                overseer_agent=DummyOverseerAgent(sp_end_point=f"{host}:8002:{port}"),
                user_name="admin",
                upload_dir="transfer",
                download_dir="transfer",
                poc=True,
                debug=False,
            )
    elif (2, 4) <= NVFLARE_VERSION_TUPLE < (2, 5):
        from nvflare.ha.dummy_overseer_agent import DummyOverseerAgent

        admin_api = FLAdminAPI(
            overseer_agent=DummyOverseerAgent(sp_end_point=f"{host}:8002:{port}"),
            user_name="admin@nvidia.com",
            ca_cert="startup/rootCA.pem",
            client_cert="startup/client.crt",
            client_key="startup/client.key",
            upload_dir="transfer",
            download_dir="transfer",
            debug=False,
        )
    else:
        raise Exception(f"Unsupported version of NVFLARE: {nvflare.__version__}")
    return admin_api


def create_admin_api_and_login(host: str, port: int, connection_timeout: float) -> FLAdminAPI:
    start = time.monotonic()
    while True:
        try:
            admin_api = _create_fl_admin_api(host=host, port=port)

            # With v2.2, there's a problem with FLAdminAPI, causing calls to
            # .login() immediately after instantiating the api object to fail.
            # Waiting a bit for the API object to initialize in the background
            # fixes that. So we put a retry loop with delays around login().
            success, failure_details = False, None
            last_exc = None
            for i in range(10):
                if i > 0:
                    time.sleep(0.2)
                try:
                    success, failure_details = try_login(admin_api)
                    if success:
                        break
                except Exception as exc:
                    last_exc = exc
            if not success:
                exc = Exception(f"Login to admin api failed: {failure_details}")
                if last_exc is not None:
                    raise exc from last_exc
                else:
                    raise exc

        except Exception as exc:
            elapsed = time.monotonic() - start
            if elapsed > connection_timeout:
                raise Exception("Connection timeout") from exc
            time.sleep(max(0.1, min(connection_timeout / 10, 1)))
        else:
            break

    return admin_api


def try_login(admin_api) -> Tuple[bool, Optional[str]]:
    if (2, 0) <= NVFLARE_VERSION_TUPLE < (2, 1):
        response: FLAdminAPIResponse = admin_api.login_with_password(username="admin", password="admin")
    elif (2, 2) <= NVFLARE_VERSION_TUPLE < (2, 4):
        response: FLAdminAPIResponse = admin_api.login_with_poc(username="admin", poc_key="admin")
    elif (2, 4) <= NVFLARE_VERSION_TUPLE < (2, 5):
        response: FLAdminAPIResponse = admin_api.login(username="admin@nvidia.com")
    else:
        raise Exception(f"Unsupported version of NVFLARE: {nvflare.__version__}")

    if response["status"] == APIStatus.SUCCESS:
        return True, None
    else:
        details = response.get("details") if response else "(No details)"
        return False, details


def wait_for_clients_to_connect(admin_api, num_clients, timeout_seconds):
    start_time = time.monotonic()
    while True:
        # Check if all FL clients are connected and waiting for instructions.
        response = admin_api.check_status(target_type=TargetType.CLIENT)
        if response["status"] == APIStatus.SUCCESS and "details" in response:
            statuses = get_client_status_namedtuples(response)
            n_clients_up = sum(1 for status in statuses if status.STATUS == WAITING_CLIENT_STATUS)
            if n_clients_up >= num_clients:
                return

        # Exit loop if timed out.
        if time.monotonic() - start_time >= timeout_seconds:
            break

        # Wait a bit before trying again.
        time.sleep(0.5)
    details = response.get("details") if response else "(No details)"
    raise Exception(f"Clients didn't connect in {timeout_seconds} seconds: {details}")


def start_app(admin_api, app_name):
    if (2, 0) <= NVFLARE_VERSION_TUPLE < (2, 1):
        run_number = 1
        response = admin_api.set_run_number(run_number)
        raise_on_response_error(response, errmsg_prefix="set_run_number failed")
        response = admin_api.upload_app(app=app_name)
        raise_on_response_error(response, errmsg_prefix="upload_app failed")
        response = admin_api.deploy_app(app=app_name, target_type=TargetType.ALL)
        raise_on_response_error(response, errmsg_prefix="deploy_app failed")
        response = admin_api.start_app(target_type=TargetType.ALL)
        raise_on_response_error(response, errmsg_prefix="start_app failed")
    elif (2, 2) <= NVFLARE_VERSION_TUPLE < (2, 4):
        response = admin_api.submit_job(job_folder=app_name)
        raise_on_response_error(response, errmsg_prefix="submit_job failed")
    elif (2, 4) <= NVFLARE_VERSION_TUPLE < (2, 5):
        response = admin_api.submit_job(job_folder="job")
        print(f"{response=}")
        raise_on_response_error(response, errmsg_prefix="submit_job failed")
    else:
        raise Exception(f"Unsupported version of NVFLARE: {nvflare.__version__}")


def wait_for_start(admin_api: FLAdminAPI, timeout_seconds: float):
    start_time = time.monotonic()
    while time.monotonic() - start_time <= timeout_seconds:
        admin_status_response = admin_api.check_status(target_type=TargetType.SERVER)
        if admin_status_response["status"] != APIStatus.SUCCESS:
            raise RuntimeError(f"check_status server failed: {admin_status_response}")
        if admin_status_response.get("details", {}).get(FLDetailKey.SERVER_ENGINE_STATUS) == "started":
            client_status_response = admin_api.check_status(target_type=TargetType.CLIENT)
            if client_status_response["status"] != APIStatus.SUCCESS:
                raise RuntimeError(f"check_status client failed: {client_status_response}")
            client_statuses = get_client_status_namedtuples(client_status_response)
            if all(status.STATUS not in ["stopped", WAITING_CLIENT_STATUS] for status in client_statuses):
                return
        time.sleep(1)
    raise RuntimeError(f"App start timed out after {timeout_seconds:.0f} seconds.")


def wait_for_completion(admin_api: FLAdminAPI, timeout_seconds: float):
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
            client_statuses = get_client_status_namedtuples(client_status_response)
            if all(status.STATUS in ["stopped", WAITING_CLIENT_STATUS] for status in client_statuses):
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
    parser.add_argument("--num-clients", type=int, default=2, help="number of clients in the FL network")
    parser.add_argument("--timeout", type=int, default=600, help="timeout for app run, in seconds")
    parser.add_argument("app_name", type=str, help="nvflare app name")

    args = parser.parse_args()

    print(f"{args=}")
    print(f"{args.host=}")

    print("Connecting to NVFLARE admin API...")
    admin_api = create_admin_api_and_login(host=args.host, port=args.port, connection_timeout=60.0)
    print(f"Waiting for clients to connect to the server...")
    wait_for_clients_to_connect(admin_api=admin_api, num_clients=args.num_clients, timeout_seconds=args.timeout)
    print(f"Starting NVFlare app named {args.app_name}...")
    start_app(admin_api=admin_api, app_name=args.app_name)
    print("App running. Waiting for training to start...")
    wait_for_start(admin_api=admin_api, timeout_seconds=min(30, args.timeout))
    print("Training started. Waiting for server and clients to stop...")
    wait_for_completion(admin_api=admin_api, timeout_seconds=args.timeout)
    print("Training stopped. Shutting down...")
    shutdown(admin_api=admin_api)
    print("All done. Goodbye!")
    return 0


if __name__ == "__main__":
    try:
        return_code = main()
    except SystemExit as exc:
        return_code = exc.code
    except BaseException:
        traceback.print_exc()
        return_code = 1

    if NVFLARE_VERSION_TUPLE >= (2, 2):
        # Use os._exit() rather than sys.exit() because something in the
        # background (from FLAdminAPI) causes the process to hang with
        # NVFLARE v2.2.
        os._exit(return_code)
    else:
        sys.exit(return_code)
