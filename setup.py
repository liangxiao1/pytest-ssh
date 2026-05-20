from setuptools import setup, find_packages
from pathlib import Path

current_directory = Path(__file__).parent
long_description = (current_directory / "README.md").read_text()

version = '0.2.1'

setup(name='pytest-ssh',
      version=version,
      description="pytest plugin for ssh command run",
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Xiao Liang',
      author_email='teddy.x.liang@hotmail.com',
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
