import logging
import paramiko
from paramiko import BadHostKeyException
import pytest
import sys
import os
import time

log = logging.getLogger(__name__)


class SSH(object):
    def __init__(self, hostname=None, username=None, password=None, keyfile=None, port=22, timeout=60, interval=5):
        self.log = logging.getLogger(__name__)
        self.hostname = hostname
        self.username = username
        self.password = password
        self.keyfile = keyfile
        self.port = port
        self.timeout = timeout
        self.interval = interval
        self.ssh_client = None

    def connect(self):
        self.log.info("Try to make connection {}@{}:{}".format(self.username, self.hostname, self.port))
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        start_time = time.time()
        while True:
            badhostkey = False
            try:
                end_time = time.time()
                if end_time-start_time > self.timeout:
                    log.info("timeout({}s) to make connection!".format(self.timeout))
                    return None
                if self.keyfile is None and self.password is None:
                    log.info("no password or keyfile for ssh access, use default ssh key setting")
                    self.ssh_client.load_system_host_keys()
                    self.ssh_client.connect(self.hostname, port=self.port, username=self.username)
                elif self.password is not None:
                    log.info("login system using password")
                    self.ssh_client.connect(
                        self.hostname,
                        port=self.port,
                        username=self.username,
                        password=self.password,
                        look_for_keys=False,
                        allow_agent=False,
                        timeout=60
                    )
                else:
                    log.info("login system using keyfile:{}".format(self.keyfile))
                    if not os.path.exists(self.keyfile):
                        log.error("{} not found".format(self.keyfile))
                        return None
                    exception_list=[]
                    pkey_RSAKey = paramiko.RSAKey.from_private_key_file(self.keyfile)
                    try:
                        log.info("Try to use {}".format(pkey_RSAKey.get_name()))
                        self.ssh_client.connect(
                            self.hostname,
                            port=self.port,
                            username=self.username,
                            #key_filename=rmt_keyfile,
                            pkey=pkey_RSAKey,
                            look_for_keys=False,
                            timeout=60
                        )
                        return self.ssh_client
                    except BadHostKeyException as e:
                        badhostkey = True
                        exception_list.append(e)
                    except Exception as e:
                        exception_list.append(e)         
                    raise Exception(exception_list)
                return self.ssh_client
            except Exception as e:
                log.info("*** Failed to connect to {}: {}".format(self.hostname, e))
                if 'Name or service not known' in str(e):
                    break
                log.info("Retry again, timeout {}!".format(self.timeout))
                time.sleep(self.interval)
                if 'does not match' in str(e) or badhostkey:
                    try:
                        know_hosts = paramiko.hostkeys.HostKeys(filename=os.path.expanduser("~/.ssh/known_hosts"))
                        know_hosts.lookup(self.hostname)
                        log.info("try to remove {} from known_hosts".format(self.hostname))
                        know_hosts.pop(self.hostname)
                        know_hosts.save(os.path.expanduser("~/.ssh/known_hosts"))
                        self.ssh_client = paramiko.SSHClient()
                        self.ssh_client.load_system_host_keys()
                        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    except Exception as e:
                        log.info('exception while cleaning known_hosts: {}'.format(e))
            return None

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
            (status, output) -- cmd return code and output(stdout+stderr)

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
            errlog = stderr.readlines()
            for line in errlog:
                log.info("%s" % line.rstrip('\n'))
            errlog = ''.join(errlog)
            output = ''.join(output+errlog)
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

    def put_file(self, local_file = None, rmt_file = None):
        if os.path.isdir(local_file):
            log.info("{} is dir, only file supported now.".format(local_file))
            return False
        log.info('sending {} from local to remote {}'.format(local_file,rmt_file))
        if not os.path.exists(local_file):
            log.info('{} not found'.format(local_file))
            return False
        self.ftp_client = self.ssh_client.open_sftp()
        try:
            self.ftp_client.put(local_file, rmt_file)
        except FileNotFoundError:
            self.log.info('{} must be a filename or not found on remote'.format(rmt_file))
            return False
        self.ftp_client.close()
        return True

    def get_file(self, rmt_file = None, local_file = None):
        log.info('retriving {} from remote to local {}'.format(rmt_file,local_file))
        if os.path.isdir(local_file):
            self.log.info("{} is dir, only file supported now.".format(local_file))
            return False
        self.ftp_client = self.ssh_client.open_sftp()
        try:
            self.ftp_client.get(rmt_file,local_file)
        except FileNotFoundError:
            self.log.info('{} must be a filename or not found on remote'.format(rmt_file))
            return False
        self.ftp_client.close()
        return True
