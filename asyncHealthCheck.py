# Asynchronous Health Check
# Author: Michal Katnik

from paramiko import SSHClient, AutoAddPolicy
import asyncio
import time

colors = {
    'yellow': '\033[38;5;228m',
    'reset': '\033[0m'
}

machines = {
    'be': {
        'Central-BE-A': '192.168.0.179',
        'Central-BE-B': '192.168.0.179',
        'EMEA-BE-A': '192.168.0.179',
        'EMEA-BE-B': '192.168.0.179'
    },
    'ds': {
        'Central-DS-A': '192.168.0.179',
        'Central-DS-B': '192.168.0.179',
        'EMEA-DS-A': '192.168.0.179',
        'EMEA-DS-B': '192.168.0.179'
    },
    'fe': {
        'Central-FE-A': '192.168.0.179',
        'Central-FE-B': '192.168.0.179',
    }
}

sshKeys = '/home/rid/.ssh/known_hosts'


async def get_status(host, machineType):
    """Runs commands related to the server type and returns status."""

    cmd = ''
    status = ''
    client = SSHClient()
    client.load_host_keys(sshKeys)
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.load_system_host_keys()

    if machineType == 'be':
        # TODO: Implement action. Dummy content for testing purpose.
        client.connect(host, username='iddirx')
        cmd = 'ps ux; echo -e "\nUptime:"; uptime'
    elif machineType == 'ds':
        # TODO: Implement action. Dummy content for testing purpose.
        client.connect(host, username='spdirx')
        cmd = 'ps ux | head -1; ps ux | grep libexec; echo -e "\nUptime:"; uptime'
    elif machineType == 'fe':
        # TODO: Implement action. Dummy content for testing purpose.
        client.connect(host, username='webmaster')
        cmd = 'systemctl status httpd 2>&1; echo -e "\nUptime:"; uptime'

    # Run a command.
    stdin, stdout, stderr = client.exec_command(cmd)

    # If exit code == 0.
    if stdout.channel.recv_exit_status() == 0:
        status = stdout.read().decode("utf8")
    else:
        status = stderr.read().decode("utf8")

    stdin.close()
    stdout.close()
    stderr.close()
    client.close()

    return status


async def main():
    # Initialize tasks.
    tasks = {
        'be': {},
        'ds': {},
        'fe': {}
    }

    for machine in machines['be']:
        tasks['be'][machine] = asyncio.create_task(
            get_status(machines['be'][machine], 'be')
        )

    for machine in machines['ds']:
        tasks['ds'][machine] = asyncio.create_task(
            get_status(machines['ds'][machine], 'ds')
        )

    for machine in machines['fe']:
        tasks['fe'][machine] = asyncio.create_task(
            get_status(machines['fe'][machine], 'fe')
        )

    # Wait for response from 'be' and print.
    for machine in tasks['be']:
        task = tasks['be'][machine]
        await task
        print(colors['yellow'] + '### ' + machine + ' ###' + colors['reset'])
        print(task.result())

    # Wait for response from 'ds' and print.
    for machine in tasks['ds']:
        task = tasks['ds'][machine]
        await task
        print(colors['yellow'] + '### ' + machine + ' ###' + colors['reset'])
        print(task.result())

    # Wait for response from 'fe' and print.
    for machine in tasks['fe']:
        task = tasks['fe'][machine]
        await task
        print(colors['yellow'] + '### ' + machine + ' ###' + colors['reset'])
        print(task.result())


mainTimerStart = time.perf_counter()
asyncio.run(main())
mainTimerStop = time.perf_counter()
mainTimer = mainTimerStop - mainTimerStart
print('[The script finished after {:0.2f} seconds]'.format(mainTimer))
