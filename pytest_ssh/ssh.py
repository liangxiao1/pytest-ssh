import logging
import paramiko
import pytest
import sys
import time

log = logging.getLogger(__name__)


class SSH(object):
    def __init__(self, hostname=None, username=None, keyfile=None, port=22, timeout=60):
        self.hostname = hostname
        self.username = username
        self.keyfile = keyfile
        self.port = port
        self.timeout = timeout

    def connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
        start_time = time.time()
        while True:
            try:
                end_time = time.time()
                if end_time-start_time > self.timeout:
                    log.error("Unable to make connection!")
                    pytest.fail(ms='Unable to make connection to %s!' %
                                (self.hostname))
                if self.keyfile is None:
                    self.ssh_client.load_system_host_keys()
                    self.ssh_client.connect(
                        self.hostname, username=self.username)
                else:
                    self.ssh_client.connect(
                        self.hostname,
                        username=self.username,
                        key_filename=self.keyfile,
                        look_for_keys=False,
                        timeout=self.timeout
                    )
                break
            except Exception as e:
                log.info(msg="*** Failed to connect to %s:%d: %r" %
                         (self.hostname, self.port, e))
                log.info("Retry more times!")
                time.sleep(10)

    def isalive(self):
        self.run_cmd('\n', expect_ret=0,
                     msg='Check ssh connect is live!')

    def close(self):
        self.ssh_client.close()

    def run_cmd(self, cmd, expect_ret=None, expect_not_ret=None, expect_kw=None, expect_not_kw=None, expect_output=None, msg=None, cancel_kw=None, timeout=60):
        """run cmd with/without checking return status/keywords

        Arguments:
            cmd {string} -- cmd to run
            expect_ret {int} -- expected return status
            expect_not_ret {int} -- unexpected return status
            expect_kw {string} -- string expected in output
            expect_not_kw {string} -- string not expected in output
            expect_output {string} -- string exactly the same as output
            cancel_kw {string} -- cancel case if kw not found
            msg {string} -- addtional info to mark cmd run.

        Return:
            (status, output) -- cmd return code and output

        """
        if msg is not None:
            log.info(msg)
        log.info("CMD: %s", cmd)
        if self.ssh_client is None:
            log.info('No connection made!')
        status = 0
        output = None

        stdin, stdout, stderr = self.ssh_client.exec_command(
            cmd, timeout=timeout)
        while not stdout.channel.exit_status_ready() and stdout.channel.recv_exit_status():
            time.sleep(60)
            log.info("Wait command complete......")
        try:
            log.info("cmd output:")
            output = stdout.readlines()

            for line in output:
                log.info("%s" % line.rstrip('\n'))
            output = ''.join(output)
            log.info("cmd error:")
            for line in stderr.readlines():
                log.info("%s" % line.rstrip('\n'))
        except Exception as e:
            log.info("Cannot get output/error: %s" % e)

        status = stdout.channel.recv_exit_status()
        log.info("CMD ret code: %s" % status)

        if expect_ret is not None:
            assert status == expect_ret, 'status %s not equal to expect_ret %s' % (
                status, expect_ret)
        if expect_not_ret is not None:
            assert status != expect_not_ret, 'status %s should not equal to expect_not_ret %s' % (
                status, expect_not_ret)
        if expect_kw is not None:
            assert expect_kw in output, 'expected %s not in output %s' % (
                expect_kw, output)
        if expect_not_kw is not None:
            assert expect_not_kw not in output, '%s is not expected in output %s' % (
                expect_not_kw, output)
        if expect_output is not None:
            assert expect_output == output, 'expected %s  is not %s' % (
                expect_output, output)

        log.info("CMD out:%s" % output)
        return status, output
