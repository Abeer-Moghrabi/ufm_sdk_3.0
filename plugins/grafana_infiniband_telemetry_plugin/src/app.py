#
# Copyright © 2013-2022 NVIDIA CORPORATION & AFFILIATES. ALL RIGHTS RESERVED.
#
# This software product is a proprietary product of Nvidia Corporation and its affiliates
# (the "Company") and all right, title, and interest in and to the software
# product, including all associated intellectual property rights, are and
# shall remain exclusively with the Company.
#
# This software product is governed by the End User License Agreement
# provided with the software product.
# @author: Anan Al-Aghbar
# @date:   Nov 09, 2022
#

import os
import sys
sys.path.append(os.getcwd())

import subprocess
from mgr.grafana_dashboard_configurations_mgr import UFMTelemetryLabelsConfigParser
from utils.logger import Logger, LOG_LEVELS
from api.labels_api import MetricLabelsGeneratorAPI
from api.conf_api import UFMTelemetryGrafanaConfigurationsAPI
from utils.flask_server import run_api
from utils.flask_server.base_flask_api_app import BaseFlaskAPIApp


def _init_logs(config_parser):
    # init logs configs
    logs_file_name = config_parser.get_logs_file_name()
    logs_level = config_parser.get_logs_level()
    max_log_file_size = config_parser.get_log_file_max_size()
    log_file_backup_count = config_parser.get_log_file_backup_count()
    Logger.init_logs_config(logs_file_name, logs_level, max_log_file_size, log_file_backup_count)


if __name__ == '__main__':

    conf = UFMTelemetryLabelsConfigParser()
    _init_logs(conf)

    try:
        Logger.log_message("Initializing the Apache configurations", LOG_LEVELS.DEBUG)
        subprocess.call('/opt/ufm/ufm_plugin_grafana-dashboard/grafana_infiniband_telemetry_plugin/scripts/init_apache.sh')
        Logger.log_message("Initializing the Apache configurations completed successfully", LOG_LEVELS.DEBUG)
    except Exception as ex:
        Logger.log_message(f'Initializing the Apache configurations completed with errors: {str(ex)}', LOG_LEVELS.ERROR)

    try:
        app_routes_map = {
            "/conf": UFMTelemetryGrafanaConfigurationsAPI(conf=conf).application
        }

        app = BaseFlaskAPIApp(app_routes_map)
        run_api(app=app, port_number=8983, run_reactor=False)

        endpoint_routes_map = {
            "/enterprise": MetricLabelsGeneratorAPI(conf=conf).application
        }

        endpoint_app = BaseFlaskAPIApp(endpoint_routes_map)
        run_api(app=endpoint_app, port_number=8984)

    except ValueError as ve:
        Logger.log_message(f'Missing configurations: {str(ve)}', LOG_LEVELS.ERROR)
    except Exception as ex:
        Logger.log_message(str(ex), LOG_LEVELS.ERROR)