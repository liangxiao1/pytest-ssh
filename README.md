# pytest-ssh
pytest-ssh is for ssh command run plugin of pytest.

It is basing on paramiko. The advantage of thhis tool is speed up pytest
case development by assertion different situation in run_cmd(), like run_cmd(cmd,expect_ret=1) to assert the return is 1 or run_cmd(cmd,expect_not_kw='test1') to assert 'test1' not should not in output.

## Intallation

```python
pip install pytest-ssh
```

## Usage
```
def test_ssh(ssh_get):
    #create a SSH instance
    session = ssh_get()
    session.hostname = '127.0.0.1"
    session.username = 'root'
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
    #close session
    session.close()

```