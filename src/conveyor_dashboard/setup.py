from setuptools import find_packages, setup

package_name = 'conveyor_dashboard'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/dashboard.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='darhf',
    maintainer_email='didier.hernandez1972@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'l510_node = conveyor_dashboard.l510_node:main',
            'webcam_node = conveyor_dashboard.webcam_node:main',
            'dashboard_node = conveyor_dashboard.dashboard_node:main',
        ],
    },
)
