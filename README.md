# plico_interferometer_server
server for interferometer control under the plico environment. This library allows it to interface with PhaseCam and Wyko interferometers that have the 4Sight SW provided by 4Dtechnology.

### 4Sight startup ###
- Launch the 4Sight SW by clicking on the icon with the necessary version.
  <table>
  <tr>
    <td><b>Interferometer</b></td>
    <td><b>SW version</b></td>
  </tr>
  <tr>
    <td>PhaseCam 4020</td>
    <td>2.24</td>
  </tr>
  </tr>
  <tr>
    <td>PhaseCam 6110</td>
    <td>???</td>
  </tr>
  <tr>
    <td>PhaseCam 4030? (Padova)</td>
    <td>2022.R1.2</td>
  </tr>
</table>
- Run default script and set interferometer parameters for you acquisition.

### Server startup
- Have a Python working environment (no specific version is required, but preferably higher than 3).
- Install the Python library using the command pip install plico_interferometer_server
During the installation, a server configuration file is created, named <i>plico_interferometer_server.conf</i> (located in …\Local\INAF Arcetri Adaptive Optics\inaf.arcetri.ao.plico_interferometer_server), which must be edited by the user so that it contains all the information relating to the interferometer to be used.
Below is an example of a configuration file:

[devicePhaseCam4020]<br>
name = Phase Cam 4020<br>
model = phase_cam_4020_4sight<br>

[devicePhaseCam6110M4]<br>
name = PhaseCam6110 M4 <br>
model = phase_cam_6110<br>
ip_address = 147.162.107.99<br>
port = 8011<br>
burst_folder_name_4d_pc = C:\\Users\\PhaseCam\\TestBurstFolder<br>

[deviceSimulatedInterferometer]<br>
name = My Simulated Interferometer<br>
model = simulated_interferometer<br>

[interferometer1]<br>
name = Server PhaseCam4020<br>
interferometer = devicePhaseCam4020<br>
host = localhost<br>
port = 7300<br>

[interferometer2]<br>
name = My Server<br>
interferometer = deviceSimulatedInterferometer<br>
host = localhost<br>
port = 7400<br>


  NOTE: In the case of interferometers using WCF it is also necessary to specify the folder path (on the interferometer's PC) to be used for burst acquisition.

- Start the server using the executable <i>plico_interferometer_server_start</i>. The executable is located inside the folder Scripts installed by the Python library in the environment used.
- This command starts the two servers specified in the configuration file at the same time: these can be started separately using the commands <i>plico_interferometer_server_1</i> or <i>plico_interferometer_server_2</i>.
The start of the server is associated with the start of the compilation of a log file.
- When you want to stop the server, use the executable <i>plico_interferometer_server_stop</i>.



 ![Python package](https://github.com/ArcetriAdaptiveOptics/plico_interferometer_server/workflows/Python%20package/badge.svg)
 [![codecov](https://codecov.io/gh/ArcetriAdaptiveOptics/plico_interferometer_server/branch/main/graph/badge.svg?token=ApWOrs49uw)](https://codecov.io/gh/ArcetriAdaptiveOptics/plico_interferometer_server)
 [![Documentation Status](https://readthedocs.org/projects/plico_interferometer_server/badge/?version=latest)](https://plico_interferometer_server.readthedocs.io/en/latest/?badge=latest)
 [![PyPI version](https://badge.fury.io/py/plico-interferometer-server.svg)](https://badge.fury.io/py/plico-interferometer-server)


plico_interferometer is an application to control interferometers under the [plico][plico] environment.

[plico]: https://github.com/ArcetriAdaptiveOptics/plico
