# The Hands-on Guidebook for MLIP Package

written by SinsuSquid (bgkang)

안녕하세요, 이번에는 MLIP를 사용하는 방법을 hands-on guidebook으로 만들어 사람마다 하여금 쉬이 익혀 날로 쓰는 데 편하게 하고자 할 따름입니다.

본 guidebook의 목표는 'MTP 학습하고 LAMMPS 돌려봤다'에 의의를 두려 합니다. Detail은 연구실 친구들이 많이 도와줄거에요.

영어로 써볼까 했는데 포기하려고요. 본의아니게 Korean-only가 되어버렸습니다.

## Backgrounds
MTP에 관련한 설명은 발표할때 썼던 PPT 파일로 대체합니다. 대부분 아래의 논문에서 참고한 내용이니 Theory 부분을 참고하세요.

[MLIP-3: Active learning on atomic environments with moment tensor potentials](https://pubs.aip.org/aip/jcp/article/159/8/084112/2908187/MLIP-3-Active-learning-on-atomic-environments-with)

[The MLIP package: moment tensor potentials with MPI and active learning](https://iopscience.iop.org/article/10.1088/2632-2153/abc9fe)

## Installation
MTP 학습을 위해서는 MLIP-3 package가 필요하고, 이를 LAMMPS에 적용하기 위해서는 LAMMPS-MLIP-interface를 설치해야 합니다. 저보다 설명을 더 잘 해놨으니 아래 repository를 참고해서 설치해주세요.

[MLIP-3](https://gitlab.com/ashapeev/mlip-3)<br>
[Interface-LAMMPS-MLIP-3](https://gitlab.com/ivannovikov/interface-lammps-mlip-3)

아래에 진행되는 설명은 MLIP-3와 interface가 올바르게 설치되어있고 PATH에 등록되어있으며 권한 또한 잘 잡혀있다는 가정에서 출발합니다. (모르겠으면 옆에 선배 붙잡고 물어보세요.)

## MTP Training
repository를 clone하고 `MTP` 디렉토리에 들어가봅시다.

### System
제가 논문 투고하며 사용했던 LiAlCl<sub>4</sub> 시스템에 대한 MTP 학습을 목표로 합니다. 다시말해 Li-Al-Cl 성분계에서 사용 가능한 force field 학습을 목표로 한다는거죠. AIMD를 비롯한 양자계산 결과를 전부 첨부하면 엄청난 용량을 차지하기에, 이미 계산되어있는 configuration에 대한 sample database를 `.cfg`형태로 제공합니다. 실제 연구 과정에서 사용된 포텐셜과는 dataset의 규모가 큰 차이가 나기 때문에 아마 LAMMPS 구동 단계에서 문제가 발생할수도 있지만 일단 진행해보도록 하겠습니다. 여기서 규모 있는 database의 중요성을 강조할 수 있겠네요.

### MLIP-3 installation check
설치가 잘 완료되었다면, 실행시 다음과 같이 출력됩니다.
```bash
$ mlp
mlp mpi version (1 cores), (C) A. Shapeev, E. Podryabinkin, I. Novkov (Skoltech).
Usage:
mlp help			prints this message
mlp list			lists all the available commands
mlp help [command]		prints the description of the command
mlp [command] [options]		executes the command (with the options)
```
### On `.cfg`
MLIP-3는 `.cfg`라는 형태로 configuration을 읽어들입니다. 아마 개발자가 만든 format인걸로 알고있는데, 그 형태를 조금 살펴보도록 하죠.
```python
BEGIN_CFG # cfg 파일의 시작
  Size # configuration 내부 atom 수
     96
  Supercell # simulation box - vector로 표현됩니다. 단위는 Angstrom
         13.915550	 0.000000	 0.000000
          0.000000	13.118209	 0.000000
         -0.635499	 0.000000	12.834844
  AtomData: 	id	type	cartes_x	cartes_y	cartes_z	fx		fy		fz
  # id, type, coordination, force (optional)에 대한 정보가 들어가네요
		1     	0	2.236920	8.21860		6.88550		-0.820236	0.841464	-0.043385
			 ...
  Energy # 해당 configuration의 energy입니다. 단위는 eV
	  -194.463467490000
  PlusStresses:	xx		yy		zz		yz		xz		xy
  # stress (optional)에 대한 정보도 추가할 수 있네요
		24.12848	27.60932	18.90875	-7.78002	5.51385		1.66769
  Feature	EFS_by	VASP # mlp convert 를 활용하면 VASP의 OUTCAR를 바로 .cfg 형태로 변환해줍니다
END_CFG # cfg 파일의 끝
```

다시 말씀드리지만, 공개된 파일은 논문 작성하면서 사용한 dataset의 일부(25%)만 포함하고 있습니다.

### On `.almtp`
repository에는 `untrained.almtp` 파일만 업로드가 되어있습니다. MLIP-3 GitLab을 살펴보시면 `MTP_templates`라는 디렉토리가 있는데, 이 안에 있는 `.almtp`중 적당한 파일을 골라 가져오시면 됩니다. 숫자가 의미하는건 MTP의 level인데, 자세한건 MLIP-3 논문을 참고하시고 지금은 숫자가 커질수록 parameter 수가 많아진다 (더 detail한 표현이 가능하다, 학습이 어렵다, etc.)고만 이해하고 넘어갑시다. 이 guidebook에서는 `08.almtp`를 사용했습니다 (`untrained.almtp`란 이름의 파일). 파일을 열어보면 다음과 같이 구성됩니다.

```python
MTP
version = 1.1.0
potential_name = MTP1m # Potential 이름 설정 가능
species_count = 1 # type 수
potential_tag = 
radial_basis_type = RBChebyshev # Chebyshev Polynomial 사용 - 논문 참고
	min_dist = 2 # .cfg 파일 보고 update됩니다
	max_dist = 5 # r_cut
	radial_basis_size = 8 
	radial_funcs_count = 2
# 여기서부터는 학습될 parameter set입니다. 학습이 진행될수록 아래 숫자들이 변화하는걸 확인할 수 있을거에요
alpha_moments_count = 18
alpha_index_basic_count = 11
alpha_index_basic = {{0, 0, 0, 0}, {0, 1, 0, 0}, {0, 0, 1, 0}, {0, 0, 0, 1}, {0, 2, 0, 0}, {0, 1, 1, 0}, {0, 1, 0, 1}, {0, 0, 2, 0}, {0, 0, 1, 1}, {0, 0, 0, 2}, {1, 0, 0, 0}}
alpha_index_times_count = 14
alpha_index_times = {{0, 0, 1, 11}, {1, 1, 1, 12}, {2, 2, 1, 12}, {3, 3, 1, 12}, {4, 4, 1, 13}, {5, 5, 2, 13}, {6, 6, 2, 13}, {7, 7, 1, 13}, {8, 8, 2, 13}, {9, 9, 1, 13}, {0, 10, 1, 14}, {0, 11, 1, 15}, {0, 12, 1, 16}, {0, 15, 1, 17}}
alpha_scalar_moments = 9
alpha_moment_mapping = {0, 10, 11, 12, 13, 14, 15, 16, 17}
```

### MTP Training
#### Training
시작하기에 앞서, `mlp help train`을 실행해 안내문을 읽어보면, 다양한 option을 적용 가능함을 알 수 있습니다. 설명은 각자 읽어보기로 하고, 제가 train할때 사용한 command는 다음과 같아요.

```bash
$ mlp train untrained.almtp training.cfg --save_to=trained.almtp # 이 옵션을 켜야 별도의 파일로 학습 결과가 저장됩니다.
# Multi-core 지원합니다
# $ mpirun -np 6 mlp train ... 처럼 사용해보세요
```

Command를 실행하면 아래와 같이 나옵니다.
```bash
Selection data was not found in MTP and will be set
Selection by configurations is set
WARNING: File trained.almtp already exists and will be overwritten during the training procedure!
Basic trainer initialization complete
... (training details) ...
179 configurations found in the training set
Folowwing atomic numbers will be added to the MTP potential: 0, 1, 2 # 3 types of atom이 포함된 system이므로
Minimal interatomic distance in the training set is 1.44325. MTP's mindist will be updated #  training할때 distance boundary의 최솟값이 자동으로 설정됩니다
Rescaling...
	scaling = 0.8333333, condition number = 79.694617
	# 적당히 어느 범위에서 parameter를 학습할지 scaling하는 단계입니다
	... (more scaling) ...
Rescaling to 0.1019606... done # scaling 완료
MTPR training started on 1 core(s) # 진짜 학습이 시작하는 지점
BFGS iter 0: f=22.900051
... (loss values) ...	
# Scaling과 training을 번갈아가며 학습이 진행되고, loss 값이 점점 줄어드는게 보일거에요
...
____________Errors report___________
# Training set에 대한 error를 보여주며 프로그램이 종료됩니다
# MAE, RMSE, etc.
Energy: 
	Errors checked for 179 configurations
	...
```
학습 완료되는데까지 6 CPU 썼을때 20 min정도 걸렸습니다.

#### Validate Trained MTP
학습이 완료되면 학습된 potential이 test set(DFT 계산 결과) 대비 얼마나 정확한 값을 제공하는지 확인해야 합니다.

먼저 `trained.almtp`를 바탕으로 `test.cfg`에 대해 MTP로 계산된 energy를 얻어야 합니다.
```bash
$ mlp calculate_efs trained.almtp test.cfg --output_filename=out.cfg
```

`out.cfg.0`이란 이름으로 MTP를 이용해 계산된 energy, force, stress가 새로운 파일에 저장되네요.

이를 위해 `.cfg` 파일에서 각 configuration이 갖는 energy만 따로 추출하여 parity plot을 그리는 `.py` 파일을 첨부했습니다. 대충 만들었기도 했고, 어려운 일도 아니니 여러분이 직접 수정하거나 새로 만들어서 사용하세요.
```bash
$ python parity.py test.cfg out.cfg.0 figure.png # figure.png라는 이름의 이미지 파일 생성
```
해당 파일을 실행하면 MAE와 RMSE가 계산되어 figure에 포함되게끔 구성했습니다. Test와 training사이 error를 비교해보세요.

## LAMMPS using MTP
이제 `trained.almtp`를 가지고 LAMMPS를 돌려볼 차례입니다. 먼저 `trained.almtp` 파일을 `LAMMPS` 디렉토리로 복사해주세요.

아까도 말씀드린 것 처럼, 설치와 관련한 부분은 도와드리기가 어렵습니다. Interface가 올바르게 설치된 LAMMPS가 준비되어있다고 가정하고 출발할게요. 

그리고 LAMMPS 사용법에 대해서는 별도로 알려드리지 않겠습니다. 너무 규모가 커지는 것 같아요.

### System
이번에는 2,592 atom이 포함된 훨씬 더 큰 시스템에서 `trained.almtp`를 가지고 300 K, 1 bar 에서 equilibration 해보도록 하겠습니다. 제공된 `init.lammps_data`는 이미 만들어진 LiAlCl<sub>4</sub>의 glass structure입니다.

### On `input.lammps`
MLIP를 사용하기 위한 LAMMPS input을 살펴보겠습니다.
```python
variable		NSTEPS			equal	20000 # 20 ps
variable		TIMESTEP		equal	0.00100 # 1 fs timestep
variable		THERMO_FREQ		equal	100 # thermo frequency
variable		DUMP_FREQ		equal	1000 # dump frequency
variable		TEBEG			equal	300.00 # beginning temperature - 300 K
variable		TEEND			equal	300.00 # end temperature
variable		TAU_T			equal	0.10000	# temperature damping parameter
variable		PRBEG			equal	1.00000 # beginning pressure - 1 bar
variable		PREND			equal	1.00000 # end pressure
variable		TAU_P			equal	1.00000 # pressure damping temperature
variable		SEED			equal	42 # random seed

units			metal # MLIP-3 는 반드시 metal unit 사용합니다
boundary		p p p
atom_style		atomic

read_data		init.lammps_data

####################################################
pair_style		mlip load_from=trained.almtp
pair_coeff		* *
####################################################

thermo_style		custom step time temp pe ke etotal press vol density
thermo			${THERMO_FREQ}

velocity		all create ${TEBEG} ${SEED}
fix			1 all npt temp ${TEBEG} ${TEEND} ${TAU_T} iso ${PRBEG} ${PREND} ${TAU_P}

dump			1 all dcd ${DUMP_FREQ} eq.dcd
dump_modift		1 unwrap yes

timestep		${TIMESTEP}
run			${NSTEPS}
```
기존 lammps script와 다른건 강조한 부분 정도가 다인것같네요.

### Run
다음 command를 통해 LAMMPS를 구동합니다.
```bash
lmp -i input.lammps
```

시뮬레이션 결과를 확인하는건 이제 여러분께 맡기겠습니다.

### Troubleshooting
간혹 MLIP-3를 적용한 LAMMPS를 구동하다보면 아래와 같은 error를 만날수도 있을거에요.

```bash
ERROR: Lost atoms: original 2592 current 2590 (../thermo.cpp:488)
Last command: run		${NSTEPS}
```

해당 오류가 발생하는 이유는 불안정한 potential로 인해 쉽게 말해 과도한 force가 계산되어 atom이 simulation box로부터 튕겨져나갔기 때문입니다. 이 문제를 해결하는 가장 좋은 방법은 training data의 수를 늘리는 것 이지만, 또 많은 DFT 계산을 소요하게 될것이니 판단은 여러분께 맡기겠어요.

## Goodbye
아마 제가 이 guidebook을 만든 이후로는 여러분과 연락할 일은 거의 없겠지만, 무운을 빌겠습니다.

## References
- Evgeny Podryabinkin, Kamil Garifullin, Alexander Shapeev, Ivan Novikov, MLIP-3: Active learning on atomic environments with moment tensor potentials, *J. Chem. Phys.* 159, 084112 (2023)
- Ivan S Novikov, Konstantin Gubaev, Evgeny V Podryabinkin and Alexander V Shapeev, The MLIP package: moment tensor potentials with MPI and active learning, *Mach. Learn.: Sci. Technol.* 2, 025002 (2020)
- Beomgyu Kang, Shinji Saito\*, Jihyun Jang\*, and Bong June Sung\*, Cascade Hopping as Ion Conduction Mechanism in Inorganic Glass Solid-State Electrolytes (*submitted*)
