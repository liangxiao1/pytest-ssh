from setuptools import setup, find_packages

version = '0.1'

setup(name='pytest-ssh',
      version=version,
      description="pytest plugin for ssh command run",
      author='Xiao Liang',
      author_email='xiliang@redhat.com',
      url='https://github.com/liangxiao1/pytest-ssh',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      license='MIT',
      install_requires=['paramiko', 'pytest'],
      entry_points={'pytest11': ['pytest_ssh=pytest_ssh.plugin']},
      classifiers=["Framework :: Pytest",
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.7'])
