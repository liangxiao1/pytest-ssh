# pytest-ssh
pytest-ssh is for ssh command run plugin of pytest.

It is based on paramiko, leveraging its capabilities to enhance pytest case development speed. By utilizing assert statements in run_cmd(), such as run_cmd(cmd, expect_ret=1), it can verify that the return value is indeed 1, or by using run_cmd(cmd, expect_not_kw='test1'), it asserts that 'test1' should not be present in the output. No need to dumplicate if-else blocks.

## Installation

```bash
# install from pypi
$ pip install pytest-ssh
# install from source code
$ pip install git+https://github.com/liangxiao1/pytest-ssh.git@master
# install from local source repo
$ pip3 install build installer
$ python -m build
$ python -m installer dist/*.whl

```

## Usage
```python
import pytest
def test_ssh(ssh_get):
    #create a SSH instance
    session = ssh_get()
    session.hostname = "127.0.0.1"
    session.username = 'root'
    session.password = "XXXX"
    #connet via default keyfile, you can also specify 'keyfile' location
    session.connect()
    cmd = 'uname -a'
    #get status and output without any checking
    status, output = session.run_cmd(cmd)
    #check cmd return is 0 when run cmd
    session.run_cmd(cmd, expect_ret=0)
    #check cmd output include specified keywords
    session.run_cmd('uname -r', expect_kw='4.18', msg='Check kernel version is 4.18')
    #check cmd output not include specified keywords
    session.run_cmd('uname -r', expect_not_kw='4.18', msg='Check kernel version is not 4.18')
    #put file from local to the remote
    session.put_file(local_file = '/tmp/test1.log', rmt_file = "/home/xiliang/test1.log")
    #retrive file from the remote to local
    session.get_file(rmt_file = "/home/xiliang/test2.log", local_file = '/tmp/test2.log')
    #close session
    session.close()

```
```bash
#run the test file
$ pytest --log-cli-level=INFO test.py
```